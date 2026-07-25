# confirm-chain

[에이전트 조직도 및 컨펌 체인](../../docs/diagrams/agent-org-confirm-chain.md) 다이어그램을 LangGraph 상태그래프로 구현한 것입니다. 사람 검수·승인 지점을 `interrupt()` 로 강제하고, 결정 이력은 체크포인트에 남겨 되돌릴 수 있게 합니다.

특정 프로젝트에 종속되지 않습니다. 위임 실행기(executor)는 주입 가능하며, 기본 실행기는 opencode 를 헤드리스로 호출합니다.

## 사전 요구사항

- **Python 3.10+**
- **Poetry**: 의존성 설치에 사용합니다.
- **opencode**: 기본 실행기가 호출합니다. `forge`, `vance`, `oracle` 서브에이전트가 정의돼 있어야 합니다. (`--stub` 으로 실행하면 불필요)
- **Ollama**: ORACLE 트랙의 리소스 확인에 `ollama ps` 를 사용합니다. (`--stub` 으로 실행하면 불필요)

## 설치

```bash
cd tools/confirm-chain
poetry install
```

## 사용법

### 새 실행

```bash
poetry run python confirm_chain.py <track> "<작업 설명>" [옵션]
```

`<track>` 은 다이어그램의 4개 진입 경로에 대응합니다.

| track | 대응 노드 | 승인 게이트 |
|---|---|---|
| `subagent` | 서브에이전트 위임 | `--needs-review` 지정 시에만 |
| `vance` | VANCE 위임 → 자동 초안 작성 | **항상** |
| `oracle` | ORACLE 호출 → 리소스 확인 → 순차 실행 | 없음 (리소스 게이트가 대신) |
| `process_doc` | 프로세스 문서 변경 | **항상** (`--needs-review` 무관) |

주요 옵션:

- `--agent <이름>` — `subagent` 트랙에서 사용할 에이전트 (기본 `forge`)
- `--thread <ID>` — 체크포인트 스레드 ID (기본 `default`)
- `--needs-review` — `subagent` 트랙 산출물도 검수를 거칩니다
- `--db <경로>` — 체크포인트 DB 경로 (기본 `.confirm-chain.sqlite`)
- `--stub` — 실제 모델을 호출하지 않는 검증용 실행기를 사용합니다

### 승인 대기와 재개

승인 게이트에 걸리면 대기 상태로 종료됩니다. 체크포인트가 파일에 저장되므로 **다른 프로세스에서 이어서 재개**할 수 있습니다.

```bash
poetry run python confirm_chain.py vance "운영 가이드 초안" --thread guide
# => 승인 대기 내용 출력, 종료 코드 2

poetry run python confirm_chain.py --resume approve --thread guide
poetry run python confirm_chain.py --resume "reject:근거 부족" --thread guide
```

종료 코드로 분기할 수 있습니다.

| 코드 | 의미 |
|---|---|
| `0` | 완료 |
| `1` | 사용 오류 또는 되감을 지점 없음 |
| `2` | **승인 대기 중** |

### 이력 조회와 되감기

```bash
poetry run python confirm_chain.py --history --thread guide
poetry run python confirm_chain.py --rewind  --thread guide
```

## 컨펌 체인 규칙이 코드에서 강제되는 지점

| 규칙 | 강제 방식 |
|---|---|
| VANCE 초안은 `status: draft` 로 시작 | 산출물에 표기가 없으면 자동으로 앞에 붙입니다 |
| 검수를 통과해야 `reviewed` 로 전환 | 승인 시에만 `draft` → `reviewed` 치환. 반려 시 `draft` 유지 |
| 프로세스 문서 변경은 승인 필수 | 게이트를 우회할 수 있는 인자가 없습니다 |
| ORACLE 은 순차 실행만 | `ollama ps` 로 상주 모델을 확인해, 하나라도 있으면 호출하지 않고 차단 사유를 남깁니다 |

## 되감기 의미론 — 반드시 알아둘 것

**승인 게이트가 걸린 체크포인트에서 그대로 재개하면 이미 내린 결정이 재생됩니다.** 그 시점에는 결정 값이 이미 기록돼 있기 때문입니다.

결정을 번복하려면 **게이트를 만든 노드 이전 시점으로 되감아** 게이트를 다시 발생시켜야 합니다. `--rewind` 가 그 지점을 찾아 포크합니다.

```bash
poetry run python confirm_chain.py --rewind --thread guide          # 게이트 재발생
poetry run python confirm_chain.py --resume "reject:다시 판단" --thread guide
```

이 동작은 `test_confirm_chain.py` 의 케이스 9에 회귀 테스트로 고정돼 있습니다. LangGraph 쪽 동작이 바뀌면 그 테스트가 먼저 깨집니다.

## 검증

```bash
cd tools/confirm-chain
poetry run python test_confirm_chain.py
```

실제 모델을 호출하지 않는 스텁 실행기로 4개 트랙, 승인·반려, ORACLE 차단, 체크포인트 되감기를 검증합니다.

## 프로세스 문서 연계

- 구현 대상 다이어그램: [docs/diagrams/agent-org-confirm-chain.md](../../docs/diagrams/agent-org-confirm-chain.md)
- 에이전트 역할과 ORACLE 호출 규칙: [docs/process/AGENT_SYSTEM.md](../../docs/process/AGENT_SYSTEM.md)

## 제한사항

- **사람의 판단을 대체하지 않습니다.** 승인 게이트는 판단을 강제하는 장치이지 대신 내려주는 장치가 아닙니다.
- 기본 실행기는 opencode 에 위임하므로, 위임된 에이전트가 파일을 수정할 수 있습니다. 실행 디렉토리에 주의하세요.
- ORACLE 리소스 확인은 `ollama ps` 결과에만 의존합니다. 다른 방식으로 메모리를 점유하는 프로세스는 감지하지 못합니다.
- 체크포인트 DB에는 작업 내용과 산출물이 그대로 저장됩니다. 민감한 내용을 다뤘다면 DB 파일 관리에 주의하세요.
