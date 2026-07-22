# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's controlTypes module, for offline unit tests."""


class _Symbol(object):
	"""A fake Role or State value with a displayString, like NVDA's real enums."""

	def __init__(self, name):
		self._name = name
		self.displayString = name.capitalize()

	def __repr__(self):
		return "<%s>" % self._name

	def __hash__(self):
		return hash(self._name)

	def __eq__(self, other):
		return self is other


_ROLE_NAMES = (
	"BUTTON", "MENUITEM", "MENUBAR", "MENU", "TAB", "TABCONTROL", "TABLE",
	"ROW", "CELL", "COLUMNHEADER", "ROWHEADER", "DOCUMENT", "PANE",
	"TREEVIEW", "TREEVIEWITEM", "LIST", "LISTITEM", "EDITABLETEXT",
	"STATICTEXT", "CHECKBOX", "RADIOBUTTON", "COMBOBOX", "GROUPING",
	"DIALOG", "WINDOW", "APPLICATION", "UNKNOWN",
)

_STATE_NAMES = ("SELECTED", "FOCUSED", "EXPANDED", "COLLAPSED")


class Role(object):
	pass


class State(object):
	pass


for _name in _ROLE_NAMES:
	setattr(Role, _name, _Symbol(_name))

for _name in _STATE_NAMES:
	setattr(State, _name, _Symbol(_name))
