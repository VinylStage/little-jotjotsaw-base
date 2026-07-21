# 문서 작성 가이드

## 폴더 구조 설명
이 레포의 `docs/` 폴더는 세 가지 주요 목적을 가진 하위 폴더로 구성됩니다:
- **`docs/process/**: 프로젝트 간 공통으로 사용되는 프로세스 가이드(예: AGENT_SYSTEM.md, GITHUB_WORKFLOW.md)를 저장합니다.
- **`docs/troubleshooting/**: 트러블슈팅 로그를 기록하는 폴더로, `YYYY-MM-프로젝트명.md` 형식의 파일로 관리됩니다.
- **`docs/projects/**: 각 프로젝트별 개요 문서를 저장합니다. 프로젝트명 폴더 내부에 `OVERVIEW.md` 파일을 위치시킵니다.

## 파일명 컨벤션
- **트러블슈팅 로그**: `docs/troubleshooting/YYYY-MM-프로젝트명.md` (예: `2026-07-finance-tracker.md`)
- **프로젝트 개요**: `docs/projects/프로젝트명/OVERVIEW.md` (예: `docs/projects/finance-tracker/OVERVIEW.md`)
- **모든 파일명은 영어, 소문자, 하이픈(-)으로 구분**합니다.  
  (예: `2026-07-finance-tracker.md` → `finance-tracker`는 프로젝트명 소문자화)

## 문서 작성 규칙
1. **내용 언어**: 모든 문서 본문은 **한국어**로 작성합니다.  
   (예외는 `README.md` 단 하나뿐이며, 영어로 작성)
2. **메타데이터**: 문서 최상단에 다음 형식의 프론트매터를 추가합니다.
   ```
   ---
   title: 문서 제목
   date: YYYY-MM-DD
   project: 관련 프로젝트명 (해당 없으면 생략)
   status: draft | reviewed
   ---
   ```
3. **트러블슈팅 로그 구조**:  
   다음 섹션을 반드시 포함합니다.
   ```
   ## 배경
   ## 증상
   ## 원인
   ## 해결
   ## 재발 방지
   ```

## 인덱스 파일 관리
- 새 문서를 추가할 때 **반드시 관련 인덱스 파일에 링크를 추가**합니다.
  - 예: `docs/troubleshooting/INDEX.md`에 새 로그 파일 링크 추가
  - 예: `docs/projects/` 폴더에 새로운 프로젝트 폴더 생성 시 `docs/projects/INDEX.md` 업데이트

## 작업 워크플로우
1. **폴더/구조 생성**: 사람이 `docs/` 하위에 새 폴더 또는 파일을 생성합니다.
2. **초안 작성**: 로컬 LLM 에이전트("VANCE")에게 초안을 위임해 작성합니다.
3. **검수**: 검수 후 `status: reviewed`로 변경합니다.
4. **관리**: `status: draft`는 **검수 전 문서**임을 표시합니다.

> **참고**: 모든 문서는 검수 전 `status: draft`로 시작하며, 검수 완료 후 `status: reviewed`로 업데이트됩니다.
