# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin App Module for NVDA
# Version: 1.2.0
#
# This module is loaded directly for spss.exe, the main process name used by
# older SPSS releases before the IBM-era rename. Alias modules in this folder
# reuse its AppModule for the other SPSS process names.
# =============================================================================
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Bouronikos Christos
# This file is covered by the GNU General Public License v2.
# =============================================================================

"""
SPSS Accessibility Plugin app module for NVDA.

Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com.
GitHub: https://github.com/ChristosBouronikos.
If this add-on helps you, please consider a kind donation via PayPal:
https://paypal.me/christosbouronikos

This module improves day-to-day use of IBM SPSS Statistics with NVDA by adding:
- Pane recognition for Output Viewer, Data Editor views, syntax, Chart Builder,
  Pivot Table Editor, and menus.
- A bilingual (English/Greek) knowledge base (the ``_spssdata`` package) that
  describes SPSS menus and submenus, statistical procedure dialogs and their
  sub-dialogs, Data Editor and Variable View controls, output item kinds, and
  a plain-language statistics glossary.
- Detailed descriptions when entering important SPSS work areas, spoken in
  English or Greek to match the language IBM SPSS Statistics itself is
  running in (detected automatically, or set manually).
- Commands for reading output items, data cells, variable definitions, whole
  dialogs, and open menus or submenus.
- Better fallback labels for unlabeled toolbar and dialog controls.

SPSS exposes different UI Automation names across versions, so most detection is
deliberately heuristic and combines object role, name, description, class name,
automation id, table coordinates, and surrounding ancestors.

Two languages are involved and are kept deliberately independent:
- The add-on's own voice (script descriptions, shortcuts list, status and
  error messages, generic template phrases such as "Cell {cell}") follows
  NVDA's own interface language, through the standard gettext catalog.
- The content that explains what a piece of SPSS actually is or does (pane
  help, menu and dialog descriptions, dialog field meaning, variable column
  meaning, output item kinds, and the statistics glossary) follows the
  language IBM SPSS Statistics is running in, resolved by
  ``AppModule._resolveLanguage``. This can be detected automatically from the
  visible SPSS menu text, or fixed to English or Greek from NVDA+Control+
  Alt+Shift+J or the SPSS Accessibility category of NVDA settings.
"""

import re

import addonHandler
import api
import appModuleHandler
import controlTypes
import ui
from logHandler import log
from scriptHandler import script

try:
	import config
except Exception:
	config = None

from . import _spssdata as kb


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

FORM_CONTROL_ROLES = tuple(
	role for role in (
		ROLE_BUTTON, ROLE_EDITABLETEXT, ROLE_CHECKBOX, ROLE_RADIOBUTTON,
		ROLE_COMBOBOX, ROLE_LIST, ROLE_LISTITEM, ROLE_TREEVIEWITEM,
	)
	if role is not None
)

CONTROL_TYPE_LABELS = (
	(ROLE_BUTTON, _("Button")),
	(ROLE_EDITABLETEXT, _("Text box")),
	(ROLE_CHECKBOX, _("Checkbox")),
	(ROLE_RADIOBUTTON, _("Radio button")),
	(ROLE_COMBOBOX, _("Dropdown menu")),
	(ROLE_LIST, _("List")),
	(ROLE_LISTITEM, _("List item")),
	(ROLE_TREEVIEWITEM, _("Tree item")),
)

# Which NVDA roles count as evidence for each SPSS pane. Combined with the
# bilingual token lists in _spssdata.panes to score candidate objects.
PANE_ROLE_MAP = {
	"overview": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL, ROLE_PANE),
	"output": (ROLE_DOCUMENT, ROLE_TREEVIEW, ROLE_TREEVIEWITEM, ROLE_PANE, ROLE_TABLE),
	"data": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL),
	"variable": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_TAB, ROLE_TABCONTROL),
	"syntax": (ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_PANE),
	"chartbuilder": (ROLE_PANE, ROLE_LIST, ROLE_LISTITEM, ROLE_TAB, ROLE_TABCONTROL, ROLE_BUTTON, ROLE_GROUPING),
	"pivottable": (ROLE_TABLE, ROLE_ROW, ROLE_CELL, ROLE_PANE, ROLE_DOCUMENT),
	"menus": (ROLE_MENUBAR, ROLE_MENU, ROLE_MENUITEM),
}

