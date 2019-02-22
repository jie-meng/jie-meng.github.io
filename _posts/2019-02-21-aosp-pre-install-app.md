---
title: AOSP pre install App
layout: post
date: 2019-02-21 05:16:44 +0800
categories: android
---

## Target

Pre install android app into android ROM

## Prepare AOSP build environment

Follow steps of [AOSP setup](https://source.android.com/setup/build/requirements).

Our sample environment:

__branch__: master (repo init -u https://android.googlesource.com/platform/manifest)

__target__: aosp_x86-eng

__device__: emulator

(Current newest version is Android 9.0.0)

Init env every time open a new terminal:

{% highlight shell %}

source ./build/envsetup.sh

lunch aosp_x86-eng

{% endhighlight %}

## Build an APK for pre-install

Use Android Studio to build an apk. I built a _TestMan.apk_.

## Place apk to aosp pre-install apps

- Make a dir _TestMan_ in _AOSP_WORKSPACE/packages/apps_.

- Put _TestMan.apk_ here.

- Make an _Android.mk_ in _AOSP_WORKSPACE/packages/apps/TestMan_.

Android.mk:

{% highlight shell %}

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_PRIVILEGED_MODULE := true
LOCAL_MODULE := TestMan
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_PATH := $(TARGET_OUT_APPS)
include $(BUILD_PREBUILT)

{% endhighlight %}

Each line should not have trailing spaces, or you would get error `Invalid characters in module stem \(LOCAL_INSTALLED_MODULE_STEM\)` when you build.

## Modify makefile

Open _AOSP_WORKSPACE/build/target/product/aosp_x86.mk_.

aosp_x86.mk:

{% highlight shell %}

# GSI for system/product
$(call inherit-product, $(SRC_TARGET_DIR)/product/gsi_common.mk)

# Emulator for vendor
$(call inherit-product-if-exists, device/generic/goldfish/x86-vendor.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/emulator_vendor.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/board/generic_x86/device.mk)

# Enable mainline checking for excat this product name
ifeq (aosp_x86,$(TARGET_PRODUCT))
PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed
endif

PRODUCT_NAME := aosp_x86
PRODUCT_DEVICE := generic_x86
PRODUCT_BRAND := Android
PRODUCT_MODEL := AOSP on x86

{% endhighlight %}

We can see there is _$(SRC_TARGET_DIR)/product/gsi_common.mk_ which every {TARGET} .mk files call.

Then we need to add _TestMan_ to Default AOSP packages in makefile.

Open _AOSP_WORKSPACE/build/target/product/gsi_common.mk_

We can see

{% highlight shell %}

# Default AOSP packages
PRODUCT_PACKAGES += \
    PhotoTable \
    WAPPushManager \

{% endhighlight %}

Add TestMan here

{% highlight shell %}

# Default AOSP packages
PRODUCT_PACKAGES += \
    PhotoTable \
    WAPPushManager \
    TestMan \

{% endhighlight %}

Add _TestMan_ to whitelist in _gsi_common.mk_.

{% highlight shell %}

# The mainline checking whitelist, should be clean up
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST := \
    system/app/messaging/messaging.apk \
    system/app/PhotoTable/PhotoTable.apk \
    system/app/WAPPushManager/WAPPushManager.apk \
    system/app/TestMan/TestMan.apk \
    system/bin/healthd \
    system/etc/init/healthd.rc \
    system/etc/seccomp_policy/crash_dump.%.policy \
    system/etc/seccomp_policy/mediacodec.policy \
    system/etc/vintf/manifest/manifest_healthd.xml \
    system/lib/libframesequence.so \
    system/lib/libgiftranscode.so \
    system/lib64/libframesequence.so \
    system/lib64/libgiftranscode.so \
    system/priv-app/Dialer/Dialer.apk \

{% endhighlight %}

## Build

- Go to _AOSP_WORKSPACE_, run `make -j8` or `make -j16` ... (depend on your CPU cores)

- If you got `#### build completed successfully (02:17 (mm:ss)) ####`, run `emulator`, you can see _TestMan_ is already an in pre-install app which cannot be uninstall.

![]({{ "/assets/img/android-pre-install-app.webp" | absolute_url }})

## How to replace default launcher with customized launcher

### Find default launcher of AOSP

Launcher is also a pre-install app, so we can find it under _AOSP_WORKSPACE/packages/apps/_.

We can see there are Luncher2 and Luncher3, why there are two launchers?

We can check their Android.mk to see what's going on. Launcher2 does not have Android.mk, but Launcher3 has.

We can see there is `LOCAL_OVERRIDES_PACKAGES := Home Launcher2 Launcher3 Launcher3QuickStep`. Check what is __LOCAL_OVERRIDES_PACKAGES__.

From [How do I add APKs in an AOSP build?](https://stackoverflow.com/questions/10579827/how-do-i-add-apks-in-an-aosp-build) we know that Launcher3 module hide `Home Launcher2 Launcher3 Launcher3QuickStep`.

So why does Launcher3 hide itself? Check _Android.mk_ again we can also see `LOCAL_PACKAGE_NAME := Launcher3QuickStepGo`.

From [Android.mk](http://android.mk/) we see:

__LOCAL_PACKAGE_NAME__ is the name of an app. For example, Dialer, Contacts, etc.

__LOCAL_MODULE__ is the name of what's supposed to be generated from your Android.mk. For exmample, for libkjs, the LOCAL_MODULE is "libkjs" (the build system adds the appropriate suffix -- .so .dylib .dll). For app modules, use LOCAL_PACKAGE_NAME instead of LOCAL_MODULE.

So we should always use __LOCAL_PACKAGE_NAME__ when pre-install module is an App and build with source code. But if we use apk instead of source code, we should always use __LOCAL_MODULE__, otherwise you'll get error when build.

Finally, we can see Launcher3's real name is __Launcher3QuickStepGo__, and there are other __LOCAL_PACKAGE_NAME__ in Android.mk of Launcher3: Launcher3, Launcher3Go, Launcher3QuickStep. We should use `LOCAL_OVERRIDES_PACKAGES := Home Launcher2 Launcher3 Launcher3QuickStep Launcher3QuickStepGo` in our own launcher app's Android.mk to hide them all.

### Build new launcher apk to replace default launcher

Then we need to build a launcher apk and place it to _AOSP_WORKSPACE/packages/apps/_ with the same way of pre-install common apk metioned above. Modify gsi_common.mk, add it to product_packages and whitelist.

Android.mk of NewLauncher:

{% highlight shell %}

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_PRIVILEGED_MODULE := true
LOCAL_MODULE := NewLauncher
LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_PATH := $(TARGET_OUT_APPS)
LOCAL_OVERRIDES_PACKAGES := Home Launcher2 Launcher3 Launcher3Go Launcher3QuickStep Launcher3QuickStepGo
include $(BUILD_PREBUILT)

{% endhighlight %}

### Build

- Run `make installclean` to remove default launcher apk which generated under _AOSP_WORKSPACE/out_ directory.

- Run `make -j8`

- Run `emulator` to see new launcher after boot.

(If you do not hide default launcher with __LOCAL_OVERRIDES_PACKAGES__, you will need to select a launcher after boot.)

## Clean

If you remove pre install app, you nedd to run `make installclean` before `make`.

If you want to clear app data, you nedd to run `make dataclean` before `make`.

## References

[AOSP setup](https://source.android.com/setup/build/requirements)

[How do I add APKs in an AOSP build?](https://stackoverflow.com/questions/10579827/how-do-i-add-apks-in-an-aosp-build)

[How do I set the default launcher in an AOSP build?](https://stackoverflow.com/questions/22911156/how-do-i-set-the-default-launcher-in-an-aosp-build)

[Android.mk](http://android.mk/)