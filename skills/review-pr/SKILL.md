---
name: review-pr
description: GitHub PR의 diff를 로컬 Ollama로 분석해 리뷰 초안을 생성하고 결과를 PR 코멘트로 등록한다. 사용자가 "PR 리뷰", "review pr", "코드 리뷰 돌려줘"를 언급하거나 SDLC 검수 단계에서 머지 전 리뷰가 필요할 때 사용한다.
---

이 스킬은 이 플러그인의 `tools/review-pr/review-pr.mjs` 스크립트를 실행해서 `sdlc-guide` 스킬의 "검수" 단계를 보조한다.

## 실행 전 확인 (전제조건)

아래를 먼저 확인하고, 실패하면 사용자에게 무엇이 안 되어 있는지 알려주고 중단한다 — 스크립트를 억지로 실행해서 알 수 없는 에러를 내지 말 것.

1. **Node.js 18+**: `node --version`
2. **Ollama 실행 중**: `curl -s http://localhost:11434/api/tags` (또는 `$OLLAMA_HOST`) 가 응답하는지 확인. 모델(`qwen3.6:27b`, 기본값)이 `ollama list`에 있는지도 확인.
3. **gh CLI 인증**: `gh auth status`

## 실행

```bash
node tools/review-pr/review-pr.mjs <pr-number> [repo] [model]
```

- `<pr-number>`: 필수
- `[repo]`: 생략하면 현재 디렉토리의 git remote origin에서 자동 추론. 다른 레포의 PR을 리뷰하려면 `owner/repo` 형식으로 명시
- `[model]`: 생략하면 `qwen3.6:27b`

## 동작 및 결과

스크립트가 내부적으로 다음을 전부 수행한다 — 에이전트가 별도로 결과를 코멘트로 옮겨 적을 필요 없음:

1. `gh pr view`로 PR 메타데이터 조회
2. `gh pr diff`로 diff 수집
3. lock 파일·바이너리·이미지 제외 후 24,000자 예산 안에서 diff 정리
4. Ollama로 "변경 요약 / 리스크·주의점 / 검수 체크포인트 / 판단 보류" 4개 섹션 리뷰 생성
5. **`gh pr comment`로 리뷰를 PR에 자동 등록** ← 이 스킬의 최종 산출물

실행 후에는 stdout 로그(브랜치/증감 라인 수, 스킵 파일 수, diff 잘림 여부, 완료 메시지)를 확인해서 사용자에게 요약 보고하면 된다. 각 단계 실패 시 스크립트가 명확한 에러 메시지와 함께 종료 코드 1로 끝나므로, 그 메시지를 그대로 사용자에게 전달할 것.

## 보고 시 반드시 전달할 것

- **`[잘림]` 로그가 출력됐다면 리뷰 범위가 부분적이라는 사실을 사용자에게 명시할 것.** 전체 diff를 본 리뷰가 아니다.
- 생성된 리뷰는 로컬 모델 출력이므로 **참고용이며 사람 리뷰를 대체하지 않는다.** 지적사항을 그대로 사실로 옮기지 말고, diff에서 확인된 것인지 구분해서 전달할 것.
- 머지 판단은 저장소 소유자가 한다. 이 스킬은 머지를 수행하지 않는다.

## 참고

- 상세 사용법/제한사항: `tools/review-pr/README.md`
- 환경변수: `OLLAMA_HOST` (기본값 `http://localhost:11434`)
- 기획 전 단계를 자동화하는 대칭 도구: `research` 스킬 / `tools/research-issue/README.md`
