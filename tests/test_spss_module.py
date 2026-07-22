# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Offline tests for addon/appModules/spss.py against stub NVDA modules.

Run with:

    python3 -m unittest discover -s tests -v

These tests do not require NVDA or SPSS. They build small fake SPSS UI
Automation trees (see tests/nvdastubs/fakeobj.py) and stub out just enough of
NVDA's API (tests/nvdastubs/*.py) to exercise the real app module code:
pane detection, bilingual menu/dialog/pane descriptions, spoken-language
resolution and override, data/variable/output cell reading, and the new
dialog-structure and menu-listing commands.
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_STUBS = os.path.join(_HERE, "nvdastubs")
_ADDON = os.path.join(_REPO_ROOT, "addon")

for path in (_STUBS, _ADDON):
	if path not in sys.path:
		sys.path.insert(0, path)

import api as fake_api  # noqa: E402  (stub module, must follow sys.path setup)
import config as fake_config  # noqa: E402
import ui as fake_ui  # noqa: E402
from fakeobj import FakeObj  # noqa: E402
import controlTypes  # noqa: E402

from appModules import spss  # noqa: E402
from appModules import _spssdata as kb  # noqa: E402


Role = controlTypes.Role


def buildEnglishMainWindow():
	"""A small English-localized SPSS Data Editor with a menu bar and grid."""
	root = FakeObj(Role.WINDOW, u"Untitled1 [DataSet0] - IBM SPSS Statistics Data Editor")

	menubar = FakeObj(Role.MENUBAR, u"Menu Bar")
	fileMenu = FakeObj(Role.MENU, u"File")
	editMenu = FakeObj(Role.MENU, u"Edit")
	analyzeMenu = FakeObj(Role.MENU, u"Analyze")
	compareMeans = FakeObj(Role.MENU, u"Compare Means and Proportions")
	indepTTest = FakeObj(Role.MENUITEM, u"Independent-Samples T Test...")
	analyzeMenu.add(compareMeans)
	compareMeans.add(indepTTest)
	menubar.add(fileMenu, editMenu, analyzeMenu)
	root.add(menubar)

	tabControl = FakeObj(Role.TABCONTROL, u"Data Editor Views")
	overviewTab = FakeObj(Role.TAB, u"Over View")
	dataTab = FakeObj(Role.TAB, u"Data View")
	variableTab = FakeObj(Role.TAB, u"Variable View")
	tabControl.add(overviewTab, dataTab, variableTab)
	root.add(tabControl)

	dataTable = FakeObj(Role.TABLE, u"Data View")
	dataCell = FakeObj(
		Role.CELL, u"", rowNumber=1, columnNumber=1,
		columnHeaderText=u"Age", value=u"34",
	)
	dataTable.add(dataCell)
	root.add(dataTable)

	variableTable = FakeObj(Role.TABLE, u"Variable View")
	typeCell = FakeObj(
		Role.CELL, u"", rowNumber=1, columnNumber=2,
		columnHeaderText=u"Type", rowHeaderText=u"age", value=u"Numeric",
	)
	variableTable.add(typeCell)
	root.add(variableTable)

	return {
		"root": root, "menubar": menubar, "fileMenu": fileMenu,
		"analyzeMenu": analyzeMenu, "compareMeans": compareMeans,
		"indepTTest": indepTTest, "dataTab": dataTab, "variableTab": variableTab,
		"dataCell": dataCell, "typeCell": typeCell,
	}


def buildGreekMainWindow():
	root = FakeObj(Role.WINDOW, u"Δεδομένα1 - Επεξεργαστής δεδομένων IBM SPSS Statistics")
	menubar = FakeObj(Role.MENUBAR, u"Γραμμή μενού")
	fileMenu = FakeObj(Role.MENU, u"Αρχείο")
	editMenu = FakeObj(Role.MENU, u"Επεξεργασία")
	viewMenu = FakeObj(Role.MENU, u"Προβολή")
	dataMenu = FakeObj(Role.MENU, u"Δεδομένα")
	analyzeMenu = FakeObj(Role.MENU, u"Ανάλυση")
	menubar.add(fileMenu, editMenu, viewMenu, dataMenu, analyzeMenu)
	root.add(menubar)
	return {"root": root, "menubar": menubar}


