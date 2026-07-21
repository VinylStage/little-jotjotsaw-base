# VinylStage 프로젝트 공통 프로세스 가이드

> 이 문서는 finance-tracker 개발 과정에서 정립된 모든 컨벤션, 워크플로우, 에이전트 운영 방식을 담은 공통 자산입니다.
> 새 프로젝트를 시작할 때 이 파일을 복사해서 프로젝트 루트에 `CLAUDE.md`로 두세요.

---

## 1. 에이전트 조직 구조

```
User (총사령관, 최종 컨펌)
 └── EVA (Claude Cowork, 오케스트레이터)
      ├── AXEL (Claude Code, bash 실행 + 로직 설계)
      │    ├── FORGE (qwen3-coder:30b, 코드/UI 구현)
      │    └── VANCE (qwen3-30b-32k, 문서/범용 실무)
      ├── NEXUS (보조 Cowork, 계획 수립 + 스케줄링)
      └── ORACLE (deepseek-r1:70b, 고난이도 추론 — 단독 동기 호출만)
```

### 역할 분리 원칙

| 에이전트 | 역할 | 금지 |
|---|---|---|
| EVA | 요구사항 명세화, 에이전트 할당, 컨펌 체인 관리 | 코드 직접 작성 금지 |
| AXEL | bash 실행, 로직 설계, FORGE/VANCE에 명세 위임 | 직접 구현 금지 (명세 전달만) |
| FORGE | 코드/UI 구현 (속도 우선) | — |
| VANCE | 문서 작성, 이메일, 분석 (균형형 32K ctx) | — |
| ORACLE | 복잡한 추론, 아키텍처 결정, 심층 분석 | 동시 다중 호출 절대 금지 |

### 컨펌 체인

```
FORGE/VANCE/ORACLE (구현)
  → AXEL/NEXUS (1차 검증)
    → EVA (2차 컨펌 + 사용자 보고)
      → User (최종 승인)
```

### ORACLE 호출 규칙 (48GB RAM 제약)

```bash
# 필수 순서
pkill -f "curl.*11434" 2>/dev/null; sleep 2
curl -s http://localhost:11434/api/tags > /dev/null || echo "Ollama 응답 없음"
curl -s --max-time 480 http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:70b","prompt":"...","stream":false}'
```

- ORACLE 응답 기준: 4096 ctx, 1200 tokens → 3~5분. 8분 초과 시 kill 후 재시도
- VANCE/FORGE 활성 중 ORACLE 동시 로드 금지 (OOM 위험)

---

## 2. GitHub 프로젝트 관리 구조

### 계층 구조

```
GitHub Project (칸반 보드)
 └── Milestone (Phase 단위, 큰 기능 묶음)
      └── Issue (Feature 단위, 구체적 작업)
           └── 이슈 본문 체크리스트 (Task 단위)
```

### 이슈 생성 템플릿

```bash
gh issue create \
  --title "[Phase N] 기능명" \
  --body "## 목표
...

## 완료 기준
- [ ] Task 1
- [ ] Task 2

## 기술 메모
..." \
  --milestone "Phase N" \
  --label "enhancement"
```

### 마일스톤 생성

```bash
gh api repos/{owner}/{repo}/milestones \
  -f title="Phase N — 설명" \
  -f description="..." \
  -f state="open"
```

### 프로젝트 보드 연동

```bash
# 프로젝트 목록 확인
gh project list --owner {owner}

# 이슈를 프로젝트에 추가
gh project item-add {project-number} --owner {owner} --url {issue-url}
```

### 라벨 컨벤션

| 라벨 | 용도 |
|---|---|
| `enhancement` | 새 기능 |
| `bug` | 버그 수정 |
| `documentation` | 문서 작업 |
| `phase:N` | Phase 구분 보조 |
| `backend` / `frontend` | 영역 구분 |
| `ux` | UI/UX 개선 |

---

## 3. Git 커밋 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 준수.

```
<type>(<scope>): <subject>

feat(dashboard): 월별 수입/지출 영역 차트 추가
fix(api): 할부 이중계산 버그 수정
style(ui): slate 라이트 테마 전환
docs(arch): ARCHITECTURE.md DB 스키마 갱신
chore: .gitignore data/ ref/ 추가
refactor(routes): 트랜잭션 집계 쿼리 분리
test: 대시보드 API 합계 검증 스크립트 추가
```

### 타입 목록

| 타입 | 용도 |
|---|---|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `style` | UI/스타일 (로직 변경 없음) |
| `refactor` | 리팩토링 (기능 변경 없음) |
| `docs` | 문서만 변경 |
| `chore` | 빌드/설정/의존성 |
| `test` | 테스트 추가/수정 |
| `perf` | 성능 개선 |

### 브랜치 전략

