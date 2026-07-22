# -*- coding: utf-8 -*-
"""Offline tests for the SPSS Accessibility helper global plugin."""

import os
import sys
import types
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_STUBS = os.path.join(_HERE, "nvdastubs")
_ADDON = os.path.join(_REPO_ROOT, "addon")

for path in (_STUBS, _ADDON):
	if path not in sys.path:
		sys.path.insert(0, path)

import appModuleHandler as fakeAppModuleHandler  # noqa: E402
import config as fakeConfig  # noqa: E402
from globalPlugins import spssAccessibilityHelper as helper  # noqa: E402


class _Choice(object):

	def __init__(self, choices=()):
		self.choices = list(choices)
		self.selection = -1

	def SetSelection(self, selection):
		self.selection = selection

	def GetSelection(self):
		return self.selection


class _StaticText(object):

	def __init__(self, parent, label=""):
		self.parent = parent
		self.label = label


class _BoxSizerHelper(object):

	def __init__(self, parent, sizer=None):
		self.parent = parent
		self.sizer = sizer

	def addLabeledControl(self, label, controlClass, choices=()):
		return controlClass(choices=choices)

	def addItem(self, item):
		return item


class GlobalPluginTests(unittest.TestCase):

	def setUp(self):
		fakeAppModuleHandler.resetRegistrations()
		fakeConfig.conf["spssAccessibility"]["language"] = "auto"

	def test_registers_and_unregisters_current_nvda_executable_mapping(self):
		plugin = helper.GlobalPlugin()
		self.assertEqual(
			fakeAppModuleHandler.registeredExecutables,
			{executable: "spss" for executable in helper.SPSS_EXECUTABLES},
		)
		self.assertIn("spssAccessibility", fakeConfig.conf.spec)
		plugin.terminate()
		self.assertEqual(fakeAppModuleHandler.registeredExecutables, {})

	def test_settings_panel_loads_and_saves_language(self):
		oldModules = {name: sys.modules.get(name) for name in ("gui", "gui.settingsDialogs", "wx")}
		gui = types.ModuleType("gui")
		settingsDialogs = types.ModuleType("gui.settingsDialogs")
		wx = types.ModuleType("wx")

		class SettingsPanel(object):
			pass

		settingsDialogs.SettingsPanel = SettingsPanel
		settingsDialogs.NVDASettingsDialog = type(
			"NVDASettingsDialog",
			(),
			{"categoryClasses": []},
		)
		gui.settingsDialogs = settingsDialogs
		gui.guiHelper = types.SimpleNamespace(BoxSizerHelper=_BoxSizerHelper)
		wx.Choice = _Choice
		wx.StaticText = _StaticText

		try:
			sys.modules["gui"] = gui
			sys.modules["gui.settingsDialogs"] = settingsDialogs
			sys.modules["wx"] = wx
			fakeConfig.conf["spssAccessibility"]["language"] = "en"
			panelClass = helper._buildSettingsPanelClass()
			panel = panelClass()
			panel.makeSettings(object())
			self.assertEqual(panel.languageList.GetSelection(), 1)
			panel.languageList.SetSelection(2)
			panel.onSave()
			self.assertEqual(fakeConfig.conf["spssAccessibility"]["language"], "el")
		finally:
			for name, oldModule in oldModules.items():
				if oldModule is None:
					sys.modules.pop(name, None)
				else:
					sys.modules[name] = oldModule


if __name__ == "__main__":
	unittest.main()
