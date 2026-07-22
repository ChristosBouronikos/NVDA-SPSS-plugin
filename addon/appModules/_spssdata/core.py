# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin - knowledge base core helpers
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
#
# Copyright (C) 2026 Bouronikos Christos
# This file is covered by the GNU General Public License v2.
# =============================================================================

"""Shared record format, text normalisation, and lookup helpers.

Every description that the add-on speaks about IBM SPSS Statistics is stored in
this package as a bilingual record, so the spoken language can follow the SPSS
interface language (or an explicit user choice) instead of the NVDA interface
language. Records are plain dictionaries created by :func:`node` to keep the
data modules compact and easy to translate.
"""

import re
import unicodedata

LANG_EN = "en"
LANG_EL = "el"
LANGUAGES = (LANG_EN, LANG_EL)

_WHITESPACE = re.compile(r"\s+")
_ACCELERATOR = re.compile(r"\(&\w\)")
_TRAILING_PUNCTUATION = re.compile(r"[\s.:…>]+$")
_SHORTCUT_SUFFIX = re.compile(r"\t.*$")


def node(en, el, enDesc="", elDesc="", keys="", kind="", children=(), aliases=()):
	"""Create one bilingual knowledge-base record.

	:param en: the English label exactly as SPSS shows it.
	:param el: the Greek label or translation of the label.
	:param enDesc: English description of what the item does.
	:param elDesc: Greek description of what the item does.
	:param keys: documented keyboard shortcut, empty when unknown.
	:param kind: control kind key from :data:`KIND_LABELS`.
	:param children: nested records, for example submenu items.
	:param aliases: extra labels that should match this record.
	"""
	return {
		"en": en,
		"el": el,
		"desc": {LANG_EN: enDesc, LANG_EL: elDesc},
		"keys": keys,
		"kind": kind,
		"children": tuple(children),
		"aliases": tuple(aliases),
	}


KIND_LABELS = {
	"menu": (u"menu", u"μενού"),
	"submenu": (u"submenu", u"υπομενού"),
	"menuitem": (u"menu item", u"στοιχείο μενού"),
	"button": (u"button", u"κουμπί"),
	"subdialog": (u"button that opens a sub-dialog", u"κουμπί που ανοίγει υποδιάλογο"),
	"checkbox": (u"check box", u"πλαίσιο ελέγχου"),
	"radio": (u"radio button", u"κουμπί επιλογής"),
	"edit": (u"text box", u"πλαίσιο κειμένου"),
	"spin": (u"number box", u"αριθμητικό πλαίσιο"),
	"combo": (u"drop-down list", u"αναπτυσσόμενη λίστα"),
	"sourcelist": (u"source variable list", u"λίστα μεταβλητών προέλευσης"),
	"targetlist": (u"target variable list", u"λίστα μεταβλητών προορισμού"),
	"list": (u"list", u"λίστα"),
	"group": (u"group of options", u"ομάδα επιλογών"),
	"tab": (u"tab", u"καρτέλα"),
	"table": (u"table", u"πίνακας"),
	"tree": (u"tree view", u"δέντρο"),
	"pane": (u"pane", u"περιοχή"),
	"toolbar": (u"toolbar button", u"κουμπί γραμμής εργαλείων"),
	"dialog": (u"dialog", u"διάλογος"),
	"wizard": (u"wizard", u"οδηγός"),
}

