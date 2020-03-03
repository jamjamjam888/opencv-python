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

#opencvの情報をプリント
print(cv2.getBuildInformation())

####################################
#params

#fps設定
fps = 1

#視野設定
#カメラのpxl:480*640pxl
threshold_pxl = 20

#積分時間(integration_time)設定
frame_integration = 3
fps_t = fps*frame_integration

#差分ではじくノイズのしきい値。差分で検出した面積が一定値以下のものをはじくようにする。検出する物体サイズにもとづいてパラメータチューニングを行う・
area_size = 500

###################
#膨張処理・収縮処理回数
noize_iters = 3

#処理が重くなるので必要かどうか要検討
###################


#captureクラスの呼び出し
cap = cv2.VideoCapture(0)

#backgroundを任意のタイミングで撮影する
while True:
    ret, frame = cap.read()
    #ret:errorのbool
    
    gray_background = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #グレースケール化した背景を保存
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

#背景差分用のbackgroundを読み込む
background = cv2.imread("/home/pi/Downloads/background.png",1)
#gray_background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

#移動量を書き込むテキストファイルを生成し日付を書き込む
f = open("/home/pi/Downloads/vector_info_log.txt","w")
f.write(str(date)+'\n')
f.close()


#背景差分による流速計測
#captureクラスの呼び出し
cap = cv2.VideoCapture(0)

#fps設定
#上記のparamsのところで指定する
cap.set(cv2.CAP_PROP_FPS, fps)
#うまくいけばtrueを返す
#setメソッドがtrueを返しても指定した値に変更されるとは限られないので注意。カメラに対応していないFPSを指定するとsetメソッドはtrueを返すが、値はそのとおりには変更されない

print(int(cap.get(cv2.CAP_PROP_FPS)))

#高速化？するためにnumpy配列を使用
ball_pre_pre_pre = np.array([])
ball_pre_pre = np.array([])
ball_pre = np.array([])
np_ball_pos = np.array([])

#背景差分で検出した輪郭を格納するリスト
areas = []
#検出した物体の重心を格納するためのリスト
ball_pos = []
 
#計算して求めた流速の値。
velocity = None

#reset変数。3フレーム以上検出物体がない場合、ball_pre_pre_preの要素をクリアする
reset_params = 0
 
#loopの最後にclearするコードを書く

