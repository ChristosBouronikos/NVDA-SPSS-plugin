# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's api module, for offline unit tests."""

_focusObject = None
_foregroundObject = None
_navigatorObject = None
clipboard = []


def getFocusObject():
	return _focusObject


def getForegroundObject():
	return _foregroundObject


def setNavigatorObject(obj):
	global _navigatorObject
	_navigatorObject = obj


def copyToClip(text):
	clipboard.append(text)
	return True


def setFocusObject(obj):
	global _focusObject
	_focusObject = obj


def setForegroundObject(obj):
	global _foregroundObject
	_foregroundObject = obj
