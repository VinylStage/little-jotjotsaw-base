# little-jotjotsaw-base

이 레포지토리는 여러 프로젝트에서 공통으로 사용하는 지식 자산을 저장하는 문서 전용 저장소입니다. 애플리케이션 코드는 포함되지 않으며, 공통 개발 프로세스, 실제 사건 기반 트러블슈팅 로그, 에이전트(AI 어시스턴트) 운영 가이드, 프로젝트 개요 문서, 교육용 프로세스 다이어그램을 모아 관리합니다.

## 누구에게 필요한가요?
이 레포는 VinylStage(소유자)와 다른 프로젝트 레포지토리에서 진행 중인 Claude Code 세션 사용자가 읽고 갱신해야 합니다.

## 레포 구조
```
little-jotjotsaw-base/
├── README.md
├── CLAUDE.md                          (Claude Code 운영 지침)
├── docs/
│   ├── DOCUMENT_GUIDE.md              (문서 기여 가이드: 파일명/구조/메타데이터)
│   ├── process/
│   │   ├── PROCESS_GUIDE.md           (공통 개발 프로세스)
│   │   ├── AGENT_SYSTEM.md            (에이전트 조직도, 위임 규칙, 세션 위생)
│   │   └── GITHUB_WORKFLOW.md         (GitHub Project/Milestone/Issue 컨벤션, release-please)
│   ├── troubleshooting/
│   │   ├── INDEX.md                   (트러블슈팅 로그 인덱스)
│   │   └── 2026-07-finance-tracker.md (날짜별 사건 로그)
│   ├── projects/
│   │   ├── finance-tracker/OVERVIEW.md
│   │   └── discord-mcp-alert/OVERVIEW.md
│   └── diagrams/                      (교육용 Mermaid 프로세스 다이어그램)
│       ├── agent-org-confirm-chain.md (에이전트 조직도 및 컨펌 체인 프로세스)
│       ├── github-workflow-hierarchy.md (GitHub 프로젝트/마일스톤/이슈 관리 계층)
│       ├── session-management-flow.md (Claude 세션 관리 프로세스)
│       └── discord-notification-flow.md (Discord 알림 전달 프로세스)
```

## 사용 방법
- Claude 운영 규칙은 [CLAUDE.md](CLAUDE.md)를 참고하세요.
- 문서 기여 컨벤션은 [docs/DOCUMENT_GUIDE.md](docs/DOCUMENT_GUIDE.md)를 참고하세요.

## 다이어그램
- `agent-org-confirm-chain.md`: 에이전트 조직도 및 컨펌 체인 프로세스
- `github-workflow-hierarchy.md`: GitHub 프로젝트/마일스톤/이슈 관리 계층
- `session-management-flow.md`: Claude 세션 관리 프로세스
- `discord-notification-flow.md`: Discord 알림 전달 프로세스

## 컨벤션 요약
- 모든 문서는 한국어로 작성되며, 예외 없이 영어 사용 금지
- 파일명은 소문자 및 하이픈(-)으로 구성 (예: `2026-07-finance-tracker.md`)

## 소유권 안내
이 레포지토리는 VinylStage의 개인 지식 저장소로, 외부 기여를 받지 않습니다.
