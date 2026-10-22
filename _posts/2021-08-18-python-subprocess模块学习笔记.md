---
layout: post
title: "python subprocess模块学习笔记"
date: "2021-08-18 20:34:00 +0800"
tags: ["python", "编程语言"]
categories: ["技术札记"]
---

# subprocess介绍

> 参考：[Python官方文档：subprocess — Subprocess management](https://docs.python.org/3.9/library/subprocess.html)

subprocess模块用于执行命令行命令。官方推荐的使用方法是使用模块中的`run()`方法，更高级的方法可以使用下层的`Popen()`方法。

## `subprocess.run()`

运行参数描述的命令，**等待命令完成**，并返回一个`CompletedProcess`实例。

参数中可以控制以下功能：

- 要执行的cmd
- 是否隐式执行shell，默认False。这个的意思是`["ls", "-l"]`和`ls -l`（隐式）的区别，后者会传递shell元字符（如`$`,`*`等）和空格，需要注意防止shell注入。
- 捕获标准输出和标准错误输出
- 设置超时
- 开启检查，cmd返回非0则报异常
- 传递环境变量
- ......

`subprocess.run()`的底层是`subprocess.Popen()`

## *class* `subprocess.CompletedProcess`

具有以下功能：

- 获取启动该进程所用的参数
- 获取返回code
- 获取标准输出和标准错误输出
- 检查返回值，若非0则报错

# 与多进程的区别

>  参考：
>
> [What is the difference between multiprocessing and subprocess?](https://stackoverflow.com/questions/13606867/what-is-the-difference-between-multiprocessing-and-subprocess)
>
> [Non blocking subprocess.call](https://stackoverflow.com/questions/16071866/non-blocking-subprocess-call)

如果想要调用非python语言的程序，可以用`subprocess`

如果想要在子进程中调用python函数，用`multiprocess`

如果想并行调用非python语言的程序，可以使用非阻塞的`subprocess.Popen()`

# 与os.system的区别

> 参考：[Difference between subprocess.Popen and os.system](https://stackoverflow.com/questions/4813238/difference-between-subprocess-popen-and-os-system)

subprocess.Popen是os.system的严格超集，它比os.system更灵活，替代了包括os.system在内的一些工具。