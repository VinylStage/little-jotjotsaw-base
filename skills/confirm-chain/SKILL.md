---
name: confirm-chain
description: 에이전트 위임 작업을 컨펌 체인 상태그래프로 실행해, 사람 검수·승인 지점에서 반드시 멈추게 한다. 사용자가 "컨펌 체인", "승인 게이트", "confirm chain"을 언급하거나, VANCE 초안 작성·프로세스 문서 변경·ORACLE 호출처럼 사람 승인이 필요한 위임을 요청할 때 사용한다.
---

이 스킬은 이 플러그인의 `tools/confirm-chain/confirm_chain.py` 를 실행해서 `docs/diagrams/agent-org-confirm-chain.md` 의 컨펌 체인을 강제한다.

## 이 스킬을 쓰는 이유

위임 결과를 사람 확인 없이 그대로 반영하는 것을 막기 위해서다. 승인 게이트는 코드로 강제되며 우회 인자가 없다.

## 실행 전 확인 (전제조건)

아래를 먼저 확인하고, 실패하면 사용자에게 무엇이 안 되어 있는지 알려주고 중단한다.

1. **Python 3.10+ 및 Poetry**: `poetry --version`
2. **의존성 설치**: `tools/confirm-chain` 에서 `poetry install`
3. **opencode 서브에이전트**: `opencode agent list` 에 `forge`, `vance`, `oracle` 이 있는지 확인 (`--stub` 사용 시 불필요)
4. **Ollama 실행 중**: ORACLE 트랙을 쓸 때만 필요

## 실행

```bash
cd tools/confirm-chain
poetry run python confirm_chain.py <track> "<작업 설명>" --thread <ID>
```

트랙 선택 기준:

| 상황 | track |
|---|---|
| 코드/구현 위임 | `subagent` (검수가 필요하면 `--needs-review`) |
| 문서 초안 작성 | `vance` |
| 아키텍처 검증·심층 분석 | `oracle` |
| 프로세스 문서 변경 | `process_doc` |

## 종료 코드로 분기할 것

| 코드 | 의미 | 에이전트가 할 일 |
|---|---|---|
| `0` | 완료 | 결과 JSON을 사용자에게 요약 보고 |
| `1` | 사용 오류 / 되감을 지점 없음 | 오류 메시지를 그대로 전달 |
| `2` | **승인 대기** | **여기서 멈추고 사용자에게 승인을 요청한다** |

## 승인 대기 시 반드시 지킬 것

- **종료 코드 2 는 사용자 판단이 필요하다는 뜻이다. 에이전트가 대신 승인하지 않는다.** 출력된 산출물을 사용자에게 보여주고 승인 여부를 물은 뒤, 답을 받고 나서 재개한다.
- 재개: `--resume approve` 또는 `--resume "reject:<사유>"`
- 결정을 번복해야 하면 `--rewind` 로 게이트를 다시 연 뒤 재개한다. 게이트 지점에서 그대로 재개하면 이전 결정이 재생되므로 새 결정이 반영되지 않는다.

## 결과 해석 시 주의

- `blocked_reason` 이 있으면 위임이 실행되지 않은 것이다. ORACLE 트랙에서는 다른 모델이 상주 중이라는 뜻이므로, 모델을 내린 뒤 재시도할지 사용자에게 확인한다.
- 산출물의 `status: draft` 는 검수 전이라는 표시다. 승인 없이 `reviewed` 로 바꾸지 않는다.
- 위임 산출물은 로컬 모델 출력이므로 그대로 사실로 옮기지 말고, 확인된 내용인지 구분해서 전달한다.

## 참고

- 상세 사용법·되감기 의미론·제한사항: `tools/confirm-chain/README.md`
- 구현 대상 다이어그램: `docs/diagrams/agent-org-confirm-chain.md`
