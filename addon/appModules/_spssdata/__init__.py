# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin - bilingual SPSS knowledge base package
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Bouronikos Christos
# This file is covered by the GNU General Public License v2.
# =============================================================================

"""Bilingual (English/Greek) knowledge base of IBM SPSS Statistics 24–31.

This package holds structured, translated descriptions of the SPSS menu bar
(:mod:`.menus`), the Data Editor/Viewer/Syntax Editor panes and their
controls (:mod:`.panes`), the statistical procedure dialogs and their
sub-dialogs (:mod:`.dialogs`), and a plain-language statistics glossary
(:mod:`.terms`). :mod:`.core` provides the shared record format and lookup
helpers used by the app module (``appModules/spss.py``) to identify what is
under focus and speak a description in the language the add-on is currently
using.

The data is grounded in IBM's SPSS Statistics 24, 27, 30, and 31 Core System,
Base, accessibility, and release documentation (Data Editor, Viewer, Pivot
Tables, Command Syntax, T Tests, One-Way ANOVA, Frequencies, Descriptives,
Explore, Crosstabs, Correlate, Regression, Reliability Analysis, and
Nonparametric Tests chapters). Recognition uses controls that remain stable
across releases and treats controls introduced in later versions as optional.
"""

from . import core
from .core import (
	LANG_EN, LANG_EL, LANGUAGES,
	label, describe, kindLabel, kindAction, pick,
	normalize, buildIndex, lookup, findAll, joinParts, entryPathText,
)
from . import menus
from . import panes
from . import dialogs
from . import terms


# Build a single searchable index over every menu, submenu, and menu item so
# a menu path lookup works regardless of which menu bar (Data Editor, Viewer,
# Syntax Editor, Pivot Table Editor) is focused.
MENU_INDEX = buildIndex(menus.MENUS)

# A separate index over dialog fields/buttons, keyed by dialog so control
# lookups can prefer the dialog currently on screen.
DIALOG_INDEX = buildIndex(dialogs.DIALOGS)

# Index only the dialogs themselves (not their child controls) by title.  This
# is deliberately separate from DIALOG_INDEX: a button named "Options" must
# never be mistaken for the title of a dialog.
DIALOG_TITLE_INDEX = {}
for _dialogEntry in dialogs.DIALOGS:
	for _key in core.labelKeys(_dialogEntry):
		DIALOG_TITLE_INDEX.setdefault(_key, []).append((_dialogEntry, ()))

GLOSSARY_INDEX = buildIndex(terms.GLOSSARY)


def findMenuItem(text, parents=()):
	"""Look up a menu or menu item by its SPSS label."""
	return lookup(MENU_INDEX, text, parents)


def findDialogControl(text, parents=()):
	"""Look up a dialog field or button by its SPSS label."""
	return lookup(DIALOG_INDEX, text, parents)


def findDialogByTitle(text):
	"""Look up a dialog from its English or Greek window title."""
	return lookup(DIALOG_TITLE_INDEX, text)[0]


def _dialogTokenMatches(dialogName, token, searchText):
	"""Match a fallback token plus any bilingual KB label it identifies."""
	alternatives = {normalize(token)}
	fieldEntry, _path = findDialogControl(token, parents=(dialogName,))
	if fieldEntry:
		alternatives.update(normalize(value) for value in (
			fieldEntry.get(LANG_EN),
			fieldEntry.get(LANG_EL),
		) if value)
	return any(value and value in searchText for value in alternatives)


def findDialogByTokens(searchText, titleText=u""):
	"""Identify which known dialog is on screen from its accessible text.

	:param searchText: normalised, lower-case text gathered from the dialog
		and its descendants (name, description, control labels).
	:param titleText: optional dialog title. Exact bilingual title recognition
		is preferred over heuristic control-token matching.
	:returns: the best matching dialog record, or ``None``.
	"""
	if titleText:
		entry = findDialogByTitle(titleText)
		if entry:
			return entry
	searchText = normalize(searchText)
	best = None
	bestScore = 0
	for dialogName, tokens in dialogs.DIALOG_TOKENS.items():
		hits = sum(1 for token in tokens if _dialogTokenMatches(dialogName, token, searchText))
		# Multi-token signatures must match at least two controls. This prevents
		# generic labels such as "Factor" or "Dependent" from identifying a
		# completely unrelated dialog. Single-token signatures are retained only
		# for controls intentionally chosen to be distinctive.
		minimumHits = 1 if len(tokens) == 1 else 2
		if hits < minimumHits:
			continue
		if hits > bestScore:
			bestScore = hits
			best = dialogName
	if not best:
		return None
	for entry in dialogs.DIALOGS:
		if entry["en"] == best:
			return entry
	return None


def findGlossaryTerm(text):
	"""Look up a glossary term by its English or Greek name."""
	matches = findAll(GLOSSARY_INDEX, text)
	if not matches:
		return None
	return matches[0][0]
