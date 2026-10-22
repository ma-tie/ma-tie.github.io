---
layout: post
title: "使用python的pyroute2在tc clsact在入口（ingress）和出口（egress）处添加bpf程序"
date: "2021-12-17 13:39:00 +0800"
tags: ["tc", "ebpf", "计算机网络"]
categories: ["技术札记"]
---

<span id="先上结论"></span>

# 先上结论

使用parent参数来控制入口（ffff:fff2）或是出口（ffff:fff3）。

```python
# add ingress clsact
ip.tc("add-filter", "bpf", idx, ":1", fd=fd, name="myprog",
      parent="ffff:fff2", classid=1, direct_action=True)
# add egress clsact
ip.tc("add-filter", "bpf", idx, ":1", fd=fd, name="myprog",
      parent="ffff:fff3", classid=1, direct_action=True)
```

<span id="前置知识"></span>

# 前置知识

> 参考资料：<a href="https://arthurchiao.art/blog/understanding-tc-da-mode-zh/" rel="noopener" target="_blank">tc基础、tc的direct-action模式及tc clsact</a>

（这里做简要复述，主要还是要看这个参考资料）

tc基础—使用tc时的大概几个步骤：

1.  创建队列规则qdisc。
2.  创建类别class，并attach到qdisc
3.  创建filter，并attach到qdisc。用于对流量分类，并将包分发至不同的class
4.  可给filter加action，决定丢包、转发等动作

tc的direct-action模式是将classifier的分类功能和action的动作功能合二唯一的一个功能，简化了流程，提升了性能。

tc clsact是一种队列规则qdisc，可以在入口（ingress）和出口（egress）处以direct-action模式attach bpf程序。

<span id="背景-amp-问题"></span>

# 背景 & 问题

使用bcc作为ebpf前端编程时，产生了如何在tc钩子处的入口和出口处添加bpf程序的疑问。

在bcc的examples里找到了一个在tc入口处丢弃所有包的<a href="https://github.com/iovisor/bcc/blob/master/examples/networking/xdp/xdp_drop_count.py" rel="noopener" target="_blank">例子</a>，该例子中，这样在tc入口处加载bpf程序：

```python
ip = pyroute2.IPRoute()
ipdb = pyroute2.IPDB(nl=ip)
idx = ipdb.interfaces[device].index
ip.tc("add", "clsact", idx)
ip.tc("add-filter", "bpf", idx, ":1", fd=fn.fd, name=fn.name,
      parent="ffff:fff2", classid=1, direct_action=True)
```

看的人很疑惑，完全找不到关于入口/出口的关键字。

<span id="解决"></span>

# 解决

<span id="pyroute2例程"></span>

## pyroute2例程

去翻了pyroute2关于clsact的<a href="https://pyroute2.org/pyroute2-0.3.21.post127/iproute.html#clsact" rel="noopener" target="_blank">官方文档</a>，里面有这样一段例程：

```python
# BPF ingress/egress example using clsact qdisc:

# open_bpf_fd is outside the scope of pyroute2
#fd = open_bpf_fd()
eth0 = ip.get_links(ifname="eth0")[0]
ip.tc("add", "clsact", eth0)
# add ingress clsact
ip.tc("add-filter", "bpf", idx, ":1", fd=fd, name="myprog",
      parent="ffff:fff2", classid=1, direct_action=True)
# add egress clsact
ip.tc("add-filter", "bpf", idx, ":1", fd=fd, name="myprog",
      parent="ffff:fff3", classid=1, direct_action=True)
```

可以看到bcc的例程和pyroute2例程的公共点是入口处的程序都使用了ffff:fff2这个parent，另外pyroute2例程在出口处使用了ffff:fff3这个parent。

<span id="小实验"></span>

## 小实验

于是自己运行代码跑了一下小实验，想看下不同的parent会有什么影响。结果除了ffff:fff2和ffff:fff3外的所有parent都会报`pr2modules.netlink.exceptions.NetlinkError: (2, 'No such file or directory')`错误。证明ffff:fff2和ffff:fff3应该是某个特定的数字。

<span id="tc-clsact相关linux源码"></span>

## tc clsact相关linux源码

去翻阅了linux tc clsact的commit记录，找到了以下代码：

```c
 #define TC_H_UNSPEC	(0U)
 #define TC_H_ROOT	(0xFFFFFFFFU)
 #define TC_H_INGRESS    (0xFFFFFFF1U)
+#define TC_H_CLSACT	TC_H_INGRESS
+
+#define TC_H_MIN_INGRESS	0xFFF2U //ffff:fff2
+#define TC_H_MIN_EGRESS		0xFFF3U // ffff:fff3
```

这说明：**ffff:fff2和ffff:fff3是tc clsact的ingress和egress两个class的ID，因此加filter时对应的parent要写它两。因此，也就不难理解上述各个例程中的写法。**
