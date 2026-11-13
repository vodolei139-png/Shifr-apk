[app]
title = Shifr
package.name = shifr
package.domain = org.vodolei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
p4a.source_dir = ~/p4a-patched

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.archs = arm64-v8a   <-- ВАЖНО: именно archs (с буквой s) и только arm64

[buildozer]
log_level = 2
warn_on_root = 1
