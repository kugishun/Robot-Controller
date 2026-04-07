# 机器人控制器

[日本語](README.md) | [English](README_en.md)

> **注意**：本文档为AI生成的翻译。请参阅原日文版README.md获取最准确的信息。

<!-- - stretch_sense的使用方法
- mocopi的使用方法
- 通过UDP通信向机械臂发送数据的方法
- 控制技巧 -->

## 文件结构
`hand_arm`：存放myCobot320 Pi的控制代码  
    L `arm_control.py`：控制代码  
    L `MyHand.py`：H-100库  
    L `test_h100.py`：H-100测试代码  
    L `requirement.txt`

`main_controller`：存放StretchSense、mocopi和myCobot的通信代码  
    L `main_controller_v1.py`：控制代码  
    L `requirement.txt`

## 环境搭建
- Python 3.11.13  
    - 各自的requirement.txt中有说明  
- Unity 6000.2.8f1或更高版本

## 应用程序设置
### 开始之前
请确认Mycobot320 Pi和电脑在同一网络上。

### mocopi应用
请在智能手机上下载mocopi应用。

请参考以下URL进行设置：  
https://www.sony.co.jp/en/Products/mocopi-dev/jp/documents/ReceiverPlugin/SendData.html

1. 设置mocopi应用与PC的连接
2. 将mocopi应用切换为发送模式

### stretch sense
请从以下URL下载Hand Engine Lite：
https://stretchsense.jp/product/hand-engine-lite/

从Edit → settings启用Open SDK。
将`Streaming IP Address`设置为`127.0.0.1`。
确认`Streaming Ports`设置为`9400`。
启用`perform/glove/status`、`animation/rotationWithMetacarpals`、`animation/slider/all`和`command/port/status`。

请按照以下教程进行设置：
英语：https://vimeo.com/953373249?fl=pl&fe=sh
日语（字幕）：https://vimeo.com/930428895?fl=pl&fe=sh

知识库：https://stretchsense.my.site.com/defaulthelpcenter26Sep/s/?language=en_US

### Unity
请从以下项目克隆到本地：
https://github.com/kugishun/mocopi_reciver

从Unity Hub的`Add project from disk`打开克隆的项目。

![alt text](img/add_new_project.png)

从图像左下方的`Assets/MoccopiReciver/Sample/Scenes`打开`ReciverSample`。
![alt text](img/add_assets.png)

确认`MocopiVectorSender`的`Remote Ip`设置为`127.0.0.1`，`Remote Port`设置为`7001`。

## 代码配置

在`/main_controller/main_controller_v1.py`中设置`MYCOBOT_IP`。
在MyCobot的终端中输入`ip a`。设置`inet`中显示的IP。

## 故障排除

如果完成这些设置后仍无法运行，可能是您的PC和MyCobot不在同一网络上。
请检查双方的网络。
