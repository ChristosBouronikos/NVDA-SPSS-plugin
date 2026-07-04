# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin App Module for NVDA
# Version: 1.1.0
# =============================================================================
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# Donation: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Bouronikos Christos
# This file is covered by the GNU General Public License v2.
# =============================================================================

"""
SPSS Accessibility Plugin app module for NVDA.

Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com.
If this add-on helps you, please consider a kind donation via PayPal:
https://paypal.me/christosbouronikos

This module improves day-to-day use of IBM SPSS Statistics with NVDA by adding:
- Pane recognition for Output Viewer, Data Editor views, syntax, Chart Builder, and menus.
- Detailed descriptions when entering important SPSS work areas.
- Commands for reading output items, data cells, and variable definitions.
- Better fallback labels for unlabeled toolbar and dialog controls.

SPSS exposes different UI Automation names across versions, so most detection is
deliberately heuristic and combines object role, name, description, class name,
automation id, table coordinates, and surrounding ancestors.
"""

import re

import addonHandler
import api
import appModuleHandler
import controlTypes
import ui
from logHandler import log
from scriptHandler import script


addonHandler.initTranslation()

MAX_OBJECTS_TO_SCAN = 900
MAX_CHILDREN_PER_OBJECT = 120


def _role(name):
	try:
		return getattr(controlTypes.Role, name)
	except AttributeError:
		return None


def _state(name):
	try:
		return getattr(controlTypes.State, name)
	except AttributeError:
		return None


ROLE_BUTTON = _role("BUTTON")
ROLE_MENUITEM = _role("MENUITEM")
ROLE_MENUBAR = _role("MENUBAR")
ROLE_MENU = _role("MENU")
ROLE_TAB = _role("TAB")
ROLE_TABCONTROL = _role("TABCONTROL")
ROLE_TABLE = _role("TABLE")
ROLE_ROW = _role("ROW")
ROLE_CELL = _role("CELL")
ROLE_COLUMNHEADER = _role("COLUMNHEADER")
ROLE_ROWHEADER = _role("ROWHEADER")
ROLE_DOCUMENT = _role("DOCUMENT")
ROLE_PANE = _role("PANE")
ROLE_TREEVIEW = _role("TREEVIEW")
ROLE_TREEVIEWITEM = _role("TREEVIEWITEM")
ROLE_LIST = _role("LIST")
ROLE_LISTITEM = _role("LISTITEM")
ROLE_EDITABLETEXT = _role("EDITABLETEXT")
ROLE_STATICTEXT = _role("STATICTEXT")
ROLE_CHECKBOX = _role("CHECKBOX")
ROLE_RADIOBUTTON = _role("RADIOBUTTON")
ROLE_COMBOBOX = _role("COMBOBOX")
ROLE_GROUPING = _role("GROUPING")
ROLE_DIALOG = _role("DIALOG")
ROLE_WINDOW = _role("WINDOW")

STATE_SELECTED = _state("SELECTED")
STATE_FOCUSED = _state("FOCUSED")
STATE_EXPANDED = _state("EXPANDED")
STATE_COLLAPSED = _state("COLLAPSED")

TABLE_ROLES = tuple(
	role for role in (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_COLUMNHEADER, ROLE_ROWHEADER)
	if role is not None
)

TEXT_ROLES = tuple(
	role for role in (ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_STATICTEXT, ROLE_CELL, ROLE_LISTITEM, ROLE_TREEVIEWITEM)
	if role is not None
)


PANE_DEFINITIONS = {
	"overview": {
		"name": _("Overview"),
		"tokens": (
			"overview", "over view", "data overview", "variable overview",
			"data set overview", "dataset overview", "update", "quality",
			"επισκόπηση", "σύνοψη", "γενική προβολή", "ενημέρωση",
		),
		"roles": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL, ROLE_PANE),
	},
	"output": {
		"name": _("Output Viewer"),
		"tokens": (
			"output viewer", "output", "viewer", "outline", "pivot table",
			"pivot", "log", "notes", "chart", "model viewer", "export output",
			"προβολή αποτελεσμάτων", "αποτελέσματα", "έξοδος", "προβολή",
			"περίγραμμα", "πίνακας pivot", "γράφημα", "σημειώσεις",
		),
		"roles": (ROLE_DOCUMENT, ROLE_TREEVIEW, ROLE_TREEVIEWITEM, ROLE_PANE, ROLE_TABLE),
	},
	"data": {
		"name": _("Data View"),
		"tokens": (
			"data view", "data editor", "data grid", "case", "case number",
			"cases", "cell editor", "data set", "active dataset",
			"προβολή δεδομένων", "δεδομένα", "επεξεργαστής δεδομένων",
			"πλέγμα δεδομένων", "περίπτωση", "περιπτώσεις", "σύνολο δεδομένων",
		),
		"roles": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL),
	},
	"variable": {
		"name": _("Variable View"),
		"tokens": (
			"variable view", "variables", "variable", "name type width",
			"decimals label values missing columns align measure role",
			"measure", "values", "missing", "variable properties",
			"προβολή μεταβλητών", "μεταβλητές", "μεταβλητή", "όνομα τύπος πλάτος",
			"δεκαδικά ετικέτα τιμές ελλείπουσες στήλες στοίχιση μέτρο ρόλος",
			"ιδιότητες μεταβλητής",
		),
		"roles": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL),
	},
	"syntax": {
		"name": _("Syntax Editor"),
		"tokens": (
			"syntax editor", "syntax", "command syntax", "spss syntax",
			"run selection", "paste syntax", "designated syntax", "syntax window",
			"gutter", "bookmarks", "breakpoints", "command spans", "error pane",
			"επεξεργαστής σύνταξης", "σύνταξη", "εντολές", "εκτέλεση επιλογής",
			"επικόλληση σύνταξης", "παράθυρο σύνταξης", "σελιδοδείκτες",
		),
		"roles": (ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_PANE),
	},
	"chartbuilder": {
		"name": _("Chart Builder"),
		"tokens": (
			"chart builder", "chart preview", "gallery", "basic elements",
			"groups/point id", "groups point id", "titles/footnotes",
			"titles footnotes", "choose from", "drop zone", "drop zones",
			"canvas", "axis set", "graphic elements", "categories list",
			"element properties", "chart type", "pie/polar", "scatter/dot",
			"histogram", "boxplot", "dual axes",
			"δημιουργός γραφημάτων", "προεπισκόπηση γραφήματος", "καμβάς",
			"συλλογή", "βασικά στοιχεία", "ζώνη απόθεσης",
		),
		"roles": (ROLE_PANE, ROLE_LIST, ROLE_LISTITEM, ROLE_TAB, ROLE_TABCONTROL, ROLE_BUTTON, ROLE_GROUPING),
	},
	"menus": {
		"name": _("SPSS menu bar"),
		"tokens": (
			"menu bar", "file edit view data transform analyze graphs utilities",
			"extensions window help", "insert format run add-ons", "analyze",
			"transform", "graphs", "add-ons",
			"γραμμή μενού", "αρχείο επεξεργασία προβολή δεδομένα μετασχηματισμός ανάλυση γραφήματα",
			"βοήθεια", "ανάλυση", "μετασχηματισμός", "γραφήματα", "πρόσθετα",
		),
		"roles": (ROLE_MENUBAR, ROLE_MENU, ROLE_MENUITEM),
	},
}

PANE_ORDER = ("output", "overview", "data", "variable", "syntax", "chartbuilder", "menus")

PANE_HELP = {
	"overview": _(
		"Overview. This Data Editor view summarizes the active dataset. It can help "
		"you check variable and data quality before moving to Data View or Variable "
		"View. Use the Update control when SPSS asks for a refreshed representation "
		"of the data."
	),
	"output": _(
		"Output Viewer. The left outline lists result blocks such as logs, notes, "
		"tables, charts, and statistical procedures. The right document area contains "
		"the selected output. Pivot tables and text output are usually readable with "
		"NVDA; charts, tree diagrams, and model views are usually not screen-reader "
		"accessible in SPSS. Use the outline to move between results, then use the "
		"read output command for a concise summary. For pivot tables, check Edit, "
		"Options, Output, Screen Reader Accessibility."
	),
	"data": _(
		"Data View. Rows are cases and columns are variables. Use arrow keys to move "
		"cell by cell, or type a value into the current cell editor. The data-cell "
		"command reports the case number, variable name, and current value when SPSS "
		"exposes that information."
	),
	"variable": _(
		"Variable View. Each row defines one variable. Columns describe properties "
		"such as name, type, width, decimals, label, values, missing values, measure, "
		"and role. Use the variable command to report the current property and value. "
		"Press Space on Type, Values, or Missing to open the detailed edit dialog "
		"when SPSS exposes that action."
	),
	"syntax": _(
		"Syntax Editor. This is the command text area. You can review, edit, and run "
		"SPSS syntax. Dialog Paste buttons often place commands here before execution. "
		"The Syntax Editor also has a command navigation pane, gutter, and error pane "
		"when those areas are visible."
	),
	"chartbuilder": _(
		"Chart Builder. The dialog contains a variables list, optional categories "
		"list, chart canvas with drop zones, and tabs such as Gallery, Basic Elements, "
		"Groups or Point ID, and Titles or Footnotes. Select a chart type from the "
		"Gallery, copy a variable from the variables list, move to a drop zone, and "
		"paste it. Use Shift+F10 on the canvas for chart-building commands."
	),
	"menus": _(
		"SPSS menus. File manages files and import or export. Data changes cases and "
		"datasets. Transform computes and recodes variables. Analyze runs statistics. "
		"Graphs creates charts. Insert and Format affect output objects. Utilities, "
		"Extensions, and Add-ons manage metadata, integration commands, and add-ons."
	),
}

PANE_BRIEF = {
	"overview": _("Overview."),
	"output": _("Output Viewer. Use the outline for results. Pivot tables and text are readable; charts and model views may need export."),
	"data": _("Data View. Rows are cases, columns are variables."),
	"variable": _("Variable View. Rows are variables, columns are properties."),
	"syntax": _("Syntax Editor. Review, edit, paste, and run SPSS commands."),
	"chartbuilder": _("Chart Builder. Use the variables list, gallery, canvas drop zones, and Shift+F10 canvas menu."),
	"menus": _("SPSS menu bar."),
}

MENU_DESCRIPTIONS = (
	_("File: new, open, save, import data, export output, print, and manage SPSS data, syntax, and output files."),
	_("Edit: undo, copy, paste, find, replace, and open Options, including Output screen-reader accessibility settings."),
	_("View: show or hide toolbars, status information, value labels, line numbers, command spans, and visible panels."),
	_("Data: define variable properties, copy data properties, sort cases, select cases, split files, weight cases, merge files, and restructure datasets."),
	_("Transform: compute variables, recode values into same or different variables, automatic recode, count values, rank cases, and prepare derived fields."),
	_("Analyze: run Frequencies, Descriptives, Explore, Crosstabs, Compare Means, Correlations, Regression, nonparametric tests, and models."),
	_("Graphs: open Chart Builder, Graphboard, legacy dialogs, and graph editing commands."),
	_("Insert: add titles, text, page breaks, charts, tables, or other output objects when the active window supports them."),
	_("Format: change table looks, fonts, alignment, chart formatting, and output object appearance when available."),
	_("Utilities: inspect variables, file information, variable sets, dictionaries, and extension or custom-dialog utilities."),
	_("Extensions and Add-ons: run extension commands, Extension Hub, Python or R integrations, and custom procedures when installed."),
	_("Run: run all syntax, selected syntax, current command, or commands up to the cursor in Syntax Editor windows."),
	_("Window: move between open Data Editor, Output Viewer, Workbook, Syntax Editor, and dialog windows."),
	_("Help: open SPSS help, tutorials, command syntax reference, accessibility topics, and product information."),
)

