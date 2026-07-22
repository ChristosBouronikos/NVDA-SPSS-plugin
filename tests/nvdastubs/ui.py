# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's ui module, for offline unit tests."""

messages = []


def message(text):
	messages.append(text)


def reset():
	del messages[:]
