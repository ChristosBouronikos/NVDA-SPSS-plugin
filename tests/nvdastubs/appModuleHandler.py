# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's appModuleHandler, for offline unit tests."""


registeredExecutables = {}


class AppModule(object):

	def __init__(self, *args, **kwargs):
		pass

	def terminate(self):
		pass


def registerExecutableWithAppModule(executableName, appModuleName):
	registeredExecutables[executableName] = appModuleName


def unregisterExecutable(executableName):
	registeredExecutables.pop(executableName, None)


def resetRegistrations():
	registeredExecutables.clear()
