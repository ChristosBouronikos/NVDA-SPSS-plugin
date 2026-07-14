# Project Structure

This repository is organized so the source tree is ready for GitHub and the NVDA Add-on Store.

## Source Files

- `addon/`: source files that are copied into the `.nvda-addon` package.
- `addon/appModules/`: SPSS app module and executable aliases.
- `addon/globalPlugins/`: global plugin helper commands.
- `addon/locale/`: compiled add-on translations and locale-specific manifest files.
- `manifest.ini`: add-on package metadata copied to the archive root during build.
- `README.md`: the single source for GitHub documentation and generated package readmes. Greek comes first, English second.
- `CHANGELOG.md`: English changelog used for GitHub releases and package `doc/en/changelog.md`.
- `docs/CHANGELOG.el.md`: Greek changelog used for package `doc/el/changelog.md`.

## Generated Files

- `dist/`: local build output. It contains `.nvda-addon` files and `SHA256SUMS`. It is ignored by Git.
- `addon/doc/`: not used as source. Package documentation is generated during build from `README.md` and changelog files.
- `addon/LICENSE`: not used as source. The package receives `LICENSE` from the repository root during build.

## Store Files

- `store/ADDON_STORE_SUBMISSION.md`: human-readable Add-on Store submission notes.
- `store/spssAccessibility-1.1.1.json`: draft metadata matching the Add-on Store schema. Update the URL and checksum after publishing the GitHub release asset.

## Automation

- `build.sh` and `build.ps1`: build the package into `dist/`.
- `scripts/validate.sh`: compiles Python, compiles Greek gettext, builds the package, and checks the archive contents.
- `.github/workflows/validate.yml`: runs the validation script in GitHub Actions and uploads the built add-on as an artifact.
