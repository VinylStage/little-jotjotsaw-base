---
title: SDLC 워크플로 가이드 (ISO/IEC/IEEE 12207 개념 기반)
date: 2026-07
status: draft
---

# SDLC 워크플로 가이드

## 1. SDLC 5단계 정의
| 단계 | GitHub 상 활동 | 주요 산출물 |
|------|----------------|------------|
| **감사** | GitHub Issue 생성 | 문제/개선점 기록 |
| **기획** | 자료조사(2-1 참고) 선행 → 마일스톤 배정, 우선순위 라벨, 인수 기준 작성 | 마일스톤, Issue (인수 기준 포함) |
| **개발** | feature 브랜치 생성, Conventional Commits, PR 생성 | PR, Commit 메시지 (feat: / fix: 등) |
| **검수** | 코드 리뷰, 빌드/테스트 검증, 인수 기준 확인 | PR 리뷰, 테스트 결과 |
| **배포** | merge → release-please 자동화 → GitHub Release 발행 | GitHub Release, CHANGELOG.md, 태그 |

## 2-1. 기획 전 자료조사 (필수)
이슈가 발생하면(자동 감사 또는 외부 요구사항) 기획 전에 반드시 자료조사를 선행한다.

**담당**: 서브에이전트 (로컬 LLM 우선, 보조로 Cowork)
**입력**: 이슈 제목 + 설명
**출력**: 조사 결과 요약 (기술 동향, 유사 구현 사례, 리스크, 추천 방향)
**저장**: 이슈 코멘트 또는 PR description에 첨부

**자료조사 트리거 기준**:
- 신규 기능 요청 (enhancement)
- major 의존성 업그레이드
- 보안 취약점 대응
- 아키텍처 변경 수반하는 chore

**자료조사 스킵 기준**:
- 오탈자/UI 텍스트 수정
- 단순 버그 수정 (재현 단계 명확)
- 이미 자료조사가 첨부된 이슈

**자동화 도구**: [tools/research-issue/](../../tools/research-issue/README.md) — 이슈 번호만 넘기면 웹 검색 + Ollama 요약을 자동 실행하고 결과를 이슈 코멘트로 등록한다. `node tools/research-issue/research-issue.mjs <issue-number> [repo] [model]`.

## 2. GitHub 계층 구조
| 계층 | GitHub 기능 | 설명 |
|------|-------------|------|
| Project | Kanban 보드 | 전체 프로젝트 관리 (예: VinylStage Projects) |
| Milestone | Phase 단위 마일스톤 | 예: `v0.2.0 - 사용자 인증` |
| Issue | Feature/Bug 단위 | 예: `#123: 로그인 기능 구현` |
| PR | 코드 변경 검수 | `feature/login → main` |
| Release | 배포 버전 | GitHub Release (v0.2.0) |

> 세부 계층 구조는 [GITHUB_WORKFLOW.md](./GITHUB_WORKFLOW.md) 참고

## 3. Issue 템플릿 3종
### 버그 리포트
```markdown
---
name: Bug Report
about: Report a bug in the application
title: "[Bug] Short description"
labels: bug, status:triage
---

**Severity**: (critical/high/medium/low)  
**재현 단계**:  
1. Step 1  
2. Step 2  
**예상 동작**:  
**실제 동작**:  
**환경 정보**:  
- OS:  
- 브라우저:  
- 버전:  
```

### 기능 요청
```markdown
---
name: Feature Request
about: Suggest a new feature
title: "[Feature] Short description"
labels: enhancement, status:planning
---

**배경**:  
**제안 내용**:  
**인수 기준(Acceptance Criteria)**:  
- [ ] [Feature] User can log in with email  
- [ ] [Feature] Login redirects to dashboard  
- [ ] [Feature] Error message shown on invalid credentials  
```

### 기술 작업/chore
```markdown
---
name: Technical Task
about: Non-functional development task
title: "[Chore] Short description"
labels: chore, status:planning
---

**작업 내용**:  
**완료 기준**:  
**관련 이슈/PR 링크**:  
```

## 4. 상태 라벨 흐름
| 상태 | 의미 | 전환 조건 |
|------|------|-----------|
| `status:triage` | 문제 분류 중 | Issue 생성 후 자동 할당 |
| `status:planning` | 기획 중 | 마일스톤/우선순위 라벨 추가 |
| `status:in-dev` | 개발 중 | PR 생성 후 브랜치 생성 |
| `status:review` | 검수 대기 | PR 생성 완료 |
| `status:done` | 완료 | PR 머지 및 배포 완료 |

## 5. PR 체크리스트 템플릿
```markdown
- [ ] 관련 이슈 링크: #123
- [ ] 변경 사항 요약: (feat: 로그인 기능 추가)
- [ ] 테스트 여부: (단위 테스트/통합 테스트 포함)
- [ ] Conventional Commit 형식 준수: (feat:, fix:, docs:)
- [ ] 브레이킹 체인지 여부: (예: `No`)
- [ ] 셀프 리뷰 완료: (예: `✅`)
```