MENU_CONTEXT_DESCRIPTIONS = {
	"overview": _(
		"Data Editor menus. Use Data for Define Variable Properties, Copy Data Properties, Sort Cases, Select Cases, Split File, and Weight Cases. Use Transform to compute or recode variables. Use Analyze to run procedures."
	),
	"data": _(
		"Data View menus. Data controls cases and datasets; Transform prepares new or recoded variables; Analyze runs procedures on the active dataset; Graphs opens Chart Builder and legacy chart dialogs."
	),
	"variable": _(
		"Variable View menus. Data includes Define Variable Properties and Copy Data Properties. Use Utilities, Variables for a readable variable information dialog with labels, missing values, measure, and value labels."
	),
	"output": _(
		"Output Viewer menus. Use the outline to select results. File exports output. Edit, Options, Output contains screen-reader accessibility for pivot-table labels. Insert and Format affect output objects. Charts and model views may need export because SPSS does not expose them as readable text."
	),
	"syntax": _(
		"Syntax Editor menus. Run executes all syntax, selected syntax, the current command, or commands to the cursor. View can show line numbers and command spans. Paste from dialogs sends syntax to the designated Syntax window."
	),
	"chartbuilder": _(
		"Chart Builder menus and dialog controls. Use Gallery or Basic Elements to choose the chart structure, copy variables from the variables list, paste them into canvas drop zones, and use Shift+F10 for canvas commands. OK and Paste are disabled until required drop zones are filled."
	),
	"menus": _("SPSS menu bar. Use left and right arrows between menus, down arrow to open a menu, and Enter to activate a command."),
}

SPSS_MENU_MAP = {
	"File": (
		("New", "Create a new Data, Syntax, Output, or Script window."),
		("Open", "Open SPSS data, syntax, output, script, or other supported files."),
		("Open Database", "Start the Database Wizard and import data from an ODBC database source."),
		("Read Text Data", "Start the Text Import Wizard for delimited or fixed-width text files."),
		("Close", "Close the active SPSS window."),
		("Save", "Save the active data, syntax, output, or workbook file."),
		("Save As", "Save the active file with a new name, location, or format."),
		("Save All Data", "Save all open datasets."),
		("Export", "Export output or data to formats such as Word, PDF, Excel, HTML, text, or image formats."),
		("Mark File Read Only", "Protect the active data file from accidental changes."),
		("Rename Dataset", "Rename the active dataset so it is easier to identify in syntax and dialogs."),
		("Display Data File Information", "Show dictionary information such as variables, labels, missing values, and value labels."),
		("Cache Data", "Cache the active dataset for faster access in some workflows."),
		("Print Preview", "Preview printed output before printing."),
		("Print", "Print the active output, data, syntax, or selected object."),
		("Recently Used Data", "Open a recently used data file."),
		("Recently Used Files", "Open a recently used SPSS file."),
		("Exit", "Exit IBM SPSS Statistics."),
	),
	"Edit": (
		("Undo", "Undo the last edit when available."),
		("Redo", "Redo the last undone edit when available."),
		("Cut", "Cut the selected text, cells, cases, variables, or output object."),
		("Copy", "Copy the selected text, cells, cases, variables, or output object."),
		("Paste", "Paste clipboard content into the active editor or dialog target."),
		("Paste Variables", "Paste copied variable definitions into Variable View."),
		("Clear", "Delete the selected content or clear selected output objects."),
		("Insert Variable", "Insert a new variable in Variable View or Data View."),
		("Insert Cases", "Insert new cases in Data View."),
		("Find", "Find text, values, variable names, or output content."),
		("Find Next", "Move to the next match."),
		("Replace", "Find and replace text or values where supported."),
		("Go to Case", "Move to a case number in Data View."),
		("Go to Variable", "Move to a variable by name or position."),
		("Options", "Open SPSS options. For output tables, check Output and Screen Reader Accessibility."),
	),
	"View": (
		("Status Bar", "Show or hide status information."),
		("Toolbars", "Show, hide, or customize SPSS toolbars."),
		("Fonts", "Change display fonts where supported."),
		("Grid Lines", "Show or hide grid lines in data and table views."),
		("Value Labels", "Toggle between raw coded values and human-readable value labels."),
		("Variables", "Open variable information when available."),
		("Data View", "Switch the Data Editor to case-by-variable data cells."),
		("Variable View", "Switch the Data Editor to variable definitions and properties."),
		("Overview", "Switch to the Data Editor overview when available."),
		("Customize Variable View", "Choose which Variable View properties are visible."),
	),
	"Data": (
		("Define Variable Properties", "Review and define labels, value labels, missing values, and measurement properties."),
		("Copy Data Properties", "Copy dictionary properties from one dataset or variable set to another."),
		("New Custom Attribute", "Create custom metadata attributes for variables."),
		("Define Dates", "Describe date/time structure for time series data."),
		("Define Multiple Response Sets", "Define sets of variables that represent multiple-response survey questions."),
		("Validation", "Check data rules, invalid values, and suspicious cases."),
		("Identify Duplicate Cases", "Find duplicate case identifiers."),
		("Identify Unusual Cases", "Find cases with unusual patterns or outliers."),
		("Sort Cases", "Sort rows by one or more variables."),
		("Sort Variables", "Sort variables by name, type, or dictionary properties."),
		("Transpose", "Turn cases into variables or variables into cases."),
		("Restructure", "Reshape data between wide and long formats."),
		("Merge Files", "Add cases or add variables from another dataset."),
		("Add Cases", "Append rows from another dataset."),
		("Add Variables", "Join columns from another dataset."),
		("Aggregate", "Create grouped summaries such as means, counts, or sums."),
		("Orthogonal Design", "Create or display orthogonal designs for conjoint workflows."),
		("Copy Dataset", "Create a copy of the active dataset."),
		("Split File", "Run output separately by group variables."),
		("Select Cases", "Filter, sample, or restrict cases used by analyses."),
		("Weight Cases", "Use a frequency or weight variable in analyses."),
	),
	"Transform": (
		("Compute Variable", "Create or replace a variable using a numeric or string expression."),
		("Count Values within Cases", "Count how many selected variables contain specified values for each case."),
		("Shift Values", "Shift values between cases for time or sequence workflows."),
		("Recode into Same Variables", "Replace values in existing variables."),
		("Recode into Different Variables", "Create new recoded variables while preserving the originals."),
		("Automatic Recode", "Convert string or numeric categories into consecutive numeric codes."),
		("Visual Binning", "Create categorical bins from scale variables using an interactive dialog."),
		("Optimal Binning", "Create supervised bins based on a guide variable."),
		("Rank Cases", "Create rank, percentile, normal score, or similar ranking variables."),
		("Date and Time Wizard", "Create or transform date and time variables."),
		("Create Time Series", "Create lag, lead, difference, moving average, or related time series variables."),
		("Replace Missing Values", "Create variables with missing values replaced by selected methods."),
		("Random Number Generators", "Set random generator settings and seeds."),
		("Run Pending Transformations", "Force pending transformations to execute immediately."),
	),
	"Analyze": (
		("Reports", "Create case summaries, report summaries, and OLAP cubes."),
		("Descriptive Statistics", "Open Frequencies, Descriptives, Explore, Crosstabs, Ratio, P-P Plots, and Q-Q Plots."),
		("Frequencies", "Count values and percentages, usually for categorical or discrete variables."),
		("Descriptives", "Report mean, standard deviation, minimum, maximum, and standardized values."),
		("Explore", "Inspect distributions, outliers, confidence intervals, and group summaries."),
		("Crosstabs", "Create contingency tables with counts, percentages, chi-square, and association measures."),
		("Compare Means", "Run Means, one-sample, independent-samples, paired-samples, and one-way ANOVA procedures."),
		("Means", "Compare descriptive statistics across groups."),
		("One-Sample T Test", "Compare a sample mean to a test value."),
		("Independent-Samples T Test", "Compare means between two independent groups."),
		("Paired-Samples T Test", "Compare paired measurements within cases."),
		("One-Way ANOVA", "Compare means across more than two groups."),
		("General Linear Model", "Run univariate, multivariate, repeated-measures, and variance components models."),
		("Mixed Models", "Run linear or generalized mixed models."),
		("Correlate", "Run bivariate correlations, partial correlations, and distance measures."),
		("Bivariate", "Compute Pearson, Spearman, or Kendall correlations."),
		("Partial", "Compute correlations while controlling for other variables."),
		("Regression", "Run linear, curve estimation, logistic, probit, nonlinear, and related regression procedures."),
		("Linear", "Run linear regression with one scale dependent variable."),
		("Binary Logistic", "Run logistic regression for a binary outcome."),
		("Multinomial Logistic", "Run logistic regression for a nominal outcome with more than two categories."),
		("Ordinal", "Run regression for an ordered categorical outcome."),
		("Curve Estimation", "Fit curve models across one predictor."),
		("Classify", "Run clustering, discriminant, nearest neighbor, decision tree, or related classification procedures."),
		("Data Reduction", "Run factor analysis, correspondence analysis, or related dimension-reduction procedures."),
		("Scale", "Run reliability analysis and multidimensional scaling procedures."),
		("Reliability Analysis", "Estimate scale reliability such as Cronbach's alpha."),
		("Nonparametric Tests", "Run tests that do not require normal distribution assumptions."),
		("Forecasting", "Run time series modeling and forecasting procedures."),
		("Survival", "Run life tables, Kaplan-Meier, and Cox regression procedures."),
		("Multiple Response", "Analyze multiple-response sets."),
		("Missing Value Analysis", "Analyze patterns of missing values."),
		("Multiple Imputation", "Impute missing values and pool analysis results."),
		("Complex Samples", "Analyze data from complex survey designs."),
		("ROC Curve", "Evaluate diagnostic or classification performance."),
		("Power Analysis", "Estimate sample size or statistical power."),
	),
	"Graphs": (
		("Chart Builder", "Create charts using gallery types, variables, and canvas drop zones."),
		("Graphboard Template Chooser", "Create graphs from Graphboard templates."),
		("Legacy Dialogs", "Open older chart dialogs such as Bar, Line, Area, Pie, Boxplot, Error Bar, Scatter, and Histogram."),
		("Bar", "Create bar charts."),
		("3-D Bar", "Create three-dimensional bar charts."),
		("Line", "Create line charts."),
		("Area", "Create area charts."),
		("Pie", "Create pie charts."),
		("High-Low", "Create high-low-close style charts."),
		("Boxplot", "Create boxplots for distributions and outliers."),
		("Error Bar", "Create charts with confidence intervals or standard errors."),
		("Population Pyramid", "Create back-to-back histograms for population structures."),
		("Scatter/Dot", "Create scatterplots or dot plots."),
		("Histogram", "Create histograms."),
	),
	"Utilities": (
		("Variables", "Show variable dictionary information in a readable dialog."),
		("File Information", "Show file and dictionary information for the active dataset."),
		("Define Variable Sets", "Create named sets of variables for easier dialogs and navigation."),
		("Use Variable Sets", "Limit visible variables to selected variable sets."),
		("Run Script", "Run an SPSS script."),
		("Custom Dialogs", "Create, install, or manage custom dialogs."),
		("Extension Bundles", "Install or manage extension bundles."),
		("OMS Control Panel", "Control Output Management System routing when available."),
	),
	"Extensions": (
		("Extension Hub", "Find, install, or manage SPSS extensions."),
		("Extension Dialog Builder", "Build custom extension dialogs."),
		("Python", "Run or manage Python-based extension commands when installed."),
		("R", "Run or manage R-based extension commands when installed."),
	),
	"Add-ons": (
		("Extension Hub", "Find, install, or manage SPSS extensions and add-ons."),
		("Custom Dialogs", "Install or manage custom dialogs."),
	),
	"Run": (
		("All", "Run all syntax in the active Syntax Editor."),
		("Selection", "Run selected syntax."),
		("Current", "Run the command containing the cursor."),
		("To End", "Run from the cursor to the end of the syntax file."),
		("To Cursor", "Run commands up to the cursor."),
	),
	"Insert": (
		("New Heading", "Insert a heading in the Output Viewer outline."),
		("Title", "Insert an output title."),
		("Text", "Insert a text block in output."),
		("Page Break", "Insert a page break in output."),
		("Chart", "Insert or create a chart object where supported."),
		("Table", "Insert or create a table object where supported."),
	),
	"Format": (
		("TableLooks", "Apply or edit table appearance for pivot tables."),
		("Cell Properties", "Change selected pivot table cell formatting."),
		("Font", "Change font formatting where supported."),
		("Alignment", "Change alignment for selected output objects or table cells."),
		("Pivot Table", "Open formatting commands for selected pivot tables."),
	),
	"Window": (
		("Minimize", "Minimize the active SPSS window."),
		("Split", "Arrange or split visible windows when supported."),
		("Data Editor", "Switch to an open Data Editor window."),
		("Output Viewer", "Switch to an open Output Viewer window."),
		("Syntax Editor", "Switch to an open Syntax Editor window."),
		("Workbook", "Switch to an open Workbook window."),
	),
	"Help": (
		("Topics", "Open SPSS help topics."),
		("Tutorial", "Open SPSS tutorials."),
		("Case Studies", "Open statistical case studies."),
		("Command Syntax Reference", "Open syntax command reference documentation."),
		("Accessibility", "Open accessibility help when available."),
		("Check for Updates", "Check for product updates."),
		("About", "Show product version and license information."),
	),
}

