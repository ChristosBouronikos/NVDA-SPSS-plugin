#!/usr/bin/env bash
# Validate source files and the distributable NVDA add-on package.
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

MANIFEST="manifest.ini"
ADDON_NAME="$(awk -F= '/^[[:space:]]*name[[:space:]]*=/ {print $2; exit}' "$MANIFEST" | xargs | sed 's/^"//; s/"$//')"
VERSION="$(awk -F= '/^[[:space:]]*version[[:space:]]*=/ {print $2; exit}' "$MANIFEST" | xargs | sed 's/^"//; s/"$//')"
PACKAGE="dist/${ADDON_NAME}-${VERSION}.nvda-addon"

echo "Checking Python syntax"
PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/nvda_spss_pycache}" \
	python3 -m py_compile addon/appModules/*.py addon/appModules/_spssdata/*.py addon/globalPlugins/*.py

echo "Running offline test suite"
python3 -m unittest discover -s tests -v

echo "Checking Greek gettext catalog"
msgfmt --check -o addon/locale/el/LC_MESSAGES/nvda.mo addon/locale/el/LC_MESSAGES/nvda.po

echo "Building package"
./build.sh

echo "Checking package archive"
unzip -t "$PACKAGE" >/dev/null
archive_listing="$(unzip -Z1 "$PACKAGE")"
grep -q '^manifest\.ini$' <<< "$archive_listing"
grep -q '^doc/en/readme\.md$' <<< "$archive_listing"
grep -q '^doc/el/readme\.md$' <<< "$archive_listing"
grep -q '^locale/el/manifest\.ini$' <<< "$archive_listing"
grep -q '^locale/el/LC_MESSAGES/nvda\.mo$' <<< "$archive_listing"

if grep -E '\.po|\.pyc|__pycache__|\.DS_Store|\.git' <<< "$archive_listing" >/dev/null; then
	echo "Error: package contains source-only or generated files that should be excluded" >&2
	exit 1
fi

echo "Checking README source policy"
readme_files="$(rg --files | rg -i '(^|/)readme[^/]*\.md$' | sort)"
expected_readme_files="$(printf '%s\n' "README.md" "docs/README.el.md" | sort)"
if [[ "$readme_files" != "$expected_readme_files" ]]; then
	echo "Error: expected exactly README.md (English) and docs/README.el.md (Greek); found:" >&2
	echo "$readme_files" >&2
	exit 1
fi

STORE_JSON="store/${ADDON_NAME}-${VERSION}.json"
if [[ -f "$STORE_JSON" ]]; then
	echo "Checking store metadata draft"
	python3 - "$MANIFEST" "$STORE_JSON" "$PACKAGE" <<'PY'
import configparser
import hashlib
import json
import sys

manifest_path, store_path, package_path = sys.argv[1:]

manifest = configparser.ConfigParser()
with open(manifest_path, "r", encoding="utf-8") as f:
	manifest.read_string("[addon]\n" + f.read())
addon = manifest["addon"]

with open(store_path, "r", encoding="utf-8") as f:
	store = json.load(f)

def manifest_value(key):
	return addon.get(key, "").strip().strip('"')

def fail(message):
	raise SystemExit(message)

if store.get("addonId") != manifest_value("name"):
	fail("store addonId does not match manifest name")
if store.get("addonVersionName") != manifest_value("version"):
	fail("store addonVersionName does not match manifest version")
if store.get("displayName") != manifest_value("summary"):
	fail("store displayName does not match manifest summary")
if store.get("homepage") != manifest_value("url"):
	fail("store homepage does not match manifest url")
if store.get("channel") != manifest_value("updateChannel"):
	fail("store channel does not match manifest updateChannel")

expected_min = ".".join(str(store["minNVDAVersion"][key]) for key in ("major", "minor", "patch"))
expected_last = ".".join(str(store["lastTestedVersion"][key]) for key in ("major", "minor", "patch"))
if expected_min != manifest_value("minimumNVDAVersion"):
	fail("store minNVDAVersion does not match manifest minimumNVDAVersion")
if expected_last != manifest_value("lastTestedNVDAVersion"):
	fail("store lastTestedVersion does not match manifest lastTestedNVDAVersion")

with open(package_path, "rb") as f:
	sha256 = hashlib.sha256(f.read()).hexdigest()
if store.get("sha256", "").lower() != sha256:
	fail("store sha256 does not match built package")
PY
fi

echo "Validation complete: $PACKAGE"
