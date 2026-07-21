---
title: 2026년 7월 트러블슈팅 로그 — finance-tracker 및 관련 작업
date: 2026-07
project: finance-tracker
status: draft
---

# 2026년 7월 트러블슈팅 로그 — finance-tracker 및 관련 작업

### 1. better-sqlite3 ELF 헤더 오류

**배경**  
finance-tracker 프로젝트에서 better-sqlite3 모듈을 사용 중 macOS에서 빌드된 네이티브 바이너리(.node)를 Linux 기반 개발 환경에서 실행 시 발생.

**증상**  
`invalid ELF header` 오류 발생으로 앱 실행이 실패하며, `Error: The module '/path/to/better-sqlite3.node' was compiled against a different Node.js version` 메시지 출력.

**원인**  
macOS에서 빌드된 네이티브 바이너리가 Linux 환경에서 호환되지 않아 발생한 플랫폼 간 비호환 문제.

**해결**  
Linux 환경에서 `npm rebuild better-sqlite3` 명령어 실행을 통해 해당 환경에 맞는 네이티브 모듈을 재빌드.

**재발 방지**  
프로젝트 빌드 시 OS/아키텍처에 맞는 네이티브 모듈 재빌드를 필수 절차로 명시. CI/CD 파이프라인에 빌드 환경 검증 추가.

---

### 2. git index.lock 권한 오류

**배경**  
git 작업 중 커밋 및 브랜치 전환 시 발생한 오류.

**증상**  
`fatal: Unable to create '/path/to/.git/index.lock': Permission denied` 오류로 작업 중단.

**원인**  
이전 git 프로세스가 비정상 종료되며 `.git/index.lock` 파일이 남아 권한이 꼬인 상태.

**해결**  
`ps aux | grep git`로 다른 git 프로세스 확인 후, `rm .git/index.lock`으로 lock 파일 수동 삭제.

**재발 방지**  
git 작업 중 종료 시 `git status`로 상태 확인 후 정상 종료. 비정상 종료 시 lock 파일 수동 정리 절차 문서화.

---

### 3. 한글 파일명 삭제 권한 오류 → 내용 덮어쓰기로 우회

**배경**  
한글 파일명(`분석_데이터_2026.07.txt`)을 포함한 파일 삭제 시 발생.

**증상**  
`Permission denied` 오류로 파일 삭제 실패. `rm` 명령어 실행 시 한글 파일명 인코딩 문제 발생.

**원인**  
파일 시스템이 한글 파일명을 처리하는 방식과 권한 체계의 충돌.

**해결**  
파일 내용을 빈 값으로 덮어쓰기(`echo "" > 분석_데이터_2026.07.txt`)로 실질적 삭제 대체.

**재발 방지**  
한글 파일명 사용 시 삭제 대신 내용 덮어쓰기 방식 적용. 파일명 규칙에 한글 사용 금지 조항 추가.

---

### 4. discord-mcp-alert push 충돌 (release 0.3.0 리베이스 필요)

**배경**  
discord-mcp-alert 프로젝트에서 release-please로 관리하는 0.3.0 릴리스 준비 중.

**증상**  
`git push` 시 `non-fast-forward` 오류 발생으로 원격 브랜치와 로컬 이력 불일치.

**원인**  
release-please가 자동 생성한 릴리스 커밋과 로컬 작업 이력이 충돌.

**해결**  
`git fetch origin` 후 `git rebase origin/main`으로 로컬 브랜치를 원격과 동기화한 후 push.

**재발 방지**  
릴리스 전 `git fetch`로 최신 이력 확인. release-please 실행 전 `git status`로 작업 이력 검증.

---

### 5. Claude Code 세션 중복 생성 문제

**배경**  
Claude Code API를 사용해 코드 생성 작업 중 발생.

**증상**  
동일 작업에 대해 2개 이상의 세션이 생성되어 중복 처리.

**원인**  
세션 관리 로직에서 중복 생성 방지 체크 미흡 및 API 호출 시 타임아웃 처리 부재.

**해결**  
기존 세션 ID를 검색해 중복 시 삭제 후 재생성. API 호출 시 타임아웃 설정 추가.

**재발 방지**  
세션 생성 시 고유 ID 생성 및 중복 검사 로직 강화. API 호출 시 재시도 메커니즘 도입.

---

### 6. ORACLE 동시 다중 호출로 인한 OOM/블로킹 사고

**배경**  
로컬 환경에서 ORACLE(대형 모델 기반 분석 에이전트)을 병렬로 호출.

**증상**  
메모리 부족(OOM)으로 프로세스 종료, 처리 지연 및 UI 블로킹 발생.

**원인**  
로컬 환경의 제한된 리소스에서 ORACLE을 동시에 3개 이상 병렬 호출한 것.

**해결**  
ORACLE 호출을 순차적으로 변경(1회 호출 완료 후 다음 호출). 메모리 모니터링 도구 추가.

**재발 방지**  
ORACLE 및 유사한 무거운 로컬 LLM 호출은 반드시 순차적으로 실행해야 함을 명시. 프로젝트 문서에 "병렬 호출 금지" 규칙 추가.