MENU_ALIASES = {
	"new data": "New",
	"new syntax": "New",
	"new output": "New",
	"read text data": "Read Text Data",
	"database wizard": "Open Database",
	"save as": "Save As",
	"display data file information": "Display Data File Information",
	"insert variable": "Insert Variable",
	"insert cases": "Insert Cases",
	"go to case": "Go to Case",
	"go to variable": "Go to Variable",
	"value labels": "Value Labels",
	"define variable properties": "Define Variable Properties",
	"copy data properties": "Copy Data Properties",
	"define multiple response sets": "Define Multiple Response Sets",
	"identify duplicate cases": "Identify Duplicate Cases",
	"identify unusual cases": "Identify Unusual Cases",
	"sort cases": "Sort Cases",
	"sort variables": "Sort Variables",
	"merge files": "Merge Files",
	"add cases": "Add Cases",
	"add variables": "Add Variables",
	"split file": "Split File",
	"select cases": "Select Cases",
	"weight cases": "Weight Cases",
	"compute variable": "Compute Variable",
	"recode into same variables": "Recode into Same Variables",
	"recode into different variables": "Recode into Different Variables",
	"automatic recode": "Automatic Recode",
	"visual binning": "Visual Binning",
	"rank cases": "Rank Cases",
	"replace missing values": "Replace Missing Values",
	"chart builder": "Chart Builder",
	"graphboard template chooser": "Graphboard Template Chooser",
	"legacy dialogs": "Legacy Dialogs",
	"extension hub": "Extension Hub",
	"command syntax reference": "Command Syntax Reference",
}

VARIABLE_COLUMNS = (
	"Name", "Type", "Width", "Decimals", "Label", "Values", "Missing",
	"Columns", "Align", "Measure", "Role",
)

VARIABLE_COLUMN_TOKENS = {
	"Name": ("name", "όνομα"),
	"Type": ("type", "τύπος"),
	"Width": ("width", "πλάτος"),
	"Decimals": ("decimals", "δεκαδικά"),
	"Label": ("label", "ετικέτα"),
	"Values": ("values", "τιμές"),
	"Missing": ("missing", "ελλείπουσες", "ελλείπουσες τιμές"),
	"Columns": ("columns", "στήλες"),
	"Align": ("align", "στοίχιση"),
	"Measure": ("measure", "μέτρο"),
	"Role": ("role", "ρόλος"),
}

VARIABLE_COLUMN_LABELS = {
	"Name": _("Name"),
	"Type": _("Type"),
	"Width": _("Width"),
	"Decimals": _("Decimals"),
	"Label": _("Label"),
	"Values": _("Values"),
	"Missing": _("Missing"),
	"Columns": _("Columns"),
	"Align": _("Align"),
	"Measure": _("Measure"),
	"Role": _("Role"),
}

VARIABLE_PROPERTY_HINTS = {
	"Type": _("Press Space to open the Variable Type dialog."),
	"Values": _("Press Space to edit value labels for this variable."),
	"Missing": _("Press Space to define missing values for this variable."),
	"Measure": _("Use this property to mark the variable as nominal, ordinal, or scale."),
	"Role": _("Use this property to mark how the variable is used in procedures, such as input or target."),
}

CONTROL_LABELS = {
	"ok": _("OK"),
	"cancel": _("Cancel"),
	"apply": _("Apply"),
	"close": _("Close"),
	"continue": _("Continue"),
	"reset": _("Reset"),
	"paste": _("Paste syntax"),
	"paste syntax": _("Paste syntax"),
	"run": _("Run command"),
	"run selection": _("Run selection"),
	"run current": _("Run current command"),
	"open": _("Open"),
	"save": _("Save"),
	"print": _("Print"),
	"browse": _("Browse"),
	"options": _("Options"),
	"spelling": _("Spelling"),
	"statistics": _("Statistics"),
	"charts": _("Charts"),
	"plots": _("Plots"),
	"posthoc": _("Post Hoc"),
	"post hoc": _("Post Hoc"),
	"contrasts": _("Contrasts"),
	"bootstrap": _("Bootstrap"),
	"exact": _("Exact tests"),
	"style": _("Style"),
	"format": _("Format"),
	"overview": _("Overview"),
	"over view": _("Overview"),
	"data view": _("Data View"),
	"προβολή δεδομένων": _("Data View"),
	"variable view": _("Variable View"),
	"προβολή μεταβλητών": _("Variable View"),
	"output": _("Output Viewer"),
	"αποτελέσματα": _("Output Viewer"),
	"syntax": _("Syntax Editor"),
	"σύνταξη": _("Syntax Editor"),
	"chart builder": _("Chart Builder"),
	"gallery": _("Gallery"),
	"basic elements": _("Basic Elements"),
	"groups/point id": _("Groups or Point ID"),
	"groups point id": _("Groups or Point ID"),
	"titles/footnotes": _("Titles or Footnotes"),
	"titles footnotes": _("Titles or Footnotes"),
	"choose from": _("Choose from chart types"),
	"chart preview": _("Chart preview canvas"),
	"canvas": _("Chart canvas"),
	"drop zone": _("Drop zone"),
	"drop zones": _("Drop zones"),
	"element properties": _("Element Properties"),
	"categories": _("Categories"),
	"source variable list": _("Source variable list"),
	"variables list": _("Variables list"),
	"variables": _("Variables"),
	"variable type": _("Variable Type"),
	"variable": _("Variable"),
	"dependent": _("Dependent variable"),
	"independent": _("Independent variable"),
	"covariates": _("Covariates"),
	"factor": _("Factor"),
	"value labels": _("Value labels"),
	"missing values": _("Missing Values"),
	"discrete missing values": _("Discrete missing values"),
	"no missing values": _("No missing values"),
	"range plus one optional discrete missing value": _("Range plus one optional discrete missing value"),
	"label": _("Label"),
	"labels": _("Labels"),
	"add": _("Add"),
	"change": _("Change"),
	"remove": _("Remove"),
	"read excel": _("Read Excel File"),
	"text import wizard": _("Text Import Wizard"),
	"database wizard": _("Database Wizard"),
	"select cases": _("Select Cases"),
	"split file": _("Split File"),
	"weight cases": _("Weight Cases"),
	"define variable properties": _("Define Variable Properties"),
	"copy data properties": _("Copy Data Properties"),
	"frequencies": _("Frequencies"),
	"descriptives": _("Descriptives"),
	"crosstabs": _("Crosstabs"),
	"compare means": _("Compare Means"),
	"correlations": _("Correlations"),
	"regression": _("Regression"),
	"extension hub": _("Extension Hub"),
}

DIALOG_HELP = {
	"frequencies": _(
		"Frequencies dialog. Choose one or more source variables, move them to the Variables target list, then use Statistics, Charts, Format, OK, or Paste. Use Paste when you want reproducible syntax."
	),
	"descriptives": _(
		"Descriptives dialog. Choose scale variables, move them to the Variables target list, then use Options for mean, standard deviation, minimum, maximum, and related statistics."
	),
	"crosstabs": _(
		"Crosstabs dialog. Move categorical variables to Row and Column target lists. Use Statistics for chi-square and measures, Cells for counts and percentages, then OK or Paste."
	),
	"regression": _(
		"Regression dialog. Move the outcome to Dependent and predictors to Independent variables. Use Statistics, Plots, Save, Options, OK, or Paste."
	),
	"linear regression": _(
		"Linear Regression dialog. Move the outcome to Dependent and predictors to Independent variables. Use Statistics, Plots, Save, Options, OK, or Paste."
	),
	"explore": _(
		"Explore dialog. Move scale variables to Dependent List and grouping variables to Factor List. Use Statistics, Plots, Options, OK, or Paste."
	),
	"nonparametric": _(
		"Nonparametric Tests dialog. Choose test fields and settings, then review model or test options before OK or Paste."
	),
	"custom tables": _(
		"Custom Tables dialog. Use source variables and the canvas row, column, and layer areas. Copy variables from the source list and paste them into the canvas or use Shift+F10 for context commands."
	),
	"compute variable": _(
		"Compute Variable dialog. Enter the target variable, build a numeric expression from variables and functions, then choose OK or Paste."
	),
	"recode into same variables": _(
		"Recode into Same Variables dialog. Select variables, define old and new values, and consider Paste so the transformation is documented."
	),
	"recode into different variables": _(
		"Recode into Different Variables dialog. Select input variables, define output variable names and labels, set old and new values, then OK or Paste."
	),
	"select cases": _(
		"Select Cases dialog. Choose whether all cases, cases satisfying a condition, a random sample, a time range, or filtered cases are used. Review the output option before OK or Paste."
	),
	"split file": _(
		"Split File dialog. Choose whether output is analyzed together or by groups, then move grouping variables into the Groups Based on list."
	),
	"weight cases": _(
		"Weight Cases dialog. Choose Do not weight cases or Weight cases by, then move a numeric frequency or weight variable to the Frequency Variable field."
	),
	"value labels": _(
		"Value Labels dialog. Enter a data value and its label, choose Add, Change, or Remove, then OK. This is used for categorical code labels such as 0 equals No and 1 equals Yes."
	),
	"missing values": _(
		"Missing Values dialog. Choose no missing values, discrete missing values, or a range plus one optional discrete value, then enter the missing-value definitions."
	),
	"variable type": _(
		"Variable Type dialog. Choose Numeric, Comma, Dot, Scientific notation, Date, Dollar, Custom Currency, or String. Review width and decimals when available."
	),
	"read excel": _(
		"Read Excel File dialog. Confirm the worksheet, variable-name row, cell range, and import settings before OK."
	),
	"text import wizard": _(
		"Text Import Wizard. Move through the wizard steps to define delimiters or fixed widths, variable names, data formats, and import range."
	),
	"database wizard": _(
		"Database Wizard. Choose the data source, select tables and fields, define joins or filters, and review variable definitions before import."
	),
	"chart builder": PANE_HELP["chartbuilder"],
}

STATISTICS_GLOSSARY = (
	_("Frequencies: Συχνότητες. Counts values and percentages for categorical or discrete variables."),
	_("Descriptives: Περιγραφικά στατιστικά. Reports mean, standard deviation, minimum, maximum, and similar summaries."),
	_("Crosstabs: Πίνακες συνάφειας. Compares categories of two or more variables in a contingency table."),
	_("Regression: Παλινδρόμηση. Models an outcome variable from one or more predictors."),
	_("Correlations: Συσχετίσεις. Measures association between variables."),
	_("Compare Means: Σύγκριση μέσων. Compares averages across groups."),
	_("Explore: Διερεύνηση. Reviews distributions, outliers, and group summaries."),
	_("Nonparametric Tests: Μη παραμετρικοί έλεγχοι. Runs tests that do not assume normal distributions."),
	_("Value Labels: Ετικέτες τιμών. Human-readable labels for coded values."),
	_("Missing Values: Ελλείπουσες τιμές. User-defined values that SPSS treats as missing."),
)


def _safe_get(obj, attr, default=None):
	try:
		return getattr(obj, attr)
	except Exception:
		return default


def _safe_str(value):
	if value is None:
		return ""
	try:
		return str(value)
	except Exception:
		return ""


def _clean(value):
	value = _safe_str(value)
	value = re.sub(r"\s+", " ", value).strip()
	return value


def _norm(value):
	return _clean(value).lower()


def _contains_token(text, token):
	token = _norm(token)
	if not token:
		return False
	if " " in token or "/" in token:
		return token in text
	if len(token) <= 4:
		return re.search(r"(?<!\w)%s(?!\w)" % re.escape(token), text) is not None
	return token in text


