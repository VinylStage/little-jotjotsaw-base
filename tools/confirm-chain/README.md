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

### 승인 상태 조회 (기계 판독용)

`--history` 는 사람이 읽는 이력이고, `--status` 는 단일 상태값으로 환원해 스크립트가 분기할 수 있게 합니다. 커밋 훅이 이걸 씁니다.

```bash
poetry run python confirm_chain.py --status --thread guide
# {"state": "approved", "track": "process_doc", "thread": "guide"}
```

| state | 종료코드 | 의미 |
|---|---|---|
| `approved` | `0` | 승인됨 |
| `pending` | `2` | 승인 대기 중 |
| `rejected` | `1` | 반려됨 |
| `none` | `1` | 해당 스레드 없음 (또는 검수를 거치지 않고 끝난 스레드) |

---

## 문서 변경 게이트 (커밋 훅 배선)

`process_doc` 트랙을 **커밋 시점에 강제**합니다. 감시 경로의 문서가 스테이징돼 있는데 승인이 없으면 커밋이 중단됩니다.

### 설치

```bash
./install-hooks.sh <대상 저장소 경로> '<감시 glob>' ['<감시 glob>' ...]

# 예
./install-hooks.sh ~/work/some-repo 'docs/process/*'
./install-hooks.sh ~/work/other-repo 'docs/audit/*' 'docs/decisions/*'
```

설치되는 것:

| 대상 | 추적 여부 | 내용 |
|---|---|---|
| `.githooks/pre-commit` | 추적됨 | 게이트 본체 |
| `.githooks/prepare-commit-msg` | 추적됨 | `Doc-Approval:` 트레일러 부착 |
| `.confirm-chain-paths` | 추적됨 | 감시 glob 목록 (저장소별) |
| `core.hooksPath`, `confirmchain.dir` | **로컬 설정** | 도구 절대경로가 커밋되지 않도록 git config 에 둡니다 |
| `.gitignore` | 추적됨 | 체크포인트 DB 제외 |

### 동작

```
git commit
   │
   ├─ 감시 경로에 스테이징된 문서 없음 ──────────────► 통과
   │
   └─ 있음 → 스테이징된 diff 내용을 해시해 스레드 ID 생성
              │
              ├─ 승인됨(exit 0) ──► 통과 + Doc-Approval 트레일러 부착
              ├─ 승인 대기(exit 2) ► 중단, 재개 명령 안내
              └─ 없음/반려(exit 1) ► 중단, 승인 절차 안내
```

**스레드 ID는 내용 해시입니다.** 문서를 한 글자라도 고치면 다른 스레드가 되므로 이전 승인이 자동으로 무효화됩니다 — 승인 한 번으로 이후 변경까지 덮는 것을 막습니다.

### 우회

`git commit --no-verify` 로 건너뛸 수 있습니다. 다만 그 커밋에는 `Doc-Approval` 트레일러가 없으므로, 사후에 트레일러만 훑으면 우회 이력이 그대로 드러납니다.

```bash
# 감시 경로 문서를 건드렸는데 승인 트레일러가 없는 커밋 찾기
git log --format='%H %s' --name-only -- 'docs/process/*' | ...
git log --format='%H %(trailers:key=Doc-Approval)' -20
```

### 알려진 한계

- **오케스트레이터가 스스로 `--resume approve` 를 할 수 있습니다.** 게이트는 "승인 절차를 거쳤는가"를 강제할 뿐 "누가 승인했는가"는 검증하지 않습니다. 자기 작업을 자기가 승인하면 게이트는 형식만 남습니다 — 실질 검수 지점은 PR 리뷰로 두고, 이 게이트는 *승인 없이 조용히 지나가는 것*을 막는 용도로 쓰는 것이 현재 설계입니다.
- 훅은 `bash` 3.2(macOS 기본)에서 동작하도록 작성했습니다. `mapfile` 등 bash 4 문법을 추가하지 마세요 — 초판이 이 문제로 위반을 놓친 적이 있습니다.
- 게이트를 수정했다면 **반드시 의도적으로 실패시켜 빨간불을 확인**하세요.

## 컨펌 체인 규칙이 코드에서 강제되는 지점

| 규칙 | 강제 방식 |
|---|---|
| VANCE 초안은 `status: draft` 로 시작 | 산출물에 표기가 없으면 자동으로 앞에 붙입니다 |
| 검수를 통과해야 `reviewed` 로 전환 | 승인 시에만 `draft` → `reviewed` 치환. 반려 시 `draft` 유지 |
| 산출물이 파일이면 그 파일도 전환 | 승인 시 산출물 문자열에 적힌 `.md` 경로를 찾아, 실재하고 `status: draft` 인 것만 바꿉니다. 셋 중 하나라도 어긋나면 건드리지 않습니다 |
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
