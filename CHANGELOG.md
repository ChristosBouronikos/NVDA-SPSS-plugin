# Changelog

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
