# NVDA Add-on Store Submission Notes

This directory contains store-facing metadata and release notes for `spssAccessibility`.

## Official Submission Flow

NVDA Add-on Store submissions are made through the `nvaccess/addon-datastore` Add-on registration issue form. The form generates store metadata from the issue fields and the add-on manifest, then automated validation checks the generated pull request.

Before submitting, publish a GitHub release with the `.nvda-addon` file attached. The store metadata requires a stable download URL and the SHA256 checksum of that exact file.

## Add-on Identity

- Add-on id: `spssAccessibility`
- Display name: `SPSS Accessibility Plugin`
- Current version: `1.1.1`
- Channel: `stable`
- Minimum NVDA version: `2023.1.0`
- Last tested NVDA version: `2026.1.1`
- Publisher: `Bouronikos Christos`
- License: `GPL v2`
- Homepage/source: `https://github.com/ChristosBouronikos/NVDA-SPSS-plugin`

These values must match:

- `manifest.ini`
- the GitHub release asset name
- `store/spssAccessibility-1.1.1.json`
- the Add-on Store issue form

## Release Asset

Build the release asset with:

```bash
./build.sh
```

Use `build.sh` for the official GitHub release asset and Add-on Store checksum. `build.ps1` is kept for Windows convenience, but the store checksum in `store/spssAccessibility-1.1.1.json` is generated from the deterministic `build.sh` archive.

Expected output:

```text
dist/spssAccessibility-1.1.1.nvda-addon
dist/SHA256SUMS
```

Suggested GitHub release asset URL:

```text
https://github.com/ChristosBouronikos/NVDA-SPSS-plugin/releases/download/v1.1.1/spssAccessibility-1.1.1.nvda-addon
```

## Package Contents

The `.nvda-addon` package contains:

- `manifest.ini`
- `LICENSE`
- `appModules/spss.py`
- SPSS executable alias modules
- `globalPlugins/spssAccessibilityHelper.py`
- English documentation under `doc/en`
- Greek documentation under `doc/el`
- Greek locale manifest under `locale/el/manifest.ini`
- Greek translation catalog under `locale/el/LC_MESSAGES/nvda.mo`

The package intentionally excludes:

- Python bytecode
- `__pycache__`
- `.DS_Store`
- `.po` translation source files
- Git metadata

## Store Description

Short summary:

```text
SPSS Accessibility Plugin
```

Long description:

```text
SPSS Accessibility Plugin improves IBM SPSS Statistics accessibility for blind and visually impaired users. Created by Bouronikos Christos, contact: chrisbouronikos@gmail.com. If this add-on helps you, please consider a kind donation via PayPal: https://paypal.me/christosbouronikos
```

Greek display name:

```text
SPSS Accessibility Plugin
```

Greek description:

```text
Το SPSS Accessibility Plugin βελτιώνει την προσβασιμότητα του IBM SPSS Statistics για τυφλούς χρήστες και χρήστες με προβλήματα όρασης. Δημιουργός: Bouronikos Christos, email: chrisbouronikos@gmail.com. Αν σας βοηθά αυτό το πρόσθετο, παρακαλώ σκεφτείτε μια ευγενική δωρεά μέσω PayPal: https://paypal.me/christosbouronikos
```

## Validation Before Submission

Before submitting a release:

1. Run `scripts/validate.sh`.
2. Confirm `dist/spssAccessibility-1.1.1.nvda-addon` exists.
3. Confirm the SHA256 in `dist/SHA256SUMS` matches `store/spssAccessibility-1.1.1.json`.
4. Confirm `manifest.ini` is at the archive root.
5. Confirm `locale/el/LC_MESSAGES/nvda.mo` and `locale/el/manifest.ini` are included.
6. Confirm no `.po`, `__pycache__`, `.pyc`, `.DS_Store`, or Git files are inside the package.
7. Install the add-on in NVDA on Windows.
8. Restart NVDA.
9. Test with IBM SPSS Statistics Data Editor, Variable View, Output Viewer, Syntax Editor, common dialogs, and Greek NVDA language.
10. Check the NVDA log for errors.

## Manual SPSS Test Matrix

- NVDA language: English
- NVDA language: Greek
- SPSS interface language: English
- SPSS interface language: Greek, if available
- SPSS Data Editor with Data View active
- SPSS Data Editor with Variable View active
- SPSS Output Viewer after running a statistical procedure
- SPSS Syntax Editor
- SPSS dialogs with OK, Cancel, Paste, Statistics, Charts, and Options buttons
- SPSS tables with value labels enabled and disabled
