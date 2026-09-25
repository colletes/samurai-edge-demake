[app]

# (str) Title of your application
title = Samurai Edge Demake

# (str) Package name
package.name = samuraiedge

# (str) Package domain (needed for android/ios packaging)
package.domain = com.antigravity

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,json,txt,spec,ttf

# (list) List of directory to include
source.include_patterns = assets/*,src/*

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,pyc,pyo,dmg,tar,gz

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests,bin,build,dist,.git,.pyinstaller,.github,__pycache__,venv,deploy

# (str) Application versioning (method 1)
version = 1.3.1

# (list) Application requirements
# pygame-ce runs on python3 and SDL2
requirements = python3,pygame-ce

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/portraits/kenshi_bust.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/portraits/kenshi_bust_circle.png

# (list) Supported orientations
# Valid options: landscape, sensorLandscape, portrait, sensorPortrait, all
orientation = landscape

# (bool) Indicate if the application should be fullscreen to the user
fullscreen = 1

# (string) Presplash background color (for android toolchain)
android.presplash_color = #0E1210

# (list) Permissions
android.permissions = VIBRATE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
