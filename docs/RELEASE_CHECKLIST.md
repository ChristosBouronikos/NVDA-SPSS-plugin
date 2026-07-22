# Release Checklist

Use this checklist for every public NVDA add-on release.

## Versioning

- Update `manifest.ini`.
- Update `buildVars.py`.
- Update `CHANGELOG.md`.
- Update `docs/CHANGELOG.el.md`.
- Confirm install examples in both `README.md` and `docs/README.el.md` mention the new `.nvda-addon` filename.

## Build

```bash
msgfmt addon/locale/el/LC_MESSAGES/nvda.po -o addon/locale/el/LC_MESSAGES/nvda.mo
PYTHONPYCACHEPREFIX=/private/tmp/nvda_spss_pycache python3 -m py_compile addon/appModules/*.py addon/appModules/_spssdata/*.py addon/globalPlugins/*.py
python3 -m unittest discover -s tests
./build.sh
```

Use `./build.sh` for the official release asset and Add-on Store checksum. The PowerShell build is available for Windows local testing. `scripts/validate.sh` runs all of the above (plus the archive and store-metadata checks below) in one step.

## Package Review

```bash
unzip -l dist/spssAccessibility-1.2.0.nvda-addon
```

Confirm:

- `manifest.ini` is at the archive root.
- `appModules/spss.py` and `appModules/_spssdata/*.py` are included.
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
- Open a statistical dialog (for example Analyze, Compare Means and Proportions, Independent-Samples T Test) and verify `NVDA+Control+Alt+Shift+I` and `NVDA+Control+Alt+Shift+K` describe it and its fields.
- Verify `NVDA+Control+Alt+Shift+Q` lists items while a menu or submenu is open.
- Verify `NVDA+Control+Alt+Shift+J` cycles the spoken SPSS-content language, and that `NVDA+N`, `Preferences`, `Settings`, `SPSS Accessibility` shows and saves the same setting.
- Switch NVDA to Greek and verify add-on messages are localized.
- If a Greek-localized SPSS installation is available, verify automatic detection speaks SPSS content in Greek.
- Check NVDA log for errors.

## GitHub Release

- Tag the release, for example `v1.2.0`.
- Attach `dist/spssAccessibility-1.2.0.nvda-addon`.
- Attach or paste the checksum from `dist/SHA256SUMS`.
- Include the changelog section for the version.
- Link to the manual test notes.

## NVDA Add-on Store

- Confirm `manifest.ini` and `store/spssAccessibility-1.2.0.json` agree on add-on id, version, display name, minimum NVDA version, last tested NVDA version, channel, homepage, and license.
- Confirm the `URL` in the store JSON points to the final GitHub release asset.
- Confirm the `sha256` in the store JSON matches `dist/SHA256SUMS`.
- Submit through the NVDA `addon-datastore` Add-on registration issue form.
