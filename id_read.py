#!/usr/bin/env python
#coding:utf-8

#(備考)
#参照:https://helloidea.org/index.php/archives/1925.html
#cv2.getBuildInformation()でViedoI/Oが有効化されているか確認。「FFMPEG」が有効ならok!
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

import time
from time import sleep
import math
import cv2
import numpy as np
from datetime import datetime

"""
拘束条件
1.新しい検出物体か？
2.最近傍
3.視野の外に出たか？
4.

ほしい情報
[検出物体id,入ってきた時間,　出ていった時間,最初の座標,　最後の座標]
"""
#まとめて読み出す
f = open("/home/pi/Desktop/vector_info_log.txt","r")
#特定行だけ読み出す
i = 1
j = j+1

frame_pre_post = []

while:
    #検出物体がないとき
    str = f.read()[i]
    if str[0][0] == None: 
        i += 1
    
    #検出物体があるとき
    else:
        #次のframe_numのものをすべてリストに格納していく
        while:
            str_post = f.read()[j]
            
            #同じframe_numのとき
            if str[0][2] = str_post[0][2]:
                #次の行へ進む
                j += 1
                
                
            #次のframe_numのとき
            elif:str[0][2] + 1 = str_post[0][2] 
            
                #opencvでは、x=0から順番に重心座標をリスト(ball_pos)に格納していく。つまり、次のframeにおいて自分よりもx座標が大きくなる点が存在しなければその点は
                #とりあえず新しいリストを作る
                
                #次の行へ進む
                j += 1
                
                
            #次の次のframe_numのとき
            else:
                #jを初期化
                j = i+1
                break

        
f.close()