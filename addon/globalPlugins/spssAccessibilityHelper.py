# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin Helper Global Plugin for NVDA
# Version: 1.1.1
# =============================================================================

"""
Registers the SPSS app module for common executable names.

Created by Bouronikos Christos. Contact: chrisbouronikos@gmail.com.
If this add-on helps you, please consider a kind donation via PayPal:
https://paypal.me/christosbouronikos

NVDA normally loads an app module from addon/appModules/<processName>.py. IBM
SPSS Statistics has used more than one process name across releases, so the
explicit registrations below improve compatibility. Alias appModule files are
also included as a fallback for NVDA builds without a public registration API.
"""

import appModuleHandler
import globalPluginHandler
from logHandler import log


# Process names (without .exe) that IBM SPSS Statistics has used across releases.
SPSS_EXECUTABLES = (
	"stats",  # stats.exe: the main IBM SPSS Statistics process in modern releases (roughly version 21 onward, including SPSS Statistics 31).
	"spss",  # spss.exe: the main process name used by older SPSS releases before the IBM-era rename.
	"spsswin",  # spsswin.exe: the main process name of early SPSS for Windows releases.
	"spssprod",  # spssprod.exe: the SPSS Production Facility component for running unattended production jobs.
)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global helper for IBM SPSS Statistics accessibility app-module loading."""

	def __init__(self):
		super().__init__()
		self._registerSpssVariants()

	def terminate(self):
		super().terminate()

	def _registerSpssVariants(self):
		try:
			from appModules import spss
		except Exception as e:
			log.debugWarning("Could not import SPSS accessibility app module: %s" % e)
			return
		register = getattr(appModuleHandler, "registerAppModule", None)
		if not callable(register):
			log.debug("No registerAppModule API; SPSS aliases will be used")
			return
		for exeName in SPSS_EXECUTABLES:
			try:
				register(exeName, spss.AppModule)
			except Exception as e:
				log.debug("Could not register SPSS app module for %s: %s" % (exeName, e))
		log.debug("Registered IBM SPSS Statistics app module variants")