**자동화 도구**: [tools/review-pr/](../../tools/review-pr/README.md) — PR 번호만 넘기면 diff를 로컬 Ollama로 분석해 "변경 요약/리스크/검수 체크포인트/판단 보류" 리뷰 초안을 PR 코멘트로 등록한다. `node tools/review-pr/review-pr.mjs <pr-number> [repo] [model]`. 참고용이며 사람 리뷰와 머지 판단을 대체하지 않는다.

## 6. 우선순위 라벨
| 라벨 | 판단 기준 | SLA 예시 |
|------|-----------|----------|
| `P1-high` | 서비스 중단/데이터 손실 (예: 로그인 실패) | 24시간 내 처리 |
| `P2-medium` | 기능 저하 (예: 메시지 전송 지연) | 3일 내 처리 |
| `P3-low` | 개선/사소한 버그 (예: UI 정렬) | 1주일 내 처리 |

## 7. 마일스톤 운영 원칙
- **이름 규칙**: `vX.Y.Z - 설명` (예: `v0.2.0 - 사용자 인증`)
- **완료 기준(DoD)**:  
  ```markdown
  - [ ] 모든 인수 기준 충족
  - [ ] 모든 PR 머지 완료
  - [ ] 테스트 커버리지 80% 이상
  ```
- **마감일**: 마일스톤 생성 시 설정 (예: `2026-07-31`)
- **회고**: 마일스톤 종료 후 1줄 요약 (예: `v0.2.0: 인증 기능 완료, 테스트 커버리지 75%`)

## 8. release-please 연동
1. **Conventional Commits** (예: `feat: 로그인 기능 추가`) →  
2. **release-please**가 자동으로 변경 이력 집계 →  
3. **릴리스 PR 생성** (예: `chore(release): v0.2.0`) →  
4. **사람 리뷰 후 머지** →  
5. **CHANGELOG.md/버전 태그 자동 갱신** →  
6. **GitHub Release 발행** (예: 레포의 `v0.2.0` 태그에 대한 Release 페이지 자동 생성)

> **예시**: 어느 프로젝트 레포가 `v0.1.0` → `v0.1.1` (fix: 버그 수정) → `v0.2.0` (feat: 로그인 기능 추가) 순으로 자동 릴리스된 흐름처럼, Conventional Commits만 지켜지면 나머지는 release-please가 처리합니다.

## 9. 유지보수 사이클

### 9.1 유지보수 개요
릴리스 이후에도 지속적으로 진행되는 코드/앱 상태 감사 프로세스로, "감사→기획→개발→검수→배포"의 SDLC 5단계가 주기적으로 반복됩니다. 유지보수 사이클은 항상 감사 단계에서 시작하며, 자동/수동 감사로 발견된 이슈도 기획 전 자료조사(2-1 참고)를 동일하게 거칩니다. 이는 릴리스 후에도 기술 부채, 보안 취약점, 의존성 문제를 체계적으로 관리하기 위한 순환적 워크플로우입니다.

### 9.2 자동 감사 항목 (GitHub Actions 기반)
매주 1회 정기 스케줄 + 수동 트리거로 실행되는 자동 감사 프로세스로, 다음 3가지 항목을 점검합니다:
- **보안 취약점 스캔**: `npm audit` 또는 `pip-audit`로 보안 취약점 검출
- **의존성 버전 갭 감사**: major 버전 미업데이트 패키지 탐지
- **빌드 실패 감지**: 빌드 실패 시 즉시 알림

```yaml
# .github/workflows/maintenance-audit.yml
name: Maintenance Audit
on:
  schedule:
    - cron: '0 0 * * 1'  # 매주 월요일 00:00
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security audit
        # 프로젝트 스택에 맞게 선택
        run: npm audit --json --production
        # 또는 Python 프로젝트: pip-audit --fail-on-severity high
      - name: Check dependency version gaps
        run: npx npm-check-updates --format group
        # major 버전이 뒤처진 패키지를 그룹별로 출력 (Python은 `pip list --outdated` 등으로 대체)
```

### 9.3 수동 감사 항목 (월 1회 권장)
- 코드 품질 리뷰 (기술 부채 식별)
- 실제 앱 동작 상태 점검 (API 응답 정상 여부, UI 정상 렌더링 여부)
- 로드맵 대비 누락된 기능 점검

### 9.4 이슈 제기 기준
| 감사 유형         | 등급             | 라벨               | 처리 방식                     |
|--------------------|------------------|--------------------|-----------------------------|
| 자동 감사 결과     | HIGH/CRITICAL    | `P1-high`          | 즉시 이슈 생성              |
| 자동 감사 결과     | MODERATE         | `P2-medium`        | 이슈 생성                   |
| 수동 감사 결과     | 모든 등급        | `chore` 또는 `enhancement` | "Maintenance" 마일스톤에 배정 |

### 9.5 완료 기준
이슈 생성(`status:triage`) → 우선순위 라벨 부여 → 마일스톤 배정(`status:planning`) → 작업 진행(`status:in-dev`) → PR 리뷰(`status:review`) → PR 머지 및 이슈 종료(`status:done`)

### 9.6 알림 연동
자동 감사 결과는 Discord로 요약 전송됩니다. 성공 시 `success` 이벤트, 취약점 발견 시 `error`/`warning` 이벤트 타입으로 알림이 전송됩니다. 상세 흐름은 [discord-notification-flow.md](../diagrams/discord-notification-flow.md)를 참고하세요.
