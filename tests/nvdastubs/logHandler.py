# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's logHandler module, for offline unit tests."""


class _Log(object):

	def __init__(self):
		self.records = []

	def info(self, message):
		self.records.append(("info", message))

	def debugWarning(self, message):
		self.records.append(("debugWarning", message))

	def debug(self, message):
		self.records.append(("debug", message))


log = _Log()
