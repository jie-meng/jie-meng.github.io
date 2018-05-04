---
title: How to use AWS IOT Device SDK CPP
layout: post
date: 2018-05-03 01:29:52 +0800
categories: iot
---

This article mainly discussing about:

- How to compile [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp).

- How to make [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp) a library for other application to use.

- How to make use of aws-iot-device-sdk-library.

on MacOS and Windows.

---

## MacOS

### Compile SDK

First you should setup the dev environment for [MacOS Platform](https://github.com/aws/aws-iot-device-sdk-cpp/blob/master/Platform.md).

- install brew

- `brew update && brew upgrade`

- `brew install cmake`

- `brew install openssl` (make sure openssl version is 1.0.2 and check openssl path by command `brew info openssl`)

- get the path of openssl, might be **/usr/local/opt/openssl**

- get source code of [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp)

- go to directory of **aws-iot-device-sdk-cpp**, `mkdir build`, `cd build`

- ```
cmake -DOPENSSL_ROOT_DIR=/usr/local/opt/openssl -DOPENSSL_LIBRARIES=/usr/local/opt/openssl/lib -DOPENSSL_INCLUDE_DIR=/usr/local/opt/openssl/include  ../.
```

- `make pub-sub-sample`, then you got **pub-sub-sample** in **project_path/build/bin**

- copy all certs and keys of your iot thing to **project_path/build/bin/certs**

- copy a **SampleConfig.json** to **project_path/build/bin/certs/config**, change following values to your keys and endpoint:

    - "endpoint": ""
    - "root_ca_relative_path": "certs/rootCA.crt"
    - "device_certificate_relative_path": "certs/cert.pem"
    - "device_private_key_relative_path": "certs/privkey.pem"

- Run `./pub-sub-sample`, it'll send & receive some test messages on the MQTT topic **sdk/test/cpp**

### Make SDK library

- setup environment (cmake, openssl) as the above steps.

- get source code (branch: feature_shared_lib) of [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git) which is a fork version of [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp), a library project implemented.

- go to directory of **aws-iot-device-sdk-cpp**, `mkdir build`, `cd build`

- ```
cmake -DOPENSSL_ROOT_DIR=/usr/local/opt/openssl -DOPENSSL_LIBRARIES=/usr/local/opt/openssl/lib -DOPENSSL_INCLUDE_DIR=/usr/local/opt/openssl/include ../.
```

- `make`, then you got all static liraries (**libiot-client.a libaws-iot-sdk-cpp.a** in project_path/build/archive) for building a shared library

- go to directory **project_path/samples/AWSIOTDevice**, `cmake .`, `make`, you'll got shared library **libaws-iot-device.dylib**, header file **AWSIOTDevice.h** is also what you need for building an application use this library

### Use SDK library

A stand-alone project **AWSIOTUser** was implemented in [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git)/samples, which would not compile when the entire project [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git) compile, you should complile it manually.

-  `cd aws-iot-device-sdk-cpp/samples/AWSIOTUser`

- `cmake .`

- `make`, then you got application **AWSIOTUser**

- copy all certs and keys of your iot thing to **project_path/samples/AWSIOTUser/certs**

- copy a **SampleConfig.json** to **project_path/samples/AWSIOTUser/config**, change following values to your keys and endpoint:

    - "endpoint": ""
    - "root_ca_relative_path": "certs/rootCA.crt"
    - "device_certificate_relative_path": "certs/cert.pem"
    - "device_private_key_relative_path": "certs/privkey.pem"

- Run `./AWSIOTUser`, it'll send a test messages on the MQTT topic **sdk/test/cpp**

---

## Windows

### Compile SDK

First you should setup the dev environment for [Windows Platform](https://github.com/aws/aws-iot-device-sdk-cpp/blob/master/Platform.md).

- install VS2017

- install cmake

- download and install [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

- get the path of openssl, might be **D:\OpenSSL-Win32** or **D:\OpenSSL-Win64**

- get source code of [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp)

- go to directory of **aws-iot-device-sdk-cpp**, `mkdir build`, `cd build`

- to build 32 bit version,
```
cmake -G "Visual Studio 15 2017" -DOPENSSL_ROOT_DIR=D:\OpenSSL-Win32 -DOPENSSL_LIBRARIES=D:\OpenSSL-Win32\lib -DOPENSSL_INCLUDE_DIR=D:\OpenSSL-Win32\include ../.
```

- to build 64 bit version,
```
cmake -G "Visual Studio 15 2017 Win64" -DOPENSSL_ROOT_DIR=D:\OpenSSL-Win64 -DOPENSSL_LIBRARIES=D:\OpenSSL-Win64\lib -DOPENSSL_INCLUDE_DIR=D:\OpenSSL-Win64\include ../.
```

- open **project_path/build/aws-iot-sdk-cpp.sln** with Visual Studio 2017, build solution

- Although there might be 4 errors (warning treated as error), ignore them. You already got **pub-sub-sample.exe** in **project_path/build/bin/Debug**

- copy all certs and keys of your iot thing to **project_path/build/Debug/bin/certs**

- copy a **SampleConfig.json** to **project_path/build/Debug/bin/certs/config**, change following values to your keys and endpoint:

    - "endpoint": ""
    - "root_ca_relative_path": "certs/rootCA.crt"
    - "device_certificate_relative_path": "certs/cert.pem"
    - "device_private_key_relative_path": "certs/privkey.pem"

- Run `pub-sub-sample.exe`, it'll send & receive some test messages on the MQTT topic **sdk/test/cpp**

### Make SDK library

- setup environment (cmake, openssl) as the above steps.

- get source code (branch: feature_shared_lib) of [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git) which is a fork version of [aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp), a library project implemented.

- go to directory of **aws-iot-device-sdk-cpp**, `mkdir build`, `cd build`

- to build 32 bit version,
```
cmake -G "Visual Studio 15 2017" -DOPENSSL_ROOT_DIR=D:\OpenSSL-Win32 -DOPENSSL_LIBRARIES=D:\OpenSSL-Win32\lib -DOPENSSL_INCLUDE_DIR=D:\OpenSSL-Win32\include ../.
```

- to build 64 bit version,
```
cmake -G "Visual Studio 15 2017 Win64" -DOPENSSL_ROOT_DIR=D:\OpenSSL-Win64 -DOPENSSL_LIBRARIES=D:\OpenSSL-Win64\lib -DOPENSSL_INCLUDE_DIR=D:\OpenSSL-Win64\include ../.
```

- open **project_path/build/aws-iot-sdk-cpp.sln** with Visual Studio 2017, build solution, then you got all static liraries (**iot-client.lib aws-iot-sdk-cpp.lib** in project_path/build/archive/Debug) for building a shared library

- go to directory **project_path/samples/AWSIOTDevice**, `cmake -G "Visual Studio 15 2017" .`

- open **project_path/samples/aws-iot-device.sln**, build solution, you'll got shared library **aws-iot-device.dll aws-iot-device.lib**, header file **AWSIOTDevice.h** is also what you need for building an application use this library

### Use SDK library

A stand-alone project **AWSIOTUser** was implemented in [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git)/samples, which would not compile when the entire project [jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git) compile, you should complile it manually.

- `cd aws-iot-device-sdk-cpp/samples/AWSIOTUser`

- `cmake -G "Visual Studio 15 2017" .`

- open **AWSIOTUser.sln** with Visual Studio 2017, build project **AWSIOTUser**. then you got application **AWSIOTUser.exe**

- copy **aws-iot-device.dll** from **project_path/build/bin/Debug** to **AWSIOTUser/Debug**

- copy all certs and keys of your iot thing to **project_path/samples/AWSIOTUser/Debug/certs**

- copy a **SampleConfig.json** to **project_path/samples/AWSIOTUser/Debug/config**, change following values to your keys and endpoint:

    - "endpoint": ""
    - "root_ca_relative_path": "certs/rootCA.crt"
    - "device_certificate_relative_path": "certs/cert.pem"
    - "device_private_key_relative_path": "certs/privkey.pem"

- Run `AWSIOTUser.exe`, it'll send a test messages on the MQTT topic **sdk/test/cpp**

## References

[aws/aws-iot-device-sdk-cpp](https://github.com/aws/aws-iot-device-sdk-cpp)

[jie-meng/aws-iot-device-sdk-cpp](https://github.com/jie-meng/aws-iot-device-sdk-cpp.git)
