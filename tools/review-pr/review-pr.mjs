#!/usr/bin/env node
// 사용법: node review-pr.mjs <pr-number> [repo] [model]
// 기본 모델: qwen3.6:27b
// repo 생략 시 현재 디렉토리의 git remote origin에서 자동 추론 (owner/repo 형태)
'use strict';

import { execSync } from 'node:child_process';

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';
const DEFAULT_MODEL = 'qwen3.6:27b';
const MAX_DIFF_CHARS = 24000;
// 자동 생성 파일 — 리뷰 가치가 없고 diff 예산만 소모하므로 제외
const SKIP_FILE_PATTERNS = [
  /(^|\/)package-lock\.json$/,
  /(^|\/)pnpm-lock\.yaml$/,
  /(^|\/)yarn\.lock$/,
  /(^|\/)poetry\.lock$/,
  /(^|\/)Cargo\.lock$/,
  /(^|\/)go\.sum$/,
  /\.(png|jpe?g|gif|webp|ico|svg|pdf|zip|woff2?|ttf)$/i,
];

const [, , prNumberArg, repoArg, modelArg] = process.argv;
const model = modelArg || DEFAULT_MODEL;

if (!prNumberArg || !/^\d+$/.test(prNumberArg)) {
  console.error('사용법: node review-pr.mjs <pr-number> [repo] [model]');
  process.exit(1);
}

if (repoArg && !/^[\w.-]+\/[\w.-]+$/.test(repoArg)) {
  console.error(`[에러] repo 형식이 올바르지 않습니다: "${repoArg}" (예: owner/repo)`);
  process.exit(1);
}

function sh(cmd, opts = {}) {
  return execSync(cmd, { encoding: 'utf8', maxBuffer: 40 * 1024 * 1024, ...opts });
}

function resolveRepo(explicitRepo) {
  if (explicitRepo) return explicitRepo;
  try {
    const url = sh('git remote get-url origin').trim();
    // git@github.com:owner/repo.git 또는 https://github.com/owner/repo.git
    const m = url.match(/github\.com[:/]([^/]+)\/([^/.]+?)(?:\.git)?$/);
    if (m) return `${m[1]}/${m[2]}`;
  } catch {
    // git remote 조회 실패 — gh CLI 자체 감지에 위임
  }
  return undefined;
}

const repo = resolveRepo(repoArg);
const repoFlag = repo ? ` --repo ${repo}` : '';

