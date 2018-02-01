---
layout:     post
title:      "Let's talk about logging module"
subtitle:   "logging模块的使用和注意事项"
date:       2018-01-31 18:00:00
author:     "wisecsj"
header-img: "img/post-bg-2015.jpg"
tags:
    - logging
    - 日志
    - Python
---
### Preface

推荐阅读：

[PEP282](https://www.python.org/dev/peps/pep-0282/)( 提出者就是logging模块的作者)

[Good logging practice in Python](https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/)

[官方文档](https://docs.python.org/3/library/logging.html)( 以及开头右端的三个Tutorial)

### 基础性的介绍

Logging是用来track在软件运行过程中事件的发生的。软件工程师可以通过它来声明某些事件的发生。事件可以由描述性信息加上数据变量组成。

我们可以声明事件的重要性，一般称作等级（level）或者严重程度(severity)。

![Five Level Introduction](/img/post-logging/five_level.png)

**Note**: 默认进行处理的level是WARNING，只有高于或等于此等级的日志会被track.

被捕捉到的时间可以用不同的方式去处理。最简单的处理莫过于直接输出到控制台；另一种通常使用的方式是写入到日志文件中。

**其他的就不多言了，阅读推荐阅读的几篇文章就好**

### 进阶与技巧

* 我们经常会有这么一个需求，需要在抛出异常时，将异常的具体信息也记录到日志中。我们可以这么做：
```
try:
    a = 1/0
except Exception as e:
    logger.exception('something error')
```

`exception`实质是对logger.error的封装，设置参数`exc_info = True`。

所以如果我们有比较奇葩的需求，譬如在 info level 也打印异常信息怎么办：`logger.info(msg,exc_info=True)`

* 另一个也很常见的需求是，我们需要把日志保存到文件，方便调试和排查错误。一开始是只有**FileHandler**的，但是在生产环境中，日志文件大小会增长。所以后来有了[RotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)以及[TimedRotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler).
前者可以通过设置 maxBytes 来使得文件大小不超过此字节数；后者可以通过设置间隔或特定时间点来更新（生成新的）日志文件。

    此外的[SMTPHandler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.SMTPHandler)也可以非常方便地发送邮件。

### 根节点（RootNode)
先来看看其定义：
```
class RootLogger(Logger):
    """
    A root logger is not that different to any other logger, except that
    it must have a logging level and there is only one instance of it in
    the hierarchy.
    """
    def __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        Logger.__init__(self, "root", level)
```
非常简单，仅仅是将Logger类初始化方法中的name参数设置为了'root'而已。

再加上这几行代码：
```
root = RootLogger(WARNING)
Logger.root = root
Logger.manager = Manager(Logger.root)

```
第一行代码意味着RootLogger的level默认值为WARNING。
Manager是一个掌握loggers层级结构的单例类。其中我们非常熟悉的Moudule-Level的getlogger就是调用的此类的同名方法。

我们再来看看Moudule-Level的info、error等方法的代码：
```
def error(msg, *args, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    if len(root.handlers) == 0:
        basicConfig()
    root.error(msg, *args, **kwargs)
```
`basicConfig()`是针对根节点logger的系列设置。当参数列表为空时，默认生成一个写入到`sys.stderr`的StreamHandler以及一个比较美观的Formatter绑到RootLogger.

**NOTE：** 当我们新生成一个Logger实例时，level默认值是NOTSET（0）。如果不调用setLevel进行设置的话，库内部会调用`getEffectiveLevel`函数不断查找其父节点level不为0的值，不存在则返回NOTSET。

### 线程安全：
> The logging system should support thread-safe operation without any special action needing to be taken by its users.

Logging是通过[threading.RLock](https://docs.python.org/3/library/threading.html?highlight=threading#threading.RLock),即可重入锁来实现线程安全的。

我们知道，当多个线程同时对共享数据，譬如Manager类里的`loggerDict`进行修改时，是需要加锁的。那么，用`threading.Lock`不行么，是什么导致的需要用可重入锁呢？

官方模块里关于此的一段注释：
> #_lock is used to serialize access to shared data structures in this module.
#This needs to be an RLock because fileConfig() creates and configures
#Handlers, and so might arbitrary user threads. Since Handler code updates the</br>
#shared dictionary _handlers, it needs to acquire the lock. But if configuring
#the lock would already have been acquired - so we need an RLock.</br>
#The same argument applies to Loggers and Manager.loggerDict.

可以看到与_handlers和fileConfig()有关系：
```
_handlers = weakref.WeakValueDictionary()  #map of handler names to handlers
_handlerList = [] # added to allow handlers to be removed in reverse of order initialized


def fileConfig(fname, defaults=None, disable_existing_loggers=True):
    """
    Read the logging configuration from a ConfigParser-format file.

    This can be called several times from an application, allowing an end user
    the ability to select from various pre-canned configurations (if the
    developer provides a mechanism to present the choices and load the chosen
    configuration).
    """
    import configparser

    if isinstance(fname, configparser.RawConfigParser):
        cp = fname
    else:
        cp = configparser.ConfigParser(defaults)
        if hasattr(fname, 'readline'):
            cp.read_file(fname)
        else:
            cp.read(fname)

    formatters = _create_formatters(cp)

    # critical section
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        # Handlers add themselves to logging._handlers
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()


```
----

关于线程安全的具体分析等之后有空再来填坑

---
最后再来一张官方文档的流程图：
![Logging Flow](https://docs.python.org/3/_images/logging_flow.png)