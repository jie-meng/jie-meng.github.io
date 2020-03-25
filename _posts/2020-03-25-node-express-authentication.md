---
title: node express authentication
layout: post 
date: 2020-03-25 13:39:07 +0800
categories: web 
---

## Introduction

This article is about how to do authentication with node express.

### Add packages to your project

_package.json_

{% highlight json %}

{
    "dependencies": {
        "express": "^4.17.1",
        "body-parser": "^1.19.0",
        "passport": "^0.4.1",
        "passport-http": "^0.3.0",
        "passport-strategy": "^1.0.0",
    }
}

{% endhighlight %}

### Create Auth module

Create an _Auth.js_ module.

{% highlight javascript %}

const passport = require('passport');
const Strategy = require('passport-http').DigestStrategy;

const STRATEGY_DIGEST = 'digest';

class Auth {
    constructor(dbManager) {
        this._dbManager = dbManager;
        this._passport = passport;
        this.init();
    }

    init() {
        this._passport.use(STRATEGY_DIGEST, new Strategy({ qop: 'auth' },
            async (username, cb) => {
                const users = await this._dbManager.userDao.findUsers(username);
                if (users.length > 0) {
                    cb(null, users[0].username, users[0].password);
                } else {
                    cb(null, false);
                }
            }));
    }

    get digestAuth() {
        return this._passport.authenticate(STRATEGY_DIGEST, { session: false });
    }
}

module.exports = Auth;

{% endhighlight %}

If your service is deployed on cloud with envoy proxy, the DigestStrategy return 400 BadRequest, you have to customize the _digest.js_ of passport-http library. 

Put the following code to digest.js url checking part to deal with envoy proxy problem.

{% highlight javascript %}

const envoyOriginalPath = req.headers['x-envoy-original-path'];
const url = envoyOriginalPath || req.originalUrl || req.url;
if (url !== creds.uri) {
    return this.fail(400);
}

{% endhighlight %}

### Use auth strategy on API

{% highlight javascript %}

const express = require('express');
const bodyParser = require('body-parser');
const Auth = require('./auth/Auth');

const app = express();
app.use(bodyParser.json());

const userService = new UserService();
app.get('/api/user/fetchUsers', auth.digestAuth, userService.fetchUsers.bind(userService)));

// start server
app.listen(8080, () => console.log(`service is listening on port 8080`));

{% endhighlight %}

### Request API from client side

If client side is node.js, use [request](https://github.com/request/request) library to do api request.

{% highlight javascript %}

request.post({
        uri: `http://localhost:8080/${api}`,
        headers: {
            'Content-Type': 'application/json',
        },
        body: {
            // params
        },
        json: true,
        auth: {
            user: process.env.USER_NAME,
            pass: process.env.PASSWORD,
            sendImmediatey: false, // Digest authentication is supported, but it only works with sendImmediately set to false (sendImmediately defaults to true, which causes a basic authentication header to be sent).
        },
    }, (error, response, body) => {
        // deal with response or error 
    });

{% endhighlight %}

### References

[Bad request on digest authentication (User: false)](https://stackoverflow.com/questions/24284377/bad-request-on-digest-authentication-user-false)
