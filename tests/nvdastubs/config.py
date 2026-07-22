# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's config module, for offline unit tests.

Real NVDA config is a ConfigObj-backed profile tree with a validated spec.
This stub is just deep enough to exercise
``AppModule._configLanguageOverride``/``_setConfigLanguageOverride`` and the
global plugin's confspec registration.
"""


class _Section(dict):

	def __getitem__(self, key):
		if key not in self:
			dict.__setitem__(self, key, _Section())
		return dict.__getitem__(self, key)


class _Conf(_Section):

	def __init__(self):
		super().__init__()
		self.spec = _Section()


conf = _Conf()
conf["spssAccessibility"]["language"] = "auto"
