---
title: Add mermaid into github pages
layout: post
date: 2018-02-22 06:32:08 +0800
categories: web
---

To render beautiful graphs, sequence and Gantt diagrams and flowcharts via code, we can use the [Mermaid](https://github.com/knsv/mermaid) library.

Jekyll has a plugin to to simplify the creation of mermaid diagrams and flowcharts in your posts and pages. 

However, for safety reasons, if you want github automatically transform your post into web pages, you can’t use a plugin. 

We will make mermaid work on github pages without plugin.

## Steps

- Dowload [release version of Mermaid](https://github.com/knsv/mermaid/releases).

- Make a dir in your github pages project, such as `/mermaid`.

- Copy all files in mermaid/dist folder to your `/mermaid` directory.

- Open your github pages project `/layout/post.html`, add following code:

{% highlight html %}

<script src="/mermaid/mermaid.min.js"></script>
<link rel="stylesheet" href="/mermaid/mermaid.css">
<script>mermaid.initialize({startOnLoad:true});</script>

{% endhighlight %}

You can also change `href="/mermaid/mermaid.css"` to `href="mermaid.dark.css"` or `href="mermaid.forest.css"`.

Everything done, you can use mermaid graphs in your posts now:

{% highlight html %}

<div class="mermaid">
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
</div>

{% endhighlight %}

Then you would see:

<div class="mermaid">
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
</div>

## References

[Adding graphs via Mermaid](https://github.com/gnab/remark/wiki/Adding-graphs-via-Mermaid)

[Embed Mermaid Charts in Jekyll without Plugin](http://kkpattern.github.io/2015/05/15/Embed-Chart-in-Jekyll.html)

[Mermaid Doc](https://mermaidjs.github.io)

