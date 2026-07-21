---
title: SDLC 워크플로 가이드 (ISO/IEC/IEEE 12207 개념 기반)
date: 2026-07
status: draft
---

# SDLC 워크플로 가이드

## 1. SDLC 5단계 정의
| 단계 | GitHub 상 활동 | 주요 산출물 |
|------|----------------|------------|
| **발견** | GitHub Issue 생성 | 문제/개선점 기록 |
| **기획** | 마일스톤 배정, 우선순위 라벨, 인수 기준 작성 | 마일스톤, Issue (인수 기준 포함) |
| **개발** | feature 브랜치 생성, Conventional Commits, PR 생성 | PR, Commit 메시지 (feat: / fix: 등) |
| **검수** | 코드 리뷰, 빌드/테스트 검증, 인수 기준 확인 | PR 리뷰, 테스트 결과 |
| **배포** | merge → release-please 자동화 → GitHub Release 발행 | GitHub Release, CHANGELOG.md, 태그 |

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
