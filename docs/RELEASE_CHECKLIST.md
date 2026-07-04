# Release Checklist

Use this checklist for every public NVDA add-on release.

## Versioning

- Update `addon/manifest.ini`.
- Update `buildVars.py`.
- Update `CHANGELOG.md`.
- Update `docs/CHANGELOG.el.md`.
- Confirm README install examples mention the new `.nvda-addon` filename.

## Build

```bash
msgfmt addon/locale/el/LC_MESSAGES/nvda.po -o addon/locale/el/LC_MESSAGES/nvda.mo
PYTHONPYCACHEPREFIX=/private/tmp/nvda_spss_pycache python3 -m py_compile addon/appModules/*.py addon/globalPlugins/*.py
./build.sh
```

Use `./build.sh` for the official release asset and Add-on Store checksum. The PowerShell build is available for Windows local testing.

## Package Review

```bash
unzip -l dist/spssAccessibility-1.1.0.nvda-addon
```

Confirm:

- `manifest.ini` is at the archive root.
- `appModules/spss.py` is included.
- `globalPlugins/spssAccessibilityHelper.py` is included.
- `doc/en/readme.md` and `doc/el/readme.md` are included.
- `locale/el/LC_MESSAGES/nvda.mo` is included.
- `.po`, `.pyc`, `__pycache__`, `.DS_Store`, and Git files are not included.

## Manual NVDA Smoke Test

- Install the add-on from external source.
- Restart NVDA.
- Open IBM SPSS Statistics.
- Verify `NVDA+Control+Alt+Shift+H` lists shortcuts.
- Verify `NVDA+Control+Alt+D` announces Data View.
- Verify `NVDA+Control+Alt+Shift+D` announces a data cell.
- Verify `NVDA+Control+Alt+V` announces Variable View.
- Verify `NVDA+Control+Alt+Shift+V` announces a variable-definition cell.
- Verify `NVDA+Control+Alt+T` announces current tab and table context.
- Run an SPSS analysis and verify `NVDA+Control+Alt+Shift+O` reads output context.
- Switch NVDA to Greek and verify add-on messages are localized.
- Check NVDA log for errors.

## GitHub Release

- Tag the release, for example `v1.1.0`.
- Attach `dist/spssAccessibility-1.1.0.nvda-addon`.
- Attach or paste the checksum from `dist/SHA256SUMS`.
- Include the changelog section for the version.
- Link to the manual test notes.

## NVDA Add-on Store

- Confirm `addon/manifest.ini` and `store/spssAccessibility-1.1.0.json` agree on add-on id, version, display name, minimum NVDA version, last tested NVDA version, channel, homepage, and license.
- Confirm the `URL` in the store JSON points to the final GitHub release asset.
- Confirm the `sha256` in the store JSON matches `dist/SHA256SUMS`.
- Submit through the NVDA `addon-datastore` Add-on registration issue form.
