---
title: AOSP partially build and test on emulator
layout: post
date: 2019-02-25 11:29:57 +0800
categories: android
---

## Make emulator filesystem writable

- After build AOSP, start emulator with command `emulator -writable-system`

- Run `adb remount` every time after emulator restart.

- Now you can use `mm` command to partially build modules of AOSP and use `adb push` to replace jars or apps of framework.

- You should always use `mm` to compile

For example, if you modified _/frameworks/base/core/res/res/values/dimens.xml_, then you can find its nearest make file _Android.bp_ under _/frameworks/base/core/res/_, then `mm` here.

After build, you'll see `[100% 8/8] Install: out/target/product/generic_x86/system/framework/framework-res.apk`, then push _framework-res.apk_ to emulator path _/system/framework/_. Restart emulator.

You put this script `push_build_output.py` to _AOSP_WORKSPACE/out/generic_x86/_ and run by _python3_, you will be asked to input output generated within minutes, script with which to find newest build outputs. After confirm, script will push all output files to emulator. Then restart emulator.

{% highlight python %}

import time
import sys
import os
import os.path
from datetime import datetime

print('Please input output generated within minutes:')
withInMins = int(input())
print('Find ouput files in {0} minutes ...'.format(withInMins))

# excludeSet
excludeSet = set()
excludeSet.add('build_fingerprint.txt')
excludeSet.add('build_thumbprint.txt')
excludeSet.add('update_time_check.py')
excludeSet.add('userdata-qemu.img.qcow2')

def filterFile(filename):
    basename = os.path.basename(filename)
    if basename in excludeSet:
        return False

    relativePath = filename.replace(os.getcwd(), '')

    if not relativePath.startswith('/system/'):
        return False

    if relativePath.startswith('/system/bin'):
        return False

    if relativePath.startswith('/system/lib'):
        return False

    return True

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)

def findFilesRecursively(path, pred = None, ls = None):
    if ls == None:
        ls = []

    for p in os.listdir(path):
        p = os.path.join(path, p)
        if os.path.isdir(p):
            findFilesRecursively(p, pred, ls)
        elif os.path.isfile(p):
            if not pred or pred(p):
                ls.append(p)

    return ls

if __name__ == "__main__":
    updateFiles = []
    ls = findFilesRecursively(os.getcwd())
    for f in ls:
        date = modification_date(f)
        difference = datetime.now() - date
        minutesDiff = int(difference.total_seconds() / 60.0)
        if minutesDiff < withInMins:
            if filterFile(f):
                updateFiles.append(f)

    # display udpate files
    for i, f in enumerate(updateFiles):
        print('{0}. {1}'.format(i + 1, f))

    print('push all files? (y/n)')
    confirm = input()
    if not confirm.lower().startswith('y'):
        print('cancel')
        sys.exit(0)

    os.system('adb remount')
    for i, f in enumerate(updateFiles):
        pathName = os.path.dirname(f.replace(os.getcwd(), ''))
        print('push {0}. {1}'.format(i + 1, f))
        os.system('adb push {0} {1}'.format(f, pathName))

    print('done')

{% endhighlight %}

## References

[How to mount /system rewritable or read-only? (RW/RO)](https://android.stackexchange.com/questions/110927/how-to-mount-system-rewritable-or-read-only-rw-ro)