async function ollamaGenerate(prompt) {
  let res;
  try {
    res = await fetch(`${OLLAMA_HOST}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt, stream: false }),
      signal: AbortSignal.timeout(600000),
    });
  } catch (e) {
    throw new Error(`Ollama(${OLLAMA_HOST}) 연결 실패: ${e.message}`);
  }
  if (!res.ok) {
    throw new Error(`Ollama 응답 실패: ${res.status} ${await res.text()}`);
  }
  const data = await res.json();
  return (data.response || '').trim();
}

// diff를 파일 단위로 쪼개서 스킵 대상 제외 후 예산 안에서 자름
function trimDiff(rawDiff) {
  const chunks = rawDiff.split(/^diff --git /m).filter(Boolean).map((c) => 'diff --git ' + c);
  const kept = [];
  const skipped = [];
  let total = 0;
  let truncated = 0;

  for (const chunk of chunks) {
    const pathMatch = chunk.match(/^diff --git a\/(\S+) b\/(\S+)/);
    const path = pathMatch ? pathMatch[2] : '(unknown)';
    if (SKIP_FILE_PATTERNS.some((re) => re.test(path))) {
      skipped.push(path);
      continue;
    }
    if (total + chunk.length > MAX_DIFF_CHARS) {
      truncated += 1;
      continue;
    }
    kept.push(chunk);
    total += chunk.length;
  }
  return { text: kept.join('\n'), skipped, truncated };
}

async function main() {
  // 1. PR 메타데이터 조회
  let pr;
  try {
    const raw = sh(`gh pr view ${prNumberArg}${repoFlag} --json title,body,files,baseRefName,headRefName,additions,deletions`);
    pr = JSON.parse(raw);
  } catch (e) {
    console.error(`[에러] PR #${prNumberArg} 조회 실패: ${e.message}`);
    process.exit(1);
  }
  console.log(`[레포] ${repo || '(gh CLI 자동 감지)'}`);
  console.log(`[PR #${prNumberArg}] ${pr.title}`);
  console.log(`[브랜치] ${pr.headRefName} -> ${pr.baseRefName} (+${pr.additions}/-${pr.deletions}, ${(pr.files || []).length}개 파일)`);

  // 2. diff 조회 및 예산 내로 정리
  let rawDiff;
  try {
    rawDiff = sh(`gh pr diff ${prNumberArg}${repoFlag}`);
  } catch (e) {
    console.error(`[에러] PR diff 조회 실패: ${e.message}`);
    process.exit(1);
  }
  if (!rawDiff.trim()) {
    console.error('[에러] diff가 비어 있습니다.');
    process.exit(1);
  }

  const { text: diff, skipped, truncated } = trimDiff(rawDiff);
  if (!diff) {
    console.error('[에러] 리뷰 대상 diff가 남지 않았습니다 (전부 스킵 대상이거나 예산 초과).');
    process.exit(1);
  }
  if (skipped.length) console.log(`[스킵] 자동 생성/바이너리 ${skipped.length}건: ${skipped.slice(0, 5).join(', ')}${skipped.length > 5 ? ' 외' : ''}`);
  if (truncated) console.log(`[잘림] 예산(${MAX_DIFF_CHARS}자) 초과로 ${truncated}개 파일 제외 — 리뷰 범위가 부분적임`);
  console.log(`[diff] ${diff.length}자 리뷰 대상`);

  // 3. Ollama 리뷰 생성
  const fileList = (pr.files || [])
    .map((f) => `- ${f.path} (+${f.additions}/-${f.deletions})`)
    .join('\n')
    .slice(0, 2000);

  const reviewPrompt = `너는 시니어 소프트웨어 엔지니어야. 아래 GitHub Pull Request를 검수하고 한국어로 리뷰를 작성해줘.

## PR 제목
${pr.title}

## PR 설명
${(pr.body || '(설명 없음)').slice(0, 2000)}

## 변경 파일
${fileList}

## 변경 내용 (diff)
${diff}

다음 형식으로 작성해 (마크다운 헤더 사용):
### 변경 요약
### 리스크·주의점
### 검수 체크포인트
### 판단 보류

작성 규칙:
- 각 섹션은 3~6개의 불릿으로 간결하게.
- diff에서 실제로 확인한 내용만 쓸 것. 추측한 내용은 "판단 보류"에 근거와 함께 분리해서 적을 것.
- 문제가 없으면 없다고 명확히 쓸 것. 억지로 지적사항을 만들지 말 것.
- 코드 위치를 언급할 때는 파일 경로를 함께 쓸 것.`;

  let review;
  try {
    review = await ollamaGenerate(reviewPrompt);
    if (!review) throw new Error('빈 응답 반환됨');
  } catch (e) {
    console.error(`[에러] 리뷰 생성 실패: ${e.message}`);
    process.exit(1);
  }

  // 4. PR 코멘트 작성
  const notes = [];
  if (skipped.length) notes.push(`자동 생성/바이너리 파일 ${skipped.length}건 제외`);
  if (truncated) notes.push(`diff 예산 초과로 ${truncated}개 파일 미포함 — **리뷰 범위가 부분적임**`);

  const commentBody = `## 🧪 자동 PR 리뷰

**모델**: \`${model}\`
**범위**: \`${pr.headRefName}\` → \`${pr.baseRefName}\` (+${pr.additions}/-${pr.deletions}, ${(pr.files || []).length}개 파일)
${notes.length ? `**제한**: ${notes.join(' / ')}\n` : ''}
${review}

---
_이 코멘트는 \`tools/review-pr/review-pr.mjs\`(로컬 Ollama)로 자동 생성되었습니다. 참고용이며 사람 검수를 대체하지 않습니다._`;

  try {
    sh(`gh pr comment ${prNumberArg}${repoFlag} --body-file -`, { input: commentBody });
  } catch (e) {
    console.error(`[에러] PR 코멘트 작성 실패: ${e.message}`);
    process.exit(1);
  }

  console.log(`[완료] PR #${prNumberArg}에 리뷰 코멘트 작성됨`);
}

main().catch((e) => {
  console.error(`[치명적 에러] ${e.message}`);
  process.exit(1);
});
