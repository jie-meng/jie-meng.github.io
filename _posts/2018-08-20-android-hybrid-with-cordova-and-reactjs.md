---
title: Android hybrid with cordova and ReactJS
layout: post
date: 2018-08-20 10:25:02 +0800
categories: android
---

In the last post [Android hybrid with cordova](https://jie-meng.github.io/android/2018/08/13/android-hybrid-with-cordova.html) we discussed how to hybrid an Android App with cordova.

Now we'll make a further step: use web framework [ReactJS](https://reactjs.org/) on web part of the hybrid App.

## Create ReactJS project

First you should have **Node.js** installed.

Then execute `npx create-react-app web` under directory of your hybrid App project.

## Configure Webpack

Webpack 4 may not work well. [Issue: Cannot read property 'thisCompilation' of undefined](https://github.com/angular/angular-cli/issues/9794). So we use webpack 3.11.0 instead of the newest version.

- `npm install --save-dev webpack@3.11.0 babel-core babel-jest babel-loader node-sass css-loader sass-loader style-loader`

- Create webpack.config.js under _App/web_

{% highlight javascript %}

const path = require('path');

const BUILD_DIR = path.resolve(__dirname, 'www');
const APP_DIR = path.resolve(__dirname, 'src');

const config = {

   "entry": `${APP_DIR}/index.js`,
   "output": {
       "path": BUILD_DIR,
       "filename": 'bundle.js'
   },
   "module": {
       "rules": [
           {
               "test": /\.(js|jsx)$/,
               "exclude": /node_modules/,
               "use": {
                   "loader": "babel-loader",
                   "options": {
                       "presets": [
                           "env",
                           "react"
                       ]
                   }
               }
           },
           {
               "test": /\.(css|scss)$/,
               "use": [
                   "style-loader",
                   "css-loader",
                   "sass-loader"
               ]
           }
       ]
   },
   resolve: {
       extensions: ['.js', '.jsx'],
   },
   devtool: 'eval'
};

module.exports = config;

{% endhighlight %}

- Modify **App/web/package.json** scripts.build to `"react-scripts build && ./node_modules/.bin/webpack --config webpack.config.js"`.

## Web code

- Move _App/web/src/logo.svg_ to _App/web/src/images_.

- We will not pack images in webpack, so we can make some changes in _App/web/src/App.js_, remove `import logo from './logo.svg';`. Change `<img src={logo} className="App-logo" alt="logo" />` to `<img src='images/logo.svg' className="App-logo" alt="logo" />`

- We need an html page to use the ReactJS code. Just copy _App/web/public/index.html_ to output directory _App/web/www_, rename it to _react.html_. Add a line `<script type="text/javascript" src="bundle.js"></script>` under `<div id="root"></div>`.

- Create some tool scripts to build and copy generated files to SD card of device. Check **android-tools.py** of [CordovaDroid](https://github.com/jie-meng/CordovaDroid).

## Native code

- Now we shall create a new native Activity to embed **react.html**. Create **ReactActivity**. Don't forget add it to **AndroidManifest.xml** and make a new button in **MainActivity** to jump to **ReactActivity**.

{% highlight java %}

public class ReactActivity extends ExtendCordovaActivity {
    @Override
    public String getConfig() {
        return "react";
    }

    @Override
    public String getWebPagePath() {
        return WebPagePath.INTERNAL_STORAGE;
    }
}

{% endhighlight %}

- Create a new **react.xml** in _App/src/main/res/xml_ which use **react.html** we just created.

{% highlight xml %}

<?xml version='1.0' encoding='utf-8'?>
<widget android-versionCode="1" id="com.jmengxy.cordovadroid" version="1.0.0" >
    <feature name="Whitelist">
        <param name="android-package" value="org.apache.cordova.whitelist.WhitelistPlugin" />
        <param name="onload" value="true" />
    </feature>
    <name>CordovaDroid</name>
    <description>
        A sample Apache Cordova application that responds to the deviceready event.
    </description>
    <author email="dev@cordova.apache.org" href="http://cordova.io">
        Apache Cordova Team
    </author>
    <content src="react.html" />
    <access origin="*" />
    <allow-intent href="http://*/*" />
    <allow-intent href="https://*/*" />
    <allow-intent href="tel:*" />
    <allow-intent href="sms:*" />
    <allow-intent href="mailto:*" />
    <allow-intent href="geo:*" />
    <allow-intent href="market:*" />
    <preference name="loglevel" value="DEBUG" />
</widget>

{% endhighlight %}

- Go to App project directory and execute `python3 android-tools.py`, select build -> qa -> debug (type 1,1,1). The script starts to build ReactJS project and Native App, then upload generated web files to SD card.

- Run App from Android Studio, click **REACT** button. You would get following page.

![]({{ "/assets/img/cordova-react-js.webp" | absolute_url }})

[Github Repo](https://github.com/jie-meng/CordovaDroid)

## References

[ReactJS](https://reactjs.org/)

[facebook/create-react-app](https://github.com/facebook/create-react-app)

[Android hybrid with cordova](https://jie-meng.github.io/android/2018/08/13/android-hybrid-with-cordova.html)

[Issue: Cannot read property 'thisCompilation' of undefined](https://github.com/angular/angular-cli/issues/9794)