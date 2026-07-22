# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""A minimal fake NVDA object tree, for offline unit tests.

Supports exactly the attributes and linked-list child traversal
(``simpleFirstChild``/``simpleNext``) that ``appModules.spss`` relies on, so
the app module's real traversal code (``_children``, ``_ancestors``,
``_iterObjects``) can run unmodified against a hand-built SPSS-like UI tree.
"""


class FakeObj(object):

	def __init__(self, role, name="", **kwargs):
		self.role = role
		self.name = name
		self.description = kwargs.pop("description", "")
		self.value = kwargs.pop("value", "")
		self.helpText = kwargs.pop("helpText", "")
		self.valueLabel = kwargs.pop("valueLabel", "")
		self.UIAAutomationId = kwargs.pop("UIAAutomationId", "")
		self.windowClassName = kwargs.pop("windowClassName", "")
		self.rowNumber = kwargs.pop("rowNumber", None)
		self.columnNumber = kwargs.pop("columnNumber", None)
		self.rowHeaderText = kwargs.pop("rowHeaderText", "")
		self.columnHeaderText = kwargs.pop("columnHeaderText", "")
		self.rowHeaderTexts = kwargs.pop("rowHeaderTexts", None)
		self.columnHeaderTexts = kwargs.pop("columnHeaderTexts", None)
		self.rowCount = kwargs.pop("rowCount", None)
		self.columnCount = kwargs.pop("columnCount", None)
		self.states = kwargs.pop("states", frozenset())
		self.level = kwargs.pop("level", None)
		self.positionInfo = kwargs.pop("positionInfo", None)
		self.displayText = kwargs.pop("displayText", "")
		if kwargs:
			raise TypeError("Unexpected FakeObj kwargs: %r" % (list(kwargs),))
		self.parent = None
		self._children = []
		self.simpleFirstChild = None
		self.simpleNext = None

	def add(self, *children):
		for child in children:
			child.parent = self
			self._children.append(child)
		self._relink()
		return self

	def _relink(self):
		self.simpleFirstChild = self._children[0] if self._children else None
		for index, child in enumerate(self._children):
			child.simpleNext = self._children[index + 1] if index + 1 < len(self._children) else None

	@property
	def children(self):
		return list(self._children)

	def setFocus(self):
		return True

	def doAction(self):
		return True

	def __repr__(self):
		roleName = getattr(self.role, "_name", self.role)
		return "<FakeObj %s %r>" % (roleName, self.name)
