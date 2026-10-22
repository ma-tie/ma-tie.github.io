---
title: influx db  max-series-per-database错误
date: "2021-01-05 16:54:28 +0800"
tags: ["influxdb", "数据库"]
categories: ["技术札记"]
layout: post
---


## 环境

- influx版本：1.8

- 使用docker容器化的influx

## 问题描述

![](/assets/img/blog/mtank/image-20210105110838773.png)

如图，默认的最大series数是100W，如果再对一个新的series进行写入，则会出现错误。

## 相关资料

- [官方错误解释](https://docs.influxdata.com/influxdb/v1.8/troubleshooting/errors/#error-max-series-per-database-exceeded)

- [Max-series-per-database limit exceeded 1000000, error question](https://community.influxdata.com/t/max-series-per-database-limit-exceeded-1000000-error-question/12273)提到series可能会引发OOM（Out Of Memory，内存溢出）问题。

> The max-series-per-database limit exists only in the `inmem` index (the default in 1.x). It exists because the `inmem` index can cause the server to OOM if too many series are added to the index. 

- [How to Setup InfluxDB, Telegraf and Grafana on Docker: Part 1](https://thenewstack.io/how-to-setup-influxdb-telegraf-and-grafana-on-docker-part-1/)

## 解决方法

需要将influx的默认series数调整为0（无限制），顺便将每个tag对应的value数也调整为了0。

尝试在已启动的influx容器内修改配置，但遇到端口占用问题，无法重启influx服务，故在启动时就更改好influx的配置。

如果是非容器化的influx，应该直接修改`/etc/influxdb/influxdb.conf`文件并重新启动influx服务就行。

1. **使用以下命令生成influxdb配置文件：**

```bash
docker run --rm influxdb influxd config > influxdb.conf
```

2. **修改配置文件为以下内容：**

```bash
[meta]
  dir = "/var/lib/influxdb/meta"

[data]
  dir = "/var/lib/influxdb/data"
  engine = "tsm1"
  wal-dir = "/var/lib/influxdb/wal"
  max-series-per-database = 0
  max-values-per-tag = 0


[http]
  flux-enabled = true
```

3. **启动influxdb容器**

```bash
docker run --name influxdbService -d -p 8086:8086 -v $PWD/influxdb.conf:/etc/influxdb/influxdb.conf influxdb -config /etc/influxdb/influxdb.conf
```

