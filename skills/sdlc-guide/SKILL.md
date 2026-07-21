---
name: sdlc-guide
description: VinylStage 프로젝트의 SDLC(감사-기획-개발-검수-배포) 5단계와 GitHub Project/Milestone/Issue 계층 구조를 안내한다. 사용자가 "sdlc", "프로세스", "이슈 등록", "마일스톤" 등을 언급하며 개발 프로세스나 이슈/마일스톤 운영 방식을 물을 때 사용한다.
---

이 스킬은 `docs/process/SDLC_WORKFLOW.md`(같은 플러그인 레포)에 정의된 SDLC 운영 가이드를 요약해서 안내한다. 세부 템플릿(Issue 3종, PR 체크리스트, 라벨 체계, release-please 연동, 유지보수 사이클)이 필요하면 그 문서를 직접 읽을 것 — 이 스킬은 빠른 요약용이다.

## SDLC 5단계

| 단계 | GitHub 상 활동 |
|---|---|
| **감사** | GitHub Issue 생성 (문제/개선점 기록) |
| **기획** | **자료조사 선행(아래 참고) →** 마일스톤 배정, 우선순위 라벨(`P1-high`/`P2-medium`/`P3-low`), 인수 기준 작성 |
| **개발** | feature 브랜치, Conventional Commits, PR 생성 |
| **검수** | 코드 리뷰, 빌드/테스트 검증, 인수 기준 확인 |
| **배포** | merge → release-please 자동화 → GitHub Release |

릴리스 이후에도 이 5단계는 끝나지 않고, 정기 감사(주 1회 자동 + 월 1회 수동)를 통해 계속 순환한다.

## 기획 전 자료조사 (필수)

기획 단계로 넘어가기 전에 반드시 자료조사를 먼저 한다.

**트리거 기준** (이 중 하나라도 해당하면 자료조사 필수):
- 신규 기능 요청(enhancement)
- major 의존성 업그레이드
- 보안 취약점 대응
- 아키텍처 변경을 수반하는 chore

**스킵 기준**: 오탈자/UI 텍스트 수정, 재현 단계가 명확한 단순 버그 수정, 이미 자료조사가 첨부된 이슈.

자료조사가 필요하면 이 플러그인의 `research` 스킬(`tools/research-issue/research-issue.mjs`)로 자동화할 수 있다.

## GitHub 계층 구조

```
Project (Kanban 보드)
 └── Milestone (Phase 단위 릴리스)
      └── Issue (Feature/Bug 단위, [feat]/[fix]/[chore] 접두사)
           └── PR → Release
```

- **상태 라벨 흐름**: `status:triage` → `status:planning` → `status:in-dev` → `status:review` → `status:done`
- **우선순위 라벨**: `P1-high`(서비스 중단급, 24시간 내) / `P2-medium`(기능 저하, 3일 내) / `P3-low`(개선/사소한 버그, 1주 내)
- Issue 템플릿 3종(버그 리포트/기능 요청/기술작업)과 PR 체크리스트 템플릿은 `docs/process/SDLC_WORKFLOW.md`에 실제 마크다운 양식으로 있음.

## 참고 문서

- 이 요약의 원본: `docs/process/SDLC_WORKFLOW.md`
- GitHub 계층 세부사항: `docs/process/GITHUB_WORKFLOW.md`
- 에이전트별 담당: 이 플러그인의 `agent-system` 스킬
