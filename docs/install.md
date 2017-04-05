# Installation Guide

This document describes how to install CENTrak from source, and run it as a dedicated 
server image. Using either [debian](http://www.debian.org/) or [ubuntu](http://www.ubuntu.com) 
for the operating system (OS) is recommended. If you choose a different server OS, you 
will need to replace the [apt-get](https://help.ubuntu.com/community/AptGet/Howto) 
command with the one corresponding to your system's package manager.

## *Required Steps*

## 1. Basic System Libraries and Packages

Install using a terminal or command-line prompt as the [root](https://wiki.debian.org/Root) 
user in debian or with the [sudo](https://help.ubuntu.com/community/RootSudo) 
command in ubuntu:

```
$ sudo apt-get update
$ sudo apt-get install build-essential git python3-dev
```

## 2. Define the centrak user account
Create <tt>centrak</tt>, the user account which will own and run the centrak processes,
and set its password:

```
$ sudo adduser centrak
$ sudo passwd centrak
```

## 3. Install [PostgreSQL](http://www.postgresql.org/)

## 4. Install [MongoDB](https://mongodb.org/)

Follow the comprehensive installation instruction by the developers of MongoDB 
for [debian](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian/) 
or [ubuntu](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/).

## 5. Install [Redis](https://redis.io/)

## *CENTrak Notes*

* Be sure to add the *celery* to the *centrak* group in order for the celeryd
process to have access to the *.pid* and *.log* files in target location own
by the *celery* user.