def buildIndependentTTestDialog():
	dialog = FakeObj(Role.DIALOG, u"Independent-Samples T Test")
	testVars = FakeObj(Role.LIST, u"Test Variable(s)")
	groupingVar = FakeObj(Role.LIST, u"Grouping Variable")
	defineGroups = FakeObj(Role.BUTTON, u"Define Groups...")
	estimateEffect = FakeObj(Role.CHECKBOX, u"Estimate effect sizes")
	optionsButton = FakeObj(Role.BUTTON, u"Options...")
	okButton = FakeObj(Role.BUTTON, u"OK")
	dialog.add(testVars, groupingVar, defineGroups, estimateEffect, optionsButton, okButton)
	return dialog, {
		"dialog": dialog, "testVars": testVars, "groupingVar": groupingVar,
		"defineGroups": defineGroups, "estimateEffect": estimateEffect,
		"okButton": okButton,
	}


def buildDocumentedIndependentTTestDialog(versionFamily):
	"""Build title-less dialog variants documented for SPSS 24 through 31.

	The stable controls identify the procedure. Later-release controls are
	intentionally optional so their absence cannot break older SPSS versions.
	"""
	dialog = FakeObj(Role.DIALOG, u"")
	testVars = FakeObj(Role.LIST, u"Test Variable(s)")
	groupingVar = FakeObj(Role.LIST, u"Grouping Variable")
	defineGroups = FakeObj(Role.BUTTON, u"Define Groups...")
	controls = [testVars, groupingVar, defineGroups]
	if versionFamily in (u"27-30", u"31"):
		controls.append(FakeObj(Role.CHECKBOX, u"Estimate effect sizes"))
	if versionFamily == u"31":
		controls.append(FakeObj(Role.CHECKBOX, u"Homogeneity of variance test"))
	controls.extend((
		FakeObj(Role.BUTTON, u"Options..."),
		FakeObj(Role.BUTTON, u"OK"),
		FakeObj(Role.BUTTON, u"Paste"),
	))
	dialog.add(*controls)
	return dialog, controls


def buildGreekIndependentTTestDialog():
	dialog = FakeObj(Role.DIALOG, u"Έλεγχος t ανεξάρτητων δειγμάτων")
	testVars = FakeObj(Role.LIST, u"Μεταβλητές ελέγχου")
	groupingVar = FakeObj(Role.LIST, u"Μεταβλητή ομαδοποίησης")
	defineGroups = FakeObj(Role.BUTTON, u"Define Groups")
	estimateEffect = FakeObj(Role.CHECKBOX, u"Εκτίμηση μεγέθους επίδρασης")
	okButton = FakeObj(Role.BUTTON, u"OK")
	dialog.add(testVars, groupingVar, defineGroups, estimateEffect, okButton)
	return dialog, {
		"dialog": dialog, "testVars": testVars, "groupingVar": groupingVar,
		"defineGroups": defineGroups, "estimateEffect": estimateEffect,
		"okButton": okButton,
	}