```
main          ← 프로덕션 (force-push 절대 금지)
feat/*        ← 기능 개발
fix/*         ← 버그 수정
chore/*       ← 설정/의존성
```

- PR → main: squash and merge
- 커밋마다 푸시 권장 (작업 중간 손실 방지)

---

## 4. Release-please 설정

```yaml
# .github/workflows/release-please.yml
name: Release Please
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node  # 또는 python, simple 등
```

```json
// release-please-config.json
{
  "packages": {
    ".": {
      "release-type": "node",
      "bump-minor-pre-major": true
    }
  }
}
```

- `feat:` 커밋 → 마이너 버전 bump (0.x.0)
- `fix:` 커밋 → 패치 버전 bump (0.0.x)
- `feat!:` 또는 `BREAKING CHANGE:` → 메이저 버전 bump

---

## 5. 코드 스타일 규칙

### 파일명 / 문서명

- **파일명**: 영어만 (예: `ARCHITECTURE.md`, `PROCESS_GUIDE.md`)
- **문서 내용**: 한국어로 작성 (README 제외 — GitHub 표준으로 영어 가능)
- **코드 주석**: 한국어 (본인이 보기 편하게)
- **코드 자체 (변수명, 함수명, API 경로)**: 영어

### Config 파일

- 주석 절대 불허 (JSON은 주석 불가, YAML도 최소화)
- 모든 설정 설명은 별도 `docs/*.md` 또는 `ARCHITECTURE.md`에 기록

### .gitignore 필수 항목

```gitignore
# 데이터 파일 절대 커밋 금지
data/
*.db
*.sqlite
*.sqlite3
ref/
*.xlsx
*.xls
*.csv

# 환경 설정
.env
.env.*
!.env.example

# 빌드
node_modules/
dist/
public/
__pycache__/
*.pyc
.venv/
```

---

## 6. 환경변수 관리

```bash
# .env (절대 커밋 금지)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
PORT=3000

# .env.example (커밋 OK — 키만, 값 없음)
DISCORD_WEBHOOK_URL=
PORT=3000
```

- 하드코드 절대 금지
- 민감 정보는 환경변수만

---

## 7. UI/UX 테마 컨벤션 (웹앱)

2025~2026 핀테크 트렌드 기반 슬레이트 라이트 테마 채택.

| 역할 | Tailwind 클래스 | 색상 |
|---|---|---|
| 배경 | `bg-slate-50` | #f8fafc |
| 카드 | `bg-white shadow-sm` | 흰색 |
| 테두리 | `border-slate-200` | 연회색 |
| 본문 텍스트 | `text-slate-800` | 진회색 |
| 보조 텍스트 | `text-slate-500` | 중간회색 |
| Primary | `text-indigo-700 / bg-indigo-50` | 인디고 |
| 수입 | `text-emerald-600` | 에메랄드 |
| 지출 | `text-rose-600` | 로즈 |
| 호버 | `hover:bg-slate-50` | 연슬레이트 |
| 입력 | `bg-white border border-slate-300` | 흰색 테두리 |

---

## 8. 백엔드 패턴 (Node.js + better-sqlite3)

### DB 마이그레이션 원칙

- **새 테이블**: `CREATE TABLE IF NOT EXISTS`
- **기존 테이블 컬럼 추가**: `ALTER TABLE ... ADD COLUMN` (기존 데이터 보존)
- **데이터 삭제 없이 논리적 삭제**: `is_active = 0` 패턴
- **절대 금지**: `DROP TABLE`, `TRUNCATE`, 스키마 재생성으로 기존 데이터 손실

```js
// ALTER TABLE 예시 (init.js에서 안전하게)
try {
  db.exec(`ALTER TABLE debts ADD COLUMN type TEXT DEFAULT '일반'`);
} catch (e) {
  if (!e.message.includes('duplicate column')) throw e;
  // 이미 존재하면 무시
}
```

### API 응답 구조

```json
// 성공
{ "data": [...], "total": 42 }

// 오류
{ "error": "설명 메시지" }
```

### 이중계산 방지 (할부/리볼빙)

```
가용현금 =
  수입 합계
  - 지출 합계 (payment_style NOT IN ('할부', '리볼빙'))
  - 이번달 청구 예정 할부 monthly_amount 합계 (status='진행중')
  - 이번달 리볼빙 paid_amount 합계
```

---

## 9. Discord MCP 알림 패턴

MCP 서버: `~/vinylstudio/discord-mcp-alert`

### 이벤트 타입

| event_type | 색상 | 용도 |
|---|---|---|
| `success` | 초록 | 단계 성공 |
| `error` | 빨강 | 오류 발생 |
| `warning` | 노랑 | 주의 필요 |
| `info` | 파랑 | 일반 알림 |
| `start` | 하늘 | 작업 시작 |
| `complete` | 밝은 초록 | 전체 완료 |
| `ask` | 핑크 | 사용자 확인 요청 |
| `phase` | 보라 | Phase 진행 보고 |

