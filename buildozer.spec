[app]

# (str) Title of your application
title = Your Mobile Store

# (str) Package name
package.name = store

# (str) Package domain
package.domain = com.yourmobile

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,txt,xml

# (str) Application versioning
version = 1.0.1

# (list) Application requirements
# RECTIFICADO: fpdf2 para evitar lxml y pyjnius para WhatsApp
requirements = python3, kivy, fpdf2, pyjnius

# (str) Supported orientation
orientation = portrait

# (list) Permissions
# RECTIFICADO: No requiere READ/WRITE EXTERNAL en Android 15 para carpetas internas
android.permissions = INTERNET

# (int) Target Android API
# Obligatorio para Android 15 (Redmi Note 13)
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (Indispensable para Android 15)
android.private_storage = True

# (list) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# --- CONFIGURACIÓN PARA COMPARTIR PDF A WHATSAPP ---

# (list) Gradle dependencies (Librería de soporte para FileProvider)
android.gradle_dependencies = androidx.core:core:1.12.0

# (str) XML file for FileProvider paths (Debes tener el archivo paths.xml)
android.res_xml = paths.xml

# (list) Android addition to the manifest
# Esto inserta el FileProvider necesario para que WhatsApp vea el PDF
android.manifest.xml_contents = 
    <provider
        android:name="androidx.core.content.FileProvider"
        android:authorities="com.yourmobile.store.fileprovider"
        android:exported="false"
        android:grantUriPermissions="true">
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/file_paths" />
    </provider>

# --- OTRAS OPCIONES ---

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1



