---
title: Run mongodb on ec2
layout: post
date: 2018-09-11 09:13:34 +0800
categories: backend
---

## Install mongodb

Launch an ubuntu EC2 instance on AWS.

Change its security groups as

![]({{ "/assets/img/mongo-security-group.webp" | absolute_url }})

(Make TCP port 27017 in Inbound port range).

Install MongoDB Community Edition.

Install mongodb follow [install-mongodb-on-ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

## Run mongodb

Create a file **mongod.service** under _/etc/systemd/system/_.

{% highlight shell %}

[Unit]
Description=MongoDB Database Server
After=network.target

[Service]
User=ubuntu
ExecStart=/usr/bin/mongod --quiet --bind_ip_all --dbpath /home/ubuntu/data/db

[Install]
WantedBy=multi-user.target

{% endhighlight %}

(Without **--bind_ip_all**, you cannot access mongodb cross internet)

Next, start MongoDB with systemctl.

`sudo systemctl start mongod`

You can also use systemctl to check that the service has started properly.

`sudo systemctl status mongod`

Output

```

mongodb.service - High-performance, schema-free document-oriented database
   Loaded: loaded (/etc/systemd/system/mongodb.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2016-04-25 14:57:20 EDT; 1min 30s ago
 Main PID: 4093 (mongod)
    Tasks: 16 (limit: 512)
   Memory: 47.1M
      CPU: 1.224s
   CGroup: /system.slice/mongodb.service
           └─4093 /usr/bin/mongod --quiet --bind_ip_all --dbpath /home/ubuntu/data/db

```

The last step is to enable automatically starting MongoDB when the system starts.

`sudo systemctl enable mongod`

The MongoDB server is now configured and running, and you can manage the MongoDB service using the systemctl command (e.g. sudo systemctl stop mongod, sudo systemctl start mongod).

## Connect mongod

You can now connect mongod service on EC2 from terminal on your PC with command: `mongo --host {ec2 public IP}:27017`.

## References

[install-mongodb-on-ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

[How to Install MongoDB on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-16-04)