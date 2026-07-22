# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Offline integrity tests for the addon/appModules/_spssdata knowledge base.

These tests have no NVDA dependency at all: they only import the plain-Python
_spssdata package and check that every bilingual record is actually
bilingual, that lookups resolve sensibly, and that the tree has no obviously
broken entries. Run with:

    python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_ADDON = os.path.join(_REPO_ROOT, "addon", "appModules")

if _ADDON not in sys.path:
	sys.path.insert(0, _ADDON)

import _spssdata as kb  # noqa: E402


def _walk(entries):
	for entry in entries:
		yield entry
		children = entry.get("children") or ()
		if children:
			for descendant in _walk(children):
				yield descendant


class KnowledgeBaseIntegrityTests(unittest.TestCase):

	def test_every_menu_entry_is_bilingual(self):
		for entry in _walk(kb.menus.MENUS):
			self.assertTrue(entry["en"], "Menu entry missing English label: %r" % entry)
			self.assertTrue(entry["el"], "Menu entry missing Greek label for %r" % entry["en"])
			self.assertTrue(entry["desc"][kb.LANG_EN], "Menu entry missing English description: %r" % entry["en"])
			self.assertTrue(entry["desc"][kb.LANG_EL], "Menu entry missing Greek description: %r" % entry["en"])

	def test_every_dialog_entry_is_bilingual(self):
		for entry in _walk(kb.dialogs.DIALOGS):
			self.assertTrue(entry["en"], "Dialog entry missing English label: %r" % entry)
			self.assertTrue(entry["el"], "Dialog entry missing Greek label for %r" % entry["en"])
			self.assertTrue(entry["desc"][kb.LANG_EN], "Dialog entry missing English description: %r" % entry["en"])
			self.assertTrue(entry["desc"][kb.LANG_EL], "Dialog entry missing Greek description: %r" % entry["en"])

	def test_every_glossary_term_is_bilingual(self):
		for entry in kb.terms.GLOSSARY:
			self.assertTrue(entry["en"])
			self.assertTrue(entry["el"])
			self.assertTrue(entry["desc"][kb.LANG_EN])
			self.assertTrue(entry["desc"][kb.LANG_EL])

	def test_every_pane_has_help_and_brief_in_both_languages(self):
		for paneKey in kb.panes.PANE_ORDER:
			helpPair = kb.panes.PANE_HELP[paneKey]
			briefPair = kb.panes.PANE_BRIEF[paneKey]
			namePair = kb.panes.PANE_NAMES[paneKey]
			for pair, label in ((helpPair, "help"), (briefPair, "brief"), (namePair, "name")):
				self.assertTrue(pair[0], "%s missing English text for pane %s" % (label, paneKey))
				self.assertTrue(pair[1], "%s missing Greek text for pane %s" % (label, paneKey))

	def test_every_variable_column_is_documented(self):
		for column in kb.panes.VARIABLE_COLUMNS:
			self.assertIn(column, kb.panes.VARIABLE_COLUMN_LABELS)
			self.assertIn(column, kb.panes.VARIABLE_COLUMN_HELP)
			labelPair = kb.panes.VARIABLE_COLUMN_LABELS[column]
			helpPair = kb.panes.VARIABLE_COLUMN_HELP[column]
			self.assertTrue(labelPair[0] and labelPair[1])
			self.assertTrue(helpPair[0] and helpPair[1])

	def test_dialog_tokens_reference_real_dialogs(self):
		dialogNames = {entry["en"] for entry in kb.dialogs.DIALOGS}
		for dialogName, tokens in kb.dialogs.DIALOG_TOKENS.items():
			self.assertIn(dialogName, dialogNames, "DIALOG_TOKENS references unknown dialog %r" % dialogName)
			self.assertTrue(tokens, "DIALOG_TOKENS entry for %r has no tokens" % dialogName)

	def test_every_documented_dialog_signature_round_trips(self):
		for dialogName, tokens in kb.dialogs.DIALOG_TOKENS.items():
			with self.subTest(dialog=dialogName):
				entry = kb.findDialogByTokens(u" ".join(tokens))
				self.assertIsNotNone(entry)
				self.assertEqual(entry["en"], dialogName)

	def test_find_menu_item_resolves_nested_procedure(self):
		entry, path = kb.findMenuItem(
			u"Independent-Samples T Test",
			parents=(u"Analyze", u"Compare Means and Proportions"),
		)
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")
		self.assertEqual([item["en"] for item in path], [u"Analyze", u"Compare Means and Proportions"])

	def test_find_menu_item_accepts_spss_24_compare_means_parent(self):
		entry, path = kb.findMenuItem(
			u"Independent-Samples T Test...",
			parents=(u"Analyze", u"Compare Means"),
		)
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")
		self.assertEqual(path[-1]["en"], u"Compare Means and Proportions")

	def test_lookup_parent_scoring_includes_version_aliases(self):
		legacyParent = kb.core.node(u"Modern Parent", u"Σύγχρονος γονέας", aliases=(u"Legacy Parent",), children=(
			kb.core.node(u"Shared Item", u"Κοινό στοιχείο", enDesc=u"legacy-compatible"),
		))
		otherParent = kb.core.node(u"Other Parent", u"Άλλος γονέας", children=(
			kb.core.node(u"Shared Item", u"Κοινό στοιχείο", enDesc=u"other"),
		))
		index = kb.buildIndex((otherParent, legacyParent))
		entry, path = kb.lookup(index, u"Shared Item", parents=(u"Legacy Parent",))
		self.assertEqual(entry["desc"][kb.LANG_EN], u"legacy-compatible")
		self.assertEqual(path[-1]["en"], u"Modern Parent")

	def test_find_menu_item_resolves_from_greek_label(self):
		entry, _path = kb.findMenuItem(u"Ανεξάρτητα δείγματα")
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent Samples")

	def test_find_dialog_control_prefers_matching_parent(self):
		entry, path = kb.findDialogControl(u"Options", parents=(u"One-Sample T Test",))
		self.assertIsNotNone(entry)
		self.assertEqual(path[-1]["en"], u"One-Sample T Test")

	def test_find_dialog_by_tokens_identifies_independent_samples_t_test(self):
		text = u"test variable(s) grouping variable define groups estimate effect sizes homogeneity of variance test"
		entry = kb.findDialogByTokens(text)
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")

	def test_spss_24_signature_does_not_require_newer_optional_controls(self):
		entry = kb.findDialogByTokens(u"test variable(s) grouping variable define groups options")
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")

	def test_find_dialog_by_greek_title(self):
		entry = kb.findDialogByTitle(u"Έλεγχος t ανεξάρτητων δειγμάτων")
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")

	def test_find_dialog_by_greek_control_tokens(self):
		text = kb.normalize(
			u"Μεταβλητές ελέγχου Μεταβλητή ομαδοποίησης Define Groups "
			u"Εκτίμηση μεγέθους επίδρασης"
		)
		entry = kb.findDialogByTokens(text)
		self.assertIsNotNone(entry)
		self.assertEqual(entry["en"], u"Independent-Samples T Test")

	def test_generic_single_token_does_not_misidentify_dialog(self):
		self.assertIsNone(kb.findDialogByTokens(u"factor"))
		self.assertIsNone(kb.findDialogByTokens(u"dependent"))

	def test_find_glossary_term_by_either_language(self):
		self.assertEqual(kb.findGlossaryTerm(u"Mean")["en"], u"Mean")
		self.assertEqual(kb.findGlossaryTerm(u"Μέσος όρος")["en"], u"Mean")

	def test_pick_prefers_greek_and_falls_back_to_english(self):
		self.assertEqual(kb.pick((u"Hello", u"Γεια"), kb.LANG_EL), u"Γεια")
		self.assertEqual(kb.pick((u"Hello", u""), kb.LANG_EL), u"Hello")
		self.assertEqual(kb.pick((u"Hello", u"Γεια"), kb.LANG_EN), u"Hello")

	def test_normalize_strips_accents_and_mnemonics(self):
		self.assertEqual(kb.normalize(u"Επισκόπηση"), kb.normalize(u"επισκοπηση"))
		self.assertEqual(kb.normalize(u"&Save As..."), kb.normalize(u"Save As"))


if __name__ == "__main__":
	unittest.main()
