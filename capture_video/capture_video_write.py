#!/usr/bin/env python
#coding:utf-8

import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

import time
from time import sleep
import math
import cv2
import numpy as np
from datetime import datetime

######

fps = 2

######

#背景撮影
date = datetime.now().strftime("%Y%m%d_%H%M%S")

print(date)

cam = cv2.VideoCapture(0)                               # カメラCh.(ここでは0)を指定

# 動画ファイル保存用の設定
fps = int(cam.get(cv2.CAP_PROP_FPS))                    # カメラのFPSを取得
Width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
Height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得

cam.set(cv2.CAP_PROP_FPS, fps)
#うまくいけばtrueを返す

print("fps:"+str(fps))
print("Width:"+str(Width))
print("Height:"+str(Height))


fourcc = cv2.VideoWriter_fourcc('m', 'p', '4','v')
out = cv2.VideoWriter("/home/pi/Desktop/output_"+date+".mp4", fourcc, fps, (Width,Height))

###参照###
    # CV_FOURCC('D','I','B',' ')    = 無圧縮
    # CV_FOURCC('P','I','M','1')    = MPEG-1 codec
    # CV_FOURCC('M','J','P','G')    = motion-jpeg codec (does not work well)
    # CV_FOURCC('M', 'P', '4', '2') = MPEG-4.2 codec
    # CV_FOURCC('D', 'I', 'V', '3') = MPEG-4.3 codec
    # CV_FOURCC('D', 'I', 'V', 'X') = MPEG-4 codec
    # CV_FOURCC('U', '2', '6', '3') = H263 codec
    # CV_FOURCC('I', '2', '6', '3') = H263I codec
    # CV_FOURCC('F', 'L', 'V', '1') = FLV1 codec


print("start videocapture")

# 撮影＝ループ中にフレームを1枚ずつ取得（qキーで撮影終了）
while True:
    ret, frame = cam.read()                             # フレームを取得
    cv2.imshow('cam', frame)                            # フレームを画面に表示                             
    #write video on raspi
    #ラズパイに書き込む場合は↓これをつかう
    out.write(frame)


    #キー入力を1ms待って、k がpだったらBreakする
    k = cv2.waitKey(100)&0xff # キー入力を待つ
    #now = datetime.now()
    #print(str(now)+"\n")
    
    if k == ord('p'):
        # 「p」キーで画像を保存
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = "/home/pi/" + "moment" + date + ".png"
        cv2.imwrite(path, frame) # ファイル保存

        
        # キャプチャをリリースして、ウィンドウをすべて閉じる
        cam.release()
        out.release()
        cv2.destroyAllWindows()
        break

#print("output:{}".format(output))
print("終了")

#動画から静止画を抽出

#参照:https://www.asanohatake.com/entry/2018/11/20/073000

video_path = "/home/pi/Desktop/output_"+date+".mp4"
cap = cv2.VideoCapture(video_path)

count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)

print("width:{}, height:{}, count:{}, fps:{}".format(Width,Height,count,fps))

for num in range(1, int(count), int(fps)):
    cap.set(cv2.CAP_PROP_POS_FRAMES, num)
    cv2.imwrite("picture{:0=3}".format(int((num-1)/int(fps)))+".jpg", cap.read()[1])
    print("save picture{:0=3}".format(int((num-1)/int(fps)))+".jpg")

cap.release()
"""
続いて、1フレームごとではなくて、もっと間隔をあけて画像として保存したい場合の方法です。
本当は1秒ごとに画像として保存したいなあと思っていたのですが、調べてもよくわからなくて、フレーム数を指定することで「1秒ごとっぽい」間隔で保存してみました。
以下のコードで、動画の1フレーム目からfpsごとに画像として保存することができます。fps（=frames per second、1秒当たりのフレーム数）ごとなので、ほぼ1秒ごとと言ってもいいのですが、これが整数でない場合は「ずれ」が生じてしまいます。
ちなみに参考までに、1フレーム目からではなくて途中から指定することもできますし、間隔もfpsごとではなくて、例えば3フレームごとなどといった指定も可能です。
"""