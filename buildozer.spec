[app]

# Application information
title = Calculator
package.name = calculator
package.domain = org.mahdirafati

# Source files
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,ttf,otf,json

# Version
version = 1.0

# Python requirements
requirements = python3,kivy

# Display settings
orientation = portrait
fullscreen = 0

# Android settings
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a
android.accept_sdk_license = True

# Permissions
android.permissions =


[buildozer]

log_level = 2
warn_on_root = 1
