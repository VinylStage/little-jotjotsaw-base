# discord-mcp-alert 개요

## 1. 프로젝트 한 줄 요약
discord-mcp-alert는 Claude Desktop, Claude Code CLI, VS Code Extension, Claude Cowork 전용으로 개발된 MIT 라이선스의 Python 3.10+ 기반 Discord 알림 서버로, 모든 작업 완료 시 풍부한 Embed 메시지로 알림을 전송합니다.

## 2. 주요 기능 목록
- Rich Embed 알림(색상·이모지·필드 포함)
- 다중 클라이언트 지원(Claude Desktop, Claude Code CLI, VS Code Extension, Claude Cowork)
- Claude Code 작업 완료 시 자동 알림을 위한 Hooks 연동
- 이벤트별 중복 알림 방지(flock 원자적 락)

## 3. 설치 방법 요약
1. `git clone https://github.com/VinylStage/discord-mcp-alert.git`
2. `./install.sh` 실행 → (1) Python 환경 자동 준비(Poetry → uv → pip), (2) Discord Webhook URL 입력, (3) 대상 클라이언트 선택(전체/개별), (4) 자동 설정 및 테스트 알림 전송

## 4. 사용법 예시
- **자연어 요청**: "배포 완료됐다고 Discord에 알려줘"
- **도구 직접 호출**: `notify_discord --event success --message "Deployment completed"`

## 5. event_type 및 source 표

### event_type
| event_type | 색상   | 이모지 | 사용 상황             |
|------------|--------|--------|-----------------------|
| success    | 초록   | ✅     | 작업 성공             |
| error      | 빨강   | ❌     | 오류 발생             |
| warning    | 노랑   | ⚠️     | 주의 필요             |
| info       | 파랑   | ℹ️     | 일반 정보             |
| start      | 하늘   | 🚀     | 작업 시작             |
| complete   | 밝은 초록 | 🎉     | 워크플로우 완료        |
| default    | 회색   | 🔔     | 기타                  |

### source
| source         | 설명               |
|----------------|--------------------|
| claude_code    | Claude Code CLI    |
| claude_desktop | Claude Desktop     |

## 6. 버전 이력 요약
- **v0.1.0**: 초기 릴리스
- **v0.2.0**: Claude Code Hooks 자동 알림 추가, 이벤트별 debounce 지원, Notification 이벤트 추가, 중복 알림 방지(flock 락), 중복 프로젝트 레벨 hook 설정 제거
- **v0.3.0**: 개발 중 (2026-07 push 충돌/리베이스 이슈로 인한 작업 진행 중)

## 7. 관련 문서
v0.3.0 준비 중 발생한 push 충돌 이슈는 [2026-07 트러블슈팅 로그](../../troubleshooting/2026-07-finance-tracker.md)를 참고하세요.
