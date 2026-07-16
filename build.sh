#!/usr/bin/env bash
# Build SPSS Accessibility Plugin as a distributable NVDA add-on.
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# Donation: https://paypal.me/christosbouronikos

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DIST_DIR="$SCRIPT_DIR/dist"
ADDON_ROOT="$SCRIPT_DIR/addon"
MANIFEST="$SCRIPT_DIR/manifest.ini"

manifest_value() {
	local key="$1"
	awk -F= -v wanted="$key" '
		$1 ~ "^[[:space:]]*" wanted "[[:space:]]*$" {
			value = $2
			gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
			gsub(/^"|"$/, "", value)
			print value
			exit
		}
	' "$MANIFEST"
}

ADDON_NAME="$(manifest_value name)"
VERSION="$(manifest_value version)"

if [[ -z "${ADDON_NAME}" || -z "${VERSION}" ]]; then
	echo "Error: name/version missing from manifest.ini" >&2
	exit 1
fi

OUTPUT_FILE="${ADDON_NAME}-${VERSION}.nvda-addon"
OUTPUT_PATH="$DIST_DIR/$OUTPUT_FILE"
TMP_STAGE="$(mktemp -d)"
trap 'rm -rf "$TMP_STAGE"' EXIT

echo "Building SPSS Accessibility Plugin NVDA Add-on"
echo "=============================================="
echo "Version: ${VERSION}"
echo "Output: ${OUTPUT_PATH}"
echo ""

mkdir -p "$DIST_DIR"
rm -f "$OUTPUT_PATH"

rsync -a "$ADDON_ROOT/" "$TMP_STAGE/" \
	--exclude '*.pyc' \
	--exclude '__pycache__' \
	--exclude '.DS_Store' \
	--exclude '.git*' \
	--exclude '*.po' \
	--exclude 'doc/'

cp "$MANIFEST" "$TMP_STAGE/manifest.ini"
cp LICENSE "$TMP_STAGE/LICENSE"

mkdir -p "$TMP_STAGE/doc/en" "$TMP_STAGE/doc/el"
cp README.md "$TMP_STAGE/doc/en/readme.md"
cp docs/README.el.md "$TMP_STAGE/doc/el/readme.md"
cp CHANGELOG.md "$TMP_STAGE/doc/en/changelog.md"
cp docs/CHANGELOG.el.md "$TMP_STAGE/doc/el/changelog.md"

STAGE_DIR="$TMP_STAGE" PACKAGE_PATH="$OUTPUT_PATH" python3 - <<'PY'
import os
import stat
import zipfile
from pathlib import Path

stage = Path(os.environ["STAGE_DIR"])
package = Path(os.environ["PACKAGE_PATH"])
fixed_time = (1980, 1, 1, 0, 0, 0)

with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
	for path in sorted(p for p in stage.rglob("*") if p.is_file()):
		relative = path.relative_to(stage).as_posix()
		info = zipfile.ZipInfo(relative, fixed_time)
		info.compress_type = zipfile.ZIP_DEFLATED
		mode = stat.S_IMODE(path.stat().st_mode)
		info.external_attr = (mode or 0o644) << 16
		with path.open("rb") as f:
			archive.writestr(info, f.read())
PY

if command -v shasum >/dev/null 2>&1; then
	(cd "$DIST_DIR" && shasum -a 256 "$OUTPUT_FILE" > SHA256SUMS)
elif command -v sha256sum >/dev/null 2>&1; then
	(cd "$DIST_DIR" && sha256sum "$OUTPUT_FILE" > SHA256SUMS)
fi

echo ""
echo "Build complete: ${OUTPUT_PATH}"
echo ""
echo "Package ready for NVDA Add-on Store submission."
