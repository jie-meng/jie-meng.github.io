---
title: setup docker registry with jenkins
layout: post
date: 2019-03-18 04:38:53 +0800
categories: ops
---

## Setup docker registry

You can setup docker registry simply by a single command

{% highlight shell %}

sudo docker run -d -p 5000:5000 -v `pwd`/data:/var/lib/registry --restart=always --name registry registry:latest

{% endhighlight %}

If you want to delete images pushed to registry, you'd better mapping the _config.yml_ locally, because you can enable delete in _config.yml_.

After registry setup, you can curl to check the catalog and taglist of images.

Here's a python3 script which can not only setup docker registry as a service but also access registry information / push image as a client.

[docker registry script](https://github.com/jie-meng/toolscripts/blob/master/docker/registry/docker-registry.py)

### http & https

If you setup docker registry on a server with https url, that would be easy to push image to registry. Otherwise you would got error message `server gave HTTP response to HTTPS client` when push image.

Then you should add registry ip:port to insecure-registries of docker client.

For linux, go to _/etc/docker/_ and create file _daemon.json_, add `{ "insecure-registries": ["ip:port"] }`. Then `service docker restart`.

For Mac, open docker client preference, edit daemon as following figure.

## Setup jenkins

If you want to use docker in jenkins, DO NOT use [jenkins-docker](https://github.com/jenkinsci/docker). That means you either need to install docker in jenkins docker or mapping host docker to jenkins. But neither of them is good choice.

You should install jenkins without docker.

On ubuntu, several commands would be OK. [install-jenkins-ubuntu](https://github.com/jie-meng/toolscripts/blob/master/jenkins/install-jenkins-ubuntu.sh)

Then you can operate it simply like [jenkins-service-op](https://github.com/jie-meng/toolscripts/blob/master/jenkins/jenkins-service-op.md).

### Give jenkins permission of host docker

Give permission of docker to jenkins user on host, or you'll error like `/var/run/docker.sock: connect: permission denied.`

{% highlight shell %}

sudo usermod -aG docker jenkins
sudo service jenkins restart

{% endhighlight %}

## CI Pipeline with docker registry

We have already setup docker-registry and jenkins, then we can setup a pipeline to clone project from github, build it on jenkins, push built image to registry.

Then we need to ssh to target machine, pull and run the image we just pushed.

### Install ssh plugins

2 plugins need to be installed on jenkins first: [SSH plugin & Publish Over SSH Plugin](https://stackoverflow.com/questions/18227009/jenkins-can-the-execute-shell-execute-ssh-commands).

### Give jenkins permission to ssh to target machine

- On Jenkins host, `sudo su -s /bin/bash jenkins`, `ssh-keygen`, `cat /var/lib/jenkins/.ssh/id_rsa.pub`, we got jenkins ssh public key.

- Add public key of jenkins to target machine's `~/.ssh/authorized_keys`.

- Login jenkins with `sudo su -s /bin/bash jenkins` on jenkins host, ssh to target machine mannualy first time, type 'yes' then jenkins can ssh to target machine freely on pipeline.

### Jenkins pipeline execute shell sample

{% highlight shell %}

docker build -t my-server .
docker tag my-server:latest docker-registry.domain.net/my-server-qa:${BUILD_NUMBER}
docker push docker-registry.domain.net/my-server-qa:${BUILD_NUMBER}
ssh ubuntu@ec2-00-11-22-33.us-west-1.compute.amazonaws.com "~/deploy-docker.sh qa ${BUILD_NUMBER}"

{% endhighlight %}

### deploy script on target machine

Target machine should install docker first, otherwise it cannot pull image from docker registry.

This is a sample deploy script of target machine which matches above execute shell sample.

{% highlight shell %}

sudo docker pull docker-registry.domain.net/my-server-$1:$2
sudo docker container stop $(sudo docker ps -f name=my-server -q)
sudo docker run --name my-server --rm -d -p 8080:8080 docker-registry.domain.net/my-server-$1:$2 $1
sudo docker system prune -a # save disk volume for server

{% endhighlight %}

## References

[部署私有Docker Registry](https://tonybai.com/2016/02/26/deploy-a-private-docker-registry/)

[docker registry script](https://github.com/jie-meng/toolscripts/blob/master/docker/registry/docker-registry.py)

[Docker学习之Docker Registry](https://www.jianshu.com/p/fef890c4d1c2)

[Private registry push fail: server gave HTTP response to HTTPS client](https://github.com/docker/distribution/issues/1874)

[jenkins-docker](https://github.com/jenkinsci/docker)

[Using Docker-in-Docker for your CI or testing environment? Think twice](http://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/)

[Jenkins在shell脚本运行docker权限报错解决](https://www.cnblogs.com/morang/p/9536622.html)

[Jenkins - can the “Execute Shell” execute SSH commands](https://stackoverflow.com/questions/18227009/jenkins-can-the-execute-shell-execute-ssh-commands)

[Jenkins Host key verification failed](https://stackoverflow.com/questions/15174194/jenkins-host-key-verification-failed)

[清理Docker的container，image与volume](http://note.qidong.name/2017/06/26/docker-clean/)
