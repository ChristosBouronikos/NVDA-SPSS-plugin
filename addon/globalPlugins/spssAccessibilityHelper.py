# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin Helper Global Plugin for NVDA
# Version: 1.2.0
#
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
# =============================================================================

"""
Registers the SPSS app module for common executable names, and adds an
"SPSS Accessibility" category to NVDA's settings dialog for choosing the
spoken language used for SPSS content.

Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com.
GitHub: https://github.com/ChristosBouronikos.
If this add-on helps you, please consider a kind donation via PayPal:
https://paypal.me/christosbouronikos

NVDA normally loads an app module from addon/appModules/<processName>.py. IBM
SPSS Statistics has used more than one process name across releases, so the
explicit registrations below improve compatibility. Alias appModule files are
also included as a fallback for NVDA builds without a public registration API.

The settings panel controls one value, config.conf["spssAccessibility"]
["language"] ("auto", "en", or "el"), that the app module reads through
AppModule._resolveLanguage(). The same value can also be cycled from SPSS
itself with NVDA+Control+Alt+Shift+J. Registration is wrapped in try/except
throughout so a settings-API mismatch on an older or newer NVDA release
degrades to "no settings panel" instead of a load failure; app module
registration, the part users actually depend on, still happens either way.
"""

import addonHandler
import appModuleHandler
import config
import globalPluginHandler
from logHandler import log


addonHandler.initTranslation()


# Process names (without .exe) that IBM SPSS Statistics has used across releases.
SPSS_EXECUTABLES = (
	"stats",  # stats.exe: the main IBM SPSS Statistics process in modern releases (roughly version 21 onward, including SPSS Statistics 31).
	"spss",  # spss.exe: the main process name used by older SPSS releases before the IBM-era rename.
	"spsswin",  # spsswin.exe: the main process name of early SPSS for Windows releases.
	"spssprod",  # spssprod.exe: the SPSS Production Facility component for running unattended production jobs.
)

CONFIG_SPEC = {
	# "auto" follows the language detected from the visible SPSS menu bar;
	# "en"/"el" pin the spoken SPSS content language regardless of detection.
	"language": 'string(default="auto")',
}


def _registerConfigSpec():
	try:
		config.conf.spec["spssAccessibility"] = CONFIG_SPEC
	except Exception as e:
		log.debugWarning("Could not register SPSS Accessibility config spec: %s" % e)


def _buildSettingsPanelClass():
	"""Build the settings panel class lazily, importing gui/wx only if present."""
	try:
		import gui
		import wx
		from gui.settingsDialogs import SettingsPanel
	except Exception as e:
		log.debugWarning("SPSS Accessibility settings panel unavailable: %s" % e)
		return None

	class SPSSAccessibilitySettingsPanel(SettingsPanel):
		title = _("SPSS Accessibility")

		_languageChoices = (
			(_("Automatic (follow the SPSS interface language)"), "auto"),
			(_("English"), "en"),
			(_("Greek"), "el"),
		)

		def makeSettings(self, settingsSizer):
			helper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
			self.languageList = helper.addLabeledControl(
				_("Spoken &language for SPSS menu, dialog, and pane descriptions:"),
				wx.Choice,
				choices=[label for label, value in self._languageChoices],
			)
			currentValue = self._currentLanguageValue()
			selectedIndex = 0
			for index, (_label, value) in enumerate(self._languageChoices):
				if value == currentValue:
					selectedIndex = index
					break
			self.languageList.SetSelection(selectedIndex)
			helper.addItem(
				wx.StaticText(
					self,
					label=_(
						"This only changes the language used to describe what SPSS menus, "
						"dialogs, and Data Editor areas mean. NVDA's own messages, such as "
						"shortcut lists and error announcements, keep following NVDA's "
						"interface language."
					),
				)
			)

		def _currentLanguageValue(self):
			try:
				value = config.conf["spssAccessibility"]["language"]
			except Exception:
				return "auto"
			return value if value in ("auto", "en", "el") else "auto"

		def onSave(self):
			try:
				index = self.languageList.GetSelection()
				config.conf["spssAccessibility"]["language"] = self._languageChoices[index][1]
			except Exception as e:
				log.debugWarning("Could not save SPSS Accessibility language setting: %s" % e)

	return SPSSAccessibilitySettingsPanel


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global helper for IBM SPSS Statistics accessibility app-module loading."""

	def __init__(self):
		super().__init__()
		_registerConfigSpec()
		self._settingsPanelClass = None
		self._registeredExecutables = []
		self._registerSettingsPanel()
		self._registerSpssVariants()

	def terminate(self):
		self._unregisterSpssVariants()
		self._unregisterSettingsPanel()
		super().terminate()

	def _registerSettingsPanel(self):
		try:
			import gui  # noqa: F401
		except Exception as e:
			log.debugWarning("Could not import gui for SPSS Accessibility settings panel: %s" % e)
			return
		panelClass = _buildSettingsPanelClass()
		if panelClass is None:
			return
		try:
			import gui
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(panelClass)
			self._settingsPanelClass = panelClass
			log.debug("Registered SPSS Accessibility settings panel")
		except Exception as e:
			log.debugWarning("Could not register SPSS Accessibility settings panel: %s" % e)

	def _unregisterSettingsPanel(self):
		if self._settingsPanelClass is None:
			return
		try:
			import gui
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(self._settingsPanelClass)
		except Exception as e:
			log.debugWarning("Could not unregister SPSS Accessibility settings panel: %s" % e)
		self._settingsPanelClass = None

	def _registerSpssVariants(self):
		try:
			from appModules import spss
		except Exception as e:
			log.debugWarning("Could not import SPSS accessibility app module: %s" % e)
			return
		register = getattr(appModuleHandler, "registerExecutableWithAppModule", None)
		if not callable(register):
			log.debug("No registerExecutableWithAppModule API; SPSS aliases will be used")
			return
		for exeName in SPSS_EXECUTABLES:
			try:
				# NVDA's registration API accepts the executable name and the
				# app-module module name, not the AppModule class itself.
				register(exeName, "spss")
				self._registeredExecutables.append(exeName)
			except Exception as e:
				log.debug("Could not register SPSS app module for %s: %s" % (exeName, e))
		log.debug("Registered IBM SPSS Statistics app module variants")

	def _unregisterSpssVariants(self):
		unregister = getattr(appModuleHandler, "unregisterExecutable", None)
		if not callable(unregister):
			self._registeredExecutables = []
			return
		for exeName in reversed(self._registeredExecutables):
			try:
				unregister(exeName)
			except Exception as e:
				log.debug("Could not unregister SPSS app module for %s: %s" % (exeName, e))
		self._registeredExecutables = []
