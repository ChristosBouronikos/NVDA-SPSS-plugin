# -*- coding: utf-8 -*-
# =============================================================================
# SPSS Accessibility Plugin Helper Global Plugin for NVDA
# Version: 1.1.0
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


SPSS_EXECUTABLES = (
	"stats",
	"spss",
	"spsswin",
	"spssstatistics",
	"ibmspssstatistics",
	"spssprod",
	"IBM SPSS Statistics",
	"IBM SPSS Statistics Data Editor",
	"IBM SPSS Statistics Viewer",
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
