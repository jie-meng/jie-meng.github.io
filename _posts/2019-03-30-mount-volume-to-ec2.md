---
title: mount volume to ec2
layout: post
date: 2019-03-30 12:00:07 +0800
categories: ops
---

## Prepare mount volume

First you need to create a volume and attach it to an existing ec2 instance on AWS console.

![]({{ "/assets/img/create-volume.webp" | absolute_url }})

## Mount volume to ec2

ssh to ec2, check volume with command `sudo fdisk -l`

![]({{ "/assets/img/fdisk.webp" | absolute_url }})

This is the 100GB volume you just attached.

format it with command `sudo mkfs.ext4 /dev/nvme1n1`

Then mount it to your expected path

`sudo mount /dev/nvme1n1 /var/lib/docker`

(e.g. _/var/lib/docker_)

## Mount volume automaticly after reboot

Above way of mount point will lost after reboot. You might need a solution to mount volume automaticly after every reboot.

You need to change _/etc/fstab_, so you should keep a backup `sudo cp /etc/fstab /etc/fstab.orig`

Then check volume UUID with command `sudo blkid`

![]({{ "/assets/img/blkid.webp" | absolute_url }})

Edit fstab `sudo vim /etc/fstab`

Append `UUID=f74db2e5-575d-427c-a907-d3167a273b52 /var/lib/docker ext4 defaults,nofail 0 2`

## Check validity

{% highlight shell %}

sudo umount /var/lib/docker
sudo mount -a
df -h

{% endhighlight %}

If you can see 100GB mount point as following figure, then it'll works on every reboot.

![]({{ "/assets/img/dfh.webp" | absolute_url }})

## References

[Making an Amazon EBS Volume Available for Use on Linux](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/ebs-using-volumes.html)

[Automatically Mount an Attached Volume After Reboot](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/ebs-using-volumes.html#ebs-mount-after-reboot)

[CREATING AN EXT4 FILE SYSTEM](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/s1-filesystem-ext4-create)

[在Amazon EC2中挂载EBS作为永久存储](https://blog.csdn.net/mxy_0223/article/details/70146153)
