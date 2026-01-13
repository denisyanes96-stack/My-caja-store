[app]
title = Your Mobile Store
package.name = yourmobilestore
package.domain = org.yubel
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Aquí están las librerías necesarias para el Word
requirements = python3,kivy,python-docx

icon.filename = icon.png
orientation = portrait
fullscreen = 0

# --- CONFIGURACIÓN DE ANDROID ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.0
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

# ESTA ES LA LÍNEA QUE FALTABA EN TU ÚLTIMO MENSAJE
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# --- FIN ---

android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1

