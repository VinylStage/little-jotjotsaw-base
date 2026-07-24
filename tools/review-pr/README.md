# review-pr

GitHub PR 번호를 기반으로 diff를 읽어 자동 리뷰를 생성하고, 결과를 PR 코멘트로 등록하는 범용 스크립트입니다.

## 사전 요구사항
- **Node.js 18+**: 내장 `fetch` API를 사용합니다.
- **Ollama**: `qwen3.6:27b` 모델이 로컬에 미리 다운로드되어 있어야 합니다 (기본값).
- **GitHub CLI (`gh`)**: `gh auth login`으로 인증이 완료되어 있어야 합니다.

## 환경변수 설정
- `OLLAMA_HOST` (기본값: `http://localhost:11434`): Ollama 서버 주소입니다.

웹 검색을 하지 않으므로 검색 API 키는 필요하지 않습니다.

## 사용법
### PR 번호만 지정
```bash
node tools/review-pr/review-pr.mjs 42
```

### `owner/repo` 지정
```bash
node tools/review-pr/review-pr.mjs 42 owner/repo
```

### 모델명까지 지정
```bash
node tools/review-pr/review-pr.mjs 42 owner/repo qwen3-coder:30b
```

## 동작 흐름
1. `gh pr view`로 PR 제목/본문/변경 파일 목록/증감 라인 수 수집
2. `gh pr diff`로 전체 diff 수집
3. 자동 생성 파일(lock 파일)과 바이너리/이미지 파일을 diff에서 제외
4. 남은 diff를 파일 단위로 24,000자 예산 안에서 자르기
5. Ollama로 "변경 요약 / 리스크·주의점 / 검수 체크포인트 / 판단 보류" 4개 섹션 한국어 리뷰 생성
6. `gh pr comment`로 결과를 PR 코멘트로 등록

## SDLC 워크플로 연계
이 도구는 [docs/process/SDLC_WORKFLOW.md](../../docs/process/SDLC_WORKFLOW.md)의 **"1. SDLC 5단계 정의"** 중 **검수** 단계를 보조합니다.
[자료조사 도구](../research-issue/README.md)가 기획 전 단계를 자동화하는 것과 대칭적으로, 이 도구는 머지 전 검수 단계에서 리뷰 초안을 만들어 놓치기 쉬운 지점을 먼저 드러냅니다.

## 제한사항
- **사람 리뷰를 대체하지 않습니다.** 생성 결과는 참고용이며, 머지 판단은 사람이 합니다.
- Ollama가 실행 중이지 않으면 실패합니다.
- diff가 24,000자를 넘으면 초과분 파일이 리뷰에서 제외되며, 이 경우 코멘트에 "리뷰 범위가 부분적임"이 명시됩니다.
- lock 파일과 바이너리/이미지 파일은 리뷰 대상에서 제외됩니다.
- `gh` CLI 인증이 완료되지 않으면 PR 조회 실패로 종료됩니다.
- 로컬 모델 출력이므로 사실관계 오류가 있을 수 있습니다. 지적사항은 반드시 diff에서 직접 확인하세요.
