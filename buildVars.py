# -*- coding: utf-8 -*-
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donation: https://paypal.me/christosbouronikos
"""Build metadata for the SPSS Accessibility Plugin NVDA add-on.

This file mirrors manifest.ini so the project can be adapted to the
standard NVDA add-on template/SCons workflow later without changing add-on
identity metadata.
"""

addon_info = {
	"addon_name": "spssAccessibility",
	"addon_summary": "SPSS Accessibility Plugin",
	"addon_description": (
		"SPSS Accessibility Plugin improves IBM SPSS Statistics accessibility for "
		"blind and visually impaired users. Created by Bouronikos Christos, contact: "
		"chrisbouronikos@gmail.com. If this add-on helps you, please consider a "
		"kind donation via PayPal: https://paypal.me/christosbouronikos"
	),
	"addon_version": "1.2.0",
	"addon_author": "Bouronikos Christos <chrisbouronikos@gmail.com>",
	"addon_url": "https://github.com/ChristosBouronikos/NVDA-SPSS-plugin",
	"addon_docFileName": "readme.md",
	"addon_minimumNVDAVersion": "2023.1.0",
	"addon_lastTestedNVDAVersion": "2026.1.1",
	"addon_updateChannel": "stable",
}
