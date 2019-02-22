---
title: AOSP pre install App
layout: post
date: 2019-02-21 05:16:44 +0800
categories: android
---

## Target

Pre install android app into android ROM

## Compile AOSP

Let's run AOSP on emulator for example.

Follow steps of [AOSP setup](https://source.android.com/setup/build/requirements).

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

## Modify makefile

- Open _AOSP_WORKSPACE/build/target/product/aosp_x86.mk_.

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

We can see there is _$(SRC_TARGET_DIR)/product/gsi_common.mk_ which every target .mk files call.

- Then we need to add _TestMan_ to Default AOSP packages in makefile.

open _AOSP_WORKSPACE/build/target/product/gsi_common.mk_

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

- Add _TestMan_ to whitelist in _gsi_common.mk_.

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

- Build and run

- Go to _AOSP_WORKSPACE_, run `make -j8` or `make -j16` ... (depend on your CPU cores)

- If you got `#### build completed successfully (02:17 (mm:ss)) ####`, run `emulator`, you can see _TestMan_ is already an in pre-install app which cannot be uninstall.

![]({{ "/assets/img/android-pre-install-app.webp" | absolute_url }})

## References

[AOSP setup](https://source.android.com/setup/build/requirements)
