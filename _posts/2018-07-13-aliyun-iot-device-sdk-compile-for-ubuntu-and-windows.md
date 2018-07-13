---
title: aliyun-iot device sdk compile for ubuntu and windows
layout: post
date: 2018-07-13 09:42:43 +0800
categories: iot
---

Aliyun-iot device SDK only provide Ubuntu16.04 compile manual, but it still support cross compile on windows with [MingGW](http://www.mingw.org/).

## Download SDK

Clone aliyun-sdk from [aliyun iotkit-embedded](https://github.com/aliyun/iotkit-embedded).

## Create cross-compile environment

Create **Dockerfile**:

{% highlight shell %}


FROM ubuntu:16.04

WORKDIR /app

RUN apt-get update &&\
        apt-get install -y build-essential make git gcc mingw-w64

CMD ["sh"]

{% endhighlight %}

Create **build_cross_compile_docker_image.py**:

{% highlight python %}

import os

os.system('docker build -t aliiotcrosscompile .')

{% endhighlight %}

Create **cross_compile_env.py**:

{% highlight python %}

import os

os.system('docker run --rm -it -v {}:/app aliiotcrosscompile sh'.format(os.getcwd()))

{% endhighlight %}

## Cross compile for windows on any OS with docker

- Create cross compile image:

    `python build_cross_compile_docker_image.py`

- Run cross compile container:

    `python cross_compile_env.py`

- Configuration and compile:

    `make reconfig`, then tips:

    ```
    1) config.ubuntu.x86
    2) config.win7.mingw32

    ```

    If you want ubuntu version select 1, for windows select 2.

    After configuration, you can type `make disclean`, and `make` to compile.

- Get output:

    Type `exit` to quit container shell, output file is under directory **output/release/bin**.

_ Help:

    - Execute `make env` in container shell, you can check current compile information.

    - If you want ubuntu version, do not exit container shell, Go to **output/release/bin** and execute compiled application. Windows version is cross compiled version，you need to copy it to windows machine and run it.

## References

[aliyun iotkit-embedded](https://github.com/aliyun/iotkit-embedded)

[MingGW](http://www.mingw.org/)
