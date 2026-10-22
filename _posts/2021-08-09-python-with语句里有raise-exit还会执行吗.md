---
layout: post
title: "python with语句里有raise， exit还会执行吗"
date: "2021-08-09 20:50:00 +0800"
tags: ["python", "编程语言"]
categories: ["技术札记"]
---

<span id="测试代码"></span>

# 测试代码

```python
# test_raise.py
class test_context:
    def __enter__(self):
        print("enter")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit")


with test_context():
    print("in test_context1")
    raise ValueError("error!")
    print("in test_context2")
```

<span id="运行结果"></span>

# 运行结果

```bash
root@pve828qzz5mf6x:~/test# /usr/bin/python3.8 /root/vemu_v_link_check/test_raise.py
enter
in test_context1
exit
Traceback (most recent call last):
  File "/root/test/test_raise.py", line 14, in <module>
    raise ValueError("error!")
ValueError: error!
```

<span id="结论"></span>

# 结论

会执行

<span id="扩展"></span>

# 扩展

<a href="https://www.jianshu.com/p/e0a82b8802fa" rel="noopener" target="_blank">python with语句里有return， exit还会执行吗</a>

该扩展的结论：会执行，且是在return语句执行之后。
