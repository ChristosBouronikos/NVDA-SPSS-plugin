# Contributing

Contributions are welcome, especially test reports from different IBM SPSS Statistics and NVDA versions.

## Useful Reports

When reporting an issue, include:

- NVDA version.
- NVDA language.
- IBM SPSS Statistics version.
- SPSS interface language.
- Windows version.
- Which SPSS window was active: Data Editor, Variable View, Output Viewer, Syntax Editor, or a dialog.
- The key command used.
- What NVDA announced.
- What you expected NVDA to announce.
- Any relevant NVDA log errors.

## Development Setup

This add-on does not require third-party Python packages for the source checks used here.

Run syntax checks:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/nvda_spss_pycache python3 -m py_compile addon/appModules/*.py addon/globalPlugins/*.py
```

Build the add-on:

```bash
./build.sh
```

Run the full release validation:

```bash
scripts/validate.sh
```

## Translation Updates

Greek strings live in:

```text
addon/locale/el/LC_MESSAGES/nvda.po
```

Compile them with:

```bash
msgfmt addon/locale/el/LC_MESSAGES/nvda.po -o addon/locale/el/LC_MESSAGES/nvda.mo
```

Only the compiled `.mo` file is included in the release package.