def _join_unique(parts, limit=12):
	seen = set()
	output = []
	for part in parts:
		part = _clean(part)
		if not part:
			continue
		key = part.lower()
		if key in seen:
			continue
		seen.add(key)
		output.append(part)
		if len(output) >= limit:
			break
	return ". ".join(output)


def _role_name(obj):
	role = _safe_get(obj, "role")
	if role is None:
		return ""
	try:
		return role.displayString
	except Exception:
		return _safe_str(role)


class AppModule(appModuleHandler.AppModule):
	"""NVDA app module for IBM SPSS Statistics."""

	scriptCategory = _("IBM SPSS Statistics")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lastPane = None
		self._verboseHelp = True
		self._announceTableMovement = False
		self._headerCache = {}
		log.info("IBM SPSS Statistics accessibility app module 1.1.0 loaded")

	def terminate(self):
		log.info("IBM SPSS Statistics accessibility app module unloaded")
		super().terminate()

	def event_NVDAObject_init(self, obj):
		"""Give unlabeled SPSS controls useful fallback names where possible."""
		try:
			if _safe_get(obj, "name"):
				return
			label = self._labelForControl(obj)
			if label:
				obj.name = label
				return
			if _safe_get(obj, "role") in TABLE_ROLES:
				cellName = self._shortCellName(obj)
				if cellName:
					obj.name = cellName
		except Exception as e:
			log.debugWarning("SPSS object labeling failed: %s" % e)

	def event_gainFocus(self, obj, nextHandler):
		nextHandler()
		try:
			if _safe_get(obj, "role") in (ROLE_MENUITEM, ROLE_MENU):
				menuMessage = self._focusedMenuItemDescription(obj)
				if menuMessage:
					ui.message(menuMessage)
					return
			if _safe_get(obj, "role") == ROLE_TAB:
				tabMessage = self._describeTab(obj)
				if tabMessage:
					ui.message(tabMessage)
					return
			pane = self._detectPaneFromObject(obj)
			if self._announceTableMovement and _safe_get(obj, "role") in TABLE_ROLES:
				cellMessage = self._describeCell(obj, preferPane=pane)
				if cellMessage:
					ui.message(cellMessage)
					return
			if pane and pane != self._lastPane:
				self._lastPane = pane
				ui.message(self._paneHelp(pane))
		except Exception as e:
			log.debugWarning("SPSS focus announcement failed: %s" % e)

	@script(
		description=_("Move to the SPSS Output Viewer or describe how to use it"),
		gesture="kb:NVDA+control+alt+o",
	)
	def script_goToOutputViewer(self, gesture):
		self._navigateToPane("output")

	@script(
		description=_("Move to SPSS Data View"),
		gesture="kb:NVDA+control+alt+d",
	)
	def script_goToDataView(self, gesture):
		self._activateView("data")

	@script(
		description=_("Move to SPSS Overview"),
		gesture="kb:NVDA+control+alt+u",
	)
	def script_goToOverview(self, gesture):
		self._activateView("overview")

	@script(
		description=_("Move to SPSS Variable View"),
		gesture="kb:NVDA+control+alt+v",
	)
	def script_goToVariableView(self, gesture):
		self._activateView("variable")

	@script(
		description=_("Move to the SPSS menu bar"),
		gesture="kb:NVDA+control+alt+m",
	)
	def script_goToMenus(self, gesture):
		if not self._navigateToPane("menus", silent=True):
			ui.message(self._paneHelp("menus"))

	@script(
		description=_("Move to the SPSS Syntax Editor"),
		gesture="kb:NVDA+control+alt+s",
	)
	def script_goToSyntaxEditor(self, gesture):
		self._navigateToPane("syntax")

	@script(
		description=_("Move to or describe SPSS Chart Builder"),
		gesture="kb:NVDA+control+alt+c",
	)
	def script_goToChartBuilder(self, gesture):
		if not self._navigateToPane("chartbuilder", silent=True):
			ui.message(self._paneHelp("chartbuilder"))
			return
		ui.message(self._paneHelp("chartbuilder"))

	@script(
		description=_("Describe the current SPSS pane"),
		gesture="kb:NVDA+control+alt+shift+p",
	)
	def script_describeCurrentPane(self, gesture):
		pane = self._detectPaneFromObject(api.getFocusObject()) or self._lastPane
		if pane:
			ui.message(self._paneHelp(pane))
		else:
			ui.message(_("Current SPSS pane could not be identified. Use Tab, Shift+Tab, or the SPSS Window menu to move between open windows."))

	@script(
		description=_("Describe SPSS menus and what each menu contains"),
		gesture="kb:NVDA+control+alt+shift+m",
	)
	def script_describeMenus(self, gesture):
		pane = self._detectPaneFromObject(api.getFocusObject()) or self._lastPane
		context = MENU_CONTEXT_DESCRIPTIONS.get(pane)
		message = " ".join(part for part in (context, self._fullMenuMapDescription()) if part)
		ui.message(message)

	@script(
		description=_("Describe SPSS output accessibility and export options"),
		gesture="kb:NVDA+control+alt+shift+e",
	)
	def script_describeOutputAccessibility(self, gesture):
		ui.message(
			_(
				"SPSS output accessibility. Pivot tables and text output are usually readable. "
				"Charts, tree diagrams, and model views are usually not screen-reader accessible. "
				"For pivot tables, choose Edit, Options, Output, then Screen Reader Accessibility "
				"to control whether full row and column labels are read. For inaccessible charts "
				"or models, export output with File, Export to Word, PDF, Excel, HTML, text, or "
				"an image format, or use syntax and OMS to capture results as data or text."
			)
		)

	@script(
		description=_("Describe where you are in SPSS and what is available"),
		gesture="kb:NVDA+control+alt+w",
	)
	def script_whereAmI(self, gesture):
		ui.message(self._whereAmI() or _("No SPSS context is available at the current focus."))

	@script(
		description=_("Read the current SPSS menu path"),
		gesture="kb:NVDA+control+alt+shift+n",
	)
	def script_readMenuPath(self, gesture):
		ui.message(self._focusedMenuItemDescription(api.getFocusObject()) or _("No SPSS menu path is available at the current focus."))

	@script(
		description=_("Describe the current SPSS dialog"),
		gesture="kb:NVDA+control+alt+shift+i",
	)
	def script_describeCurrentDialog(self, gesture):
		ui.message(self._dialogHelp(api.getFocusObject()) or _("No SPSS dialog help is available at the current focus."))

	@script(
		description=_("Summarize SPSS dialog variable lists"),
		gesture="kb:NVDA+control+alt+shift+l",
	)
	def script_summarizeDialogLists(self, gesture):
		ui.message(self._dialogListSummary(api.getFocusObject()) or _("No source or target variable lists were found in the current SPSS dialog."))

	@script(
		description=_("Read the current SPSS table summary"),
		gesture="kb:NVDA+control+alt+shift+t",
	)
	def script_readTableSummary(self, gesture):
		ui.message(self._tableSummary(api.getFocusObject()) or _("No SPSS table summary is available at the current focus."))

	@script(
		description=_("Read all available properties for the current SPSS variable"),
		gesture="kb:NVDA+control+alt+shift+r",
	)
	def script_readVariableRowSummary(self, gesture):
		ui.message(self._variableRowSummary(api.getFocusObject()) or _("No SPSS variable row summary is available at the current focus."))

	@script(
		description=_("Summarize the SPSS Output Viewer outline"),
		gesture="kb:NVDA+control+alt+shift+u",
	)
	def script_summarizeOutputOutline(self, gesture):
		ui.message(self._outputOutlineSummary() or _("No SPSS output outline was found."))

	@script(
		description=_("Read current SPSS output table row and column"),
		gesture="kb:NVDA+control+alt+shift+y",
	)
	def script_readOutputTableRowAndColumn(self, gesture):
		ui.message(self._outputRowColumnSummary(api.getFocusObject()) or _("No SPSS output table row or column summary is available at the current focus."))

	@script(
		description=_("Copy a readable SPSS output summary to the clipboard"),
		gesture="kb:NVDA+control+alt+shift+c",
	)
	def script_copyReadableOutputSummary(self, gesture):
		summary = self._readOutputContext() or self._outputOutlineSummary()
		if not summary:
			ui.message(_("No readable SPSS output summary is available to copy."))
			return
		if self._copyToClipboard(summary):
			ui.message(_("Copied readable SPSS output summary to the clipboard."))
		else:
			log.info("SPSS readable output summary:\n%s" % summary)
			ui.message(_("Clipboard copy is unavailable. The readable SPSS output summary was written to the NVDA log."))

	@script(
		description=_("Copy the current SPSS output table row to the clipboard"),
		gesture="kb:NVDA+control+alt+shift+x",
	)
	def script_copyOutputTableRow(self, gesture):
		rowText = self._outputTableRowText(api.getFocusObject())
		if not rowText:
			ui.message(_("No SPSS output table row is available to copy."))
			return
		if self._copyToClipboard(rowText):
			ui.message(_("Copied current SPSS output table row to the clipboard."))
		else:
			log.info("SPSS output table row:\n%s" % rowText)
			ui.message(_("Clipboard copy is unavailable. The current SPSS output table row was written to the NVDA log."))

	@script(
		description=_("Read Greek and English SPSS statistics glossary"),
		gesture="kb:NVDA+control+alt+shift+f",
	)
	def script_readStatisticsGlossary(self, gesture):
		ui.message(" ".join(STATISTICS_GLOSSARY))

	@script(
		description=_("Read the current SPSS tab and table context"),
		gesture="kb:NVDA+control+alt+t",
	)
	def script_readCurrentTabAndTable(self, gesture):
		obj = api.getFocusObject()
		message = self._describeTabAndTableContext(obj)
		ui.message(message or _("No SPSS tab or table context is available at the current focus."))

	@script(
		description=_("Read the current SPSS output item or selected output block"),
		gesture="kb:NVDA+control+alt+shift+o",
	)
	def script_readOutputItem(self, gesture):
		message = self._readOutputContext()
		ui.message(message or _("No readable SPSS output item was found at the current focus. Try moving to the Output Viewer outline or document area first."))

	@script(
		description=_("Read the current SPSS Data View cell with row, variable, and value"),
		gesture="kb:NVDA+control+alt+shift+d",
	)
	def script_readDataCell(self, gesture):
		obj = api.getFocusObject()
		message = self._describeCell(obj, preferPane="data")
		ui.message(message or _("No SPSS data cell information is available at the current focus."))

	@script(
		description=_("Read the current SPSS Variable View definition cell"),
		gesture="kb:NVDA+control+alt+shift+v",
	)
	def script_readVariableDefinition(self, gesture):
		obj = api.getFocusObject()
		message = self._describeCell(obj, preferPane="variable")
		if not message:
			message = self._describeVariableContext(obj)
		ui.message(message or _("No SPSS variable definition information is available at the current focus."))

	@script(
		description=_("List SPSS accessibility add-on shortcuts"),
		gesture="kb:NVDA+control+alt+shift+h",
	)
	def script_listShortcuts(self, gesture):
		shortcuts = (
			_("NVDA+Control+Alt+O: Output Viewer."),
			_("NVDA+Control+Alt+D: Data View."),
			_("NVDA+Control+Alt+U: Overview."),
			_("NVDA+Control+Alt+V: Variable View."),
			_("NVDA+Control+Alt+M: Menu bar."),
			_("NVDA+Control+Alt+S: Syntax Editor."),
			_("NVDA+Control+Alt+C: Chart Builder."),
			_("NVDA+Control+Alt+W: where am I in SPSS."),
			_("NVDA+Control+Alt+T: read current tab and table context."),
			_("NVDA+Control+Alt+Shift+O: read current output item."),
			_("NVDA+Control+Alt+Shift+D: read current data cell."),
			_("NVDA+Control+Alt+Shift+V: read current variable definition."),
			_("NVDA+Control+Alt+Shift+N: read current menu path."),
			_("NVDA+Control+Alt+Shift+I: describe current dialog."),
			_("NVDA+Control+Alt+Shift+L: summarize dialog variable lists."),
			_("NVDA+Control+Alt+Shift+T: read table summary."),
			_("NVDA+Control+Alt+Shift+R: read all properties for current variable."),
			_("NVDA+Control+Alt+Shift+U: summarize Output Viewer outline."),
			_("NVDA+Control+Alt+Shift+Y: read output table row and column."),
			_("NVDA+Control+Alt+Shift+C: copy readable output summary."),
			_("NVDA+Control+Alt+Shift+X: copy current output table row."),
			_("NVDA+Control+Alt+Shift+F: read Greek and English statistics glossary."),
			_("NVDA+Control+Alt+Shift+P: describe current pane."),
			_("NVDA+Control+Alt+Shift+M: describe SPSS menus."),
			_("NVDA+Control+Alt+Shift+E: describe output accessibility and export options."),
			_("NVDA+Control+Alt+Shift+B: toggle beginner or concise SPSS guidance."),
			_("NVDA+Control+Alt+Shift+A: toggle automatic table cell announcements."),
			_("NVDA+Control+Alt+Shift+G: log the current SPSS accessibility object for troubleshooting."),
			_("NVDA+Control+Alt+Shift+H: list these shortcuts."),
		)
		ui.message(" ".join(shortcuts))

	@script(
		description=_("Toggle beginner or concise SPSS guidance"),
		gesture="kb:NVDA+control+alt+shift+b",
	)
	def script_toggleGuidanceVerbosity(self, gesture):
		self._verboseHelp = not self._verboseHelp
		if self._verboseHelp:
			ui.message(_("SPSS guidance set to beginner detail."))
		else:
			ui.message(_("SPSS guidance set to concise announcements."))

	@script(
		description=_("Toggle automatic SPSS table cell announcements"),
		gesture="kb:NVDA+control+alt+shift+a",
	)
	def script_toggleAutomaticTableAnnouncements(self, gesture):
		self._announceTableMovement = not self._announceTableMovement
		if self._announceTableMovement:
			ui.message(_("Automatic SPSS table cell announcements on."))
		else:
			ui.message(_("Automatic SPSS table cell announcements off."))

	@script(
		description=_("Log the current SPSS accessibility object for troubleshooting"),
		gesture="kb:NVDA+control+alt+shift+g",
	)
	def script_logCurrentAccessibilityObject(self, gesture):
		obj = api.getFocusObject()
		report = self._debugObjectReport(obj)
		log.info("SPSS accessibility object report:\n%s" % report)
		ui.message(_("Current SPSS accessibility object was written to the NVDA log."))

	def _whereAmI(self):
		obj = api.getFocusObject()
		if not obj:
			return ""
		parts = []
		window = self._rootObject()
		windowName = _clean(_safe_get(window, "name"))
		if windowName:
			parts.append(_("Window {name}").format(name=windowName))
		pane = self._detectPaneFromObject(obj) or self._lastPane
		if pane:
			parts.append(_("Pane {pane}").format(pane=PANE_DEFINITIONS[pane]["name"]))
		tab = self._describeTab()
		if tab:
			parts.append(tab)
		menuPath = self._menuPathDescription(obj)
		if menuPath:
			parts.append(menuPath)
		dialogHelp = self._dialogHelp(obj, concise=True)
		if dialogHelp:
			parts.append(dialogHelp)
		table = self._describeTableContext(obj)
		if table:
			parts.append(table)
		outputKind = self._outputObjectKind(obj)
		if outputKind and pane == "output":
			parts.append(outputKind)
		action = self._availableActionHint(obj, pane)
		if action:
			parts.append(action)
		return _join_unique(parts, limit=10)

	def _availableActionHint(self, obj, pane=None):
		role = _safe_get(obj, "role")
		text = self._objectSearchText(obj)
		if role in (ROLE_BUTTON, ROLE_MENUITEM):
			return _("Press Enter or Space to activate.")
		if role in (ROLE_LIST, ROLE_LISTITEM):
			if pane == "chartbuilder":
				return _("Use arrow keys to move, Space to select, Control+C to copy a variable, and Shift+F10 for context commands.")
			return _("Use arrow keys to move and Space to select items.")
		if role in TABLE_ROLES:
			if pane == "variable":
				propertyKey = self._variablePropertyKey(
					self._headerText(obj, ("columnHeaderText", "columnHeaderTexts")),
					self._numericAttr(obj, ("columnNumber", "column")),
				)
				return VARIABLE_PROPERTY_HINTS.get(propertyKey, _("Use arrow keys to move in the table."))
			return _("Use arrow keys to move in the table.")
		if "drop zone" in text:
			return _("Paste a copied variable here with Control+V, or open context commands with Shift+F10.")
		return ""

	def _menuPathDescription(self, obj):
		items = []
		for candidate in self._ancestors(obj, maxDepth=12):
			if _safe_get(candidate, "role") in (ROLE_MENUITEM, ROLE_MENU, ROLE_MENUBAR):
				name = _clean(_safe_get(candidate, "name"))
				if name:
					items.append(name)
		items = list(reversed(items))
		if not items:
			return ""
		return _("Menu path: {path}").format(path=" > ".join(items))

	def _focusedMenuItemDescription(self, obj):
		path = self._menuPathItems(obj)
		if not path:
			return ""
		helpText = self._menuItemHelp(path)
		pathText = _("Menu path: {path}").format(path=" > ".join(path))
		if helpText:
			return _("{path}. {help}").format(path=pathText, help=helpText)
		return pathText

	def _menuPathItems(self, obj):
		items = []
		for candidate in self._ancestors(obj, maxDepth=12):
			if _safe_get(candidate, "role") in (ROLE_MENUITEM, ROLE_MENU, ROLE_MENUBAR):
				name = _clean(_safe_get(candidate, "name"))
				if name:
					items.append(name)
		return list(reversed(items))

	def _menuItemHelp(self, path):
		if not path:
			return ""
		menuName = self._canonicalMenuName(path[0])
		itemName = self._canonicalMenuItemName(path[-1])
		if not itemName:
			return ""
		candidates = []
		if menuName:
			candidates.extend((menuName,))
		candidates.extend(menu for menu in SPSS_MENU_MAP if menu not in candidates)
		for candidateMenu in candidates:
			for label, description in SPSS_MENU_MAP.get(candidateMenu, ()):
				if self._sameMenuItem(label, itemName):
					return _("{item}: {description}").format(item=label, description=description)
		return ""

	def _canonicalMenuName(self, value):
		text = _norm(value)
		for menuName in SPSS_MENU_MAP:
			if _norm(menuName) == text:
				return menuName
		for menuName in SPSS_MENU_MAP:
			if _norm(menuName) in text or text in _norm(menuName):
				return menuName
		return ""

	def _canonicalMenuItemName(self, value):
		text = _norm(value)
		text = re.sub(r"\s+", " ", text.replace("&", "")).strip()
		return MENU_ALIASES.get(text, value)

	def _sameMenuItem(self, left, right):
		leftNorm = _norm(left)
		rightNorm = _norm(right)
		if not leftNorm or not rightNorm:
			return False
		if leftNorm == rightNorm:
			return True
		if leftNorm in rightNorm or rightNorm in leftNorm:
			return True
		alias = MENU_ALIASES.get(rightNorm)
		return bool(alias and _norm(alias) == leftNorm)

	def _fullMenuMapDescription(self):
		parts = list(MENU_DESCRIPTIONS)
		for menuName, items in SPSS_MENU_MAP.items():
			itemTexts = [_("{item}, {description}").format(item=item, description=description) for item, description in items]
			parts.append(_("{menu} menu items: {items}").format(menu=menuName, items="; ".join(itemTexts)))
		return " ".join(parts)

	def _dialogHelp(self, obj, concise=False):
		dialog = self._dialogObject(obj)
		if not dialog:
			return ""
		name = _clean(_safe_get(dialog, "name")) or _("SPSS dialog")
		text = self._objectSearchText(dialog)
		for token, helpText in DIALOG_HELP.items():
			if token in text:
				if concise:
					return _("Dialog {name}.").format(name=name)
				return helpText
		if concise:
			return _("Dialog {name}.").format(name=name)
		return _(
			"SPSS dialog {name}. Use Tab and Shift+Tab to move between controls, arrow keys inside lists or option groups, Space to select, Enter for the default action, Escape to cancel, and Paste when you want syntax."
		).format(name=name)

	def _dialogObject(self, obj):
		for candidate in self._ancestors(obj, maxDepth=16):
			role = _safe_get(candidate, "role")
			text = self._objectSearchText(candidate)
			if role in (ROLE_DIALOG, ROLE_WINDOW) and ("spss" in text or any(token in text for token in DIALOG_HELP)):
				return candidate
			if role == ROLE_PANE and any(token in text for token in DIALOG_HELP):
				return candidate
		return None

	def _dialogListSummary(self, obj):
		dialog = self._dialogObject(obj) or self._rootObject()
		if not dialog:
			return ""
		lists = []
		for candidate in self._iterObjects(dialog, maxObjects=360):
			if _safe_get(candidate, "role") not in (ROLE_LIST, ROLE_TREEVIEW):
				continue
			summary = self._listSummary(candidate)
			if summary:
				lists.append(summary)
			if len(lists) >= 6:
				break
		if not lists:
			return ""
		return _("Dialog variable lists. {summary}").format(summary=". ".join(lists))

	def _listSummary(self, obj):
		name = _clean(_safe_get(obj, "name")) or self._nearbyHeaderText(obj)
		text = self._objectSearchText(obj)
		if not name:
			if "source" in text:
				name = _("Source variable list")
			elif "target" in text or "dependent" in text or "independent" in text:
				name = _("Target variable list")
			else:
				name = _("Variable list")
		items = []
		selected = []
		for child in self._iterObjects(obj, maxObjects=80):
			if child is obj or _safe_get(child, "role") not in (ROLE_LISTITEM, ROLE_TREEVIEWITEM):
				continue
			childName = _clean(_safe_get(child, "name")) or _clean(_safe_get(child, "value"))
			if not childName:
				continue
			items.append(childName)
			if self._isSelectedOrFocused(child):
				selected.append(childName)
			if len(items) >= 8:
				break
		if selected:
			return _("{name}. Selected {selected}. Visible items {items}.").format(
				name=name,
				selected=", ".join(selected[:4]),
				items=", ".join(items[:8]) or _("none"),
			)
		return _("{name}. Visible items {items}.").format(name=name, items=", ".join(items[:8]) or _("none"))

	def _tableSummary(self, obj):
		cell = self._nearestTableObject(obj)
		table = self._nearestRoleObject(obj, ROLE_TABLE) if ROLE_TABLE is not None else None
		if not table and cell:
			table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		target = table or cell
		if not target:
			return ""
		pane = self._detectPaneFromObject(obj) or self._guessPaneFromCell(cell) or self._lastPane
		name = self._tableName(target, pane)
		rowCount, columnCount = self._tableDimensions(target)
		current = self._describeCell(obj, preferPane=pane)
		parts = [name]
		if rowCount:
			if pane == "data":
				parts.append(_("Cases {count}").format(count=rowCount))
			else:
				parts.append(_("Rows {count}").format(count=rowCount))
		if columnCount:
			if pane in ("data", "variable"):
				parts.append(_("Variables or properties {count}").format(count=columnCount))
			else:
				parts.append(_("Columns {count}").format(count=columnCount))
		if current:
			parts.append(current)
		return ". ".join(parts)

	def _tableDimensions(self, table):
		rowCount = self._numericAttr(table, ("rowCount", "rowCountText", "rows"))
		columnCount = self._numericAttr(table, ("columnCount", "columnCountText", "columns"))
		if rowCount or columnCount:
			return rowCount, columnCount
		rows = set()
		columns = set()
		for child in self._iterObjects(table, maxObjects=420):
			if _safe_get(child, "role") not in TABLE_ROLES:
				continue
			row = self._numericAttr(child, ("rowNumber", "row"))
			column = self._numericAttr(child, ("columnNumber", "column"))
			if row:
				rows.add(row)
			if column:
				columns.add(column)
		return len(rows) or None, len(columns) or None

	def _variableRowSummary(self, obj):
		cell = self._nearestTableObject(obj)
		if not cell:
			return ""
		pane = self._detectPaneFromObject(cell) or self._guessPaneFromCell(cell)
		if pane != "variable":
			return ""
		table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		rowNumber = self._numericAttr(cell, ("rowNumber", "row"))
		if not table or not rowNumber:
			return self._describeVariableContext(cell)
		properties = {}
		for candidate in self._iterObjects(table, maxObjects=520):
			if _safe_get(candidate, "role") not in TABLE_ROLES:
				continue
			if self._numericAttr(candidate, ("rowNumber", "row")) != rowNumber:
				continue
			columnNumber = self._numericAttr(candidate, ("columnNumber", "column"))
			propertyName = (
				self._headerText(candidate, ("columnHeaderText", "columnHeaderTexts"))
				or self._cachedHeader(candidate, "column", columnNumber)
				or self._columnNameFromNumber(columnNumber)
			)
			value = self._cellValue(candidate)
			if propertyName and value:
				properties[propertyName] = value
		if not properties:
			return self._describeVariableContext(cell)
		ordered = []
		for column in VARIABLE_COLUMNS:
			label = VARIABLE_COLUMN_LABELS.get(column, column)
			for key, value in properties.items():
				if self._variablePropertyKey(key) == column:
					ordered.append(_("{property}: {value}").format(property=label, value=value))
					break
		if not ordered:
			ordered = [_("{property}: {value}").format(property=k, value=v) for k, v in properties.items()]
		variableName = properties.get("Name") or properties.get(VARIABLE_COLUMN_LABELS["Name"]) or _("current variable")
		return _("Variable summary for {variable}. {summary}").format(variable=variableName, summary=". ".join(ordered[:12]))

	def _outputOutlineSummary(self):
		pane = self._findBestPaneObject("output")
		if not pane:
			return ""
		items = []
		for obj in self._iterObjects(pane, maxObjects=420):
			if _safe_get(obj, "role") not in (ROLE_TREEVIEWITEM, ROLE_LISTITEM):
				continue
			name = _clean(_safe_get(obj, "name"))
			if not name:
				continue
			level = self._positionInfoValue(obj, "level") or _safe_get(obj, "level")
			state = self._expandedStateLabel(obj)
			label = name
			if level:
				label = _("Level {level} {name}").format(level=level, name=label)
			if state:
				label = _("{label}, {state}").format(label=label, state=state)
			items.append(label)
			if len(items) >= 18:
				break
		if not items:
			return ""
		return _("Output outline contains {count} visible items. {items}").format(count=len(items), items=". ".join(items))

	def _outputRowColumnSummary(self, obj):
		cell = self._nearestTableObject(obj)
		if not cell:
			return ""
		pane = self._detectPaneFromObject(cell) or self._guessPaneFromCell(cell) or self._lastPane
		if pane != "output":
			return ""
		table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		if not table:
			return self._describeCell(cell, preferPane="output")
		rowNumber = self._numericAttr(cell, ("rowNumber", "row"))
		columnNumber = self._numericAttr(cell, ("columnNumber", "column"))
		rowCount, columnCount = self._tableDimensions(table)
		rowCells = []
		columnCells = []
		for candidate in self._iterObjects(table, maxObjects=900):
			if candidate is cell or _safe_get(candidate, "role") not in TABLE_ROLES:
				continue
			value = self._cellValue(candidate)
			if not value:
				continue
			candidateRow = self._numericAttr(candidate, ("rowNumber", "row"))
			candidateColumn = self._numericAttr(candidate, ("columnNumber", "column"))
			if rowNumber and candidateRow == rowNumber:
				header = self._headerText(candidate, ("columnHeaderText", "columnHeaderTexts")) or self._cachedHeader(candidate, "column", candidateColumn) or self._columnNameFromNumber(candidateColumn)
				rowCells.append(_("{header}: {value}").format(header=header or _("Column {column}").format(column=candidateColumn), value=value))
			if columnNumber and candidateColumn == columnNumber:
				header = self._headerText(candidate, ("rowHeaderText", "rowHeaderTexts")) or self._cachedHeader(candidate, "row", candidateRow)
				columnCells.append(_("{header}: {value}").format(header=header or _("Row {row}").format(row=candidateRow), value=value))
			if len(rowCells) >= 14 and len(columnCells) >= 14:
				break
		current = self._describeCell(cell, preferPane="output")
		parts = [current] if current else []
		tableName = self._tableName(table, "output")
		if tableName:
			parts.insert(0, tableName)
		if rowCount or columnCount:
			dimensions = []
			if rowCount:
				dimensions.append(_("Rows {count}").format(count=rowCount))
			if columnCount:
				dimensions.append(_("Columns {count}").format(count=columnCount))
			parts.append(_("Table size: {dimensions}").format(dimensions=", ".join(dimensions)))
		if rowCells:
			parts.append(_("Current output row: {items}").format(items=". ".join(rowCells[:14])))
		if columnCells:
			parts.append(_("Current output column: {items}").format(items=". ".join(columnCells[:14])))
		return ". ".join(parts)

	def _outputTableRowText(self, obj):
		cell = self._nearestTableObject(obj)
		if not cell:
			return ""
		pane = self._detectPaneFromObject(cell) or self._guessPaneFromCell(cell) or self._lastPane
		if pane != "output":
			return ""
		table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		if not table:
			return ""
		rowNumber = self._numericAttr(cell, ("rowNumber", "row"))
		if not rowNumber:
			return ""
		rowItems = []
		for candidate in self._iterObjects(table, maxObjects=1200):
			if _safe_get(candidate, "role") not in TABLE_ROLES:
				continue
			if self._numericAttr(candidate, ("rowNumber", "row")) != rowNumber:
				continue
			value = self._cellValue(candidate)
			if not value:
				continue
			columnNumber = self._numericAttr(candidate, ("columnNumber", "column"))
			header = (
				self._headerText(candidate, ("columnHeaderText", "columnHeaderTexts"))
				or self._cachedHeader(candidate, "column", columnNumber)
				or self._columnNameFromNumber(columnNumber)
				or _("Column {column}").format(column=columnNumber)
			)
			rowItems.append((columnNumber or 0, header, value))
		if not rowItems:
			return ""
		rowItems.sort(key=lambda item: item[0])
		tableName = self._tableName(table, "output") or _("Output table")
		lines = [tableName, _("Row {row}").format(row=rowNumber)]
		lines.extend(_("{header}: {value}").format(header=header, value=value) for _column, header, value in rowItems)
		return "\n".join(lines)

	def _copyToClipboard(self, text):
		copyToClip = getattr(api, "copyToClip", None)
		if not callable(copyToClip):
			return False
		try:
			copyToClip(text)
			return True
		except Exception as e:
			log.debugWarning("Could not copy SPSS summary to clipboard: %s" % e)
			return False

	def _paneHelp(self, paneKey):
		if self._verboseHelp:
			return PANE_HELP[paneKey]
		return PANE_BRIEF.get(paneKey, PANE_HELP[paneKey])

	def _debugObjectReport(self, obj):
		if not obj:
			return "No focus object."
		lines = [_("Focus object")]
		lines.extend(self._debugObjectLines(obj, prefix=""))
		lines.append(_("Ancestors"))
		for index, ancestor in enumerate(self._ancestors(obj, maxDepth=8)):
			if index == 0:
				continue
			lines.append("  %s." % index)
			lines.extend(self._debugObjectLines(ancestor, prefix="    "))
		return "\n".join(lines)

	def _debugObjectLines(self, obj, prefix=""):
		attrs = (
			("role", _role_name(obj)),
			("name", _clean(_safe_get(obj, "name"))),
			("value", _clean(_safe_get(obj, "value"))),
			("description", _clean(_safe_get(obj, "description"))),
			("helpText", _clean(_safe_get(obj, "helpText"))),
			("valueLabel", _clean(_safe_get(obj, "valueLabel"))),
			("UIAAutomationId", _clean(_safe_get(obj, "UIAAutomationId"))),
			("windowClassName", _clean(_safe_get(obj, "windowClassName"))),
			("rowNumber", _safe_get(obj, "rowNumber")),
			("columnNumber", _safe_get(obj, "columnNumber")),
			("rowHeaderText", _clean(_safe_get(obj, "rowHeaderText"))),
			("columnHeaderText", _clean(_safe_get(obj, "columnHeaderText"))),
			("positionInfo", _safe_get(obj, "positionInfo")),
			("states", self._debugStates(obj)),
			("detectedPane", self._detectPaneFromObject(obj)),
		)
		return ["%s%s: %s" % (prefix, key, value) for key, value in attrs if value not in (None, "", set())]

	def _debugStates(self, obj):
		states = _safe_get(obj, "states", set()) or set()
		names = []
		try:
			for state in states:
				try:
					names.append(state.displayString)
				except Exception:
					names.append(_safe_str(state))
		except Exception:
			return ""
		return ", ".join(sorted(_clean(name) for name in names if _clean(name)))

	def _labelForControl(self, obj):
		role = _safe_get(obj, "role")
		if role not in (ROLE_BUTTON, ROLE_MENUITEM, ROLE_TAB, ROLE_LIST, ROLE_LISTITEM, ROLE_CHECKBOX, ROLE_RADIOBUTTON, ROLE_COMBOBOX):
			return None
		text = self._objectSearchText(obj)
		for token, label in CONTROL_LABELS.items():
			if _contains_token(text, token):
				return label
		description = _clean(_safe_get(obj, "description"))
		if description:
			return description
		helpText = _clean(_safe_get(obj, "helpText"))
		if helpText:
			return helpText
		return None

	def _navigateToPane(self, paneKey, silent=False):
		target = self._findBestPaneObject(paneKey)
		if not target:
			if not silent:
				ui.message(self._paneNotFoundMessage(paneKey))
			return False
		self._focusOrNavigate(target)
		self._lastPane = paneKey
		if not silent:
			ui.message(self._paneHelp(paneKey))
		return True

	def _activateView(self, paneKey):
		tab = self._findTabForView(paneKey)
		if tab:
			self._activateObject(tab)
			self._lastPane = paneKey
			ui.message(self._paneHelp(paneKey))
			return
		if self._navigateToPane(paneKey, silent=True):
			ui.message(self._paneHelp(paneKey))
			return
		ui.message(self._paneNotFoundMessage(paneKey))

	def _findTabForView(self, paneKey):
		wantedByPane = {
			"overview": ("overview", "over view"),
			"data": ("data view",),
			"variable": ("variable view",),
		}
		wantedTokens = wantedByPane.get(paneKey)
		if not wantedTokens:
			return None
		root = self._rootObject()
		if not root:
			return None
		best = None
		bestScore = 0
		for obj in self._iterObjects(root, maxObjects=MAX_OBJECTS_TO_SCAN):
			role = _safe_get(obj, "role")
			if role not in (ROLE_TAB, ROLE_TABCONTROL, ROLE_BUTTON, ROLE_MENUITEM):
				continue
			text = self._objectSearchText(obj)
			score = 0
			if any(token in text for token in wantedTokens):
				score += 80
			if paneKey == "data" and "data" in text and "view" in text:
				score += 25
			if paneKey == "variable" and "variable" in text and "view" in text:
				score += 25
			if paneKey == "overview" and ("overview" in text or ("over" in text and "view" in text)):
				score += 25
			if score > bestScore:
				bestScore = score
				best = obj
		return best if bestScore >= 25 else None

	def _findBestPaneObject(self, paneKey):
		root = self._rootObject()
		if not root:
			return None
		best = None
		bestScore = 0
		for obj in self._iterObjects(root, maxObjects=MAX_OBJECTS_TO_SCAN):
			score = self._scorePaneObject(obj, paneKey)
			if score > bestScore:
				bestScore = score
				best = obj
		return best if bestScore >= 20 else None

	def _detectPaneFromObject(self, obj):
		if not obj:
			return None
		bestPane = None
		bestScore = 0
		for candidate in self._ancestors(obj):
			for paneKey in PANE_ORDER:
				score = self._scorePaneObject(candidate, paneKey)
				if score > bestScore:
					bestScore = score
					bestPane = paneKey
		if bestScore >= 20:
			return bestPane
		return self._guessPaneFromCell(obj)

	def _scorePaneObject(self, obj, paneKey):
		definition = PANE_DEFINITIONS[paneKey]
		text = self._objectSearchText(obj)
		name = _norm(_safe_get(obj, "name"))
		role = _safe_get(obj, "role")
		score = 0
		if role in tuple(role for role in definition["roles"] if role is not None):
			score += 8
		for token in definition["tokens"]:
			token = token.lower()
			if not token:
				continue
			if name == token:
				score += 55
			elif token in name:
				score += 35
			elif token in text:
				score += 16
		if paneKey != "menus" and role in (ROLE_MENUBAR, ROLE_MENU, ROLE_MENUITEM):
			score = max(0, score - 35)
		if paneKey == "menus" and role in (ROLE_MENUBAR, ROLE_MENU):
			score += 45
		if paneKey == "menus" and role == ROLE_MENUITEM:
			score += 25
		if paneKey in ("overview", "data", "variable") and role in TABLE_ROLES:
			score += 8
		if paneKey == "variable" and self._looksLikeVariableView(obj):
			score += 35
		if paneKey == "data" and self._looksLikeDataView(obj):
			score += 20
		if paneKey == "overview" and self._looksLikeOverview(obj):
			score += 25
		if paneKey == "chartbuilder" and self._looksLikeChartBuilder(obj):
			score += 45
		return score

	def _looksLikeVariableView(self, obj):
		text = self._objectSearchText(obj)
		hits = 0
		for tokens in VARIABLE_COLUMN_TOKENS.values():
			if any(token.lower() in text for token in tokens):
				hits += 1
		if hits >= 3:
			return True
		columnHeader = _norm(_safe_get(obj, "columnHeaderText"))
		return self._isVariableColumnName(columnHeader)

	def _looksLikeDataView(self, obj):
		text = self._objectSearchText(obj)
		if "data view" in text or "data editor" in text:
			return True
		if _safe_get(obj, "role") not in TABLE_ROLES:
			return False
		columnHeader = _clean(_safe_get(obj, "columnHeaderText"))
		rowHeader = _clean(_safe_get(obj, "rowHeaderText"))
		if columnHeader and not self._isVariableColumnName(columnHeader):
			return True
		return bool(rowHeader)

	def _looksLikeOverview(self, obj):
		text = self._objectSearchText(obj)
		if "overview" in text or "over view" in text or "επισκόπηση" in text:
			return True
		return "data editor" in text and "update" in text

	def _looksLikeChartBuilder(self, obj):
		text = self._objectSearchText(obj)
		hits = 0
		for token in ("chart builder", "gallery", "basic elements", "canvas", "drop zone", "choose from", "chart preview"):
			if token in text:
				hits += 1
		return hits >= 2

	def _guessPaneFromCell(self, obj):
		for candidate in self._ancestors(obj):
			if _safe_get(candidate, "role") not in TABLE_ROLES:
				continue
			if self._looksLikeVariableView(candidate):
				return "variable"
			if self._looksLikeDataView(candidate):
				return "data"
		return None

	def _readOutputContext(self):
		focus = api.getFocusObject()
		pane = self._findContainingOrBestPane(focus, "output")
		candidates = []
		if focus:
			candidates.extend(self._outputObjectContextParts(focus))
			candidates.extend(self._selectedOrFocusedText(focus))
			candidates.extend(self._cellDetailsAsParts(focus, preferPane="output"))
		if pane and pane is not focus:
			for obj in self._iterObjects(pane, maxObjects=260):
				if self._isSelectedOrFocused(obj):
					candidates.extend(self._outputObjectContextParts(obj))
					candidates.extend(self._meaningfulTextParts(obj))
					candidates.extend(self._cellDetailsAsParts(obj, preferPane="output"))
				if len(candidates) >= 16:
					break
			if len(candidates) < 4:
				for obj in self._iterObjects(pane, maxObjects=120):
					if _safe_get(obj, "role") in TEXT_ROLES:
						candidates.extend(self._outputObjectContextParts(obj))
						candidates.extend(self._meaningfulTextParts(obj))
					if len(candidates) >= 12:
						break
		summary = _join_unique(candidates, limit=10)
		if summary:
			return _("Output Viewer. {summary}").format(summary=summary)
		if pane:
			return self._paneHelp("output")
		return None

	def _outputObjectContextParts(self, obj):
		parts = []
		kind = self._outputObjectKind(obj)
		if kind:
			parts.append(kind)
		if _safe_get(obj, "role") in (ROLE_TREEVIEWITEM, ROLE_LISTITEM):
			parts.append(_("Output outline item"))
			level = self._positionInfoValue(obj, "level") or _safe_get(obj, "level")
			index = self._positionInfoValue(obj, "indexInGroup")
			total = self._positionInfoValue(obj, "similarItemsInGroup")
			state = self._expandedStateLabel(obj)
			if level:
				parts.append(_("Outline level {level}").format(level=level))
			if index and total:
				parts.append(_("Item {index} of {total}").format(index=index, total=total))
			if state:
				parts.append(state)
		return parts

	def _outputObjectKind(self, obj):
		text = self._objectSearchText(obj)
		role = _safe_get(obj, "role")
		if role in TABLE_ROLES or "pivot table" in text or "pivot" in text:
			return _("Output item type: pivot table or table. This is usually readable with NVDA.")
		if "tree diagram" in text or "tree model" in text:
			return _("Output item type: tree diagram or tree model. SPSS usually does not expose this as screen-reader accessible text.")
		if "model viewer" in text or "model view" in text or "model" in text:
			return _("Output item type: model view. SPSS usually does not expose this as screen-reader accessible text.")
		if "chart" in text or "graph" in text:
			return _("Output item type: chart. SPSS usually does not expose charts as screen-reader accessible text; export the output or review the source table when possible.")
		if "log" in text:
			return _("Output item type: log.")
		if "notes" in text or "note" in text:
			return _("Output item type: notes.")
		if "warning" in text:
			return _("Output item type: warning.")
		if "title" in text:
			return _("Output item type: title.")
		if role in (ROLE_TREEVIEWITEM, ROLE_LISTITEM):
			return _("Output item type: outline entry.")
		if role == ROLE_DOCUMENT:
			return _("Output document area.")
		return ""

	def _expandedStateLabel(self, obj):
		states = _safe_get(obj, "states", set()) or set()
		try:
			if STATE_EXPANDED is not None and STATE_EXPANDED in states:
				return _("Expanded")
			if STATE_COLLAPSED is not None and STATE_COLLAPSED in states:
				return _("Collapsed")
		except Exception:
			return ""
		return ""

	def _positionInfoValue(self, obj, key):
		positionInfo = _safe_get(obj, "positionInfo")
		if not positionInfo:
			return None
		try:
			return positionInfo.get(key)
		except Exception:
			return None

	def _describeTabAndTableContext(self, obj):
		tab = self._selectedTabObject() or self._nearestRoleObject(obj, ROLE_TAB)
		tabMessage = self._describeTab(tab)
		tableMessage = self._describeTableContext(obj)
		if tabMessage and tableMessage:
			return _("{tab}. {table}").format(tab=tabMessage, table=tableMessage)
		return tableMessage or tabMessage

	def _describeTab(self, obj=None):
		if not obj:
			pane = self._detectPaneFromObject(api.getFocusObject()) or self._lastPane
			if pane:
				return _("Selected tab: {tab}").format(tab=PANE_DEFINITIONS[pane]["name"])
			return None
		name = _clean(_safe_get(obj, "name")) or self._tabNameFromPane(obj)
		if not name:
			return None
		pane = self._paneFromTabName(name)
		if pane:
			self._lastPane = pane
			return _("Selected tab: {tab}. {description}").format(
				tab=PANE_DEFINITIONS[pane]["name"],
				description=self._paneHelp(pane),
			)
		return _("Selected tab: {tab}").format(tab=name)

	def _describeTableContext(self, obj):
		cell = self._nearestTableObject(obj)
		table = self._nearestRoleObject(obj, ROLE_TABLE) if ROLE_TABLE is not None else None
		if not table and cell:
			table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		pane = self._detectPaneFromObject(obj) or self._guessPaneFromCell(cell) or self._lastPane
		tableName = self._tableName(table or cell, pane)
		if cell:
			cellMessage = self._describeCell(cell, preferPane=pane)
			if cellMessage and tableName:
				return _("{table}. {cell}").format(table=tableName, cell=cellMessage)
			return cellMessage
		return tableName

	def _describeCell(self, obj, preferPane=None):
		cell = self._nearestTableObject(obj)
		if not cell:
			pane = preferPane or self._detectPaneFromObject(obj)
			if pane == "data" and _safe_get(obj, "role") == ROLE_EDITABLETEXT:
				value = self._cellValue(obj)
				if value:
					return _("Data View cell editor. Current value {value}").format(value=value)
				return _("Data View cell editor.")
			return None
		pane = preferPane or self._guessPaneFromCell(cell) or self._detectPaneFromObject(cell)
		value = self._cellValue(cell)
		rowNumber = self._numericAttr(cell, ("rowNumber", "row"))
		columnNumber = self._numericAttr(cell, ("columnNumber", "column"))
		rowHeader = (
			self._headerText(cell, ("rowHeaderText", "rowHeaderTexts"))
			or self._inferHeaderText(cell, axis="row")
			or self._cachedHeader(cell, "row", rowNumber)
		)
		columnHeader = (
			self._headerText(cell, ("columnHeaderText", "columnHeaderTexts"))
			or self._inferHeaderText(cell, axis="column")
			or self._cachedHeader(cell, "column", columnNumber)
		)
		if rowHeader:
			self._updateHeaderCache(cell, "row", rowNumber, rowHeader)
		if columnHeader:
			self._updateHeaderCache(cell, "column", columnNumber, columnHeader)
		cellReference = self._cellReference(rowNumber, columnNumber)
		tabName = PANE_DEFINITIONS.get(pane, {}).get("name", _("SPSS table"))
		if pane == "variable":
			variableName = rowHeader or self._nearbyHeaderText(cell, preferRow=True) or _("current variable")
			propertyName = columnHeader or self._columnNameFromNumber(columnNumber) or _("current property")
			details = [_("{tab} cell").format(tab=tabName)]
			if cellReference:
				details.append(_("Cell {cell}").format(cell=cellReference))
			details.append(_("Variable {variable}").format(variable=variableName))
			details.append(_("Property {property}").format(property=propertyName))
			if columnNumber:
				details.append(_("Column {column}").format(column=columnNumber))
			if rowNumber:
				details.append(_("Row {row}").format(row=rowNumber))
			if value:
				details.append(_("Value {value}").format(value=value))
			propertyKey = self._variablePropertyKey(propertyName, columnNumber)
			hint = VARIABLE_PROPERTY_HINTS.get(propertyKey)
			if hint:
				details.append(hint)
			return ". ".join(details)
		if pane == "output":
			details = [_("{tab} table cell").format(tab=tabName)]
			if cellReference:
				details.append(_("Cell {cell}").format(cell=cellReference))
			if rowHeader:
				details.append(_("Row header {header}").format(header=rowHeader))
			elif rowNumber:
				details.append(_("Row {row}").format(row=rowNumber))
			if columnHeader:
				details.append(_("Column header {header}").format(header=columnHeader))
			elif columnNumber:
				details.append(_("Column {column}").format(column=columnNumber))
			if value:
				details.append(_("Value {value}").format(value=value))
			return ". ".join(details)
		details = [_("{tab} cell").format(tab=tabName)]
		if cellReference:
			details.append(_("Cell {cell}").format(cell=cellReference))
		if rowNumber:
			details.append(_("Case {row}").format(row=rowNumber))
		if rowHeader:
			details.append(_("Row header {header}").format(header=rowHeader))
		if columnHeader:
			details.append(_("Variable {variable}").format(variable=columnHeader))
		elif columnNumber:
			details.append(_("Column {column}").format(column=columnNumber))
		if value:
			details.append(_("Value {value}").format(value=value))
		valueLabel = self._cellValueLabel(cell, value, rowHeader=rowHeader, columnHeader=columnHeader)
		if valueLabel:
			details.append(_("Value label {label}").format(label=valueLabel))
		return ". ".join(details)

	def _describeVariableContext(self, obj):
		parts = []
		for candidate in self._ancestors(obj):
			parts.extend(self._meaningfulTextParts(candidate))
			if len(parts) >= 8:
				break
		summary = _join_unique(parts, limit=6)
		if summary:
			return _("Variable View. {summary}").format(summary=summary)
		return None

	def _shortCellName(self, obj):
		value = self._cellValue(obj)
		columnHeader = self._headerText(obj, ("columnHeaderText", "columnHeaderTexts"))
		rowNumber = self._numericAttr(obj, ("rowNumber", "row"))
		if columnHeader and value:
			return _("{column}: {value}").format(column=columnHeader, value=value)
		if rowNumber and value:
			return _("Row {row}: {value}").format(row=rowNumber, value=value)
		return value

	def _selectedTabObject(self):
		root = self._rootObject()
		if not root or ROLE_TAB is None:
			return None
		firstTab = None
		for obj in self._iterObjects(root, maxObjects=MAX_OBJECTS_TO_SCAN):
			if _safe_get(obj, "role") != ROLE_TAB:
				continue
			if firstTab is None:
				firstTab = obj
			if self._isSelectedOrFocused(obj):
				return obj
		return firstTab

	def _paneFromTabName(self, name):
		text = _norm(name)
		if "overview" in text or "over view" in text or "επισκόπ" in text:
			return "overview"
		if "variable" in text or "μεταβλητ" in text:
			return "variable"
		if "data" in text or "δεδομ" in text:
			return "data"
		if "output" in text or "viewer" in text or "αποτελέ" in text:
			return "output"
		if "syntax" in text or "σύνταξ" in text:
			return "syntax"
		if "chart builder" in text or "δημιουργ" in text and "γραφ" in text:
			return "chartbuilder"
		for paneKey in PANE_ORDER:
			for token in PANE_DEFINITIONS[paneKey]["tokens"]:
				if token.lower() in text:
					return paneKey
		return None

	def _tabNameFromPane(self, obj):
		pane = self._detectPaneFromObject(obj)
		if pane:
			return PANE_DEFINITIONS[pane]["name"]
		return ""

	def _tableName(self, obj, pane=None):
		if not obj:
			if pane:
				return _("Table in {tab}").format(tab=PANE_DEFINITIONS[pane]["name"])
			return ""
		name = _clean(_safe_get(obj, "name")) or _clean(_safe_get(obj, "description"))
		if name:
			return _("Table: {name}").format(name=name)
		if pane == "data":
			return _("Data table")
		if pane == "variable":
			return _("Variables table")
		if pane == "overview":
			return _("Overview table")
		if pane == "output":
			return _("Output table")
		return _("SPSS table")

	def _headerText(self, obj, attrs):
		for attr in attrs:
			value = _safe_get(obj, attr)
			if isinstance(value, (list, tuple)):
				value = " ".join(_clean(part) for part in value if _clean(part))
			value = _clean(value)
			if value:
				return value
		return ""

	def _tableCacheKey(self, obj):
		table = self._nearestRoleObject(obj, ROLE_TABLE) if ROLE_TABLE is not None else None
		target = table or obj
		return id(target)

	def _updateHeaderCache(self, obj, axis, number, text):
		if not number or not text:
			return
		key = (self._tableCacheKey(obj), axis, number)
		self._headerCache[key] = text
		if len(self._headerCache) > 800:
			self._headerCache.clear()

	def _cachedHeader(self, obj, axis, number):
		if not number:
			return ""
		return self._headerCache.get((self._tableCacheKey(obj), axis, number), "")

	def _inferHeaderText(self, cell, axis):
		table = self._nearestRoleObject(cell, ROLE_TABLE) if ROLE_TABLE is not None else None
		if not table:
			return ""
		rowNumber = self._numericAttr(cell, ("rowNumber", "row"))
		columnNumber = self._numericAttr(cell, ("columnNumber", "column"))
		if axis == "column" and not columnNumber:
			return ""
		if axis == "row" and not rowNumber:
			return ""
		for candidate in self._iterObjects(table, maxObjects=360):
			if candidate is cell:
				continue
			candidateRole = _safe_get(candidate, "role")
			candidateText = self._cellValue(candidate)
			if not candidateText:
				continue
			candidateRow = self._numericAttr(candidate, ("rowNumber", "row"))
			candidateColumn = self._numericAttr(candidate, ("columnNumber", "column"))
			if axis == "column":
				if candidateRole == ROLE_COLUMNHEADER and candidateColumn == columnNumber:
					return candidateText
				if candidateColumn == columnNumber and candidateRow in (0, 1):
					return candidateText
			else:
				if candidateRole == ROLE_ROWHEADER and candidateRow == rowNumber:
					return candidateText
				if candidateRow == rowNumber and candidateColumn in (0, 1):
					return candidateText
		return ""

	def _cellReference(self, rowNumber, columnNumber):
		if not rowNumber or not columnNumber:
			return ""
		try:
			column = self._columnLetters(int(columnNumber))
			row = int(rowNumber)
		except Exception:
			return ""
		if not column or row < 1:
			return ""
		return "%s%s" % (column, row)

	def _columnLetters(self, number):
		try:
			number = int(number)
		except Exception:
			return ""
		if number < 1:
			return ""
		letters = []
		while number:
			number, remainder = divmod(number - 1, 26)
			letters.append(chr(65 + remainder))
		return "".join(reversed(letters))

	def _nearestRoleObject(self, obj, role):
		if role is None:
			return None
		for candidate in self._ancestors(obj):
			if _safe_get(candidate, "role") == role:
				return candidate
		return None

	def _nearestTableObject(self, obj):
		for candidate in self._ancestors(obj):
			if _safe_get(candidate, "role") in TABLE_ROLES:
				return candidate
		return None

	def _cellValue(self, obj):
		for attr in ("value", "name", "displayText", "description"):
			value = _clean(_safe_get(obj, attr))
			if value:
				return value
		return ""

	def _cellValueLabel(self, obj, value, rowHeader="", columnHeader=""):
		if not value:
			return ""
		skip = {
			_norm(value),
			_norm(rowHeader),
			_norm(columnHeader),
			_norm(_role_name(obj)),
			_norm(_safe_get(obj, "name")),
			_norm(_safe_get(obj, "value")),
			_norm(_safe_get(obj, "displayText")),
		}
		for attr in ("valueLabel", "valueLabels", "description", "helpText"):
			label = _safe_get(obj, attr)
			if isinstance(label, (list, tuple)):
				label = " ".join(_clean(part) for part in label if _clean(part))
			label = _clean(label)
			if not label:
				continue
			normalized = _norm(label)
			if normalized in skip:
				continue
			if normalized.startswith("role "):
				continue
			return label
		return ""

	def _cellDetailsAsParts(self, obj, preferPane=None):
		message = self._describeCell(obj, preferPane=preferPane)
		return [message] if message else []

	def _selectedOrFocusedText(self, obj):
		parts = []
		for candidate in self._ancestors(obj, maxDepth=4):
			if self._isSelectedOrFocused(candidate):
				parts.extend(self._meaningfulTextParts(candidate))
		return parts

	def _meaningfulTextParts(self, obj):
		parts = [
			_safe_get(obj, "name"),
			_safe_get(obj, "value"),
			_safe_get(obj, "description"),
		]
		role = _role_name(obj)
		if role and _safe_get(obj, "role") in (ROLE_TREEVIEWITEM, ROLE_LISTITEM, ROLE_MENUITEM):
			name = _clean(_safe_get(obj, "name"))
			if name:
				parts.append(_("{role}: {name}").format(role=role, name=name))
		return [_clean(part) for part in parts if _clean(part)]

	def _isSelectedOrFocused(self, obj):
		if obj is api.getFocusObject():
			return True
		states = _safe_get(obj, "states", set()) or set()
		try:
			if STATE_SELECTED is not None and STATE_SELECTED in states:
				return True
			if STATE_FOCUSED is not None and STATE_FOCUSED in states:
				return True
		except Exception:
			return False
		return False

	def _columnNameFromNumber(self, columnNumber):
		if not columnNumber:
			return ""
		try:
			index = int(columnNumber) - 1
		except Exception:
			return ""
		if 0 <= index < len(VARIABLE_COLUMNS):
			column = VARIABLE_COLUMNS[index]
			return VARIABLE_COLUMN_LABELS.get(column, column)
		return ""

	def _variablePropertyKey(self, propertyName, columnNumber=None):
		text = _norm(propertyName)
		for column, tokens in VARIABLE_COLUMN_TOKENS.items():
			if any(token.lower() in text for token in tokens):
				return column
		if columnNumber:
			try:
				index = int(columnNumber) - 1
			except Exception:
				return None
			if 0 <= index < len(VARIABLE_COLUMNS):
				return VARIABLE_COLUMNS[index]
		return None

	def _isVariableColumnName(self, value):
		value = _norm(value)
		if not value:
			return False
		for tokens in VARIABLE_COLUMN_TOKENS.values():
			if value in tuple(token.lower() for token in tokens):
				return True
		return False

	def _nearbyHeaderText(self, obj, preferRow=False):
		parent = _safe_get(obj, "parent")
		if not parent:
			return ""
		for child in self._children(parent):
			if child is obj:
				continue
			text = _clean(_safe_get(child, "name")) or _clean(_safe_get(child, "value"))
			if not text:
				continue
			if preferRow and self._isVariableColumnName(text):
				continue
			return text
		return ""

	def _numericAttr(self, obj, attrs):
		for attr in attrs:
			value = _safe_get(obj, attr)
			if value in (None, ""):
				continue
			try:
				return int(value)
			except Exception:
				return value
		return None

	def _findContainingOrBestPane(self, obj, paneKey):
		for candidate in self._ancestors(obj):
			if self._scorePaneObject(candidate, paneKey) >= 20:
				return candidate
		return self._findBestPaneObject(paneKey)

	def _paneNotFoundMessage(self, paneKey):
		name = PANE_DEFINITIONS[paneKey]["name"]
		if paneKey in ("overview", "data", "variable"):
			return _(
				"{name} was not found in the current SPSS window. Open the Data Editor, "
				"then use the Overview, Data View, or Variable View tabs in the editor."
			).format(name=name)
		if paneKey == "output":
			return _(
				"Output Viewer was not found. Run an analysis or open an SPSS output file, "
				"then use the Window menu to bring the Output Viewer forward."
			)
		if paneKey == "syntax":
			return _(
				"Syntax Editor was not found. Open a syntax file or use Paste from an SPSS dialog to create syntax."
			)
		if paneKey == "chartbuilder":
			return _("Chart Builder was not found. Open it from Graphs, Chart Builder.")
		return _("{name} was not found in the current SPSS window.").format(name=name)

	def _rootObject(self):
		root = api.getForegroundObject()
		if root:
			return root
		obj = api.getFocusObject()
		last = obj
		for parent in self._ancestors(obj, maxDepth=40):
			last = parent
		return last

	def _objectSearchText(self, obj):
		parts = [
			_safe_get(obj, "name"),
			_safe_get(obj, "description"),
			_safe_get(obj, "value"),
			_safe_get(obj, "helpText"),
			_safe_get(obj, "UIAAutomationId"),
			_safe_get(obj, "windowClassName"),
			_role_name(obj),
		]
		return _norm(" ".join(_safe_str(part) for part in parts if part))

	def _focusOrNavigate(self, obj):
		try:
			obj.setFocus()
			return True
		except Exception:
			pass
		try:
			api.setNavigatorObject(obj)
			return True
		except Exception:
			return False

	def _activateObject(self, obj):
		try:
			obj.setFocus()
		except Exception:
			pass
		try:
			obj.doAction()
			return True
		except Exception:
			pass
		try:
			api.setNavigatorObject(obj)
			return True
		except Exception:
			return False

	def _iterObjects(self, root, maxObjects=MAX_OBJECTS_TO_SCAN):
		seen = set()
		queue = [root]
		count = 0
		while queue and count < maxObjects:
			obj = queue.pop(0)
			if not obj:
				continue
			identity = id(obj)
			if identity in seen:
				continue
			seen.add(identity)
			count += 1
			yield obj
			for child in self._children(obj):
				queue.append(child)

	def _children(self, obj):
		child = _safe_get(obj, "simpleFirstChild")
		count = 0
		while child and count < MAX_CHILDREN_PER_OBJECT:
			yield child
			count += 1
			child = _safe_get(child, "simpleNext")
		if count:
			return
		children = _safe_get(obj, "children")
		if not children:
			return
		try:
			for index, child in enumerate(children):
				if index >= MAX_CHILDREN_PER_OBJECT:
					break
				yield child
		except Exception:
			return

	def _ancestors(self, obj, maxDepth=14):
		depth = 0
		current = obj
		seen = set()
		while current and depth < maxDepth:
			identity = id(current)
			if identity in seen:
				break
			seen.add(identity)
			yield current
			current = _safe_get(current, "parent")
			depth += 1
