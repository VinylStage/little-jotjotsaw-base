#!/usr/bin/env bash
# confirm-chain 문서 변경 게이트를 임의의 저장소에 설치한다.
#
# 사용법:
#   ./install-hooks.sh <대상 저장소 경로> [감시경로 ...]
#
# 예:
#   ./install-hooks.sh ~/work/some-repo 'docs/process/*'
#   ./install-hooks.sh ~/work/other-repo 'docs/audit/*' 'docs/decisions/*'
#
# 하는 일:
#   1. 대상 저장소에 .githooks/ 를 만들고 훅을 복사한다(추적 대상 — 팀 공유).
#   2. core.hooksPath 를 .githooks 로 설정한다(로컬 설정).
#   3. confirmchain.dir 을 이 도구 경로로 설정한다(로컬 설정 — 경로가 커밋되지 않음).
#   4. 감시 경로를 .confirm-chain-paths 에 기록한다(추적 대상). 인자가 없으면 기존 파일을 유지한다.
#   5. 체크포인트 DB를 .gitignore 에 추가한다.
set -euo pipefail

TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo "사용법: $0 <대상 저장소 경로> [감시경로 ...]" >&2
  exit 1
fi

TARGET="$(cd "$1" && git rev-parse --show-toplevel)"
shift

echo "대상 저장소: $TARGET"
echo "도구 경로  : $TOOL_DIR"

# 1. 훅 복사
mkdir -p "$TARGET/.githooks"
for h in pre-commit prepare-commit-msg; do
  cp "$TOOL_DIR/hooks/$h" "$TARGET/.githooks/$h"
  chmod +x "$TARGET/.githooks/$h"
  echo "  설치: .githooks/$h"
done

# 2~3. 로컬 git 설정 (커밋되지 않으므로 경로 하드코딩이 저장소에 남지 않는다)
git -C "$TARGET" config core.hooksPath .githooks
git -C "$TARGET" config confirmchain.dir "$TOOL_DIR"
echo "  설정: core.hooksPath=.githooks"
echo "  설정: confirmchain.dir=$TOOL_DIR"

# 4. 감시 경로
PATHS_FILE="$TARGET/.confirm-chain-paths"
if [ $# -gt 0 ]; then
  {
    echo "# confirm-chain 문서 변경 게이트 감시 경로"
    echo "# 이 경로에 걸리는 파일이 스테이징되면 process_doc 승인 없이는 커밋되지 않는다."
    echo "# 형식: 셸 glob 패턴 (저장소 루트 기준 상대경로)"
    for p in "$@"; do echo "$p"; done
  } > "$PATHS_FILE"
  echo "  기록: .confirm-chain-paths ($#개 패턴)"
elif [ -f "$PATHS_FILE" ]; then
  echo "  유지: .confirm-chain-paths (기존 설정 그대로)"
else
  echo "  경고: 감시 경로가 지정되지 않아 게이트가 아무것도 잡지 않습니다." >&2
fi

# 5. 체크포인트 DB 를 추적에서 제외
GI="$TARGET/.gitignore"
if ! grep -qxF '.confirm-chain.sqlite' "$GI" 2>/dev/null; then
  printf '\n# confirm-chain 승인 체크포인트 (로컬 전용)\n.confirm-chain.sqlite\n' >> "$GI"
  echo "  추가: .gitignore <- .confirm-chain.sqlite"
fi

echo
echo "완료. 확인:"
echo "  git -C $TARGET config core.hooksPath"
