---
title: AOSP partially build and test on emulator
layout: post
date: 2019-02-25 11:29:57 +0800
categories: android
---

- After build AOSP, start emulator with command `emulator -writable-system`

- Run `adb remount` every time after emulator restart.

- Now you can use `mm` command to partially build modules of AOSP and use `adb push` to replace jars or apps of framework.

- You should always use `mm` to compile

For example, if you modified _/frameworks/base/core/res/res/values/dimens.xml_, then you can find its nearest make file _Android.bp_ under _/frameworks/base/core/res/_, then `mm` here.

After build, you'll see `[100% 8/8] Install: out/target/product/generic_x86/system/framework/framework-res.apk`, then push _framework-res.apk_ to emulator path _/system/framework/_. Restart emulator.

You can do this simply by `adb sync`. Put the following code into a shell script _adbsync_. Just run it after `mm`. Emulator will sync the build outputs and restart.

{% highlight shell %}

adb remount
adb sync
adb shell stop
adb shell start

{% endhighlight %}

## References

[How to mount /system rewritable or read-only? (RW/RO)](https://android.stackexchange.com/questions/110927/how-to-mount-system-rewritable-or-read-only-rw-ro)

[AOSP Part 1: Get the code using the Manifest and Repo tool](http://blog.udinic.com/2014/05/24/aosp-part-1-get-the-code-using-the-manifest-and-repo/)

[AOSP Part 2: Build variants](http://blog.udinic.com/2014/06/04/aosp-part-2-build-variants)

[AOSP Part 3: Developing Efficiently](http://blog.udinic.com/2014/07/24/aosp-part-3-developing-efficiently)