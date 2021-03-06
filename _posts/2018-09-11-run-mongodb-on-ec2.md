---
title: Run mongodb on ec2
layout: post
date: 2018-09-11 09:13:34 +0800
categories: ops
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
Restart=always

[Install]
WantedBy=multi-user.target

{% endhighlight %}

Without **--bind_ip_all**, you cannot access mongodb cross internet.

**Restart=always** restarts mongod whenever it be killed or exit with an exception.

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

You can now connect mongod service on EC2 from terminal on your PC with command: `mongo --host {ec2 public IP}:{port}`.

## References

[install-mongodb-on-ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

[How to Install MongoDB on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-16-04)

[MongoDB: exception in initAndListen: 20 Attempted to create a lock file on a read-only directory: /data/db, terminating](https://stackoverflow.com/questions/42446931/mongodb-exception-in-initandlisten-20-attempted-to-create-a-lock-file-on-a-rea/43347884)

[mongodb：设置并使用账号密码登录](https://amberwest.github.io/2018/06/14/mongodb%EF%BC%9A%E8%AE%BE%E7%BD%AE%E5%B9%B6%E4%BD%BF%E7%94%A8%E8%B4%A6%E5%8F%B7%E5%AF%86%E7%A0%81%E7%99%BB%E5%BD%95/)

[给你的mongodb设置密码](https://segmentfault.com/a/1190000011554055)

[MongoDB 用户名密码登录](https://www.jianshu.com/p/79caa1cc49a5)