while (True):
    #VideoCaptureから1フレーム読み込む
    ret, frame = cap.read()

    #出力1:差分でどのように物体が検出されるか確認する
    gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #差分検出
    color_diff_ini = cv2.absdiff(gray1, gray_background)
    #閾値処理
    retval, black_diff = cv2.threshold(color_diff_ini, 80, 255, cv2.THRESH_BINARY)
    
    #ノイズ除去
    #operator
    operator = np.ones((3, 3), np.uint8)
    #膨張処理
    black_diff = cv2.dilate(black_diff, operator, iterations = noize_iters)
    #収縮処理
    black_diff = cv2.erode(black_diff, operator, iterations = noize_iters)
    
    #加工ありの画像を表示    
    cv2.imshow('black_diff',black_diff)

    #################################################################

    #出力2:こっちで重心や矩形を書き込む
    
    #重心を計算していく
    
    #①差分により検出した物体のうち、その領域面積が小さいものは光の反射のよるノイズとしてはじく
    contours, hierarchy = cv2.findContours(black_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:#cnt:輪郭#輪郭の数だけループする
        area = cv2.contourArea(cnt)#cv2.contourArea(cnt):領域が占める面積を計算
        if area > area_size:#輪郭の面積がthreshold以上の場合、リストに追加する
            epsilon = 0.1*cv2.arcLength(cnt,True)
            #領域を囲む周囲長を計算する
            #第二引数は対象とする領域が閉じている(True)か単なる曲線かを表すフラグ
            
            approx = cv2.approxPolyDP(cnt,epsilon,True)
            #approx:輪郭の近似を行う
            #第二引数は実際の輪郭と近似輪郭の最大距離を表し近似の精度を表すパラメータ
            
            areas.append(approx)
            #近似した座標を格納

    #重心を描画
    #②検出した物体の数だけ重心位置を計算、配列に格納する
    #重心を計算する方法はいくつかある。
    #今回は、輪郭から計算して求めた。
    #各検出物体の輪郭を構成するすべての点をnとすると、重心x座標はすべてのx座標を足し合わせ、最後にnで割れば平均となるので計算できる。
    
    detect_numbers = len(areas) #検出した物体の数
    if detect_numbers > 10: #検出した物体の数が異常に多い場合、カメラが動いた等の問題が発生していると考える
        print("too much detect!")
        break
    
    for detect_id in range(detect_numbers): #各検出物体の重心を計算
        
        n = len(areas[detect_id]) #各検出物体の輪郭を構成する座標数
        x, y = 0.0, 0.0 #x,yの初期値。local変数
        for coords in range(n): #すべての輪郭を構成する点の座標の和を計算する。※coords=coordinates:座標
            x += areas[detect_id][coords][0][0]
            y += areas[detect_id][coords][0][1]

        #重心計算
        x_moment = int(x/n)
        y_moment = int(y/n)

        ball_pos.append([x_moment, y_moment])
    
    #後で差分量を行列で計算したいため、numpy配列にしておく
    np_ball_pos = np.array(ball_pos)
    print("moment:\n"+str(np_ball_pos))

#######################calcurate diff#######################################
    #初期loop。ball_pre_pre_preとball_posを比較するため、はじめの3フレームは何もしない
    #また、物体を何も検出しなかった場合もこのloopに入る
    #このloopに入ると、フレームの更新・キーボード入力の待機時間等の処理を行わずに物体検出のloopのみを繰り返すので注意
    if len(ball_pre) == 0:
        ball_pre = np_ball_pos
        print(1)
        continue
    
    if len(ball_pre_pre) == 0:
        ball_pre_pre = ball_pre
        print(2)
        
        #reset_params初期化
        reset_params = 0
        
        continue
    
    if len(ball_pre_pre_pre) == 0:
        ball_pre_pre_pre = ball_pre_pre
        print(3)
        continue

###############################################################################
    #物体の移動量を計算する
    #3秒前に検出した物体の数が一致した場合のみ処理を行う
    #検出する物体の数は毎回異なる可能性はどうするか？
    #今回は撮影対象が水路上をランダムに流れるペットボトルであり、定性的に低速かつ離散的であるため、さほど影響が出ないと判断
    if len(np_ball_pos) == len(ball_pre_pre_pre):
        
        #要素が空のとき
        if len(np_ball_pos) == 0:
            print("null")
            continue
        
        #水路を流れるペットボトルは離散的なことから、配列の先頭と対応する検出物体の速度を評価する
        ##流すペットボトルの数によるが、基本的にはカメラの視野内に存在する検出物体の数が一つになることを想定
        
        #差分量を計算
        x_abs_diff = abs(np_ball_pos[0][0] - ball_pre_pre_pre[0][0])
        y_abs_diff = abs(np_ball_pos[0][1] - ball_pre_pre_pre[0][1])
        
        
        #####################################################################
        #差分量が大きすぎる場合、フレーム間での検出物体の対応付けができていないものと判断する
        #上記のparamsの、threshold_pxlで指定している
        if (x_abs_diff > threshold_pxl) or (y_abs_diff > threshold_pxl):
            print("対応付失敗")
            continue
        #####################################################################
        
        #画像内での移動量と現実の移動量との対応関係
        x_real_diff = round(x_abs_diff*4.8)
        y_real_diff = round(y_abs_diff*4.8)
        #2乗
        cal = x_real_diff**2 + y_real_diff**2
        
        #√abs*fps
        velocity = (round(np.sqrt(cal)))

        #画像での移動量を積分時間で割った値。要するに画像上での移動量のベクトル
        diff = np_ball_pos -ball_pre_pre_pre
        vector = diff/fps_t
        print("\n"+"vector"+"\n"+str(vector))
       
        
    else:
        vector = []
        print("error")
    
    ####################################################################
    #write vector_info on the livevideo
    position1 = (50,50)
    cv2.putText(frame, str(vector), position1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), thickness=3)
        
        
    #write boll_position
    position2 = (50,100)
    cv2.putText(frame, str(ball_pos), position2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), thickness=3)

    #現在と3フレーム間の重心を書き込む
    #3フレーム前
    for number in range(len(ball_pre_pre_pre)): #水色
        cv2.circle(frame, tuple(ball_pre_pre_pre[number]), 1, (255, 0, 0), thickness = 10)
    
    #重心座標を書き込む
    for number in range(len(np_ball_pos)): #赤
        cv2.circle(frame, tuple(np_ball_pos[number]), 1, (0, 0, 255), thickness = 10)
    
    #検出した物体の数が一致すれば重心同士の対応を線分で可視化
    if len(ball_pre_pre_pre) == len(np_ball_pos):
        for detect_id in range(len(np_ball_pos)):
            #現在と3フレーム前の座標をそれぞれ結び、検出物体の紐付けを行う
            cv2.line(frame, tuple(ball_pre_pre_pre[detect_id]), tuple(np_ball_pos[detect_id]), (0, 255, 0), 10)
    
    
    #update ball_position
    ball_pre = np_ball_pos
    ball_pre_pre = ball_pre
    ball_pre_pre_pre = ball_pre_pre
    
    #リストの要素をclear()する
    areas.clear()
    ball_pos.clear()
####################################################
    
    #加工なし画像を表示する
    cv2.imshow('Moment Frame', frame)
    
    #velocityをtexifileに書き込む
    #textfile作成
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
    
    
    #キー入力を1ms待って、k がpだったらBreakする
    k = cv2.waitKey(1)&0xff # キー入力を待つ

    if k == ord('p'):
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
cap.release()
cv2.destroyAllWindows()
#cv2.destroyAllWindows()
print("終了")
