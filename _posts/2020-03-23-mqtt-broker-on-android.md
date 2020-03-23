---
title: mqtt broker on android
layout: post 
date: 2020-03-23 14:47:00 +0800
categories: iot 
---

## Introduction

On android device, we often use [paho mqtt client](https://github.com/eclipse/paho.mqtt.java) to setup mqtt client.

If you want android device to become a mqtt broker. you can use [Moquette MQTT broker](https://moquette-io.github.io/moquette).

This article is about how to setup mqtt broker on android device with moqutte.

## Android app settings

Following settings is not mandatory, it's just the pre-settings of the sample app.

language: Kotlin

{% highlight groovy %}

minSdkVersion 26
minSdkVersion 29

multiDexEnabled true

compileOptions {
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
}

{% endhighlight %}

{% highlight xml %}

<uses-permission android:name="android.permission.INTERNET" />

{% endhighlight %}

## Steps

### Add dependency

Add dependency to app build.gradle.

{% highlight groovy %}

dependencies {
    implementation 'io.moquette:moquette-broker:0.12.1'
}

{% endhighlight %}

### Configure packagingOptions

Sync gradle, then you might got errors such as:

{% highlight shell %}

More than one file was found with OS independent path 'META-INF/io.netty.versions.properties'

More than one file was found with OS independent path 'META-INF/INDEX.LIST'

{% endhighlight %}

Exclude them in build.gradle of app:

{% highlight groovy %}

android {
    ...
    packagingOptions {
        exclude 'META-INF/io.netty.versions.properties'
        exclude 'META-INF/INDEX.LIST'
    }
}

{% endhighlight %}

### Start & stop server

{% highlight kotlin %}

private fun startMqttBroker() {
    val properties = Properties()
    properties.setProperty("host", "0.0.0.0")
    properties.setProperty("port", "1883")
    mqttBroker.startServer(properties)
}

private fun stopMqttBroker() {
    mqttBroker.stopServer()
}

{% endhighlight %}

It's already ok for mqttBroker. If you want to make more detailed configurations, follow the next step.

### Configure

Check the properties in mosquitto.conf, and set it to mqttBroker.

{% highlight shell %}

##############################################
#  Moquette configuration file.
#
#  The synthax is equals to mosquitto.conf
#
##############################################

port 1883

websocket_port 8080

host 0.0.0.0

#false to accept only client connetions with credentials
#true to accept client connection without credentails, validating only the one that provides
allow_anonymous true

#false to prohibit clients from connecting without a clientid.
#true to allow clients to connect without a clientid. One will be generated for them.
allow_zero_byte_client_id false

{% endhighlight %}

## References

[mqtt-broker-for-android](https://stackoverflow.com/questions/28623707/mqtt-broker-for-android)

[mqtt-client-library](https://www.hivemq.com/tags/mqtt-client-library)

[paho mqtt client](https://github.com/eclipse/paho.mqtt.java)

[Moquette MQTT broker](https://moquette-io.github.io/moquette)

[mosquitto-conf](https://www.eclipse.org/mosquitto/man/mosquitto-conf-5.php)

[mosquitto.conf](https://github.com/eclipse/mosquitto/blob/master/mosquitto.conf)
