# Project Structure

This repository is organized so the source tree is ready for GitHub and the NVDA Add-on Store.

## Source Files

- `addon/`: source files that are copied into the `.nvda-addon` package.
- `addon/appModules/`: SPSS app module and executable aliases.
- `addon/appModules/_spssdata/`: bilingual (English/Greek) knowledge base package of SPSS menus, dialogs, panes, and statistics terms, imported by `appModules/spss.py`.
- `addon/globalPlugins/`: global plugin helper commands, including SPSS app-module registration and the "SPSS Accessibility" NVDA settings panel.
- `addon/locale/`: compiled add-on translations and locale-specific manifest files.
- `manifest.ini`: add-on package metadata copied to the archive root during build.
- `README.md`: English readme, the source for GitHub documentation and package `doc/en/readme.md`.
- `docs/README.el.md`: Greek readme used for package `doc/el/readme.md`.
- `CHANGELOG.md`: English changelog used for GitHub releases and package `doc/en/changelog.md`.
- `docs/CHANGELOG.el.md`: Greek changelog used for package `doc/el/changelog.md`.
- `tests/`: offline automated tests (no NVDA or SPSS required) covering the `_spssdata` knowledge base, app module, helper global plugin, settings panel, and executable registration, using stub NVDA modules in `tests/nvdastubs/`. Not packaged into the add-on.

## Generated Files

- `dist/`: local build output. It contains `.nvda-addon` files and `SHA256SUMS`. It is ignored by Git.
- `addon/doc/`: not used as source. Package documentation is generated during build from `README.md` and changelog files.
- `addon/LICENSE`: not used as source. The package receives `LICENSE` from the repository root during build.

## Store Files

- `store/ADDON_STORE_SUBMISSION.md`: human-readable Add-on Store submission notes.
- `store/spssAccessibility-1.2.0.json`: draft metadata matching the Add-on Store schema. Update the URL and checksum after publishing the GitHub release asset.

## Automation

- `build.sh` and `build.ps1`: build the package into `dist/`.
- `scripts/validate.sh`: compiles Python, runs the `tests/` suite, compiles Greek gettext, builds the package, and checks the archive contents.
- `.github/workflows/validate.yml`: runs the validation script in GitHub Actions and uploads the built add-on as an artifact.