PANE_DEFINITIONS = {
	paneKey: {
		"tokens": kb.panes.PANE_TOKENS[paneKey],
		"roles": tuple(role for role in PANE_ROLE_MAP[paneKey] if role is not None),
	}
	for paneKey in kb.panes.PANE_ORDER
}

PANE_ORDER = kb.panes.PANE_ORDER

# Bilingual (English, Greek) fallback labels for controls that SPSS exposes
# with no accessible name. Keys must be lower-case and accent-free, matching
# what AppModule._norm produces, since Greek SPSS text carries accents that
# are stripped before matching.
GENERIC_CONTROL_LOOKUP = {
	"ok": (u"OK", u"OK"),
	"cancel": (u"Cancel", u"Ακύρωση"),
	"apply": (u"Apply", u"Εφαρμογή"),
	"close": (u"Close", u"Κλείσιμο"),
	"continue": (u"Continue", u"Συνέχεια"),
	"reset": (u"Reset", u"Επαναφορά"),
	"paste": (u"Paste syntax", u"Επικόλληση σύνταξης"),
	"paste syntax": (u"Paste syntax", u"Επικόλληση σύνταξης"),
	"run": (u"Run command", u"Εκτέλεση εντολής"),
	"run selection": (u"Run selection", u"Εκτέλεση επιλογής"),
	"run current": (u"Run current command", u"Εκτέλεση τρέχουσας εντολής"),
	"open": (u"Open", u"Άνοιγμα"),
	"save": (u"Save", u"Αποθήκευση"),
	"print": (u"Print", u"Εκτύπωση"),
	"browse": (u"Browse", u"Αναζήτηση"),
	"options": (u"Options", u"Επιλογές"),
	"spelling": (u"Spelling", u"Ορθογραφία"),
	"statistics": (u"Statistics", u"Statistics"),
	"charts": (u"Charts", u"Charts"),
	"plots": (u"Plots", u"Plots"),
	"posthoc": (u"Post Hoc", u"Post Hoc"),
	"post hoc": (u"Post Hoc", u"Post Hoc"),
	"contrasts": (u"Contrasts", u"Contrasts"),
	"bootstrap": (u"Bootstrap", u"Bootstrap"),
	"exact": (u"Exact tests", u"Ακριβείς έλεγχοι"),
	"style": (u"Style", u"Στυλ"),
	"format": (u"Format", u"Μορφοποίηση"),
	"gallery": (u"Gallery", u"Gallery"),
	"basic elements": (u"Basic Elements", u"Basic Elements"),
	"groups/point id": (u"Groups or Point ID", u"Groups or Point ID"),
	"groups point id": (u"Groups or Point ID", u"Groups or Point ID"),
	"titles/footnotes": (u"Titles or Footnotes", u"Titles or Footnotes"),
	"titles footnotes": (u"Titles or Footnotes", u"Titles or Footnotes"),
	"choose from": (u"Choose from chart types", u"Επιλογή τύπου γραφήματος"),
	"chart preview": (u"Chart preview canvas", u"Καμβάς προεπισκόπησης γραφήματος"),
	"canvas": (u"Chart canvas", u"Καμβάς γραφήματος"),
	"drop zone": (u"Drop zone", u"Ζώνη απόθεσης"),
	"drop zones": (u"Drop zones", u"Ζώνες απόθεσης"),
	"element properties": (u"Element Properties", u"Element Properties"),
	"categories": (u"Categories", u"Κατηγορίες"),
	"source variable list": (u"Source variable list", u"Λίστα μεταβλητών προέλευσης"),
	"variables list": (u"Variables list", u"Λίστα μεταβλητών"),
	"variables": (u"Variables", u"Μεταβλητές"),
	"variable type": (u"Variable Type", u"Τύπος μεταβλητής"),
	"variable": (u"Variable", u"Μεταβλητή"),
	"dependent": (u"Dependent variable", u"Εξαρτημένη μεταβλητή"),
	"independent": (u"Independent variable", u"Ανεξάρτητη μεταβλητή"),
	"covariates": (u"Covariates", u"Συμμεταβλητές"),
	"factor": (u"Factor", u"Παράγοντας"),
	"label": (u"Label", u"Ετικέτα"),
	"labels": (u"Labels", u"Ετικέτες"),
	"add": (u"Add", u"Add"),
	"change": (u"Change", u"Change"),
	"remove": (u"Remove", u"Remove"),
	"read excel": (u"Read Excel File", u"Ανάγνωση αρχείου Excel"),
	"text import wizard": (u"Text Import Wizard", u"Οδηγός εισαγωγής κειμένου"),
	"database wizard": (u"Database Wizard", u"Οδηγός βάσης δεδομένων"),
}


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
	"""Normalise SPSS text for matching: clean, strip accents, lower-case.

	Accent stripping matters for Greek: NVDA reports Greek SPSS text with its
	normal tonos accents (for example "Επισκόπηση"), while the token lists in
	``_spssdata`` are written without accents so a single token list matches
	every accented form. See ``_spssdata.core.stripAccents``.
	"""
	return kb.core.stripAccents(_clean(value)).lower()


