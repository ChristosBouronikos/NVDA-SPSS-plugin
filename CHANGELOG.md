# Changelog

## 1.2.0

A major content and architecture release: reads far more of SPSS, in the language SPSS itself is running in.

- Added `addon/appModules/_spssdata`, a bilingual (English/Greek) knowledge base package covering the full IBM SPSS Statistics 31 menu tree (including submenus and statistical-procedure submenus such as Analyze, Compare Means and Proportions, Independent-Samples T Test), Data Editor/Viewer/Syntax Editor/Pivot Table Editor panes, Variable View columns, output item kinds, statistical procedure dialogs with their sub-dialogs, and a plain-language statistics glossary. Content is grounded in the IBM SPSS Statistics 31 Core System and Base documentation.
- Added detailed dialog coverage for T Tests (One-Sample, Independent-Samples with Define Groups/Options/Bootstrap, Paired-Samples), One-Way ANOVA (with Contrasts and Post Hoc), Frequencies, Descriptives, Explore, Crosstabs, Bivariate Correlations, Linear Regression, Binary Logistic Regression, Reliability Analysis, modern and legacy Nonparametric Tests, and data-preparation dialogs (Value Labels, Missing Values, Variable Type, Select Cases, Split File, Weight Cases, Compute Variable, Recode into Different Variables, Bootstrap).
- Added spoken-language resolution for SPSS content: the add-on detects whether SPSS itself is running in English or Greek from its visible menu text, and speaks menu, dialog, pane, variable-column, output-kind, and glossary descriptions in that language. This can be overridden with `NVDA+Control+Alt+Shift+J` (cycles automatic/English/Greek) or from the new SPSS Accessibility settings panel. This is independent of NVDA's own interface language, which continues to drive the add-on's own voice (shortcut lists, status/error messages).
- Added an "SPSS Accessibility" category to NVDA's Settings dialog (`addon/globalPlugins/spssAccessibilityHelper.py`), with a persistent spoken-language choice.
- Added `NVDA+Control+Alt+Shift+K` to read every field and button currently visible in the focused SPSS dialog, each with its kind and a short description — for getting the whole picture of a dialog with many options (like a t-test's main fields plus its sub-dialog buttons) before tabbing through it.
- Added `NVDA+Control+Alt+Shift+Q` to list every item in the menu or submenu that is currently open.
- Added a Pivot Table Editor pane, recognized alongside the existing Overview, Data View, Variable View, Output Viewer, Syntax Editor, and Chart Builder panes.
- Menu-item and dialog-field recognition now uses accent-insensitive, alias-aware lookup, so Greek SPSS text (which carries accents) matches the same knowledge base entries as English text.
- Replaced the flat, English-only `SPSS_MENU_MAP` with the full nested menu tree from `_spssdata.menus`, including previously uncovered menus (Tools, Pivot) and dozens of previously uncovered submenu items and statistical procedures.
- Regenerated the Greek gettext catalogue (`addon/locale/el/LC_MESSAGES/nvda.po`) for the rewritten app module; every message the add-on itself speaks (as opposed to SPSS content, which now follows the resolved SPSS language) is translated.
- Added an offline automated test suite (`tests/`), including stub NVDA modules and a fake UI Automation tree builder, that exercises pane detection, language resolution, menu/dialog recognition, and the new commands without requiring NVDA or SPSS to be installed. Wired into `scripts/validate.sh`.
- Hardened modal-dialog support after review: foreground dialog roots and dialog windows are now recognized correctly; bilingual title matching is preferred before heuristic control matching; Greek dialog controls participate in fallback recognition; generic single controls can no longer misidentify a dialog; and the detected SPSS language is preserved while a modal dialog hides the menu bar. Added regression tests for these paths, the settings panel, and current NVDA executable registration/cleanup.
- Added documentation-based compatibility coverage for IBM SPSS Statistics 24–31. Legacy `Compare Means` parent aliases now participate in menu-path matching, newer optional t-test controls are not required for dialog recognition, and offline tests cover SPSS 24–26, 27–30, and 31 dialog profiles plus the pre-Overview Data Editor layout.
- `scripts/validate.sh` now also compiles `addon/appModules/_spssdata` and runs the new test suite before building the package.

## 1.1.2

Documentation release addressing NVDA Add-on Store review feedback.

- Split the README into an English source file (`README.md`) and a Greek translation (`docs/README.el.md`), matching the existing changelog split, instead of one bilingual file.
- Added a link to the IBM SPSS Statistics product page in the README overview.

## 1.1.1

Maintenance release addressing NVDA Add-on Store review feedback.

- Updated the last tested NVDA version to 2026.1.1 after testing with NVDA 2026.1.1 (64-bit), IBM SPSS Statistics 31.0.0.0 (build 117), and Windows 11.
- Removed the unnecessary `__init__.py` files from `appModules` and `globalPlugins`.
- Documented each registered SPSS executable name with a source comment explaining which SPSS release or component uses it.
- Removed window-title-like entries and undocumented executable aliases (`spssstatistics`, `ibmspssstatistics`) from executable registration.
- Added a Testing section and an AI Assistance Disclosure section to the README in English and Greek.

## 1.1.0

- Added Overview and Chart Builder recognition, help, and shortcuts.
- Expanded SPSS menu descriptions with context-aware guidance for Data Editor, Output Viewer, Syntax Editor, Chart Builder, and menu bar focus.
- Added output accessibility guidance, including pivot-table screen-reader settings and export workflows for inaccessible charts, trees, and model views.
- Added Output Viewer item type, outline level, item position, and expanded/collapsed announcements when SPSS exposes them.
- Added Variable View action hints for Type, Values, Missing, Measure, and Role cells.
- Added fallback labels for Value Labels, Missing Values, Variable Type, import wizards, case-selection dialogs, common analysis dialogs, and Chart Builder regions.
- Added beginner/concise guidance toggle and an NVDA-log troubleshooting command for the current SPSS accessibility object.
- Expanded Greek translations and Greek documentation for the new workflows.
- Added `NVDA+Control+Alt+T` to read the current SPSS tab and table context.
- Improved Excel-like cell announcements for Data View, Variable View, and output tables.
- Added A1-style cell references when row and column numbers are exposed by SPSS.
- Added row header, column header, table name, and selected-tab reporting.
- Added Greek translation files for NVDA messages.
- Added Greek documentation packaging support.
- Added where-am-I, menu-path, dialog-help, dialog-list, table-summary, output-outline, output row/column, output-copy, variable-row, and bilingual glossary commands.
- Added optional automatic table-cell announcements while moving through SPSS tables.
- Added value-label reporting for data cells when SPSS exposes a readable label separately from the raw value.
- Merged project documentation into a single Greek-first, English-second README source.
- Expanded menu coverage with a detailed map for standard SPSS menu items and focused menu-item help while navigating menus.
- Improved output table reading with table size, richer row/column summaries, and a command to copy the current output table row.

## 1.0.0

Initial release.

- Added IBM SPSS Statistics app module for NVDA.
- Added pane detection for Output Viewer, Data View, Variable View, Syntax Editor, and menus.
- Added detailed pane descriptions when focus enters recognized SPSS areas.
- Added output reading command for selected or focused output blocks.
- Added Data View cell description command.
- Added Variable View definition description command.
- Added SPSS menu explanation command.
- Added fallback labels for common SPSS dialog and toolbar controls.
- Added executable aliases for common SPSS process names.
- Added macOS/Linux and Windows build scripts.