# Short guidance spoken after a control kind, so a new user knows what to press.
KIND_ACTIONS = {
	"button": (
		u"Press Space or Enter to activate it.",
		u"Πατήστε Space ή Enter για ενεργοποίηση.",
	),
	"subdialog": (
		u"Press Space to open the sub-dialog, set the options, then choose Continue to return.",
		u"Πατήστε Space για να ανοίξει ο υποδιάλογος, ορίστε τις επιλογές και μετά επιλέξτε Continue για επιστροφή.",
	),
	"checkbox": (
		u"Press Space to select or clear it.",
		u"Πατήστε Space για επιλογή ή αποεπιλογή.",
	),
	"radio": (
		u"Use the arrow keys to move between the options in this group.",
		u"Χρησιμοποιήστε τα βέλη για να μετακινηθείτε ανάμεσα στις επιλογές της ομάδας.",
	),
	"edit": (
		u"Type a value.",
		u"Πληκτρολογήστε μια τιμή.",
	),
	"spin": (
		u"Type a number, or use the up and down arrows to change it.",
		u"Πληκτρολογήστε αριθμό ή αλλάξτε τον με τα πάνω και κάτω βέλη.",
	),
	"combo": (
		u"Press Alt+Down Arrow to open the list, then the arrow keys to choose.",
		u"Πατήστε Alt+Κάτω βέλος για να ανοίξει η λίστα και μετά τα βέλη για επιλογή.",
	),
	"sourcelist": (
		u"Use the arrow keys to move through the variables, Control+click or Shift+arrows for several, then press the arrow button to move them to the target list.",
		u"Χρησιμοποιήστε τα βέλη για μετακίνηση στις μεταβλητές, Control+κλικ ή Shift+βέλη για πολλές, και μετά το κουμπί βέλους για μεταφορά στη λίστα προορισμού.",
	),
	"targetlist": (
		u"This list holds the variables the procedure will use. Select a variable and press the arrow button to send it back.",
		u"Η λίστα περιέχει τις μεταβλητές που θα χρησιμοποιήσει η διαδικασία. Επιλέξτε μεταβλητή και πατήστε το κουμπί βέλους για να την επιστρέψετε.",
	),
	"list": (
		u"Use the arrow keys to move through the items.",
		u"Χρησιμοποιήστε τα βέλη για μετακίνηση στα στοιχεία.",
	),
	"tab": (
		u"Use Control+Tab or the arrow keys to move between tabs.",
		u"Χρησιμοποιήστε Control+Tab ή τα βέλη για μετακίνηση ανάμεσα στις καρτέλες.",
	),
	"menuitem": (
		u"Press Enter to run it.",
		u"Πατήστε Enter για εκτέλεση.",
	),
	"submenu": (
		u"Press Right Arrow or Enter to open the submenu.",
		u"Πατήστε Δεξί βέλος ή Enter για να ανοίξει το υπομενού.",
	),
}


def label(entry, lang=LANG_EN):
	"""Return the label of a record in the requested language."""
	if not entry:
		return u""
	return entry.get(lang) or entry.get(LANG_EN) or u""


def describe(entry, lang=LANG_EN):
	"""Return the description of a record in the requested language."""
	if not entry:
		return u""
	descriptions = entry.get("desc") or {}
	return descriptions.get(lang) or descriptions.get(LANG_EN) or u""


def pick(pair, lang=LANG_EN):
	"""Pick the right value from a plain ``(english, greek)`` tuple.

	Several smaller tables in this package (pane help text, output item
	kinds) are stored as plain two-item tuples instead of full :func:`node`
	records, since they need no keys, kind, or children. This helper reads
	them the same way :func:`label`/:func:`describe` read a record.
	"""
	if not pair:
		return u""
	if lang == LANG_EL and len(pair) > 1 and pair[1]:
		return pair[1]
	return pair[0] if pair else u""


def kindLabel(kind, lang=LANG_EN):
	"""Return the readable name of a control kind."""
	pair = KIND_LABELS.get(kind)
	if not pair:
		return u""
	return pair[1] if lang == LANG_EL else pair[0]


def kindAction(kind, lang=LANG_EN):
	"""Return the how-to-use hint for a control kind."""
	pair = KIND_ACTIONS.get(kind)
	if not pair:
		return u""
	return pair[1] if lang == LANG_EL else pair[0]


