---
layout: post
title: "python signal OSError [Errno 22] Invalid argument错误"
date: "2021-08-10 20:12:00 +0800"
tags: ["python", "编程语言"]
categories: ["技术札记"]
---

错误代码内容：

```python
import signal
def signal_handler(sig, frame):
    pass
signal.signal(signal.SIGKILL, signal_handler)
```

报错:

```bash
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/python3/lib/python3.8/signal.py", line 47, in signal
    handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))
OSError: [Errno 22] Invalid argument
```

错误原因：

From the `man 7 signal`, it says

> The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored.

参考资料：

<a href="https://stackoverflow.com/questions/64282634/oserror-when-setting-sigkill-handler-in-mac-os-and-python" rel="noopener" target="_blank">OSError when setting SIGKILL handler in mac os and python</a>
