"""confirm_chain 그래프 검증."""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from confirm_chain import build_graph, rewind_target, stub_executor

FAIL = []


def check(label, cond, detail=""):
    print(("  OK   " if cond else " FAIL  ") + label + (f"  <- {detail}" if not cond and detail else ""))
    if not cond:
        FAIL.append(label)


def app(resident=None):
    return build_graph(
        executor=stub_executor,
        resident_models=(lambda: resident or []),
    ).compile(checkpointer=MemorySaver())


print("[1] subagent 트랙 — 검수 불필요 시 바로 완료")
a = app()
cfg = {"configurable": {"thread_id": "t1"}}
s = a.invoke({"track": "subagent", "task": "라우트 추가", "agent": "forge", "needs_review": False, "log": []}, cfg)
check("인터럽트 없이 완료", "__interrupt__" not in s)
check("산출물 존재", s.get("output", "").startswith("[stub:forge]"), s.get("output"))

print("\n[2] subagent 트랙 — 검수 필요 시 게이트에서 중단")
a = app()
cfg = {"configurable": {"thread_id": "t2"}}
s = a.invoke({"track": "subagent", "task": "스키마 변경", "agent": "forge", "needs_review": True, "log": []}, cfg)
check("승인 게이트에서 중단됨", "__interrupt__" in s)
s = a.invoke(Command(resume="approve"), cfg)
check("재개 후 승인됨", s.get("approved") is True)

print("\n[3] vance 트랙 — status: draft 강제 + 검수 통과 시 reviewed 전환")
a = app()
cfg = {"configurable": {"thread_id": "t3"}}
s = a.invoke({"track": "vance", "task": "가이드 초안", "log": []}, cfg)
check("검수 필요 없이는 못 넘어감", "__interrupt__" in s)
payload = s["__interrupt__"][0].value
check("중단 시점 산출물이 draft", "status: draft" in payload["산출물"], payload["산출물"][:60])
s = a.invoke(Command(resume="approve"), cfg)
check("승인 후 reviewed 로 전환", "status: reviewed" in s.get("output", ""), s.get("output", "")[:60])
check("draft 표기 제거됨", "status: draft" not in s.get("output", ""))

print("\n[4] vance 트랙 — 반려")
a = app()
cfg = {"configurable": {"thread_id": "t4"}}
a.invoke({"track": "vance", "task": "가이드 초안", "log": []}, cfg)
s = a.invoke(Command(resume="reject:근거 부족"), cfg)
check("반려 처리됨", s.get("approved") is False)
check("반려 사유 기록", s.get("rejected_reason") == "근거 부족", s.get("rejected_reason"))
check("반려 시 reviewed 로 안 바뀜", "status: draft" in s.get("output", ""))

print("\n[5] oracle 트랙 — 다른 모델 상주 시 차단 (병렬 금지)")
a = app(resident=["qwen3-coder:30b"])
cfg = {"configurable": {"thread_id": "t5"}}
s = a.invoke({"track": "oracle", "task": "아키텍처 검증", "log": []}, cfg)
check("차단됨", bool(s.get("blocked_reason")), s.get("blocked_reason"))
check("oracle 호출 안 됨", not s.get("output"))
check("차단 사유에 상주 모델명 포함", "qwen3-coder:30b" in s.get("blocked_reason", ""))

print("\n[6] oracle 트랙 — 상주 모델 없으면 실행")
a = app(resident=[])
cfg = {"configurable": {"thread_id": "t6"}}
s = a.invoke({"track": "oracle", "task": "아키텍처 검증", "log": []}, cfg)
check("차단 없음", not s.get("blocked_reason"))
check("oracle 산출물 존재", s.get("output", "").startswith("[stub:oracle]"))

print("\n[7] process_doc 트랙 — 승인 없이는 절대 통과 못 함")
a = app()
cfg = {"configurable": {"thread_id": "t7"}}
s = a.invoke({"track": "process_doc", "task": "PROCESS_GUIDE 개정", "needs_review": False, "log": []}, cfg)
check("needs_review=False 여도 중단됨", "__interrupt__" in s)

print("\n[8] 체크포인트 이력 / 롤백")
a = app()
cfg = {"configurable": {"thread_id": "t8"}}
a.invoke({"track": "vance", "task": "롤백 대상", "log": []}, cfg)
s = a.invoke(Command(resume="approve"), cfg)
check("1차 결정 = 승인", s.get("approved") is True)
hist = list(a.get_state_history(cfg))
check("체크포인트 이력 2건 이상", len(hist) >= 2, f"{len(hist)}건")

# 인터럽트가 걸린 체크포인트에서 그대로 재개하면 저장된 결정이 재생된다.
# 결정을 바꾸려면 인터럽트를 만든 노드 이전 시점에서 포크해야 한다.
target = rewind_target(a, cfg)
check("되감을 지점을 찾음", target is not None)
if target is not None:
    check("되감을 지점이 게이트 이전", target.next == ("vance_draft",), str(target.next))
    s2 = a.invoke(None, target.config)
    check("되감은 뒤 승인 게이트 재발생", "__interrupt__" in s2)
    s3 = a.invoke(Command(resume="reject:다시 판단"), cfg)
    check("되감은 뒤 다른 결정 적용됨", s3.get("approved") is False, str(s3.get("approved")))
    check("반려 사유 기록", s3.get("rejected_reason") == "다시 판단")
    check("반려이므로 draft 유지", "status: draft" in s3.get("output", ""))

print("\n[9] 인터럽트 지점 그대로 재개 시 이전 결정이 재생된다 (알려진 의미론)")
a = app()
cfg = {"configurable": {"thread_id": "t9"}}
a.invoke({"track": "vance", "task": "재생 확인", "log": []}, cfg)
a.invoke(Command(resume="approve"), cfg)
gate = [h for h in a.get_state_history(cfg) if any(t.interrupts for t in h.tasks)][0]
s4 = a.invoke(Command(resume="reject:무시될 결정"), gate.config)
check("게이트 지점 재개는 새 결정을 반영하지 않음", s4.get("approved") is True,
      "이 동작이 바뀌면 rewind_target 설명을 갱신해야 한다")

print()
if FAIL:
    print(f"실패 {len(FAIL)}건: {FAIL}")
    raise SystemExit(1)
print("전체 통과")
