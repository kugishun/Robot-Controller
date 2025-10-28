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
- Unity 6000.1.15f1>=

## 設定

