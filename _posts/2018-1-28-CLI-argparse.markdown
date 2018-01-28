---
layout:     post
title:      "命令行应用的编写与调试"
subtitle:   "实验楼比赛题目\"增加服务器管理功能\"题解 "
date:       2018-01-28
author:     "Wisecsj"
header-img: "img/post-bg-2015.jpg"
tags:
    - Python
    - CLI
    - VSCode
---

## [题目](https://www.shiyanlou.com/challenges/?tag=Python)

题目请自己点击链接查看

## 坑点

1. Python编写命令行程序库的选择，优先选 [argparse](https://docs.python.org/3/howto/argparse.html#id1)

2. 因为argparse会自动为我们添加optional options，与题目要求会冲突。解决办法也很简单,禁用**add_help**：`p = argparse.ArgumentParser(add_help=False)`

3. 题目要求的是支持 `server.py add -h 127.0.0.1 -u shiyanlou -p shiyanlou`这种方式的调用。命令的开头是没有Python的。所以你必须得在代码的第一行加上 `#! /usr/bin/python3 `。

4. VSCode如何对这种命令行参数的应用进行调试：修改lanuch.json，添加args字段，如下所示：
![launch.json](/img/in-post/post-cli-argparse/VSCode_config.png)

5. 
```
with open('test2.py','a+') as f:
    # or ` for l in f:`
    for l in f.readlines():     
        print(l)
```
上面的代码，执行你会发现没有输出。原因是当你以mode a+ 打开一个文件的时候：
> The file pointer is at the end of the file if the file exists.

[File Mode](https://stackoverflow.com/a/23566951)

所以你得先 `f.seek(0)`(将文件指针移到开头)


## 题解


```
#! /usr/bin/python3
# -*- coding: utf-8 -*-


""" 
@author: W@I@S@E </br>
@contact: wisecsj@gmail.com </br>
@site: https://wisecsj.github.io </br>
@file: server.py </br>
"""
import os, sys
import argparse

STORAGE_PATH = os.path.join(sys.path[0], 'serverinfo')
STORAGE_PATH_BAK = os.path.join(sys.path[0], 'serverinfo_bak')


def parser():
    p = argparse.ArgumentParser(add_help=False)

    # group = parser.add_mutually_exclusive_group()

    p.add_argument("operation", help='add | delete | list')

    p.add_argument('-h', help='server hostname')
    p.add_argument('-u', help='username')
    p.add_argument('-p', help='password')

    return p


class NEParaException(Exception):
    """
    Not Enough Para
    """

    def __init__(self, err='Not Enough Para'):
        super().__init__(err)


class NSOException(Exception):
    """
    Not Support Operation
    """

    def __init__(self, err='Not Support Operation'):
        super().__init__(err)


class SSAException(Exception):
    """
    Same Server Added
    """

    def __init__(self, err='Same Server Added'):
        super().__init__(err)


class ServerManager(object):
    def __init__(self, parser_generate):
        """

        :param parser_generate: func used to generate parser instance
        """
        if not os.path.exists(STORAGE_PATH):
            # os.mknod(STORAGE_PATH)    not support on windows
            with open(STORAGE_PATH, 'w'):
                pass

        self.parser = parser_generate()

        self.args = self.parser.parse_args()
        self.opr = self.args.operation

    def _add(self):
        h = self.args.h
        u = self.args.u
        p = self.args.p
        if h and u and p:
            with open(STORAGE_PATH, 'a+') as f:
                f.seek(0)
                for line in f:
                    exist_host = line.split()[0]
                    if h == exist_host:
                        raise SSAException
                else:
                    f.write('{} {}  {}\n'.format(h, u, p))
        else:
            raise NEParaException

    def _list(self):

        with open(STORAGE_PATH, 'r') as f:
            for line in f:
                print(line, end='')

    def _delete(self):

        with open(STORAGE_PATH, 'r') as f:
            with open(STORAGE_PATH_BAK, 'w') as g:
                h = self.args.h
                g.writelines(line for line in f if h not in line)
        os.remove(STORAGE_PATH)
        os.rename(STORAGE_PATH_BAK, STORAGE_PATH)

    def run(self):
        try:
            self.__getattribute__('_' + self.opr)()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    s = ServerManager(parser)
    s.run()

```