def _containsGreek(value):
	"""Return whether text contains a Greek or Greek Extended character."""
	return re.search(r"[\u0370-\u03ff\u1f00-\u1fff]", _safe_str(value)) is not None


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


# Unaccented Greek words that only appear on a genuinely Greek-localized SPSS
# menu bar, used to auto-detect which language SPSS itself is running in.
SPSS_GREEK_MENU_TOKENS = (
	u"αρχειο", u"επεξεργασια", u"προβολη", u"δεδομενα", u"μετασχηματισμος",
	u"αναλυση", u"γραφηματα", u"βοηθεια", u"προσθετα", u"παραθυρο", u"μορφοποιηση",
)


class AppModule(appModuleHandler.AppModule):
	"""NVDA app module for IBM SPSS Statistics."""

	scriptCategory = _("IBM SPSS Statistics")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lastPane = None
		self._verboseHelp = True
		self._announceTableMovement = False
		self._headerCache = {}
		self._dialogEntryCache = {}
		self._languageCache = {}
		self._lastDetectedLanguage = None
		log.info("IBM SPSS Statistics accessibility app module 1.2.0 loaded")

	def terminate(self):
		log.info("IBM SPSS Statistics accessibility app module unloaded")
		super().terminate()

	# ------------------------------------------------------------------
	# Spoken-language resolution for SPSS content (menus, dialogs, panes,
	# variable columns, output kinds, glossary). Independent from NVDA's own
	# interface language, which continues to drive the add-on's own voice
	# through the normal gettext ``_()`` calls used throughout this file.
	# ------------------------------------------------------------------

	def _configLanguageOverride(self):
		if config is None:
			return "auto"
		try:
			value = config.conf["spssAccessibility"]["language"]
		except Exception:
			return "auto"
		return value if value in ("auto", kb.LANG_EN, kb.LANG_EL) else "auto"

	def _setConfigLanguageOverride(self, value):
		if config is None:
			return
		try:
			config.conf["spssAccessibility"]["language"] = value
		except Exception as e:
			log.debugWarning("Could not persist SPSS Accessibility language setting: %s" % e)

	def _detectSpssLanguage(self):
		root = self._rootObject()
		cacheKey = id(root) if root is not None else None
		cached = self._languageCache
		if cacheKey is not None and cached.get("key") == cacheKey:
			return cached["lang"]
		lang = self._lastDetectedLanguage or kb.LANG_EN
		try:
			hits = 0
			scanned = 0
			for obj in self._iterObjects(root, maxObjects=260):
				if _safe_get(obj, "role") not in (ROLE_MENUBAR, ROLE_MENU, ROLE_MENUITEM):
					continue
				text = _norm(_safe_get(obj, "name"))
				if not text:
					continue
				scanned += 1
				if any(token in text for token in SPSS_GREEK_MENU_TOKENS):
					hits += 1
				if scanned >= 24:
					break
			if hits >= 2:
				lang = kb.LANG_EL
				self._lastDetectedLanguage = lang
			elif scanned >= 2:
				lang = kb.LANG_EN
				self._lastDetectedLanguage = lang
			else:
				# Modal dialogs usually have no menu bar. Preserve the language
				# established by the parent SPSS window; if no window has been seen
				# yet, use Greek text in the dialog itself as positive evidence.
				greekObjects = 0
				for obj in self._iterObjects(root, maxObjects=80):
					if any(_containsGreek(_safe_get(obj, attr)) for attr in ("name", "description", "value")):
						greekObjects += 1
						if greekObjects >= 2:
							lang = kb.LANG_EL
							self._lastDetectedLanguage = lang
							break
		except Exception as e:
			log.debugWarning("SPSS language detection failed: %s" % e)
		self._languageCache = {"key": cacheKey, "lang": lang}
		return lang

	def _resolveLanguage(self):
		override = self._configLanguageOverride()
		if override in (kb.LANG_EN, kb.LANG_EL):
			return override
		return self._detectSpssLanguage()

	# ------------------------------------------------------------------
	# Object labeling and description
	# ------------------------------------------------------------------

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

	def _controlTypeLabel(self, obj):
		role = _safe_get(obj, "role")
		for candidateRole, label in CONTROL_TYPE_LABELS:
			if candidateRole is not None and role == candidateRole:
				return label
		return _role_name(obj)

	def _controlActionHint(self, obj):
		role = _safe_get(obj, "role")
		if role == ROLE_COMBOBOX:
			return _("Press Alt+Down Arrow or Space to open the dropdown menu.")
		if role == ROLE_BUTTON:
			return _("Press Space or Enter to activate.")
		if role == ROLE_EDITABLETEXT:
			return _("Type text or use editing commands.")
		if role in (ROLE_CHECKBOX, ROLE_RADIOBUTTON):
			return _("Press Space to change the selection.")
		if role in (ROLE_LIST, ROLE_LISTITEM, ROLE_TREEVIEWITEM):
			return _("Use arrow keys to move through items.")
		return ""

	def _describeControl(self, obj):
		lang = self._resolveLanguage()
		name = _clean(_safe_get(obj, "name")) or self._labelForControl(obj)
		dialogEntry, dialogObj = self._currentDialogEntry(obj)
		fieldEntry = None
		if dialogEntry and name and dialogObj is not None:
			fieldEntry, _path = kb.findDialogControl(name, parents=(dialogEntry["en"],))
		controlType = self._controlTypeLabel(obj)
		value = _clean(_safe_get(obj, "value")) or _clean(_safe_get(obj, "displayText"))
		parts = []
		if fieldEntry:
			parts.append(kb.label(fieldEntry, lang))
			kindText = kb.kindLabel(fieldEntry.get("kind"), lang)
			parts.append(kindText or controlType)
		else:
			if controlType:
				parts.append(controlType)
			if name:
				parts.append(name)
		if value and _norm(value) != _norm(name):
			parts.append(_("Current value {value}").format(value=value))
		if fieldEntry:
			desc = kb.describe(fieldEntry, lang)
			if desc:
				parts.append(desc)
			action = kb.kindAction(fieldEntry.get("kind"), lang)
			if action:
				parts.append(action)
		else:
			hint = self._controlActionHint(obj)
			if hint:
				parts.append(hint)
		return kb.joinParts(parts)

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
			if _safe_get(obj, "role") in FORM_CONTROL_ROLES:
				controlMessage = self._describeControl(obj)
				if controlMessage:
					ui.message(controlMessage)
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

	# ------------------------------------------------------------------
	# Scripts: navigation
	# ------------------------------------------------------------------

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

	# ------------------------------------------------------------------
	# Scripts: orientation and description
	# ------------------------------------------------------------------

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
		context = self._menuContextHelp(pane)
		message = " ".join(part for part in (context, self._topLevelMenuSummary()) if part)
		ui.message(message)

	@script(
		description=_("Describe SPSS output accessibility and export options"),
		gesture="kb:NVDA+control+alt+shift+e",
	)
	def script_describeOutputAccessibility(self, gesture):
		lang = self._resolveLanguage()
		ui.message(kb.pick(kb.panes.OUTPUT_ACCESSIBILITY_HELP, lang))

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
		description=_("List the items in the current SPSS menu or submenu"),
		gesture="kb:NVDA+control+alt+shift+q",
	)
	def script_listMenuItems(self, gesture):
		message = self._currentMenuItemsSummary(api.getFocusObject())
		ui.message(message or _("No open SPSS menu or submenu was found at the current focus."))

	@script(
		description=_("Describe the current SPSS dialog"),
		gesture="kb:NVDA+control+alt+shift+i",
	)
	def script_describeCurrentDialog(self, gesture):
		ui.message(self._dialogHelp(api.getFocusObject()) or _("No SPSS dialog help is available at the current focus."))

	@script(
		description=_("Read every field and button in the current SPSS dialog"),
		gesture="kb:NVDA+control+alt+shift+k",
	)
	def script_describeDialogStructure(self, gesture):
		message = self._dialogStructureSummary(api.getFocusObject())
		ui.message(message or _("No SPSS dialog was found at the current focus."))

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
		lines = []
		for entry in kb.terms.GLOSSARY:
			en = kb.label(entry, kb.LANG_EN)
			el = kb.label(entry, kb.LANG_EL)
			enDesc = kb.describe(entry, kb.LANG_EN)
			elDesc = kb.describe(entry, kb.LANG_EL)
			lines.append(_("{en} ({el}): {enDesc} {elDesc}").format(en=en, el=el, enDesc=enDesc, elDesc=elDesc))
		ui.message(" ".join(lines))

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
		description=_("Cycle the spoken language for SPSS content between automatic, English, and Greek"),
		gesture="kb:NVDA+control+alt+shift+j",
	)
	def script_cycleSpokenLanguage(self, gesture):
		order = ("auto", kb.LANG_EN, kb.LANG_EL)
		current = self._configLanguageOverride()
		try:
			nextValue = order[(order.index(current) + 1) % len(order)]
		except ValueError:
			nextValue = "auto"
		self._setConfigLanguageOverride(nextValue)
		self._languageCache = {}
		messages = {
			"auto": _("SPSS content language set to automatic, following the SPSS interface language."),
			kb.LANG_EN: _("SPSS content language set to English."),
			kb.LANG_EL: _("SPSS content language set to Greek."),
		}
		ui.message(messages[nextValue])

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
			_("NVDA+Control+Alt+Shift+Q: list items in the current menu or submenu."),
			_("NVDA+Control+Alt+Shift+I: describe current dialog."),
			_("NVDA+Control+Alt+Shift+K: read every field and button in the current dialog."),
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
			_("NVDA+Control+Alt+Shift+J: cycle spoken language for SPSS content."),
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

	# ------------------------------------------------------------------
	# Where am I
	# ------------------------------------------------------------------

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
			parts.append(_("Pane {pane}").format(pane=self._paneName(pane)))
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
				if propertyKey:
					lang = self._resolveLanguage()
					hint = kb.pick(kb.panes.VARIABLE_COLUMN_HELP.get(propertyKey, ()), lang)
					if hint:
						return hint
				return _("Use arrow keys to move in the table.")
			return _("Use arrow keys to move in the table.")
		if "drop zone" in text:
			return _("Paste a copied variable here with Control+V, or open context commands with Shift+F10.")
		return ""

	# ------------------------------------------------------------------
	# Menus
	# ------------------------------------------------------------------

	def _paneName(self, paneKey):
		lang = self._resolveLanguage()
		return kb.pick(kb.panes.PANE_NAMES.get(paneKey, (paneKey, paneKey)), lang)

	def _menuPathDescription(self, obj):
		items = self._menuPathItems(obj)
		if not items:
			return ""
		return _("Menu path: {path}").format(path=" > ".join(items))

	def _focusedMenuItemDescription(self, obj):
		path = self._menuPathItems(obj)
		if not path:
			return ""
		lang = self._resolveLanguage()
		entry, _kbPath = kb.findMenuItem(path[-1], parents=tuple(path[:-1]))
		pathText = _("Menu path: {path}").format(path=" > ".join(path))
		if not entry:
			return pathText
		parts = [pathText]
		desc = kb.describe(entry, lang)
		if desc:
			parts.append(desc)
		action = kb.kindAction(entry.get("kind"), lang)
		if action:
			parts.append(action)
		return kb.joinParts(parts)

	def _menuPathItems(self, obj):
		items = []
		for candidate in self._ancestors(obj, maxDepth=12):
			if _safe_get(candidate, "role") in (ROLE_MENUITEM, ROLE_MENU, ROLE_MENUBAR):
				name = _clean(_safe_get(candidate, "name"))
				if name:
					items.append(name)
		return list(reversed(items))

	def _currentMenuItemsSummary(self, obj):
		if not obj:
			return ""
		role = _safe_get(obj, "role")
		if role in (ROLE_MENU, ROLE_MENUBAR):
			container = obj
			parentPath = self._menuPathItems(obj)
		elif role == ROLE_MENUITEM:
			container = _safe_get(obj, "parent")
			fullPath = self._menuPathItems(obj)
			parentPath = fullPath[:-1]
		else:
			return ""
		if not container or _safe_get(container, "role") not in (ROLE_MENU, ROLE_MENUBAR):
			return ""
		lang = self._resolveLanguage()
		items = []
		for child in self._children(container):
			if _safe_get(child, "role") not in (ROLE_MENUITEM, ROLE_MENU):
				continue
			childName = _clean(_safe_get(child, "name"))
			if not childName:
				continue
			entry, _p = kb.findMenuItem(childName, parents=tuple(parentPath))
			items.append(kb.label(entry, lang) if entry else childName)
			if len(items) >= 40:
				break
		if not items:
			return ""
		containerName = _clean(_safe_get(container, "name")) or (parentPath[-1] if parentPath else _("menu"))
		return _("{menu} has {count} items: {items}").format(menu=containerName, count=len(items), items=", ".join(items))

	def _topLevelMenuSummary(self):
		lang = self._resolveLanguage()
		parts = []
		for entry in kb.menus.MENUS:
			name = kb.label(entry, lang)
			desc = kb.describe(entry, lang)
			parts.append(_("{menu}: {description}").format(menu=name, description=desc) if desc else name)
		return " ".join(parts)

	def _menuContextHelp(self, pane):
		lang = self._resolveLanguage()
		menuNames = kb.menus.WINDOW_MENUS.get(pane)
		if not menuNames:
			return ""
		labels = []
		for menuName in menuNames:
			entry, _p = kb.findMenuItem(menuName)
			labels.append(kb.label(entry, lang) if entry else menuName)
		return _("Menus available here: {menus}.").format(menus=", ".join(labels))

	# ------------------------------------------------------------------
	# Dialogs
	# ------------------------------------------------------------------

	def _dialogObject(self, obj):
		root = self._rootObject()
		for candidate in self._ancestors(obj, maxDepth=16):
			role = _safe_get(candidate, "role")
			if role == ROLE_DIALOG:
				return candidate
			if role == ROLE_WINDOW:
				# Nested windows are dialogs. A foreground root window is accepted
				# only when its title identifies a known SPSS dialog, avoiding the
				# main Data Editor/Viewer window being treated as a dialog.
				if candidate is not root or kb.findDialogByTitle(_safe_get(candidate, "name")):
					return candidate
			if root is not None and candidate is root:
				break
		return None

	def _currentDialogEntry(self, obj):
		dialog = self._dialogObject(obj)
		if not dialog:
			return None, None
		key = id(dialog)
		cached = self._dialogEntryCache.get(key)
		if cached is not None:
			return cached, dialog
		textParts = [self._objectSearchText(dialog)]
		count = 0
		for child in self._iterObjects(dialog, maxObjects=260):
			textParts.append(self._objectSearchText(child))
			count += 1
			if count >= 260:
				break
		entry = kb.findDialogByTokens(
			" ".join(textParts),
			titleText=_safe_get(dialog, "name"),
		)
		if len(self._dialogEntryCache) > 200:
			self._dialogEntryCache.clear()
		self._dialogEntryCache[key] = entry
		return entry, dialog

	def _dialogHelp(self, obj, concise=False):
		entry, dialog = self._currentDialogEntry(obj)
		if not dialog:
			return ""
		lang = self._resolveLanguage()
		name = _clean(_safe_get(dialog, "name")) or (kb.label(entry, lang) if entry else "") or _("SPSS dialog")
		if concise:
			return _("Dialog {name}.").format(name=name)
		if entry:
			return kb.describe(entry, lang)
		return _(
			"SPSS dialog {name}. Use Tab and Shift+Tab to move between controls, arrow keys inside lists or option groups, Space to select, Enter for the default action, Escape to cancel, and Paste when you want syntax."
		).format(name=name)

	def _dialogStructureSummary(self, obj):
		entry, dialog = self._currentDialogEntry(obj)
		if not dialog:
			return ""
		lang = self._resolveLanguage()
		name = _clean(_safe_get(dialog, "name")) or (kb.label(entry, lang) if entry else "") or _("SPSS dialog")
		parents = (entry["en"],) if entry else ()
		items = []
		seen = set()
		for child in self._iterObjects(dialog, maxObjects=520):
			role = _safe_get(child, "role")
			if role not in FORM_CONTROL_ROLES and role != ROLE_TAB:
				continue
			childLabel = _clean(_safe_get(child, "name"))
			if not childLabel:
				continue
			key = childLabel.lower()
			if key in seen:
				continue
			seen.add(key)
			fieldEntry, _p = kb.findDialogControl(childLabel, parents=parents)
			if fieldEntry:
				kindText = kb.kindLabel(fieldEntry.get("kind"), lang)
				items.append(kb.joinParts([kb.label(fieldEntry, lang), kindText]))
			else:
				controlType = self._controlTypeLabel(child)
				items.append(kb.joinParts([childLabel, controlType]))
			if len(items) >= 40:
				break
		if not items:
			return ""
		header = _("{name}. {count} controls:").format(name=name, count=len(items))
		return header + " " + ". ".join(items)

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

	# ------------------------------------------------------------------
	# Tables
	# ------------------------------------------------------------------

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
		lang = self._resolveLanguage()
		ordered = []
		for column in kb.panes.VARIABLE_COLUMNS:
			columnLabel = kb.pick(kb.panes.VARIABLE_COLUMN_LABELS.get(column, (column, column)), lang)
			for key, value in properties.items():
				if self._variablePropertyKey(key) == column:
					ordered.append(_("{property}: {value}").format(property=columnLabel, value=value))
					break
		if not ordered:
			ordered = [_("{property}: {value}").format(property=k, value=v) for k, v in properties.items()]
		variableName = properties.get("Name") or _("current variable")
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
		lang = self._resolveLanguage()
		table = kb.panes.PANE_HELP if self._verboseHelp else kb.panes.PANE_BRIEF
		pair = table.get(paneKey) or kb.panes.PANE_HELP.get(paneKey)
		return kb.pick(pair, lang)

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
		lang = self._resolveLanguage()
		text = self._objectSearchText(obj)
		for paneKey, names in kb.panes.PANE_NAMES.items():
			if _contains_token(text, names[0]) or (len(names) > 1 and _contains_token(text, names[1])):
				return kb.pick(names, lang)
		for token, pair in GENERIC_CONTROL_LOOKUP.items():
			if _contains_token(text, token):
				return kb.pick(pair, lang)
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
			"overview": (u"overview", u"over view", u"επισκοπηση"),
			"data": (u"data view", u"προβολη δεδομενων"),
			"variable": (u"variable view", u"προβολη μεταβλητων"),
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
			if paneKey == "data" and (("data" in text and "view" in text) or ("δεδομεν" in text and "προβολ" in text)):
				score += 25
			if paneKey == "variable" and (("variable" in text and "view" in text) or ("μεταβλητ" in text and "προβολ" in text)):
				score += 25
			if paneKey == "overview" and (("overview" in text or ("over" in text and "view" in text)) or "επισκοπ" in text):
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
		if role in definition["roles"]:
			score += 8
		for token in definition["tokens"]:
			token = _norm(token)
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
		if paneKey in ("overview", "data", "variable", "pivottable") and role in TABLE_ROLES:
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
		for tokens in kb.panes.VARIABLE_COLUMN_TOKENS.values():
			if any(_norm(token) in text for token in tokens):
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
		if "overview" in text or "over view" in text or "επισκοπηση" in text:
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
		lang = self._resolveLanguage()
		if role in TABLE_ROLES or "pivot table" in text or "pivot" in text:
			return kb.pick(kb.panes.OUTPUT_ITEM_KINDS[0][1], lang)
		for tokens, pair in kb.panes.OUTPUT_ITEM_KINDS:
			if any(token in text for token in tokens):
				return kb.pick(pair, lang)
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
				return _("Selected tab: {tab}").format(tab=self._paneName(pane))
			return None
		name = _clean(_safe_get(obj, "name")) or self._tabNameFromPane(obj)
		if not name:
			return None
		pane = self._paneFromTabName(name)
		if pane:
			self._lastPane = pane
			return _("Selected tab: {tab}. {description}").format(
				tab=self._paneName(pane),
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
					return _("Data View cell editor. Text box. Current value {value}").format(value=value)
				return _("Data View cell editor. Text box.")
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
		tabName = self._paneName(pane) if pane in PANE_ORDER else _("SPSS table")
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
				details.append(_("Current value {value}").format(value=value))
			propertyKey = self._variablePropertyKey(propertyName, columnNumber)
			lang = self._resolveLanguage()
			hint = kb.pick(kb.panes.VARIABLE_COLUMN_HELP.get(propertyKey, ()), lang)
			if hint:
				details.append(hint)
			if propertyKey in ("Align", "Measure", "Role"):
				details.append(_("Press Alt+Down Arrow or Space to open the dropdown menu."))
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
		if "overview" in text or "over view" in text or "επισκοπ" in text:
			return "overview"
		if "variable" in text or "μεταβλητ" in text:
			return "variable"
		if "data" in text or "δεδομ" in text:
			return "data"
		if "output" in text or "viewer" in text or "αποτελε" in text:
			return "output"
		if "syntax" in text or "συνταξ" in text:
			return "syntax"
		if "chart builder" in text or ("δημιουργ" in text and "γραφ" in text):
			return "chartbuilder"
		for paneKey in PANE_ORDER:
			for token in PANE_DEFINITIONS[paneKey]["tokens"]:
				if _norm(token) in text:
					return paneKey
		return None

	def _tabNameFromPane(self, obj):
		pane = self._detectPaneFromObject(obj)
		if pane:
			return self._paneName(pane)
		return ""

	def _tableName(self, obj, pane=None):
		if not obj:
			if pane:
				return _("Table in {tab}").format(tab=self._paneName(pane))
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
		if 0 <= index < len(kb.panes.VARIABLE_COLUMNS):
			column = kb.panes.VARIABLE_COLUMNS[index]
			lang = self._resolveLanguage()
			return kb.pick(kb.panes.VARIABLE_COLUMN_LABELS.get(column, (column, column)), lang)
		return ""

	def _variablePropertyKey(self, propertyName, columnNumber=None):
		text = _norm(propertyName)
		for column, tokens in kb.panes.VARIABLE_COLUMN_TOKENS.items():
			if any(_norm(token) in text for token in tokens):
				return column
		if columnNumber:
			try:
				index = int(columnNumber) - 1
			except Exception:
				return None
			if 0 <= index < len(kb.panes.VARIABLE_COLUMNS):
				return kb.panes.VARIABLE_COLUMNS[index]
		return None

	def _isVariableColumnName(self, value):
		value = _norm(value)
		if not value:
			return False
		for tokens in kb.panes.VARIABLE_COLUMN_TOKENS.values():
			if value in tuple(_norm(token) for token in tokens):
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
		name = self._paneName(paneKey)
		if paneKey in ("overview", "data", "variable"):
			return _(
				"{name} was not found in the current SPSS window. Open the Data Editor, then use the Overview, Data View, or Variable View tabs in the editor."
			).format(name=name)
		if paneKey == "output":
			return _(
				"Output Viewer was not found. Run an analysis or open an SPSS output file, then use the Window menu to bring the Output Viewer forward."
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
