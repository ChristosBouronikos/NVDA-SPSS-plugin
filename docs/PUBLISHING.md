# Publishing Guide

This guide prepares `SPSS Accessibility Plugin` for GitHub and the NVDA Add-on Store.

## Repository

The repository should be published as:

```text
https://github.com/ChristosBouronikos/NVDA-SPSS-plugin
```

The technical add-on ID remains:

```text
spssAccessibility
```

Do not rename the technical add-on ID unless you intentionally want NVDA and the Add-on Store to treat it as a different add-on.

## Validate

Run this before every release:

```bash
./scripts/validate.sh
```

Expected release files:

```text
dist/spssAccessibility-1.1.2.nvda-addon
dist/SHA256SUMS
```

Current SHA256:

```text
04642a6e6433feb4461765ccaaf01274b57ee6ad536e572ff162316f4a9af5fe
```

## GitHub Release

Create a GitHub release with:

```text
Tag: v1.1.2
Title: SPSS Accessibility Plugin 1.1.2
Asset: dist/spssAccessibility-1.1.2.nvda-addon
```

After the release is published, the asset URL should be:

```text
https://github.com/ChristosBouronikos/NVDA-SPSS-plugin/releases/download/v1.1.2/spssAccessibility-1.1.2.nvda-addon
```

Use that exact URL in the NVDA Add-on Store submission.

## NVDA Add-on Store

Submit through the Add-on Store issue form:

```text
https://github.com/nvaccess/addon-datastore/issues/new?template=add-on-registration.yml
```

Use these values:

```text
Add-on ID: spssAccessibility
Version: 1.1.2
Channel: stable
Display name: SPSS Accessibility Plugin
Publisher: Bouronikos Christos
Homepage: https://github.com/ChristosBouronikos/NVDA-SPSS-plugin
Source URL: https://github.com/ChristosBouronikos/NVDA-SPSS-plugin
Download URL: https://github.com/ChristosBouronikos/NVDA-SPSS-plugin/releases/download/v1.1.2/spssAccessibility-1.1.2.nvda-addon
SHA256: 04642a6e6433feb4461765ccaaf01274b57ee6ad536e572ff162316f4a9af5fe
License: GPL v2
License URL: https://github.com/ChristosBouronikos/NVDA-SPSS-plugin/blob/main/LICENSE
Minimum NVDA version: 2023.1.0
Last tested NVDA version: 2026.1.1
```

First-time submissions can require manual NV Access approval. The generated pull request must pass validation and VirusTotal checks before the add-on appears in the store.
