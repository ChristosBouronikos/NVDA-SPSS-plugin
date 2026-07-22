# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's addonHandler, for offline unit tests.

Real NVDA installs a gettext-backed ``_`` into the caller's module globals.
For tests we install an identity function instead, so the app module's own
wrapper phrases stay in English and are easy to assert on.
"""

import sys


def initTranslation():
	frame = sys._getframe(1)
	frame.f_globals.setdefault("_", lambda text: text)
