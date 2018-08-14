---
title: Android hybrid with cordova
layout: post
date: 2018-08-14 05:04:39 +0800
categories: android
---

## Introduction

When we need to build a hybrid Android App with cordova, we'll need to know how to embeded cordova page into native App.

But cordova official document for [Embeded cordova into native App](https://cordova.apache.org/docs/en/latest/guide/platforms/android/webview.html) is too old to follow.

Here are the new steps to build a hybrid Android App with cordova.

## Build cordova library

- Download cordova Android source **cordova-android-x.x.x.tgz** from [cordova-source](http://apache.website-solution.net/cordova/platforms/).

- Unzip it. Go to directory _framework_, execute `gradle build`, then you got **framework-release.aar** in _framework/build/outputs/aar_.

## Build a native Android project

- Create a native Android project, use kotlin as example

- Make sure its minSdkVersion not lower than 19.

- Copy **framework-release.aar** to _project/app/libs_.

- Add `implementation fileTree(dir: 'libs', include: ['*.jar','*.aar'])` to dependencies of _app/build.gradle_.

- Write a class **ExtendCordovaConfigXmlParser** with which we can parse arbitrary config.xml:

{% highlight kotlin %}

import android.content.Context
import org.apache.cordova.CordovaPreferences
import org.apache.cordova.LOG
import org.apache.cordova.PluginEntry
import org.xmlpull.v1.XmlPullParser
import org.xmlpull.v1.XmlPullParserException
import java.io.IOException
import java.util.*
import java.util.regex.Pattern

class ExtendCordovaConfigXmlParser {

    companion object {
        private val TAG = "ExtendCordovaConfigXmlParser"
    }

    var launchUrl = "file:///android_asset/www/index.html"
    val preferences = CordovaPreferences()
    val pluginEntries: ArrayList<PluginEntry> = ArrayList(20)
    internal var insideFeature = false
    internal var service = ""
    internal var pluginClass = ""
    internal var paramType = ""
    internal var onload = false

    fun parse(action: Context) {
        var id = action.resources.getIdentifier("config", "xml", action.javaClass.getPackage().name)
        if (id == 0) {
            id = action.resources.getIdentifier("config", "xml", action.packageName)
            if (id == 0) {
                LOG.e(TAG, "res/xml/config.xml is missing!")
                return
            }
        }

        this.parse(action.resources.getXml(id) as XmlPullParser)
    }

    fun parse(action: Context, config: String) {
        var id = action.resources.getIdentifier(config, "xml", action.javaClass.getPackage().name)
        if (id == 0) {
            id = action.resources.getIdentifier(config, "xml", action.packageName)
            if (id == 0) {
                LOG.e(TAG, "res/xml/$config.xml is missing!")
                return
            }
        }

        this.parse(action.resources.getXml(id) as XmlPullParser)
    }

    fun parse(xml: XmlPullParser) {
        var eventType = -1

        while (eventType != 1) {
            if (eventType == 2) {
                this.handleStartTag(xml)
            } else if (eventType == 3) {
                this.handleEndTag(xml)
            }

            try {
                eventType = xml.next()
            } catch (var4: XmlPullParserException) {
                var4.printStackTrace()
            } catch (var5: IOException) {
                var5.printStackTrace()
            }

        }

    }

    fun handleStartTag(xml: XmlPullParser) {
        val strNode = xml.name
        if (strNode == "feature") {
            this.insideFeature = true
            this.service = xml.getAttributeValue(null as String?, "name")
        } else if (this.insideFeature && strNode == "param") {
            this.paramType = xml.getAttributeValue(null as String?, "name")
            if (this.paramType == "service") {
                this.service = xml.getAttributeValue(null as String?, "value")
            } else if (this.paramType != "package" && this.paramType != "android-package") {
                if (this.paramType == "onload") {
                    this.onload = "true" == xml.getAttributeValue(null as String?, "value")
                }
            } else {
                this.pluginClass = xml.getAttributeValue(null as String?, "value")
            }
        } else {
            val src: String?
            if (strNode == "preference") {
                src = xml.getAttributeValue(null as String?, "name").toLowerCase(Locale.ENGLISH)
                val value = xml.getAttributeValue(null as String?, "value")
                this.preferences.set(src, value)
            } else if (strNode == "content") {
                src = xml.getAttributeValue(null as String?, "src")
                if (src != null) {
                    this.setStartUrl(src)
                }
            }
        }

    }

    fun handleEndTag(xml: XmlPullParser) {
        val strNode = xml.name
        if (strNode == "feature") {
            this.pluginEntries.add(PluginEntry(this.service, this.pluginClass, this.onload))
            this.service = ""
            this.pluginClass = ""
            this.insideFeature = false
            this.onload = false
        }

    }

    private fun setStartUrl(src: String) {
        var copysrc = src
        val schemeRegex = Pattern.compile("^[a-z-]+://")
        val matcher = schemeRegex.matcher(copysrc)
        if (matcher.find()) {
            this.launchUrl = copysrc
        } else {
            if (copysrc[0] == '/') {
                copysrc = copysrc.substring(1)
            }

            this.launchUrl = "file:///android_asset/www/$copysrc"
        }
    }
}

{% endhighlight %}

- Write a class **ExtendCordovaActivity** with which we can build hybrid page easily:

{% highlight kotlin %}

import android.os.Bundle
import org.apache.cordova.CordovaActivity

abstract class ExtendCordovaActivity : CordovaActivity() {

    abstract fun getConfig(): String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val extras = intent.extras
        if (extras != null && extras.getBoolean("cdvStartInBackground", false)) {
            moveTaskToBack(true)
        }

        loadUrl(launchUrl)
    }

    override fun loadConfig() {
        val parser = ExtendCordovaConfigXmlParser()
        parser.parse(this, getConfig())
        this.preferences = parser.preferences
        this.preferences.setPreferencesBundle(this.intent.extras)
        this.launchUrl = parser.launchUrl
        this.pluginEntries = parser.pluginEntries
    }
}

{% endhighlight %}

## Build a cordova project by npm command

We can copy config files, plugins simply from pure cordova project.

- Create a pure cordova project by `cordova create <path>`.

- Create Android platform by `cordova platform add android`.

## Create first hybrid page in native App

- Copy `platforms/android/app/src/main/com/apache/cordova/whitelist/WhitelistPlugin.java` from **cordova project** to **native project**. Do not change its package name.

- Copy `platforms/android/app/src/main/res/xml/config.xml` from **cordova project** to **native project**.

- Copy `platforms/android/app/src/assets/www` from from **cordova project** to **native project**.

- Create an Activity **IndexActivity**.

{% highlight kotlin %}

import com.example.native.base.ExtendCordovaActivity

class IndexActivity : ExtendCordovaActivity() {

    override fun getConfig(): String {
        return "index"
    }
}

{% endhighlight %}

- Create a config file **index.xml** in `app/src/main/res/xml/` of **native project**. Copy content from **config.xml**, change widget id to package name of IndexActivity. `<content src="index.html" />` points to `assets/www/index.html`.

- Make a button in MainActivity which jump to IndexActivity.

- Run project and click button in MainActivity, you can see:

![]({{ "/assets/img/cordova.webp" | absolute_url }})

## Use plugin

Use alert dialog plugin as an example.

- Execute `cordova plugin add cordova-plugin-dialogs` in **cordova project**.

- Copy `platforms/android/app/src/main/com/apache/cordova/dialogs` from **cordova project** to **native project**. Do not change its package name.

- Copy `platforms/android/src/assets/www/plugins/cordova-plugin-dialogs` from from **cordova project** to **native project**.

- Copy **cordova-plugin-dialogs.notification** related code from **cordova project/platforms/android/app/src/assets/www/cordova_plugins.js** to **native project/app/src/assets/www/cordova_plugins.js**.

- Add a line `<script type="text/javascript" src="notification.js"></script>` under `<script type="text/javascript" src="js/index.js"></script>` in **native project/app/src/assets/www/index.html**.

- Create `notification.js` in **native project/platforms/android/app/src/assets/www**, with content:

{% highlight javascript %}

function onDeviceReady() {
    navigator.notification.alert('This is message', function() {}, 'Title', 'CLICK');
}
document.addEventListener("deviceready", onDeviceReady, false);

{% endhighlight %}

- Run project and click button in MainActivity, you can see:

![]({{ "/assets/img/cordova-plugin-dialogs.webp" | absolute_url }})

## References

[Cordova](https://cordova.apache.org/)

[Embeded cordova into native App](https://cordova.apache.org/docs/en/latest/guide/platforms/android/webview.html)

[Cordova plugin dialogs](https://cordova.apache.org/docs/en/latest/reference/cordova-plugin-dialogs/index.html)
