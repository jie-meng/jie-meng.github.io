---
title: Embedded scripting in Java/Android
layout: post
date: '2017-12-23 01:06:00 +0800'
categories: android
---

## TASK 1

Here comes a task, the requirements are:

- Make a ChatBot program. 
- We can talk to him, and he would respond as pre-defined scene.
- If not pre-defined, respond “I don’t know what you say”
- Input & Output are both pure string text.

### A simple scene
![]({{ "/assets/img/embedded-scripting-on-java-android/a-simple-scene.webp" | absolute_url }})

Here might be your code v1.0 looks like:

{% highlight java %}
public class ChatBot {

   public String talk(String ask) {
       if (ask.toLowerCase().contains("what is your mission")) {
           return "Kill John Conner.";
       } else {
           return "I don't know what you say.";
       }
   }
}

{% endhighlight %}

Try it again, but it does not work as expected...

### Something wrong?
![]({{ "/assets/img/embedded-scripting-on-java-android/something-wrong.webp" | absolute_url }})

Refactor code, you got v1.1

{% highlight java %}
public class ChatBot {

   public String talk(String ask) {
       if (ask.toLowerCase().contains("what is your mission")
               || ask.toLowerCase().contains("what's your mission")) {
           return "Kill John Conner.";
       } else {
           return "I don't know what you say.";
       }
   }
}
{% endhighlight %}

### It works
![]({{ "/assets/img/embedded-scripting-on-java-android/it-works.webp" | absolute_url }})

A few days later, requirements changed:

### A new scene added
![]({{ "/assets/img/embedded-scripting-on-java-android/a-new-scene-added.webp" | absolute_url }})

You should refactor code again, then you got something like:

{% highlight java %}
public class ChatBot {

   public String talk(String ask) {
       if (ask.toLowerCase().contains("what is your mission")
               || ask.toLowerCase().contains("what's your mission")) {
           return "Kill John Conner.";
       } else if (ask.toLowerCase().contains("What will you do after mission")) {
           return "Terminate myself.";
       } else {
           return "I don't know what you say.";
       }
   }
}
{% endhighlight %}

Things become more and more complicate, then you may want to extract the mutable logic:

![]({{ "/assets/img/embedded-scripting-on-java-android/application-structure.webp" | absolute_url }})

Scene can be describe as json easily:

{% highlight json %}
mission.json
----------------------------------------------------
{
 "rule": "what is your mission | what's your mission",
 "response": "Kill John Conner"
}


next_mission.json
----------------------------------------------------
{
 "rule": "what will you do after mission",
 "response": "Terminate myself"
}
{% endhighlight %}

The simplest SceneManager implementation:

{% highlight java %}
class SceneManager {

   private List<Scene> scenes;

   public SceneManager() {
       loadSceneJson();
   }

   public Scene findScene(String request) {
       for (Scene scene : scenes) {
           String[] split = scene.getRule().split("|");
           for (String s : split) {
               if (request.toLowerCase().contains(s.trim())) {
                   return scene;
               }
           }
       }

       return null;
   }
}
{% endhighlight %}

But mutable logic still in application.

If you want to define more complex scenes, SceneManger logic should be modified again and again.

Such as:

{% highlight json %}
"rule": "(what | how) & after mission"
{% endhighlight %}

A better way to describe rule is like:

{% highlight json %}
mission.json
-----------------------------------------------------------------------------------------------------
{
 "rule": "r = s.contains('what is your mission') or s.contains('what\'s your mission')",
 "response": "Kill John Conner"
}


next_mission.json
-----------------------------------------------------------------------------------------------------
{
 "rule": "r = (s.contains('what') or s.contains('how')) and s.contains('after mission')",
 "response": "Terminate myself."
}
{% endhighlight %}

Write rule as DSL format would got more flexibility.

This is how rule parser works:

![]({{ "/assets/img/embedded-scripting-on-java-android/rule-parser.webp" | absolute_url }})

Then you got a clear version of SceneManager:

{% highlight java %}
public Scene findScene(String request) {
   ruleParser.set("s", request);
   for (Scene scene : scenes) {
       if (ruleParser.execute(scene.getRule())) {
           if (ruleParser.get("r")) {
               return scene;
           }
       }
   }

   return null;
}
{% endhighlight %}

## EMBEDDED SCRIPT

Now we need an embedded script to implement our Rule Parser.

But what is embedded scripting language?

- An embedded scripting language would be a scripting language interpreter that can be embedded into applications. 
- The interpreter allowing scripts to control all or parts of the application.

With embedded scripting language, Application developers only have to provide the interface which can interact with the language, they don't need to implement the actual language.

To make an application "scriptable" can add great flexibility to an application or framework without recompiling.

There are many embedded scripting language for Java, such as Jython, JRuby, Groovy.

This is how embedded script work on Java:

![]({{ "/assets/img/embedded-scripting-on-java-android/embedded-script-on-java.webp" | absolute_url }})

## TASK 2

Not we try to port ChatBot program to Android, but it failed.

![]({{ "/assets/img/embedded-scripting-on-java-android/interpreters-cannot-work-on-android.webp" | absolute_url }})

Jython/JRuby/Groovy do not support compile to .dex

Lua is a powerful, efficient, lightweight, embeddable scripting language which written by C programming language. It is fast, portable, embeddable, powerful and small, works well with C.

We can make a Lua wrapper in Android native c++ and make a proxy in Java layer.

Let's see how it works:

![]({{ "/assets/img/embedded-scripting-on-java-android/lua.webp" | absolute_url }})

[Github Repo](https://github.com/jie-meng/LuaDroid)
