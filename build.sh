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
	' "$ADDON_ROOT/manifest.ini"
}

ADDON_NAME="$(manifest_value name)"
VERSION="$(manifest_value version)"

if [[ -z "${ADDON_NAME}" || -z "${VERSION}" ]]; then
	echo "Error: name/version missing from addon/manifest.ini" >&2
	exit 1
fi

OUTPUT_FILE="${ADDON_NAME}-${VERSION}.nvda-addon"
OUTPUT_PATH="$DIST_DIR/$OUTPUT_FILE"
TMP_STAGE="$(mktemp -d)"
trap 'rm -rf "$TMP_STAGE"' EXIT

extract_readme_section() {
	local start_marker="$1"
	local end_marker="$2"
	local output_path="$3"
	awk -v start="$start_marker" -v end="$end_marker" '
		$0 == start { in_section = 1; next }
		$0 == end { in_section = 0; exit }
		in_section { print }
	' README.md > "$output_path"
	if [[ ! -s "$output_path" ]]; then
		echo "Error: could not extract $start_marker from README.md" >&2
		exit 1
	fi
}

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

cp LICENSE "$TMP_STAGE/LICENSE"

mkdir -p "$TMP_STAGE/doc/en" "$TMP_STAGE/doc/el"
extract_readme_section "<!-- ENGLISH-README-START -->" "<!-- ENGLISH-README-END -->" "$TMP_STAGE/doc/en/readme.md"
extract_readme_section "<!-- GREEK-README-START -->" "<!-- GREEK-README-END -->" "$TMP_STAGE/doc/el/readme.md"
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
echo "Install by double-clicking the .nvda-addon file on a Windows machine with NVDA installed."
