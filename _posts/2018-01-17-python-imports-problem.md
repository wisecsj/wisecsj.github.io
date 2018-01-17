---
layout:     post
title:      "Parent module '' not loaded ?"
subtitle:   "Python package,relative and absolute import"
date:       2018-01-17 23:00:00
author:     "wisecsj"
header-img: "img/post-bg-2015.jpg"
tags:
    - Python
    - Flask
---


## Preface

之前，在简书也有过写一些文章，但都比较水，也不怎么认真写。

在现在这个时代，记录一些东西是美好的，可贵的。

这也是为什么我又在github弄了一个Blog。

希望能帮助到自己和大家！

## 正文

起因是这样的：我在运行Flask官方文档的示例应用（不完全一致）的时候，出现了这么一个错误：

> SystemError: Parent module '' not loaded, cannot perform relative import

在这里，你得先弄明白模块的搜索路径 **sys.path**作用原理；以及什么是relative import，什么是 absolute import，参考[PEP328](https://www.python.org/dev/peps/pep-0328/).

这里说下我对绝对和相对的理解：使用到了 **.** 的import或者from...import语句为相对导入，其余的为绝对导入。(有误敬请指出)

如下：为代码结构，省去无关文件夹

```
└─flaskr
    │  app.py
    │  schema.sql
    │  views.py
    │  __init__.py

```
因为flaskr文件夹包含了 **\_\_init__.py** 文件，所以它被认为是一个 **Pacakge** 。

我首先在 **\_\_init__.py**文件内初始化了一个Flask实例：`app = Flask(__name__)`,用以给 **app.py** 和 **views.py**作相对导入：`from . import app`。

app.py 你可以简单理解为运行应用，等效于：
```
if __name__ == '__main__':
    app.run(debug=True)
```

(**这并不是最佳实践，请不要这么做。**)

views.py 是视图函数集合。

接下来，当我在Pycharm里的app.py文件右键Run，运行的时候，就出现了正文开头的错误。

----
## 原因
（windows下）

假设我们的当前工作目录是 /flaskr，当我们执行`python app.py` 时，解释器认为我们执行的是脚本文件。它会把文件的 **\_\_name__** 设置为`__main__`。而相对导入是 **根据`__name__`属性来工作的**。所以，当执行相对导入时，编译器不知道 **.** 指代哪个包，从而报错。

那么，如果把 app.py 相对导入改成绝对导入，是否可行呢？譬如：
`from flaskr import app`。答案是仍然不行。当解释器执行一个脚本文件时，它会把脚本文件的父级目录添加进 sys.path 中，即 /flaskr。也就是说，解释器会在 flaskr 文件夹下去寻找名为 flaskr 的Package,自然找不到了。

### Solution

那么，该怎么办呢？通过 `python -m ` 来完成。`python --help ` 查看 `-m` 的定义：
> -m mod : run library module as a script (terminates option list)

即将包下的某个模块作为脚本来运行。需要注意的是： **这条命令会将当前工作路径（cwd）加入到 sys.path，一定与之前情况进行区别**。

所以我们首先切换工作目录到 flaskr 的父目录 ，称之为 A。然后在 /A 下执行：`python -m flaskr.app` 即可。

### Surprise

然后，当我满心欢喜地照做的时候，还是没有正常执行。What the fuck ？？？

后来调试，发现，设置 `debug = False ` 就好了。如果你们用Flask并且开启调试模式，细心的话会发现控制台会打印 ` Restarting with stat` 这么一句话。

简而言之就是，应用会被重启一次，而第二次重启会被简单地当成脚本运行，导致又会出现正文开头的错误。

**PS**：不知道你发现没，flaksr package 下 ，我有一个名为 app 的module，同时还有一个名为 app 的Flask 实例。那么，当我执行` from flaskr import app `，它导入的是模块还是变量呢？大家不妨试试。

（**任何问题与错误敬请指出**）


