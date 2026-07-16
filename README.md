# SPSS Accessibility Plugin

**Author:** Bouronikos Christos  
**Email:** chrisbouronikos@gmail.com  
**Donation:** If this add-on helps you, please consider a kind donation via PayPal: https://paypal.me/christosbouronikos

## Overview

SPSS Accessibility Plugin improves access to [IBM SPSS Statistics](https://www.ibm.com/products/spss-statistics) for blind and visually impaired users. Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com. It focuses on SPSS areas that are often difficult with a screen reader:

- SPSS menus and context-aware descriptions of what each menu contains.
- Data Editor views: Overview, Data View, and Variable View.
- Output Viewer outline, output document area, pivot tables, and output limitations.
- Chart Builder dialog regions, including variables, gallery, canvas, and drop zones.
- Syntax Editor, Paste workflow, Run menu, and common syntax-window areas.
- Excel-like table reading with tab, row, column, headers, cell reference, and value.
- Optional automatic table-cell announcements and value-label reading when SPSS exposes both a coded value and a label.
- Common SPSS dialog controls such as Value Labels, Missing Values, Variable Type, Select Cases, Split File, Weight Cases, import wizards, and analysis dialogs.
- A detailed menu map for File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions/Add-ons, Run, Insert, Format, Window, and Help.

The add-on uses SPSS UI Automation information when SPSS exposes it. Because SPSS versions differ, it also uses fallback heuristics based on object names, roles, class names, automation ids, table headers, and surrounding panes.

## What Is The NVDA Key?

The NVDA key is the modifier used for NVDA commands. By default it is usually Insert, Numpad Insert, or Caps Lock if enabled in NVDA settings.

For example, `NVDA+Control+Alt+D` means hold the NVDA key, Control, and Alt, then press D.

## Main Features

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

### Menus And Dialog Labels

`NVDA+Control+Alt+Shift+M` gives a context-aware menu summary based on the current SPSS pane, then reads a detailed menu map. The map covers key commands and submenus in File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions/Add-ons, Run, Insert, Format, Window, and Help. While you move inside menus, the add-on also tries to announce the current menu path and purpose of the focused menu item.

The add-on also supplies fallback labels for common unlabeled or icon-only SPSS controls, including:

- OK, Cancel, Apply, Continue, Reset, Paste, Run.
- Value Labels, Missing Values, Variable Type, Spelling, Add, Change, Remove.
- Read Excel File, Text Import Wizard, Database Wizard.
- Select Cases, Split File, Weight Cases, Define Variable Properties, Copy Data Properties.
- Frequencies, Descriptives, Crosstabs, Compare Means, Correlations, Regression.
- Data View, Variable View, Overview, Output Viewer, Syntax Editor, and Chart Builder controls.

`NVDA+Control+Alt+Shift+N` reads the current menu path plus a description when the item is in the menu map. `NVDA+Control+Alt+Shift+I` gives help for the current SPSS dialog, and `NVDA+Control+Alt+Shift+L` summarizes dialog variable lists.

### Greek And English SPSS Glossary

`NVDA+Control+Alt+Shift+F` reads a short Greek and English glossary for common procedures and terms, including Frequencies, Descriptives, Crosstabs, Regression, Correlations, Compare Means, Explore, Nonparametric Tests, Value Labels, and Missing Values.

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
- `NVDA+Control+Alt+Shift+I`: describe the current SPSS dialog.
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

## Testing

Version 1.1.2 carries no functional add-on changes over 1.1.1, which was tested with NVDA 2026.1.1 (64-bit) and IBM SPSS Statistics 31.0.0.0 (build 117) on Windows 11. The author is sighted, so testing verifies the add-on's announcements and commands rather than complete blind-user workflows. Feedback from screen reader users is very welcome through GitHub issues or email.

## AI Assistance Disclosure

This add-on was developed with substantial AI assistance (Anthropic's Claude), including much of the app module code and the documentation. The design goals, SPSS-specific behavior, feature decisions, and all testing on a real setup (NVDA 2026.1.1 64-bit, IBM SPSS Statistics 31.0.0.0 build 117, Windows 11) were done by the author, who maintains and takes responsibility for the code.

## License

GNU General Public License v2.0.
