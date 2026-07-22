# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Minimal stand-in for NVDA's scriptHandler module, for offline unit tests."""


def script(**kwargs):
	def decorator(func):
		func.__scriptInfo__ = kwargs
		return func
	return decorator
