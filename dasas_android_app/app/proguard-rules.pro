# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# Keep data classes
-keep class com.dasas.android.model.** { *; }

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class com.google.gson.** { *; }
