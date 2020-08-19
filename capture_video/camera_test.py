#cv2.getBuildInformation()でViedoI/Oが有効化されているか確認。「FFMPEG」が有効ならok!

import cv2
print(cv2.getBuildInformation())

#captureクラスの呼び出し
for i in range(1000):
    cap = cv2.VideoCapture(i)
    value = cap.isOpened()
    print(value)
    
    if value == True:
        break
########################