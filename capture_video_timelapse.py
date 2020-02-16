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
print(cv2.getBuildInformation())
#captureクラスの呼び出し
#vedeoio error
cap = cv2.VideoCapture(0)
########################
t_pre = time.time()
#backgroundを任意のタイミングで撮影する
while True:
    ret, frame = cap.read()

    gray_background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("background_capture", gray_background)

    k = cv2.waitKey(1)&0xff # キー入力を待つ
    if k == ord('p'):
        # 「p」キーで画像を保存
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        #path = "/home/pi/" + "background" + date + ".png"
        path = "/home/pi/Downloads/background.png"
        cv2.imwrite(path, frame) # ファイル保存

        cv2.imshow(path, frame) # キャプチャした画像を表示
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
cap.release()
cv2.destroyAllWindows()
print("背景撮影完了")
###########################################################################################

#backgroundを読み込む
background = cv2.imread("/home/pi/Downloads/background.png",1)
#gray_background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

#移動量を書き込むテキストファイルを生成し日付を書き込む
f = open("/home/pi/Downloads/vector_info_log.txt","w")
f.write(str(date)+'\n')
f.close()

#フレーム間差分を計算
cap = cv2.VideoCapture(0)

#fpsを1にするといかれる
fps = 2

print("fps:",fps)
#distance_lapse
ball_pre = []
velocity = -1
while (True):
    velocity = 0
    #VideoCaptureから1フレーム読み込む
    ret, frame = cap.read()

    gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #差分検出
    color_diff_ini = cv2.absdiff(gray1, gray_background)
    #閾値処理
    retval, black_diff = cv2.threshold(color_diff_ini, 80, 255, cv2.THRESH_BINARY)

    #加工ありの画像を表示    
    cv2.imshow('black_diff',black_diff)
    #################################################################
    #重心を計算
    contours, hierarchy = cv2.findContours(black_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    areas = []
    for cnt in contours:#cnt:輪郭#輪郭の数だけループする
        area = cv2.contourArea(cnt)#cv2.contourArea(cnt):領域が占める面積を計算
        if area > 200:#輪郭の面積がthreshold以上の場合、リストに追加する
            epsilon = 0.1*cv2.arcLength(cnt,True)
            #領域を囲む周囲長を計算する
            #第二引数は対象とする領域が閉じている(True)か単なる曲線かを表すフラグ
            approx = cv2.approxPolyDP(cnt,epsilon,True)
            #approx:輪郭の近似を行う
            #第二引数は実際の輪郭と近似輪郭の最大距離を表し近似の精度を表すパラメータ
            areas.append(approx)

        #重心を描画
    ball_pos = []
    for i in range(len(areas)):  #重心位置を計算
        count = len(areas[i])
        area = cv2.contourArea(areas[i])  #面積計算
        x, y = 0.0, 0.0
        for j in range(count):
            x += areas[i][j][0][0]
            y += areas[i][j][0][1]

        x /= count
        y /= count
        x = int(x)
        y = int(y)
        ball_pos.append([x, y])
        #重心座標を書き込む
        ball_position = (x,y)
        #cv2.putText(frame, str(0), ball_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))        
        
        
    np_ball_pos = np.array(ball_pos)
    print("moment:\n"+str(np_ball_pos))

#######################calcurate diff#######################################
    #ball_pre
    print("\n"+"ball_pre"+"\n"+str(ball_pre))
    
    if len(np_ball_pos) == len(ball_pre):
        np_ball_pre = np.array(ball_pre)
        diff = np_ball_pos - np_ball_pre
        print("\n"+"diff"+"\n"+str(diff))
        
        if len(diff) != 0:#配列の中身が空じゃないとき
            diff_list = diff.tolist()
            print("diff_list",diff_list)
            real_x = round(diff_list[0][0]*4.8)
            real_y = round(diff_list[0][1]*4.8)
            print(real_x,real_y)
            #絶対値の2乗計算
            x_abs = abs(real_x)
            y_abs = abs(real_y)
            cal = x_abs**2 + y_abs**2
            #√abs*fps
            velocity = (round(np.sqrt(cal)))
            print("\n"+"velocity"+"\n"+str(velocity))
        
        #calcurate time_lapse
        t_now = time.time()
        t_lapse = t_now - t_pre
        
        #calcurate vector
        vector = diff/t_lapse
        print("\n"+"vector"+"\n"+str(vector))
        #write moment + vector on the livevideo
        for number in range(len(np_ball_pos)):
            moment = np_ball_pos[number]
            #cv2.arrowedLine(frame, tuple(np_ball_pre[number]),tuple(np_ball_pos[number]), (0, 0, 255), thickness=1)
            #cv2.drawMarker(frame, tuple(np_ball_pos[number]), (0, 0, 255))
            #probably can't use arrowedLine, drawMarker
            cv2.circle(frame, tuple(np_ball_pos[number]), 15, (0, 0, 255), thickness=3)    
    
    else:
        vector = []
        print("error")
         #only write moment
        for number in range(len(np_ball_pos)):
            moment = np_ball_pos[number]
            #cv2.drawMarker(frame, tuple(np_ball_pos[number]), (0, 0, 255))
            #cv2.circle(frame, tuple(np_ball_pos[number]), 15, (0, 0, 255), thickness=1)
    
    #write vector_info on the livevideo
    position1 = (50,50)
    cv2.putText(frame, str(vector), position1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), thickness=3)
        
        
    #write boll_position
    position2 = (50,100)
    cv2.putText(frame, str(ball_pos), position2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), thickness=3)

    #get pre_info
    ball_pre = np_ball_pos
    t_pre = time.time()

####################################################
    
    #加工なし画像を表示する
    cv2.imshow('Moment Frame', frame)
    
    #velocityをtexifileに書き込む
    #textfile作成
    #watchdogで監視用と、log用のファイル２つに書き込む
    if velocity != 0:
        #テキストファイルに時系列データを保存(時系列を特定できるようにしてもよい)
        f1 = open("/home/pi/Downloads/vector_info_log.txt","a")
        f1.write(str(velocity)+'\n')
        f1.close()
        #最新の値をテキストファイルに上書き保存
        f2 = open("/home/pi/Downloads/vector_info_.txt","w")
        f2.write(str(velocity))
        f2.close()
   
    else:
    #テキストファイルに時系列データを保存(時系列を特定できるようにしてもよい)
        f1 = open("/home/pi/Downloads/vector_info_log.txt","a")
        f1.write("-1" + '\n')
        f1.close()
        #最新の値をテキストファイルに上書き保存
        f2 = open("/home/pi/Downloads/vector_info_.txt","w")
        f2.write(str(velocity))
        f2.close()
    
    #符号器呼び出し
    #キー入力を1ms待って、k がpだったらBreakする
    k = cv2.waitKey(500)&0xff # キー入力を待つ
    #now = datetime.now()
    #print(str(now)+"\n")
    
    if k == ord('p'):
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
cap.release()
cv2.destroyAllWindows()
#cv2.destroyAllWindows()
print("終了")
