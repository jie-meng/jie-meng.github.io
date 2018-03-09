---
title: Set up Android Jenkins CI on AWS EC2
layout: post
date: 2018-03-08 11:46:28 +0800
categories: android
---

## Goal

- Set up Jenkins CI master on EC2 (t2.micro)
- Set up Jenkins CI agent on EC2 (t2.small)
- Trigger CI on master, task run on agent.

<div class="mermaid">

sequenceDiagram
    participant Developer
    participant Github
    participant CI
    participant CI_agent
    Developer ->> Github: push code to Github master branch
    Developer ->> CI: trigger CI
    CI ->> CI_agent: assign task to agent
    CI_agent -->> Github: fetch code from Github
    CI_agent -->> CI_agent: build and test
    CI_agent -->> CI: Show result on CI master
</div>

## Set up Jenkins master

Launch an EC2 instance, t2.micro is enough.

### Allocate Elastic IP (Optional)

If you don't want your IP address of CI change after restart EC2 instance, you should allocate an Elastic IP to it.

Select your EC2 instance on console. Click **Actions -> Networking -> Manage IP Address**.

Then click **Allocate an Elastic IP**.

Click **Allocate** Button.

Bind your EC2 instance with Elastic IP. Make sure you do not have unused Elastic IP, otherwise it'll cost additional charge.

An Elastic IP address doesn’t incur charges as long as the following conditions are true:

- The Elastic IP address is associated with an Amazon EC2 instance.
- The instance associated with the Elastic IP address is running.
- The instance has only one Elastic IP address attached to it.

If you’ve stopped or terminated an EC2 instance with an associated Elastic IP address and you don’t need that Elastic IP address any more, consider disassociating or releasing the Elastic IP address.

After an Elastic IP address is released, you can’t provision that same Elastic IP address again, though you can provision a different Elastic IP address.

### Install docker

Connect to your EC2 instance with ssh, execute command:

**If your EC2 is Amazon Linux AMI**

{% highlight shell %}

sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker $USER

exit

{% endhighlight %}

**If your EC2 is Ubuntu**

{% highlight shell %}

sudo apt-get update
sudo apt-get install docker.io
sudo usermod -a -G docker $USER

exit
{% endhighlight %}

### Run jenkins

Connect to your EC2 instance again (After set docker sudo authority, you should exit and re-login, then it can take effect), execute command:

{% highlight shell %}

docker run -d -p 8080:8080 -p 8090:8090 jenkins

{% endhighlight %}

You can notice 8080 and 8090 port are exposed. (8080 for Jenkins server, 8090 for JNLP)

Then you should go back to your EC2 console, click the item belongs to you EC2 instance in **Security Groups** column.

Click **Inbound -> Edit -> Add Rule**.

Select **Custom TCP Rule**, input 8080 in **Port range** field. give a description such as: Jenkins.

Add Rule again, Then select **Custom TCP Rule**, input 8090 in **Port range** field. give a description such as: JNLP.

**Security Groups** is like firewall of EC2 instance, unless you add rules for specific ports, you cannot access them from internet.

![]({{ "/assets/img/ec2-inbound-add-rule.webp" | absolute_url }})

### Configure jenkins

Type (Public IP of EC2):8080 in your browser. you can access Jenkins now.

First you should input administrator password.

You can get it using `docker exec (container id) cat ...` on EC2.

After basic configuration, click **Manage Jenkins -> Configure Global Security**.

Set **TCP port for JNLP agents** to Fixed: 8090, then **Save**.

Click **Manage Jenkins -> Manage Nodes**, add a new agent.

- Name: android-agent-1
- #of executors: 1
- Remote root directory: /opt/jenkins
- Label: android
- Usage: Only build jobs with label expressions matching the node
- Launch method: Launch agent via Java Web Start
- Availability: Keep this agent online as much as possible

### Create Pipeline

Create a pipeline:
- Select **Pipeline script from SCM**
- SCM **Git**
- Repository URL **git@github.com:username/Project**
- Script Path **Jenkinsfile**

Add **credentials -> SSH Username with private key**.

Set your Username with your github username.

Select **Enter directly** for Private Key.

Input your private key (Get it from `cat ~/.ssh/id_rsa`) in **Key** field.

The Jenkinsfile in your project can be like this:

{% highlight shell %}

pipeline {
    agent {
        label "android"
    }
    stages {
        stage('Test') {
             steps {
                sh "./gradlew clean lintDevDebug checkDevDebug testDevDebug"
             }
        }
    }
}

{% endhighlight %}

## Set up Jenkins agent

Launch an EC2 instance, should be at least t2.small.

t2.micro cannot stand Android build task. (Gradle build daemon disappeared unexpectedly (it may have been killed or may have crashed)
)

Connect the agent instance, install docker.

Go back to your CI master page, click **android-agent-1** (which is still offline) in Build Executor Status.

![]({{ "/assets/img/jenkins-build-executor-status-offline.webp" | absolute_url }})

You can see:

_java -jar slave.jar -jnlpUrl http://(ip):8080/computer/android-agent-1/slave-agent.jnlp -secret a4234d6bca1e04c9421x8b27484a3d780c7g7af0aecsdb8fd2c96c89ac53ae42_

Copy the **ip** and **secret**.

Execute command on angent ec2 instance:

{% highlight shell %}

docker run -d --rm --name android-agent-1 jmengxy/android-sdk:jenkins-3.15-3859397-26-26.0.2 http://(ip):8080/ a4234d6bca1e04c9421x8b27484a3d780c7g7af0aecsdb8fd2c96c89ac53ae42 android-agent-1

{% endhighlight %}

Wait several seconds you would see:

![]({{ "/assets/img/jenkins-build-executor-status-ok.webp" | absolute_url }})

**android-agent-1** in no longer offline.

Trigger a build on CI, it'll work as you expected.

## References

[Install docker on AWS EC2 AMI instance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html#install_docker)

[What are Elastic IP addresses, and how do I use them?](https://aws.amazon.com/premiumsupport/knowledge-center/intro-elastic-ip-addresses/)

[Solving Docker permission denied while trying to connect to the Docker daemon socket](https://techoverflow.net/2017/03/01/solving-docker-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket/)
