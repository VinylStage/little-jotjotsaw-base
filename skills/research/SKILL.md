---
name: research
description: GitHub 이슈에 대해 웹 검색 + 로컬 Ollama 요약으로 자료조사를 자동 실행하고 결과를 이슈 코멘트로 등록한다. 사용자가 "자료조사", "research", "이슈 리서치"를 언급하거나 SDLC 기획 전 자료조사가 필요할 때 사용한다.
---

이 스킬은 이 플러그인의 `tools/research-issue/research-issue.mjs` 스크립트를 실행해서 `sdlc-guide` 스킬의 "기획 전 자료조사" 단계를 자동화한다.

## 실행 전 확인 (전제조건)

아래를 먼저 확인하고, 실패하면 사용자에게 무엇이 안 되어 있는지 알려주고 중단한다 — 스크립트를 억지로 실행해서 알 수 없는 에러를 내지 말 것.

1. **Node.js 18+**: `node --version`
2. **Ollama 실행 중**: `curl -s http://localhost:11434/api/tags` (또는 `$OLLAMA_HOST`) 가 응답하는지 확인. 모델(`qwen3-30b-32k`, 기본값)이 `ollama list`에 있는지도 확인.
3. **gh CLI 인증**: `gh auth status`

## 실행

```bash
node tools/research-issue/research-issue.mjs <issue-number> [repo] [model]
```

- `<issue-number>`: 필수
- `[repo]`: 생략하면 현재 디렉토리의 git remote origin에서 자동 추론. 다른 레포의 이슈를 조사하려면 `owner/repo` 형식으로 명시
- `[model]`: 생략하면 `qwen3-30b-32k`

## 동작 및 결과

스크립트가 내부적으로 다음을 전부 수행한다 — 에이전트가 별도로 결과를 코멘트로 옮겨 적을 필요 없음:

1. `gh issue view`로 이슈 조회
2. Ollama로 검색어 추출
3. Brave Search(`BRAVE_API_KEY` 설정 시) 또는 DuckDuckGo로 웹 검색
4. 상위 결과 페이지 텍스트 추출 (실패한 페이지는 건너뜀)
5. Ollama로 "기술 동향/유사 구현 사례/리스크/추천 방향" 4개 섹션 요약 생성
6. **`gh issue comment`로 요약 + 출처를 이슈에 자동 등록** ← 이 스킬의 최종 산출물

실행 후에는 stdout 로그(검색어, 검색 결과 수, 페이지 추출 성공/실패, 완료 메시지)를 확인해서 사용자에게 요약 보고하면 된다. 각 단계 실패 시 스크립트가 명확한 에러 메시지와 함께 종료 코드 1로 끝나므로, 그 메시지를 그대로 사용자에게 전달할 것.

## 참고

- 상세 사용법/제한사항: `tools/research-issue/README.md`
- 환경변수: `tools/research-issue/.env.example` 참고 (`BRAVE_API_KEY` 선택, `OLLAMA_HOST` 기본값 `http://localhost:11434`)
