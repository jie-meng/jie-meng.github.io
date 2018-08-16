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

- Create a native Android project

- Make sure its minSdkVersion not lower than 19.

- Copy **framework-release.aar** to _project/app/libs_.

- Add `implementation fileTree(dir: 'libs', include: ['*.jar','*.aar'])` to dependencies of _app/build.gradle_.

- Write a class **ExtendCordovaConfigXmlParser** with which we can parse arbitrary config.xml:

{% highlight java %}

import android.content.Context;

import org.apache.cordova.CordovaPreferences;
import org.apache.cordova.LOG;
import org.apache.cordova.PluginEntry;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ExtendCordovaConfigXmlParser {
    private static String TAG = "ExtendCordovaConfigXmlParser";
    private String webPagePath;
    private String launchUrl = webPagePath + "/index.html";
    private CordovaPreferences prefs = new CordovaPreferences();
    private ArrayList<PluginEntry> pluginEntries = new ArrayList(20);
    boolean insideFeature = false;
    String service = "";
    String pluginClass = "";
    String paramType = "";
    boolean onload = false;

    public ExtendCordovaConfigXmlParser(String webPagePath) {
        this.webPagePath = webPagePath;
    }

    public CordovaPreferences getPreferences() {
        return this.prefs;
    }

    public ArrayList<PluginEntry> getPluginEntries() {
        return this.pluginEntries;
    }

    public String getLaunchUrl() {
        return this.launchUrl;
    }

    public void parse(Context action, String config) {
        int id = action.getResources().getIdentifier(config, "xml", action.getClass().getPackage().getName());
        if (id == 0) {
            id = action.getResources().getIdentifier(config, "xml", action.getPackageName());
            if (id == 0) {
                LOG.e(TAG, String.format("res/xml/%s.xml is missing!", config));
                return;
            }
        }

        this.parse(action.getResources().getXml(id));
    }

    public void parse(XmlPullParser xml) {
        int eventType = -1;

        while (eventType != 1) {
            if (eventType == 2) {
                this.handleStartTag(xml);
            } else if (eventType == 3) {
                this.handleEndTag(xml);
            }

            try {
                eventType = xml.next();
            } catch (XmlPullParserException var4) {
                var4.printStackTrace();
            } catch (IOException var5) {
                var5.printStackTrace();
            }
        }
    }

    public void handleStartTag(XmlPullParser xml) {
        String strNode = xml.getName();
        if (strNode.equals("feature")) {
            this.insideFeature = true;
            this.service = xml.getAttributeValue(null, "name");
        } else if (this.insideFeature && strNode.equals("param")) {
            this.paramType = xml.getAttributeValue(null, "name");
            if (this.paramType.equals("service")) {
                this.service = xml.getAttributeValue(null, "value");
            } else if (!this.paramType.equals("package") && !this.paramType.equals("android-package")) {
                if (this.paramType.equals("onload")) {
                    this.onload = "true".equals(xml.getAttributeValue(null, "value"));
                }
            } else {
                this.pluginClass = xml.getAttributeValue(null, "value");
            }
        } else {
            String src;
            if (strNode.equals("preference")) {
                src = xml.getAttributeValue(null, "name").toLowerCase(Locale.ENGLISH);
                String value = xml.getAttributeValue(null, "value");
                this.prefs.set(src, value);
            } else if (strNode.equals("content")) {
                src = xml.getAttributeValue(null, "src");
                if (src != null) {
                    this.setStartUrl(src);
                }
            }
        }
    }

    public void handleEndTag(XmlPullParser xml) {
        String strNode = xml.getName();
        if (strNode.equals("feature")) {
            this.pluginEntries.add(new PluginEntry(this.service, this.pluginClass, this.onload));
            this.service = "";
            this.pluginClass = "";
            this.insideFeature = false;
            this.onload = false;
        }
    }

    private void setStartUrl(String src) {
        if (src == null) {
            return;
        }

        Pattern schemeRegex = Pattern.compile("^[a-z-]+://");
        Matcher matcher = schemeRegex.matcher(src);
        if (matcher.find()) {
            this.launchUrl = src;
        } else {
            if (src.charAt(0) == '/') {
                src = src.substring(1);
            }

            this.launchUrl = webPagePath + "/" + src;
        }
    }
}

{% endhighlight %}

- Write a class **ExtendCordovaActivity** with which we can build hybrid page easily:

{% highlight java %}

import android.os.Bundle;

import org.apache.cordova.CordovaActivity;

public abstract class ExtendCordovaActivity extends CordovaActivity {

    public abstract String getConfig();

    public abstract String getWebPagePath();

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        loadConfig();

        Bundle extras = getIntent().getExtras();
        if (extras != null && extras.getBoolean("cdvStartInBackground", false)) {
            moveTaskToBack(true);
        }

        loadUrl(launchUrl);
    }

    @Override
    protected void loadConfig() {
        ExtendCordovaConfigXmlParser parser = new ExtendCordovaConfigXmlParser(getWebPagePath());
        parser.parse(this, getConfig());
        this.preferences = parser.getPreferences();
        this.preferences.setPreferencesBundle(getIntent().getExtras());
        this.launchUrl = parser.getLaunchUrl();
        this.pluginEntries = parser.getPluginEntries();
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

- Create `WebPagePath` which can switch web page directory.

{% highlight java %}

import com.jmengxy.cordovadroid.base.ExtendCordovaActivity;
import com.jmengxy.cordovadroid.definitions.WebPagePath;

import com.jmengxy.cordovadroid.BuildConfig;

public class WebPagePath {
    public static final String ASSETS = "file:///android_asset/www";
    public static final String INTERNAL_STORAGE = "file:///sdcard/Android/data/" + BuildConfig.APPLICATION_ID + "/www";
    public static final String EXTERNAL_STORAGE = "file:///sdcard/CordovaDroid/www";
}

{% endhighlight %}

- Create an Activity **IndexActivity**.

{% highlight java %}

import com.jmengxy.cordovadroid.base.ExtendCordovaActivity;
import com.jmengxy.cordovadroid.definitions.WebPagePath;

public class IndexActivity extends ExtendCordovaActivity {

    @Override
    public String getConfig() {
        return "index";
    }

    @Override
    public String getWebPagePath() {
        return WebPagePath.ASSETS;
    }
}

{% endhighlight %}

- Create a config file **index.xml** in `app/src/main/res/xml/` of **native project**. Copy content from **config.xml**, change widget id to package name of IndexActivity. `<content src="index.html" />` points to `{web page directory}/index.html`.

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

## Proguard

If you use proguard in release version, you would got `java.lang.RuntimeException: Failed to create webview.` when start a Cordova WebView.

Add `-keep public class org.apache.cordova.** { *; }` in **proguard-rules.prod** would solve this problem.

[Github Repo](https://github.com/jie-meng/CordovaDroid)

## References

[Cordova](https://cordova.apache.org/)

[Embeded cordova into native App](https://cordova.apache.org/docs/en/latest/guide/platforms/android/webview.html)

[Cordova plugin dialogs](https://cordova.apache.org/docs/en/latest/reference/cordova-plugin-dialogs/index.html)
