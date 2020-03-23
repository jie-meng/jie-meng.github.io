---
title: protobuf on android
layout: post 
date: 2020-03-23 13:46:07 +0800
categories: android 
---

## Introduction

Protocol buffers are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data – think XML, but smaller, faster, and simpler. You define how you want your data to be structured once, then you can use special generated source code to easily write and read your structured data to and from a variety of data streams and using a variety of languages.

This article is about how to setup protobuf on android.

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

## Steps

### Add plugin for gradle

The latest version is 0.8.12. It requires at least Gradle 5.6 and Java 8. It is available on Maven Central. To add dependency to it in the build.gradle of root:

{% highlight groovy %}

buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath 'com.google.protobuf:protobuf-gradle-plugin:0.8.12'
    }
}

{% endhighlight %}

### Add plugin to your project

{% highlight groovy %}

apply plugin: 'com.android.application'  // or 'com.android.library'
apply plugin: 'com.google.protobuf'

{% endhighlight %}

### Customizing source directories

- Create directory _app/src/main/proto_.

- Put *.proto files to _app/src/main/proto_.

### Add dependency

Add dependency to app build.gradle and configure protobuf tasks.

{% highlight groovy %}

dependencies {
  // You need to depend on the lite runtime library, not protobuf-java
  compile 'com.google.protobuf:protobuf-javalite:3.8.0'
}

protobuf {
  protoc {
    artifact = 'com.google.protobuf:protoc:3.8.0'
  }
  generateProtoTasks {
    all().each { task ->
      task.builtins {
        java {
          option "lite"
        }
      }
    }
  }
}

{% endhighlight %}

Everything's ok, clean project and build. you can use the generated class.

## References

[protocol-buffers](https://developers.google.com/protocol-buffers)

[protobuf-gradle-plugin](https://github.com/google/protobuf-gradle-plugin)

