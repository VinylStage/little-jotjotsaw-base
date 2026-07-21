# research-issue

GitHub 이슈 번호를 기반으로 자동으로 자료조사를 수행하고, 결과를 이슈 코멘트로 등록하는 범용 스크립트입니다.

## 사전 요구사항
- **Node.js 18+**: 내장 `fetch` API를 사용합니다.
- **Ollama**: `qwen3-30b-32k` 모델이 로컬에 미리 다운로드되어 있어야 합니다 (기본값).
- **GitHub CLI (`gh`)**: `gh auth login`으로 인증이 완료되어 있어야 합니다.

## 환경변수 설정
`.env.example` 파일을 `.env`로 복사하여 설정합니다.
- `BRAVE_API_KEY` (선택): Brave Search API 키. 미설정 시 DuckDuckGo로 폴백됩니다.
- `OLLAMA_HOST` (기본값: `http://localhost:11434`): Ollama 서버 주소입니다.

예시 `.env` 파일:
```env
BRAVE_API_KEY=your_brave_api_key_here
OLLAMA_HOST=http://localhost:11434
```

## 사용법
### 이슈 번호만 지정
```bash
node tools/research-issue/research-issue.mjs 123
```

### `owner/repo` 지정
```bash
node tools/research-issue/research-issue.mjs 123 owner/repo
```

### 모델명까지 지정
```bash
node tools/research-issue/research-issue.mjs 123 owner/repo qwen3-30b-32k
```

## 동작 흐름
1. `gh issue view`로 이슈 제목/본문/라벨 수집
2. Ollama로 영어 검색어 추출
3. Brave Search API (사용 가능 시) 또는 DuckDuckGo로 웹 검색
4. 검색 결과 8개 페이지 → 2000자로 자르기 → 요약 처리
5. Ollama로 "기술 동향/유사 구현 사례/리스크/추천 방향" 4개 섹션 한국어 요약 생성
6. `gh issue comment`로 결과를 이슈 코멘트로 등록

## SDLC 워크플로 연계
이 도구는 [docs/process/SDLC_WORKFLOW.md](../../docs/process/SDLC_WORKFLOW.md)의 **"2-1. 기획 전 자료조사 (필수)"** 절차를 자동화합니다.  
신규 기능/중대한 의존성 업그레이드/보안 취약점 대응/아키텍처 변경 시 필수로 수행해야 하는 자료조사 결과를 이슈 코멘트로 저장해, SDLC 요구사항을 충족합니다.

## 제한사항
- Ollama가 실행 중이지 않으면 실패합니다.
- `BRAVE_API_KEY` 미설정 시 DuckDuckGo로 폴백되며, 검색 결과가 없으면 실행 중단됩니다.
- 검색 결과 페이지가 403 등 오류 시 해당 페이지만 건너뛰고 계속 실행됩니다.
- `gh` CLI 인증이 완료되지 않으면 이슈 조회 실패로 종료됩니다.