def stripAccents(text):
	"""Remove Greek and Latin accents so lookups are accent insensitive."""
	try:
		decomposed = unicodedata.normalize("NFD", text)
	except Exception:
		return text
	return u"".join(char for char in decomposed if not unicodedata.combining(char))


def normalize(text):
	"""Normalise an SPSS label so it can be used as a lookup key."""
	if text is None:
		return u""
	try:
		text = u"%s" % text
	except Exception:
		return u""
	text = _SHORTCUT_SUFFIX.sub(u"", text)
	text = _ACCELERATOR.sub(u"", text)
	text = text.replace(u"&", u"")
	text = _WHITESPACE.sub(u" ", text).strip()
	text = _TRAILING_PUNCTUATION.sub(u"", text)
	text = stripAccents(text).lower()
	return text


def labelKeys(entry):
	"""Yield every normalised label that should match a record."""
	seen = set()
	for value in (entry.get("en"), entry.get("el")) + tuple(entry.get("aliases", ())):
		key = normalize(value)
		if key and key not in seen:
			seen.add(key)
			yield key


def buildIndex(entries, path=(), index=None):
	"""Build a normalised label index over a tree of records.

	The index maps a normalised label to a list of ``(entry, path)`` pairs,
	where ``path`` is the tuple of ancestor records.
	"""
	if index is None:
		index = {}
	for entry in entries:
		for key in labelKeys(entry):
			index.setdefault(key, []).append((entry, path))
		children = entry.get("children") or ()
		if children:
			buildIndex(children, path + (entry,), index)
	return index


def lookup(index, text, parents=()):
	"""Find the best record for a label, preferring a matching parent path.

	:param index: an index built by :func:`buildIndex`.
	:param text: the label reported by SPSS.
	:param parents: labels of ancestor menus or dialogs, outermost first.
	"""
	key = normalize(text)
	if not key:
		return None, ()
	matches = index.get(key)
	if not matches:
		matches = _partialMatches(index, key)
	if not matches:
		return None, ()
	if len(matches) == 1 or not parents:
		return matches[0]
	parentKeys = [normalize(parent) for parent in parents if normalize(parent)]
	best = matches[0]
	bestScore = -1
	for entry, path in matches:
		# Include aliases when scoring the parent path. This matters across SPSS
		# versions: for example, the older "Compare Means" submenu is an alias
		# of the newer "Compare Means and Proportions" record.
		pathKeys = [key for item in path for key in labelKeys(item)]
		score = sum(1 for parentKey in parentKeys if parentKey in pathKeys)
		if score > bestScore:
			bestScore = score
			best = (entry, path)
	return best


def _partialMatches(index, key):
	"""Fall back to a containment match for labels SPSS decorates."""
	if len(key) < 4:
		return []
	candidates = []
	for indexKey, matches in index.items():
		if len(indexKey) < 4:
			continue
		if indexKey == key or indexKey in key or key in indexKey:
			candidates.extend(matches)
	if not candidates:
		return []
	candidates.sort(key=lambda match: -len(normalize(label(match[0], LANG_EN))))
	return candidates[:1]


def findAll(index, text):
	"""Return every record whose label matches, for ambiguous lookups."""
	key = normalize(text)
	if not key:
		return []
	return list(index.get(key, ()))


def joinParts(parts, separator=u". "):
	"""Join non-empty, non-duplicated fragments into one spoken message."""
	seen = set()
	output = []
	for part in parts:
		if not part:
			continue
		part = _WHITESPACE.sub(u" ", u"%s" % part).strip()
		if not part:
			continue
		key = part.lower()
		if key in seen:
			continue
		seen.add(key)
		output.append(part)
	return separator.join(output)


def entryPathText(path, entry, lang=LANG_EN):
	"""Return a readable ``Menu > Submenu > Item`` style path."""
	names = [label(item, lang) for item in path]
	names.append(label(entry, lang))
	return u" > ".join(name for name in names if name)
