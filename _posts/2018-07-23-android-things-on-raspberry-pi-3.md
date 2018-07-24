---
title: Android Things on Raspberry Pi 3
layout: post
date: 2018-07-23 04:31:56 +0800
categories: iot
---

## Flashing image on Raspberry Pi 3 model B

Before you begin flashing, you will need the following items in addition to your Raspberry Pi:

- Micro-USB cable
- Ethernet cable
- MicroSD card reader
- 8 GB or larger microSD card

Optional items:

- HDMI cable
- HDMI-enabled display

Follow steps on [Flash Android Things on Raspberry Pi 3](https://developer.android.google.cn/things/hardware/raspberrypi).

## Start Android Things and configure network

After flashing image on SD card. plug SD card into Raspberry Pi 3, Connect a USB cable to J1 for power. (Don not use PC usb power, use 220V adapter.)

When Android Things system launcher started, you can configure its Network.

## Connect it with adb

Let PC connect to same network as Raspberry Pi 3, Use `adb connect <Raspberry IP>`, you can found device with `adb devices`.

## Develop an APP

Create an Android Things App with Android studio.

Open AndroidManifest.xml, change `<category android:name="android.intent.category.IOT_LAUNCHER" />` to `<category android:name="android.intent.category.HOME" />` which makes the app auto-start after reboot.

Install app to Raspberry 3 with Android Studio or adb.

## References

[Android Things on Raspberry Pi 3](https://developer.android.google.cn/things/hardware/raspberrypi)
