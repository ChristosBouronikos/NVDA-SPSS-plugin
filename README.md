# SPSS Accessibility Plugin

**Author:** Bouronikos Christos  
**Email:** chrisbouronikos@gmail.com  
**Donation:** If this add-on helps you, please consider a kind donation via PayPal: https://paypal.me/christosbouronikos

## Overview

SPSS Accessibility Plugin improves access to [IBM SPSS Statistics](https://www.ibm.com/products/spss-statistics) for blind and visually impaired users. Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com. It focuses on SPSS areas that are often difficult with a screen reader:

- SPSS menus and submenus, with context-aware descriptions of what each menu and menu item does, down to individual statistical procedures such as Independent-Samples T Test or One-Way ANOVA.
- Data Editor views: Overview, Data View, and Variable View, including every Variable View column (Name, Type, Width, Decimals, Label, Values, Missing, Columns, Align, Measure, Role).
- Output Viewer outline, output document area, pivot tables, Pivot Table Editor, and output limitations.
- Statistical procedure dialogs and their sub-dialogs: T Tests, One-Way ANOVA, Frequencies, Descriptives, Explore, Crosstabs, Correlations, Regression, Reliability Analysis, Nonparametric Tests, and common data-preparation dialogs such as Value Labels, Missing Values, Variable Type, Select Cases, Split File, Weight Cases, Compute Variable, Recode, and Bootstrap. A dedicated command reads every field and button in whichever dialog is open, so a dialog with many options — like a t-test's Define Groups, Options, and Bootstrap sub-dialogs — can be understood as a whole before you start tabbing through it.
- Chart Builder dialog regions, including variables, gallery, canvas, and drop zones.
- Syntax Editor, Paste workflow, Run menu, and common syntax-window areas.
- Excel-like table reading with tab, row, column, headers, cell reference, and value.
- Optional automatic table-cell announcements and value-label reading when SPSS exposes both a coded value and a label.
- A plain-language, bilingual statistics glossary (mean, standard deviation, significance level, effect size, Cronbach's alpha, and more).

**Everything above is available in English and Greek.** The add-on detects which language IBM SPSS Statistics itself is running in from its visible menu text, and speaks its menu, dialog, pane, and glossary descriptions in that language. This can also be set manually to always use English or always use Greek — see [Spoken Language For SPSS Content](#spoken-language-for-spss-content) below. NVDA's own messages (shortcut lists, error and status announcements) always follow NVDA's own interface language, independent of this setting.

The add-on uses SPSS UI Automation information when SPSS exposes it. Because SPSS versions differ, it also uses fallback heuristics based on object names, roles, class names, automation ids, table headers, and surrounding panes.

## What Is The NVDA Key?

The NVDA key is the modifier used for NVDA commands. By default it is usually Insert, Numpad Insert, or Caps Lock if enabled in NVDA settings.

For example, `NVDA+Control+Alt+D` means hold the NVDA key, Control, and Alt, then press D.

## Main Features

### Spoken Language For SPSS Content

The add-on decides which language to use for menu, dialog, pane, variable-column, output-kind, and glossary descriptions in one of two ways:

- **Automatic (default):** it looks at the visible SPSS menu bar text. If it recognizes Greek menu words (Αρχείο, Επεξεργασία, Δεδομένα, and so on), it speaks SPSS content in Greek; otherwise it speaks English.
- **Manual:** you can pin it to English or Greek regardless of what SPSS is showing.

Two ways to change it:

- Press `NVDA+Control+Alt+Shift+J` to cycle between Automatic, English, and Greek. NVDA announces the new setting.
- Open NVDA's menu with `NVDA+N`, choose `Preferences`, then `Settings`, then the `SPSS Accessibility` category, and choose from the `Spoken language for SPSS menu, dialog, and pane descriptions` list.

Either way, the setting is saved with your NVDA configuration and used the next time NVDA starts. This setting only affects how the add-on explains what SPSS content *means*; NVDA's own voice (shortcut lists, error messages, template phrases such as "Cell B12") always follows NVDA's own interface language.

### Pane Descriptions

When focus enters a recognized SPSS area, NVDA announces a description. Beginner guidance is enabled by default and can be changed to concise announcements.

- Overview: summarizes the active dataset and the Update workflow.
- Data View: explains cases, variables, cells, and the current cell editor.
- Variable View: explains variable rows and properties such as Name, Type, Label, Values, Missing, Measure, and Role.
- Output Viewer: explains the left outline, right output pane, readable pivot/text output, and inaccessible chart/model output.
- Syntax Editor: explains command text, Paste workflow, command navigation pane, gutter, and error pane.
- Chart Builder: explains variables list, categories list, Gallery, Basic Elements, canvas, drop zones, and Shift+F10 commands.
- Menus: summarizes File, Edit, View, Data, Transform, Analyze, Graphs, Insert, Format, Utilities, Extensions/Add-ons, Run, Window, and Help.

### Output Viewer Support

`NVDA+Control+Alt+Shift+O` reads the current output context. It tries to report:

- The selected output outline item.
- Outline level, item position, and expanded or collapsed state when exposed.
- Output item type, such as table, pivot table, log, notes, warning, title, chart, tree model, or model view.
- Pivot table or table-cell row and column headers when available.
- Nearby readable text from notes, logs, or text output.

`NVDA+Control+Alt+Shift+Y` is specifically for pivot tables and output tables. It reports the table name, table size, current cell, row and column headers, and more items from the current row and column. `NVDA+Control+Alt+Shift+X` copies the current output table row as plain text in `header: value` format.

SPSS usually exposes pivot tables and text output to screen readers. Charts, tree diagrams, and model views are usually not exposed as readable text. Use `NVDA+Control+Alt+Shift+E` for output accessibility and export guidance.

### Data View Support

`NVDA+Control+Alt+Shift+D` describes the current data cell. When SPSS exposes enough table metadata, NVDA reports:

- Selected tab and table name.
- A1-style cell reference, such as B12.
- Case row number.
- Variable name or column number.
- Row and column headers when available.
- Current cell value or current cell editor value.
- A value label when SPSS exposes a separate description, for example code `1` with label `Yes`.

### Variable View Support

`NVDA+Control+Alt+Shift+V` describes the current variable-definition cell. When available, NVDA reports:

- Current variable row.
- Current property, such as Name, Type, Label, Values, Missing, Measure, or Role.
- Row and column coordinates.
- Current value.
- Action hints for Type, Values, Missing, Measure, and Role.

For `Type`, `Values`, and `Missing`, SPSS commonly opens a detailed edit dialog when you press Space.

`NVDA+Control+Alt+Shift+R` tries to read the whole current variable row, including Name, Type, Width, Decimals, Label, Values, Missing, Measure, and Role when that information is present in the table.

### Additional Table, Dialog, And Output Commands

- `NVDA+Control+Alt+W`: describes where you are in SPSS, the pane, tab, table or dialog, and the likely available action.
- `NVDA+Control+Alt+Shift+T`: reads a table summary with rows, columns, and the current cell.
- `NVDA+Control+Alt+Shift+A`: toggles automatic cell announcements while moving through tables.
- `NVDA+Control+Alt+Shift+U`: summarizes visible Output Viewer outline items.
- `NVDA+Control+Alt+Shift+Y`: reads the current output table row and column.
- `NVDA+Control+Alt+Shift+C`: copies a short readable output summary to the clipboard when available.

### Chart Builder Support

`NVDA+Control+Alt+C` moves to or describes Chart Builder. The add-on labels common Chart Builder regions and controls:

- Variables list and Categories list.
- Chart preview canvas and drop zones.
- Gallery, Basic Elements, Groups or Point ID, and Titles or Footnotes tabs.
- Choose-from chart type list.
- Element Properties and common OK, Paste, Reset, Cancel, and Help controls.

Keyboard workflow: select a chart type in Gallery, copy a variable from the variables list, move to a canvas drop zone, paste it, and use Shift+F10 on the canvas for chart-building commands.

### Menus And Submenus

`NVDA+Control+Alt+Shift+M` gives a context-aware menu summary based on the current SPSS pane, then reads a top-level summary of File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions, Run, Tools, Insert, Format, Pivot, Window, and Help. While you move inside menus, the add-on announces the current menu path and the purpose of the focused menu item — including deep submenu items such as Analyze, Compare Means and Proportions, Independent-Samples T Test, or Analyze, Nonparametric Tests, Legacy Dialogs, Chi-square. `NVDA+Control+Alt+Shift+N` reads the current menu path plus its description on demand. `NVDA+Control+Alt+Shift+Q` lists every item in the menu or submenu that is currently open, so you can hear the whole set of choices before picking one.

### Statistical Procedure Dialogs

The add-on recognizes the Base-edition statistical dialogs by their fields and buttons — for example, seeing "Test Variable(s)", "Grouping Variable", and "Define Groups" together identifies the Independent-Samples T Test dialog — and explains what each field, list, checkbox, and sub-dialog button does:

- T Tests: One-Sample, Independent-Samples (with Define Groups, Options, Bootstrap), and Paired-Samples.
- One-Way ANOVA (with Contrasts and Post Hoc sub-dialogs).
- Frequencies, Descriptives, and Explore (with their Statistics, Charts, Plots, Format, and Options sub-dialogs).
- Crosstabs (with Statistics and Cells sub-dialogs).
- Bivariate Correlations, Linear Regression, Binary Logistic Regression.
- Reliability Analysis, and the modern and legacy Nonparametric Tests dialogs.
- Data-preparation dialogs: Value Labels, Missing Values, Variable Type, Select Cases, Split File, Weight Cases, Compute Variable, Recode into Different Variables, and Bootstrap.

`NVDA+Control+Alt+Shift+I` gives an overview of whichever dialog is focused. `NVDA+Control+Alt+Shift+K` goes further: it reads **every field and button currently visible in the dialog**, each with its kind (text box, list, button that opens a sub-dialog, and so on) and a short description — useful for getting the whole picture of a dialog with many options, such as a t-test's main fields plus its Define Groups, Options, and Bootstrap buttons, before tabbing through it one control at a time. `NVDA+Control+Alt+Shift+L` summarizes the source and target variable lists in the current dialog.

The add-on also supplies fallback labels for common unlabeled or icon-only SPSS controls: OK, Cancel, Apply, Continue, Reset, Paste, Run, Value Labels, Missing Values, Variable Type, Add, Change, Remove, Read Excel File, Text Import Wizard, Database Wizard, and Data View/Variable View/Overview/Output Viewer/Syntax Editor/Chart Builder tab and region names.

### Greek And English SPSS Glossary

`NVDA+Control+Alt+Shift+F` reads a bilingual glossary of common statistics terms and procedures — mean, median, standard deviation, confidence interval, significance level, t test, chi-square, correlation coefficient, R squared, regression coefficient, odds ratio, effect size, Cronbach's alpha, Levene's test, ANOVA, and more — each spoken in both English and Greek so the terminology carries over regardless of which language you work in day to day.

### Troubleshooting Support

`NVDA+Control+Alt+Shift+G` writes the current SPSS accessibility object to the NVDA log. The report includes role, name, value, description, help text, UI Automation id, class name, row and column metadata, headers, states, detected pane, and ancestors. This is useful when reporting unlabeled controls or version-specific SPSS behavior.

## Keyboard Shortcuts

### Navigation

- `NVDA+Control+Alt+O`: move to or describe the Output Viewer.
- `NVDA+Control+Alt+D`: move to Data View.
- `NVDA+Control+Alt+U`: move to Overview.
- `NVDA+Control+Alt+V`: move to Variable View.
- `NVDA+Control+Alt+M`: move to the SPSS menu bar or describe the menus.
- `NVDA+Control+Alt+S`: move to the Syntax Editor.
- `NVDA+Control+Alt+C`: move to or describe Chart Builder.
- `NVDA+Control+Alt+W`: where am I in SPSS and what is available.
- `NVDA+Control+Alt+T`: read the current tab and table context.

### Reading And Descriptions

- `NVDA+Control+Alt+Shift+O`: read current output item.
- `NVDA+Control+Alt+Shift+D`: read current Data View cell.
- `NVDA+Control+Alt+Shift+V`: read current Variable View definition cell.
- `NVDA+Control+Alt+Shift+N`: read the current menu path.
- `NVDA+Control+Alt+Shift+Q`: list the items in the current menu or submenu.
- `NVDA+Control+Alt+Shift+I`: describe the current SPSS dialog.
- `NVDA+Control+Alt+Shift+K`: read every field and button in the current SPSS dialog.
- `NVDA+Control+Alt+Shift+L`: summarize dialog variable lists.
- `NVDA+Control+Alt+Shift+T`: summarize the current table.
- `NVDA+Control+Alt+Shift+R`: read all available properties for the current variable.
- `NVDA+Control+Alt+Shift+U`: summarize the Output Viewer outline.
- `NVDA+Control+Alt+Shift+Y`: read the current output table row and column.
- `NVDA+Control+Alt+Shift+C`: copy a readable output summary to the clipboard.
- `NVDA+Control+Alt+Shift+X`: copy the current output table row.
- `NVDA+Control+Alt+Shift+F`: read the Greek and English SPSS glossary.
- `NVDA+Control+Alt+Shift+P`: describe the current SPSS pane.
- `NVDA+Control+Alt+Shift+M`: describe SPSS menus.
- `NVDA+Control+Alt+Shift+E`: describe output accessibility and export options.
- `NVDA+Control+Alt+Shift+J`: cycle the spoken language for SPSS content (automatic, English, Greek).
- `NVDA+Control+Alt+Shift+B`: toggle beginner or concise SPSS guidance.
- `NVDA+Control+Alt+Shift+A`: toggle automatic table cell announcements.
- `NVDA+Control+Alt+Shift+G`: log the current SPSS accessibility object.
- `NVDA+Control+Alt+Shift+H`: list add-on shortcuts.

## Output Accessibility Workflow

For pivot tables, open `Edit > Options > Output > Screen Reader Accessibility` and choose whether SPSS reads full row and column labels for each cell or only labels that change.

For charts, tree diagrams, and model views, SPSS often does not expose readable text. Use one of these paths:

- Prefer the source pivot table or text output when it contains the same information.
- Export output with `File > Export` to Word, PDF, Excel, HTML, text, or an image format.
- Use SPSS syntax and OMS to capture results as data or text when you need repeatable accessible output.

## Installation

### Install From The NVDA Add-on Store

This is the recommended method when the add-on is available in the NVDA Add-on Store. With this method, NVDA downloads the add-on from the store and checks its integrity.

1. Open NVDA on a Windows computer.
2. Open the NVDA menu with `NVDA+N`.
3. Choose `Tools`.
4. Choose `Add-on Store`.
5. Search for `SPSS Accessibility Plugin`.
6. Select the add-on and install it from the store.
7. Restart NVDA when prompted.
8. Open IBM SPSS Statistics and verify that the add-on shortcuts work.


## Notes And Limitations

SPSS does not expose every part of its interface consistently across versions. This add-on improves the experience where UI Automation information is available, but some charts, legacy dialogs, model viewers, and custom extension windows may still need SPSS keyboard commands, object navigation, export, or syntax-based workflows.

If a pane is not detected, bring the relevant SPSS window forward from the Window menu, then try the add-on command again. If a control is not labeled correctly, use the troubleshooting command and include the NVDA log report when filing an issue.

### SPSS Version Compatibility

The add-on is designed to work with **IBM SPSS Statistics 24 through 31**. This range is covered from IBM's version-specific documentation and offline simulated UI Automation tests; it is not yet a claim of hands-on testing on every release.

| SPSS versions | Documentation-based coverage |
| --- | --- |
| 24–26 | The classic `Analyze > Compare Means` path, Data View and Variable View without an Overview tab, and the stable Independent-Samples T Test controls are covered. |
| 27–30 | The same stable controls are covered, with effect-size controls introduced in version 27 treated as optional additions. |
| 31 | Both `Compare Means` and the newer `Compare Means and Proportions` label are recognized; the optional Homogeneity of variance control is also covered. |

The add-on registers `stats.exe`, the main process name used by this version range, and also retains the older `spss.exe` and `spsswin.exe` aliases. Dialog recognition deliberately relies on stable controls such as `Grouping Variable` and `Define Groups`; it does not require newer optional controls to exist. The compatibility comparison is grounded in IBM's [SPSS Statistics 24 Base guide](https://public.dhe.ibm.com/software/analytics/spss/documentation/statistics/24.0/en/client/Manuals/IBM_SPSS_Statistics_Base.pdf), [SPSS Statistics 24 accessibility guide](https://public.dhe.ibm.com/software/analytics/spss/documentation/statistics/24.0/en/client/InstallationDocuments/Windows/Accessibility.pdf), [SPSS Statistics 27 Base guide](https://public.dhe.ibm.com/software/analytics/spss/documentation/statistics/27.0/en/client/Manuals/IBM_SPSS_Statistics_Base.pdf), and IBM's [SPSS Statistics 31 release documentation](https://www.ibm.com/docs/en/spss-statistics/31.0.0?topic=SSLVMB_31.0.0%2Fstatistics_mainhelp_ddita%2Fspss%2Fbase%2Fwhatsnew_30.html).

## Testing

Version 1.2.0 is a substantial rewrite: it adds the bilingual `_spssdata` knowledge base, spoken-language detection, the SPSS Accessibility settings panel, and several new commands. It has an automated offline test suite (`tests/`, runnable with `python3 -m unittest discover -s tests`) that exercises pane detection, menu and dialog recognition, foreground modal-dialog roots, genuinely Greek dialog labels, language persistence while dialogs hide the menu bar, settings-panel persistence, executable registration and cleanup, bilingual output, the new commands, and documented SPSS 24–31 UI variants against a simulated SPSS UI Automation tree. It also passes the full packaging validation in `scripts/validate.sh`. **Version 1.2.0 has not yet been exercised against a real NVDA and IBM SPSS Statistics installation.** Earlier versions (up to 1.1.2) were tested with NVDA 2026.1.1 (64-bit) and IBM SPSS Statistics 31.0.0.0 (build 117) on Windows 11; that real-system testing needs to be repeated for 1.2.0 before it should be treated as verified on real hardware. The author is sighted, so even real-system testing verifies the add-on's announcements and commands rather than complete blind-user workflows. Feedback from screen reader users is very welcome through GitHub issues or email.

## AI Assistance Disclosure

This add-on was developed with substantial AI assistance (Anthropic's Claude), including the app module code, the `_spssdata` knowledge base, the automated test suite, and this documentation. SPSS content in the knowledge base (menu, dialog, and glossary descriptions) was grounded in IBM's own SPSS Statistics 24–31 Core System, Base, accessibility, and release documentation rather than generated from unverified assumptions, but it has not been cross-checked field-by-field against a running SPSS installation. The design goals, SPSS-specific priorities, and feature decisions were directed by the author, who maintains and takes responsibility for the code. Real-system testing on NVDA 2026.1.1 (64-bit), IBM SPSS Statistics 31.0.0.0 (build 117), and Windows 11 was completed for versions through 1.1.2; see the Testing section above for the current status of 1.2.0.

## License

GNU General Public License v2.0.
