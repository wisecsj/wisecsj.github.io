---
layout:     post
title:      "How Fiddler works with other proxy on Windows"
subtitle:   "Dial-up/VPN Proxy and LAN Settings"
date:       2018-01-22 18:00:00
author:     "wisecsj"
header-img: "img/post-bg-2015.jpg"
tags:
    - Windows
    - Proxy
    - Fiddler
---

### [问题描述](https://www.v2ex.com/t/424749)

简而言之就是，在我先开启$$（无论是PAC还是全局模式）再开启Fiddler的情景下：各方代理是如何工作的，为何能保证各自功能正确实现？

我先是在V站提了这个问题（问题描述的链接），后来又Google到一篇写的很好的关于Windows代理的blog：

[Understanding Web Proxy Configuration](https://blogs.msdn.microsoft.com/ieinternals/2013/10/11/understanding-web-proxy-configuration/)

并且本文最后会附上这篇文章的译文（部分我觉得无关紧要的没有翻译）

### 问题答案

（请先看过上文提到的blog）

Windows并没有真正系统层面上的代理（截至blog发表时间），各应用可以通过WinINET或者WinHTTP或者其他方法设置代理。譬如IE的代理（Chrome代理设置走的就是IE的）是通过WinINET设置的，并且会作用在系统设置中的代理上。

具体表现行为就是，在我打开$$的PAC模式，他们虽然UI不同，但是代理设置是一致的。见下图：

![IE_proxy](/img/in-post/post-windows-proxy/IE_proxy.png)

![System_proxy](/img/in-post/post-windows-proxy/System_proxy.png)

那么，当我再打开Fiddler会发生什么呢？自然就是**LAN代理服务器**被设置为127.0.0.1:8888(默认端口下)。

问题来了，这时你访问Google，你会发现还能够正常访问。并且，**Fiddler是能够正常抓到浏览器发出的HTTP/HTTPS包的**

Excume me???

原因在于，Fiddler内部在设置“系统代理”时，会先检测代理是否为空，不为空，记录下来，称作A代理。这样，Chrome发出请求时，就会先走Fiddler，Fiddler再转发给A代理，从而实现Google的正常访问（同时数据包也能够正常抓取了）。


### 译文



在过去的十年里，我学到了很多关于Web代理方面的知识，并且将我的Web debugger作为一个代理来实现。在这篇文章里，我将提供代理相关知识的一个概览，譬如发生在Internet Explorer 11 / Windows 8.1 的改变。

### The "System Proxy"

不同于其它的系统，譬如Mac OSX,Windows 事实上并没有系统代理这么一个概念。
**大多数**应用尊重WinINET代理设置，但也有的并不。

* Firefox 尊重WinINET设置，当代理设置被设为"使用系统代理设置"
* WinHTTP-based 应用有可能尊重也有可能不尊重（见下文）。
* 使用.NET 框架建立的应用一般都会采用系统代理，当它们启动时（并且在运行时并不会去检测是否改变）。同时，`app.exe.config`或者`machine.config`文件可以覆盖代理设置。

由于历史原因，大多数应用通过WinINET建立，因此直接遵守代理设置。但是如今，越来越多的应用依赖WinHTTP（或者是像BITS这样的后起框架）和System.NET而建立，所以可能需要额外的设置。

### Setting are Per-User

WinINET代理设置一般是对用户而言而不是单台机器。这意味着个人用户（甚至非管理员）可以设置他们自己的代理设置而不影响其他账号。WinINET可以通过在注册表创建一个名为`HKLM\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ProxySettingsPerUser`，类型为DWORD，值为0的键来使得代理配置在机器范围内生效。之后，只有获得管理员权限的应用可以对代理设置进行更改。

### Configuring the Proxy

通过在IE浏览器里点击 **Tools > Internet Options > Connections**可以设置WinINET代理设置。在`connetctions`选项上，选择一个连接然后点击`Settings`按钮。对大多数用户而言，代理是通过对话框底部的**LAN Settings**按钮来设置的。

**设置优先级: Part 1：** 虽然拨号/ VPN / RAS连接和LAN设置按钮的代理设置可以独立配置，但内部，WinINET将使用任何活动/已连接的拨号/ VPN / RAS连接设置。否则，LAN代理设置将被采用。许多用户错误地期望WinINET在选择代理之前首先确定使用哪个网络接口来建立给定的连接;但它并非如此工作。

### Proxy Configurations

当你设置你的代理时，下面的对话框将会出现![](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Blogs.Components.WeblogFiles/00/00/00/47/13/metablogapi/3173.image_0DBDE717.png)

**设置优先级: Part 2:** 

上图中的设置按其优先级顺序依次排列下来。首先，参考**自动检测设置**，然后是**自动配置脚本**，如果他们两个都未设置的话，最后才是**固定代理服务器**。

### Automatically Detect Settings

当开启**自动检测代理设置**后，IE执行一个叫做[ Web Proxy Auto-Detection ](http://en.wikipedia.org/wiki/Wpad)(WPAD)的进程。这个进程由两部分组成：

1. 发出DHCP INFORM查询，要求DHCP提供代理脚本的URL
2. 搜索当前域中前缀为WPAD的服务器(e.g. wpad.corp.contoso.com)

这些操作不一定是并行执行的，取决于网络栈。一些浏览器，比如Firefox,只负责了DNS检测，跳过了[DHCP detection](https://bugzilla.mozilla.org/show_bug.cgi?id=356831)。为性能着想，某些客户端可能会在每个网络的基础上缓存检测结果（“SmartWPAD”），当连接到已知不使用WPAD的网络时，会跳过未来会话中的WPAD进程。

如果客户端自动检测到了代理脚本的URL，它将会尝试下载并作为配置使用。

### Automatic Configuration Script

用户也可以直接在对话框的第二个复选框里声明代理配置脚本的URL。下面的URL直接指向目标脚本(e.g. http://proxy.contoso.com/proxy.pac).

[Proxy configuration scripts](http://en.wikipedia.org/wiki/Proxy_auto-config)，无论是通过WPAD发现还是用户手动设置，都是一个至少包含函数`FindProxyForURL(url, host)`的JavaScript文件。每当浏览器需要决定一个给定请求需要发送到哪儿时，这个函数就会被其调用。它返回一个字符串，可以是：

1. `“DIRECT”`，意味着这次请求不走代理

2. `PROXY PrimaryProxy:8080; BackupProxy:81`，意味着请求应该被转发到代理 **PrimaryProxy**的8080端口，若此服务器不可达，将被转发到 **BackupProxy** 的81端口。

WinINET还提供了另一个函数[ FindProxyForURLEx](http://msdn.microsoft.com/en-us/library/windows/desktop/gg308477(v=vs.85).aspx),用来支持[IPv6-aware proxy scripts](http://blogs.msdn.com/b/wndp/archive/2006/07/18/ipv6-wpad-for-winhttp-and-wininet.aspx).

#### NOTE: Proxy Scripts Impact the Zone

Warning:代理脚本一个有时令人惊讶的方面是它们影响了Internet Explorer安全区的确定。 总结我的长篇MSDN文章和博文，默认情况下，如果代理脚本正在使用并返回DIRECT，目标站点将被映射到本地Intranet区域。

#### NOTE: File://-based Proxy Scripts Deprecated

PASS 

#### NOTE: File://-based Proxy Scripts Require “Unhealthy” Syntax

PASS

#### NOTE: IE11 Deprecates Non-Silent Auth when downloading Proxy Script

PASS

### Fixed Proxy Configuration

除了自动代理检测外，用户也可以手动配置代理。默认情况下，UI如下：![](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Blogs.Components.WeblogFiles/00/00/00/47/13/metablogapi/5875.image_04A135C9.png)

...点击**高级**按钮显示更多选项：![](https://msdnshared.blob.core.windows.net/media/MSDNBlogsFS/prod.evol.blogs.msdn.com/CommunityServer.Blogs.Components.WeblogFiles/00/00/00/47/13/metablogapi/1261.image_689076DD.png)

你可以为不同的协议配置不同的代理服务器，也可以使用默认选项让所有协议走同一个代理服务器。

### Setting the Proxy Programmatically

Fiddler和一些其他的应用可能会通过编程的方式来改变WinINET代理设置。

相比较于直接尝试修改注册表的键，通过`InternetSetOption `API来更新代理设置是更为合适的方法。

无论你用的是C/C++或者 .NET,使用这个API都很简单。

### WinHTTP Considerations

> 感谢 Eric Loewenthal，WinHTTP 代理代码的作者，提供了这一章节所需的专业知识。

WinHTTP栈是为了在服务中使用和其他WinINET不适合的场景下而设计的。WinHTTP提供代理支持的有限子集-----通常来讲，调用代码是期望直接设置代理设置在每个会话或者请求对象上。

配置工具主要是用作系统运行的WinHTTP应用程序（无需用户模拟）。

编写规范的WinHTTP应用将会：

1. If not running in a user's process, impersonate a user

2. Call `WinHttpGetIEProxyConfigForCurrentUser`

3. Plug the returned settings into WinHttpGetProxyForUrl
