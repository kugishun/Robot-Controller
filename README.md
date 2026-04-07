# Robot-Controller
<!-- - stretch_senseの使い方
- mocopino使い方
- UDP通信をしてロボットアームにデータを送信する方法
- 制御方法のコツ -->


## ファイル構成
 ``hand_arm``: myCobot320 Piの制御用コードが格納されている  
    L ``arm_control.py``    : 制御用コード  
    L ``MyHand.py`` : H-100のライブラリ  
    L ``test_h100.py``  : H-100のテストコード  
    L ``requirement.txt``

``main_controller``: StretuchSenseとmocopiとの通信とmyCobotとの通信用コードが格納されている  
    L ``main_controller_v1.py``    : 制御用コード
    L``requirement.txt``

## 環境構築
- python 3.11.13  
    - それぞれのrequirement.txtに記述  
- Unity 6000.2.8f1>=

## 設定
### mocopiアプリ
スマホにmocopiアプリをダウンロードしてください｡

以下のURLを参考に設定してください｡  
https://www.sony.co.jp/en/Products/mocopi-dev/jp/documents/ReceiverPlugin/SendData.html

1. mocopiアプリとPCとの接続を設定
2. mocopiアプリを送信モードに切り替える

### stretch sense
下記のURLからHand Engin Liteをダウンロードしてください｡
https://stretchsense.jp/product/hand-engine-lite/

Edit → settingからOpen SDKを有効化してください｡
``Streaming IP Adress``を``127.0.0.1``に設定してください｡
``Streaming Ports``が``9400``になっているか確認してください
``perform/glove/status``, ``animation/rotationWithMetacarpals``, ``aniation/slider/all``, ``command/port/status``を有効化してください｡

以下のチュートリアルに従って設定をしてください｡
English: https://vimeo.com/953373249?fl=pl&fe=sh
Japanse(subtitle): https://vimeo.com/930428895?fl=pl&fe=sh

Knowledge base: https://stretchsense.my.site.com/defaulthelpcenter26Sep/s/?language=en_US


### Unity
以下のプロジェクトからローカルにクローンをしてください｡
https://github.com/kugishun/mocopi_reciver

Unity Hubの``Add project from disk``からクローンしたプロジェクトを展開してください｡

![alt text](img/add_new_project.png)

画像左下の``Assets/MoccopiReciver/Sample/Seans``から``ReciverSample``を展開してください｡
![alt text](img/add_assets.png)

``MocopiVectorSender``の``Remote Ip``が``127.0.0.1``､``Remote Port``が``7001``になっている事を確認してください｡