### 표준 호출 패턴

```python
# Phase 완료 보고
notify_discord(
    "Phase 2 할부/리볼빙/부채 화면 구현 완료.",
    title="Phase 2 완료",
    event_type="phase",
    source="axel",            # 발신 에이전트
    project="finance-tracker",
    fields=[
        {"name": "커밋", "value": "feat(phase2): ...", "inline": True},
        {"name": "다음 단계", "value": "Phase 3 대시보드 확장", "inline": True},
    ]
)

# 사용자 확인 요청
notify_discord(
    "아키텍처 변경이 필요합니다. 승인해주세요.",
    event_type="ask",
    source="eva",
    project="finance-tracker",
)
```

---

## 10. 세션 위생 (Session Hygiene)

### 원칙

- 새 작업 시작 전 **기존 세션 현황 확인** (`list_sessions`)
- 동일 저장소 작업은 **기존 idle 세션 재사용** (`send_message`)
- 중복 세션 생성 최소화 (동일 cwd에 여러 세션 금지)
- Code 세션은 Mac 실행 전용 — bash, git, npm 등

### Cowork vs Code 세션 구분

| 작업 유형 | 사용 세션 |
|---|---|
| 파일 작성/편집, 문서 | Cowork (EVA) 직접 또는 NEXUS |
| bash 실행, git, npm | Code (AXEL) |
| 설계/이슈 작성 | Cowork |
| 로컬 LLM 호출 | Code (curl via AXEL) |

### 로컬 LLM 우선 원칙

- 루틴 실행, 반복 작업, 폴링/모니터링 → 로컬 LLM(FORGE/VANCE)에 위임
- Claude 토큰은 설계·컨펌·사용자 커뮤니케이션에 집중

---

## 11. Python 프로젝트 규칙

```bash
# 절대 python3 직접 호출 금지
poetry run python script.py   # ✅
python3 script.py             # ❌

# 의존성 추가
poetry add package-name

# 실행
poetry run pytest
```

---

## 12. 필수 문서 체계

| 파일 | 위치 | 내용 | 언어 |
|---|---|---|---|
| `README.md` | 루트 | 프로젝트 소개, 설치/실행법 | 영어 (GitHub 표준) |
| `ARCHITECTURE.md` | 루트 | 기술 스택, 디렉토리 구조, DB 스키마, API 목록 | 한국어 |
| `docs/ROADMAP.md` | docs/ | Phase별 완료 기준 + 체크리스트 | 한국어 |
| `docs/REQUIREMENTS.md` | docs/ | 기능 요구사항(FR), 비기능 요구사항 | 한국어 |
| `docs/AGENTS.md` | docs/ | 에이전트 조직도, 역할, 컨펌 체인, ORACLE 패턴 | 한국어 |
| `PROCESS_GUIDE.md` | ~/vinylstudio/ | 이 문서 — 공통 자산 | 한국어 |

### 커밋 완료 기준

코드 커밋과 문서 커밋은 항상 함께:
```
feat(phase2): 할부/리볼빙/부채 화면 구현
docs: ARCHITECTURE.md Phase 2 API 엔드포인트 갱신
```

---

## 13. 프로젝트 초기화 체크리스트

새 프로젝트 시작 시 순서:

```
□ 1. GitHub 레포 생성 (SSH URL: git@github.com:VinylStage/repo-name.git)
□ 2. release-please-config.json + .github/workflows/release-please.yml 추가
□ 3. .gitignore 필수 항목 확인 (data/, *.db, .env, ref/)
□ 4. GitHub Milestones 생성 (Phase 0~N)
□ 5. GitHub Project 칸반 보드 생성 + 마일스톤 연동
□ 6. 필수 문서 생성 (README.md, ARCHITECTURE.md, docs/)
□ 7. Discord MCP webhook 설정 (.env에 DISCORD_WEBHOOK_URL)
□ 8. docs/AGENTS.md 에이전트 역할 명세
□ 9. Phase 0 이슈 등록 + 프로젝트 보드 연동
□ 10. 첫 커밋: "chore: initial project scaffold"
```

---

## 14. 보안 규칙

- 회사 정보(GroMetric, SIEM, DevSecOps, Sigma rule 등) 절대 예제로 사용 금지
- 개인 비공개 프로젝트(SPECTRUM 등) 내용 공개 금지 (기술 패턴만 일반화)
- API 키, webhook URL → 환경변수만, 절대 하드코드 금지
- DB 암호화: 프로덕션은 AES-256-GCM 필수 (로컬 개발은 예외)

---

*마지막 갱신: 2026-07-21 | 기반 프로젝트: finance-tracker*
