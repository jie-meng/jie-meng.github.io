---
title: node mysql migration 
layout: post 
date: 2020-03-25 12:14:07 +0800
categories: web 
---

## Introduction

This article is about how to do mysql migration in node.js project.

## Setup mysql databse

We can setup a docker mysql for example.

{% highlight shell %}
docker run --name mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:5.7
{% endhighlight %}

after docker container started.

{% highlight shell %}

run 'mysql -h 127.0.0.1 -u root -p'
type 'root'
CREATE DATABASE mydb CHARACTER SET utf8 COLLATE utf8_general_ci;

{% endhighlight %}

### Add packages to your project and configure migrate scripts

_package.json_

{% highlight json %}

{
    "scripts": {
        "start": "node_modules/db-migrate/bin/db-migrate up && node src/main.js",
        "migrate-up": "node_modules/db-migrate/bin/db-migrate up",
        "migrate-down": "node_modules/db-migrate/bin/db-migrate down",
      },
    "dependencies": {
        "mysql": "^2.17.1",
        "db-migrate": "^0.11.6",
        "db-migrate-mysql": "^2.1.0"
    }
}

{% endhighlight %}

When you run `npm start`, migration-up will check all migration files and upgrade to the latest before application start.

When you run `npm run migrate-down`, the current database would only downgrade the latest migration in database. If you want to migrate-down 3 migrations, you should run `npm run migrate-down` 3 times.

### Create database.json

Create a _database.json_ file to the root of project. With database.json, db-migrate would know how to connect to database. [db-migrate Configuration](https://db-migrate.readthedocs.io/en/latest/Getting%20Started/configuration/)

_database.json_

{% highlight json %}

{
    "dev": {
        "host": { "ENV" : "MYSQL_HOST" },
        "user": { "ENV" : "MYSQL_USER" },
        "password" : { "ENV" : "MYSQL_PASSWORD" },
        "database": { "ENV" : "MYSQL_DATABASE" },
        "driver": "mysql"
    }
}

{% endhighlight %}

Make sure you have exported MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD and MYSQL_DATABASE to environment.

If the environment is not specified by the -e or --env option (db-migrate up --config config/database.json -e prod), db-migrate will look for an environment named dev or development. You can change this default behavior with the database.json file:

{% highlight json %}

{
    "defaultEnv": "local",
    "local": {
        "driver": "sqlite3",
        "filename": ":memory:"
    }
}

{% endhighlight %}

### Create migration files

Create a directory _migrations_ to the root of project.

Create a script new-migration.sh

{% highlight shell %}
node_modules/db-migrate/bin/db-migrate create $1
{% endhighlight %}

Execute `./new-migration.sh create-table-user`

There will be a new migration file _{timestamp}-create-table-user.js_ generated under ./migrations/

{% highlight javascript %}

'use strict';

var dbm;
var type;
var seed;

/**
  * We receive the dbmigrate dependency from dbmigrate initially.
  * This enables us to not have to rely on NODE_PATH.
  */
exports.setup = function(options, seedLink) {
  dbm = options.dbmigrate;
  type = dbm.dataType;
  seed = seedLink;
};

exports.up = function(db) {
  return null;
};

exports.down = function(db) {
  return null;
};

exports._meta = {
  "version": 1
};

{% endhighlight %}

Then you should implement the exports.up function and exports.down function such as 

{% highlight javascript %}

'use strict';

let dbm;
let type;
let seed;

/**
  * We receive the dbmigrate dependency from dbmigrate initially.
  * This enables us to not have to rely on NODE_PATH.
  */
exports.setup = (options, seedLink) => {
    dbm = options.dbmigrate;
    type = dbm.dataType;
    seed = seedLink;
};

exports.up = (db) => {
    return db.createTable('user', {
        id: {
            type: 'int',
            primaryKey: true,
            unsigned: true,
            notNull: true,
            autoIncrement: true,
            length: 10,
        },
        type: {
            type: 'string',
            notNull: true,
            length: 10,
        },
        username: {
            type: 'string',
            notNull: true,
            length: 32,
            unique: true,
        },
        password: {
            type: 'string',
            notNull: true,
            length: 32,
        },
        createdAt: {
            type: 'timestamp',
            defaultValue: String('CURRENT_TIMESTAMP'),
        },
        updatedAt: {
            type: 'timestamp',
            defaultValue: String('CURRENT_TIMESTAMP'),
        },
    }).then(() => {
        db.runSql('ALTER TABLE `user` CHANGE COLUMN `updatedAt` `updatedAt` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER `createdAt`;');
    });
};

exports.down = (db) => {
    return db.dropTable('user');
};

exports._meta = {
    version: 1,
};

{% endhighlight %}

{% highlight javascript %}

/* eslint-disable no-underscore-dangle */
/* eslint-disable arrow-body-style */
/* eslint-disable no-new-wrappers */
'use strict';

let dbm;
let type;
let seed;

/**
  * We receive the dbmigrate dependency from dbmigrate initially.
  * This enables us to not have to rely on NODE_PATH.
  */
exports.setup = (options, seedLink) => {
    dbm = options.dbmigrate;
    type = dbm.dataType;
    seed = seedLink;
};

exports.up = (db) => {
    return db.addColumn('user', 'phone', {
        type: 'string',
        length: 20,
    });
};

exports.down = (db) => {
    return db.removeColumn('user', 'phone');
};

exports._meta = {
    version: 1,
};

{% endhighlight %}

You can always do _db.runSql()_ if syntax of db-migrate cannot feed your demand.

{% highlight javascript %}

/* eslint-disable no-underscore-dangle */
/* eslint-disable arrow-body-style */
/* eslint-disable no-new-wrappers */
'use strict';

let dbm;
let type;
let seed;

/**
  * We receive the dbmigrate dependency from dbmigrate initially.
  * This enables us to not have to rely on NODE_PATH.
  */
exports.setup = (options, seedLink) => {
    dbm = options.dbmigrate;
    type = dbm.dataType;
    seed = seedLink;
};

exports.up = (db) => {
    return db.addColumn('user', 'notes', {
        type: 'text',
        notNull: true,
    }).then(() => {
        db.runSql("UPDATE user SET notes='';");
    }).then(() => {
        db.runSql('ALTER TABLE user MODIFY COLUMN notes TEXT NOT NULL;');
    });
};

exports.down = (db) => {
    return db.removeColumn('user', 'notes');
};

exports._meta = {
    version: 1,
};

{% endhighlight %}


## References

[db-migrate github](https://github.com/db-migrate/node-db-migrate)

[db-migrate doc](https://db-migrate.readthedocs.io/en/latest/)

[db-migrate Configuration](https://db-migrate.readthedocs.io/en/latest/Getting%20Started/configuration/)

[createing migrations](https://db-migrate.readthedocs.io/en/latest/Getting%20Started/usage/#creating-migrations)
