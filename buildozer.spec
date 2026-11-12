[app]
title = Shifr
package.name = shifr
package.domain = org.vodolei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
orientation = portrait
requirements = python3,kivy
osx.python_version = 3
osx.kivy_version = 1.9.1

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_version = 25b
aoid.build_tools_version = 33.0.2
android.accept_sdk_license = True
p4a.source_dir = /home/runner/build/python-for-android
p4a.branch = master
android.arch = arm64-v8a
android.gradle_dependencies = androidx.core:core:1.9.0

[buildozer]
log_level = 2
warn_on_root = 1