class SpssModuleTests(unittest.TestCase):

	def setUp(self):
		fake_ui.reset()
		fake_config.conf["spssAccessibility"]["language"] = "auto"
		fake_api.setFocusObject(None)
		fake_api.setForegroundObject(None)
		self.module = spss.AppModule()

	# -- language resolution -------------------------------------------------

	def test_detects_english_by_default(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EN)

	def test_detects_greek_from_menu_bar(self):
		scene = buildGreekMainWindow()
		fake_api.setForegroundObject(scene["root"])
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EL)

	def test_preserves_detected_language_inside_modal_dialog_without_menu(self):
		scene = buildGreekMainWindow()
		fake_api.setForegroundObject(scene["root"])
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EL)
		dialog, controls = buildIndependentTTestDialog()
		fake_api.setForegroundObject(dialog)
		fake_api.setFocusObject(controls["okButton"])
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EL)

	def test_manual_language_override_wins_over_detection(self):
		scene = buildGreekMainWindow()
		fake_api.setForegroundObject(scene["root"])
		fake_config.conf["spssAccessibility"]["language"] = kb.LANG_EN
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EN)

	def test_cycle_spoken_language_script(self):
		self.assertEqual(self.module._configLanguageOverride(), "auto")
		self.module.script_cycleSpokenLanguage(None)
		self.assertEqual(self.module._configLanguageOverride(), kb.LANG_EN)
		self.module.script_cycleSpokenLanguage(None)
		self.assertEqual(self.module._configLanguageOverride(), kb.LANG_EL)
		self.module.script_cycleSpokenLanguage(None)
		self.assertEqual(self.module._configLanguageOverride(), "auto")
		self.assertEqual(len(fake_ui.messages), 3)

	# -- pane detection --------------------------------------------------------

	def test_detects_data_and_variable_panes(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		self.assertEqual(self.module._detectPaneFromObject(scene["dataCell"]), "data")
		self.assertEqual(self.module._detectPaneFromObject(scene["typeCell"]), "variable")

	def test_spss_24_data_editor_does_not_require_overview_tab(self):
		root = FakeObj(Role.WINDOW, u"IBM SPSS Statistics Data Editor")
		tabs = FakeObj(Role.TABCONTROL, u"Data Editor Views")
		dataTab = FakeObj(Role.TAB, u"Data View")
		variableTab = FakeObj(Role.TAB, u"Variable View")
		tabs.add(dataTab, variableTab)
		root.add(tabs)
		fake_api.setForegroundObject(root)
		self.assertEqual(self.module._detectPaneFromObject(dataTab), "data")
		self.assertEqual(self.module._detectPaneFromObject(variableTab), "variable")

	def test_pane_help_follows_resolved_language(self):
		scene = buildGreekMainWindow()
		fake_api.setForegroundObject(scene["root"])
		helpText = self.module._paneHelp("data")
		self.assertIn(u"Προβολή δεδομένων", helpText)

	# -- menus -------------------------------------------------------------

	def test_focused_menu_item_description_includes_kb_content(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		message = self.module._focusedMenuItemDescription(scene["indepTTest"])
		self.assertIn(u"Analyze > Compare Means and Proportions > Independent-Samples T Test", message)
		self.assertIn(u"independent", message.lower())

	def test_list_menu_items_summary(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		message = self.module._currentMenuItemsSummary(scene["fileMenu"])
		# fileMenu itself has no children in this fixture; test the parent menu bar instead.
		message = self.module._currentMenuItemsSummary(scene["menubar"])
		self.assertIn(u"File", message)
		self.assertIn(u"Analyze", message)

	# -- dialogs -------------------------------------------------------------

	def test_dialog_is_recognised_from_control_labels(self):
		dialog, controls = buildIndependentTTestDialog()
		entry, foundDialog = self.module._currentDialogEntry(controls["defineGroups"])
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")
		self.assertIs(foundDialog, dialog)

	def test_documented_spss_24_through_31_dialog_profiles(self):
		for versionFamily in (u"24-26", u"27-30", u"31"):
			with self.subTest(versionFamily=versionFamily):
				dialog, controls = buildDocumentedIndependentTTestDialog(versionFamily)
				entry, foundDialog = self.module._currentDialogEntry(controls[-2])
				self.assertIsNotNone(entry)
				self.assertEqual(entry["en"], u"Independent-Samples T Test")
				self.assertIs(foundDialog, dialog)

	def test_foreground_modal_dialog_root_is_recognised(self):
		dialog, controls = buildIndependentTTestDialog()
		fake_api.setForegroundObject(dialog)
		fake_api.setFocusObject(controls["okButton"])
		message = self.module._dialogHelp(controls["okButton"])
		self.assertIn(u"Levene", message)

	def test_foreground_window_role_with_known_dialog_title_is_recognised(self):
		dialog, controls = buildIndependentTTestDialog()
		dialog.role = Role.WINDOW
		fake_api.setForegroundObject(dialog)
		fake_api.setFocusObject(controls["okButton"])
		self.assertIs(self.module._dialogObject(controls["okButton"]), dialog)

	def test_main_foreground_window_is_not_treated_as_dialog(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		fake_api.setFocusObject(scene["dataCell"])
		self.assertIsNone(self.module._dialogObject(scene["dataCell"]))

	def test_greek_localized_dialog_is_recognised_by_title_and_controls(self):
		dialog, controls = buildGreekIndependentTTestDialog()
		fake_api.setForegroundObject(dialog)
		fake_api.setFocusObject(controls["okButton"])
		entry, foundDialog = self.module._currentDialogEntry(controls["okButton"])
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")
		self.assertIs(foundDialog, dialog)
		self.assertEqual(self.module._resolveLanguage(), kb.LANG_EL)

	def test_dialog_help_uses_kb_description(self):
		dialog, controls = buildIndependentTTestDialog()
		message = self.module._dialogHelp(controls["okButton"])
		self.assertIn(u"Levene", message)

	def test_describe_control_matches_kb_field(self):
		dialog, controls = buildIndependentTTestDialog()
		message = self.module._describeControl(controls["defineGroups"])
		self.assertIn(u"Define Groups", message)
		self.assertIn(u"sub-dialog", message.lower())

	def test_dialog_structure_summary_lists_every_control(self):
		dialog, controls = buildIndependentTTestDialog()
		message = self.module._dialogStructureSummary(controls["okButton"])
		for label in (u"Test Variable(s)", u"Grouping Variable", u"Define Groups", u"Estimate effect sizes", u"OK"):
			self.assertIn(label, message)

	def test_dialog_structure_summary_in_greek(self):
		dialog, controls = buildIndependentTTestDialog()
		fake_config.conf["spssAccessibility"]["language"] = kb.LANG_EL
		message = self.module._dialogStructureSummary(controls["okButton"])
		self.assertIn(u"Μεταβλητές ελέγχου", message)

	# -- data / variable cells -----------------------------------------------

	def test_describe_data_cell(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		message = self.module._describeCell(scene["dataCell"], preferPane="data")
		self.assertIn(u"Age", message)
		self.assertIn(u"34", message)

	def test_describe_variable_cell_includes_kb_hint(self):
		scene = buildEnglishMainWindow()
		fake_api.setForegroundObject(scene["root"])
		message = self.module._describeCell(scene["typeCell"], preferPane="variable")
		self.assertIn(u"Type", message)
		self.assertIn(u"Variable Type dialog", message)

	# -- glossary and shortcuts ------------------------------------------------

	def test_glossary_script_speaks_both_languages(self):
		self.module.script_readStatisticsGlossary(None)
		self.assertEqual(len(fake_ui.messages), 1)
		message = fake_ui.messages[0]
		self.assertIn(u"Mean", message)
		self.assertIn(u"Μέσος όρος", message)

	def test_shortcuts_list_mentions_new_commands(self):
		self.module.script_listShortcuts(None)
		message = fake_ui.messages[-1]
		self.assertIn(u"Shift+K", message)
		self.assertIn(u"Shift+Q", message)
		self.assertIn(u"Shift+J", message)

	def test_toggle_scripts(self):
		self.assertTrue(self.module._verboseHelp)
		self.module.script_toggleGuidanceVerbosity(None)
		self.assertFalse(self.module._verboseHelp)
		self.assertFalse(self.module._announceTableMovement)
		self.module.script_toggleAutomaticTableAnnouncements(None)
		self.assertTrue(self.module._announceTableMovement)


if __name__ == "__main__":
	unittest.main()
