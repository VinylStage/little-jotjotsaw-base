"""에이전트 컨펌 체인을 LangGraph 상태그래프로 구현한다.

`docs/diagrams/agent-org-confirm-chain.md` 의 흐름을 1:1로 옮긴 것이다.
사람 검수/승인 지점은 interrupt() 로, 롤백은 checkpointer 의 이력으로 처리한다.

특정 프로젝트에 종속되지 않는다. 위임 실행기(executor)는 주입 가능하며,
기본 실행기는 opencode 를 헤드리스로 호출한다.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

# 다이어그램의 4개 진입 트랙
TrackName = Literal["subagent", "vance", "oracle", "process_doc"]

# ORACLE 이 요구하는 여유 메모리 (GB). 42GB 모델 + 여유분 기준.
ORACLE_REQUIRED_FREE_GB = 44.0


class ChainState(TypedDict, total=False):
    track: TrackName
    task: str
    agent: str
    output: str
    needs_review: bool
    approved: bool
    rejected_reason: str
    blocked_reason: str
    log: list[str]


@dataclass
class DelegationResult:
    ok: bool
    output: str
    detail: str = ""


Executor = Callable[[str, str], DelegationResult]
"""(agent, prompt) -> DelegationResult"""


def opencode_executor(agent: str, prompt: str) -> DelegationResult:
    """opencode 를 헤드리스로 호출한다."""
    if shutil.which("opencode") is None:
        return DelegationResult(False, "", "opencode 실행 파일을 찾을 수 없다")
    try:
        proc = subprocess.run(
            ["opencode", "run", "--agent", agent, prompt],
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        return DelegationResult(False, "", f"{agent} 호출이 30분 내에 끝나지 않았다")
    if proc.returncode != 0:
        return DelegationResult(False, "", f"{agent} 종료코드 {proc.returncode}: {proc.stderr[-500:]}")
    return DelegationResult(True, proc.stdout.strip())


def stub_executor(agent: str, prompt: str) -> DelegationResult:
    """실제 모델을 호출하지 않는 검증용 실행기."""
    return DelegationResult(True, f"[stub:{agent}] {prompt[:60]}")


def _resident_models() -> list[str]:
    """현재 Ollama 에 상주 중인 모델 목록."""
    if shutil.which("ollama") is None:
        return []
    try:
        proc = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return []
    if proc.returncode != 0:
        return []
    lines = [ln for ln in proc.stdout.splitlines()[1:] if ln.strip()]
    return [ln.split()[0] for ln in lines]


def build_graph(
    executor: Executor = opencode_executor,
    resident_models: Callable[[], list[str]] = _resident_models,
) -> StateGraph:
    def _log(state: ChainState, msg: str) -> list[str]:
        return [*state.get("log", []), msg]

    # 다이어그램: Claude Code --> 각 트랙
    def dispatch(state: ChainState) -> ChainState:
        return {"log": _log(state, f"dispatch -> {state['track']}")}

    # 다이어그램: 서브에이전트 위임
    def delegate_subagent(state: ChainState) -> ChainState:
        agent = state.get("agent") or "forge"
        result = executor(agent, state["task"])
        if not result.ok:
            return {"blocked_reason": result.detail, "log": _log(state, f"subagent 실패: {result.detail}")}
        return {"output": result.output, "log": _log(state, f"subagent({agent}) 완료")}

    # 다이어그램: VANCE 위임 --> 자동 초안 작성 (status: draft)
    def vance_draft(state: ChainState) -> ChainState:
        result = executor("vance", state["task"])
        if not result.ok:
            return {"blocked_reason": result.detail, "log": _log(state, f"vance 실패: {result.detail}")}
        output = result.output
        # 초안은 반드시 검수 전 상태로 표기된다. 누락 시 보정한다.
        if "status: draft" not in output:
            output = f"---\nstatus: draft\n---\n{output}"
            note = "vance 완료 (status: draft 보정됨)"
        else:
            note = "vance 완료"
        # VANCE 초안은 항상 사람 검수를 거친다.
        return {"output": output, "needs_review": True, "log": _log(state, note)}

    # 다이어그램: ORACLE 호출 --> 리소스 확인 --> 순차 실행만 허용
    def oracle_guard(state: ChainState) -> ChainState:
        resident = resident_models()
        if resident:
            reason = f"다른 모델이 상주 중이라 ORACLE 을 실행하지 않는다: {', '.join(resident)}"
            return {"blocked_reason": reason, "log": _log(state, f"oracle 차단: {reason}")}
        return {"log": _log(state, "oracle 리소스 확인 통과")}

    def oracle_call(state: ChainState) -> ChainState:
        result = executor("oracle", state["task"])
        if not result.ok:
            return {"blocked_reason": result.detail, "log": _log(state, f"oracle 실패: {result.detail}")}
        return {"output": result.output, "log": _log(state, "oracle 완료")}

    # 다이어그램: 프로세스 문서 변경 --> 승인 필요
    def process_doc_change(state: ChainState) -> ChainState:
        # 프로세스 문서 변경은 예외 없이 승인을 받는다.
        return {"output": state["task"], "needs_review": True, "log": _log(state, "프로세스 문서 변경 준비")}

    # 다이어그램: 사람 검수 / 승인
    def human_review(state: ChainState) -> ChainState:
        decision = interrupt(
            {
                "track": state["track"],
                "질문": "이 산출물을 승인하는가?",
                "산출물": state.get("output", ""),
                "응답형식": "approve | reject:<사유>",
            }
        )
        text = str(decision).strip()
        if text == "approve":
            output = state.get("output", "")
            # 검수를 통과한 초안만 reviewed 로 전환된다.
            output = output.replace("status: draft", "status: reviewed")
            return {"approved": True, "output": output, "log": _log(state, "사람 검수: 승인")}
        reason = text.split(":", 1)[1].strip() if text.startswith("reject:") else text
        return {"approved": False, "rejected_reason": reason, "log": _log(state, f"사람 검수: 반려 ({reason})")}

    def finalize(state: ChainState) -> ChainState:
        return {"log": _log(state, "완료")}

    # --- 라우팅 ---
    def route_track(state: ChainState) -> str:
        return {
            "subagent": "delegate_subagent",
            "vance": "vance_draft",
            "oracle": "oracle_guard",
            "process_doc": "process_doc_change",
        }[state["track"]]

    def route_after_work(state: ChainState) -> str:
        if state.get("blocked_reason"):
            return "finalize"
        return "human_review" if state.get("needs_review") else "finalize"

    def route_after_guard(state: ChainState) -> str:
        return "finalize" if state.get("blocked_reason") else "oracle_call"

    g = StateGraph(ChainState)
    g.add_node("dispatch", dispatch)
    g.add_node("delegate_subagent", delegate_subagent)
    g.add_node("vance_draft", vance_draft)
    g.add_node("oracle_guard", oracle_guard)
    g.add_node("oracle_call", oracle_call)
    g.add_node("process_doc_change", process_doc_change)
    g.add_node("human_review", human_review)
    g.add_node("finalize", finalize)

    g.add_edge(START, "dispatch")
    g.add_conditional_edges("dispatch", route_track)
    g.add_conditional_edges("delegate_subagent", route_after_work)
    g.add_conditional_edges("vance_draft", route_after_work)
    g.add_conditional_edges("oracle_guard", route_after_guard)
    g.add_conditional_edges("oracle_call", route_after_work)
    g.add_conditional_edges("process_doc_change", route_after_work)
    g.add_edge("human_review", "finalize")
    g.add_edge("finalize", END)
    return g


def rewind_target(app, cfg):
    """결정을 다시 내리기 위해 되감을 체크포인트를 찾는다.

    인터럽트가 걸린 체크포인트에서 그대로 재개하면 이미 저장된 결정이 재생된다.
    결정을 바꾸려면 인터럽트를 만든 노드 **이전** 시점에서 포크해야 한다.
    """
    hist = list(app.get_state_history(cfg))
    for i, snap in enumerate(hist):
        if any(t.interrupts for t in snap.tasks):
            # 이력은 최신 -> 과거 순이므로 다음 원소가 직전 시점이다.
            return hist[i + 1] if i + 1 < len(hist) else None
    return None


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="에이전트 컨펌 체인 실행")
    p.add_argument("track", nargs="?", choices=["subagent", "vance", "oracle", "process_doc"])
    p.add_argument("task", nargs="?", help="위임할 작업 설명")
    p.add_argument("--agent", default="forge", help="subagent 트랙에서 사용할 에이전트 (기본 forge)")
    p.add_argument("--thread", default="default", help="체크포인트 스레드 ID")
    p.add_argument("--needs-review", action="store_true", help="subagent 트랙 산출물도 검수를 거친다")
    p.add_argument("--resume", help="중단된 스레드를 재개한다: approve 또는 reject:<사유>")
    p.add_argument("--rewind", action="store_true",
                   help="이미 내린 결정을 취소하고 승인 게이트 직전으로 되감는다")
    p.add_argument("--history", action="store_true", help="스레드의 체크포인트 이력을 출력하고 종료")
    p.add_argument("--db", default=".confirm-chain.sqlite", help="체크포인트 DB 경로")
    p.add_argument("--stub", action="store_true", help="실제 모델을 호출하지 않고 검증용 실행기를 쓴다")
    args = p.parse_args(argv)

    if not (args.resume or args.rewind or args.history) and not (args.track and args.task):
        p.error("track 과 task 는 새 실행에 필수다")

    executor = stub_executor if args.stub else opencode_executor
    cfg = {"configurable": {"thread_id": args.thread}}

    with SqliteSaver.from_conn_string(args.db) as saver:
        app = build_graph(executor=executor).compile(checkpointer=saver)

        if args.history:
            for snap in app.get_state_history(cfg):
                pending = "인터럽트대기" if any(t.interrupts for t in snap.tasks) else ""
                print(f"{snap.config['configurable'].get('checkpoint_id')} next={snap.next} {pending}")
            return 0

        if args.rewind:
            target = rewind_target(app, cfg)
            if target is None:
                print("되감을 지점을 찾지 못했다. 이 스레드에 대기 중인 승인 게이트가 없다.")
                return 1
            state = app.invoke(None, target.config)
        elif args.resume:
            state = app.invoke(Command(resume=args.resume), cfg)
        else:
            state = app.invoke(
                {
                    "track": args.track,
                    "task": args.task,
                    "agent": args.agent,
                    "needs_review": args.needs_review,
                    "log": [],
                },
                cfg,
            )

        if "__interrupt__" in state:
            payload = state["__interrupt__"][0].value
            print("=== 승인 대기 ===")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            print(f"\n재개: --thread {args.thread} --resume approve  (또는 --resume 'reject:사유')")
            return 2

        print(json.dumps(
            {k: v for k, v in state.items() if k != "__interrupt__"},
            ensure_ascii=False,
            indent=2,
        ))
        return 0


if __name__ == "__main__":
    sys.exit(main())
