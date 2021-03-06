## 参考動画

![Ref_movie](https://github.com/jamjamjam888/DOC-kaken/blob/master/issue/download.gif)

検出物体の中心座標を計算して画面上に表示+テキストファイルに書き込む.

gifを見てわかるように, 影や光の影響をかなり受けている.
下水道に適用した場合はどのように見えるかと言う検証が必要.
また, 水面に浮いているか, 水中に沈んでいるかで見え方も変わる.

背景差分法を用いているので背景となる画像の輝度値との差分がパラメータ以上のものを検出する.
今回は背景となる水路が暗いので輝度値の低い物体は検出精度が悪い.

(備考)パラメータを変えることで検出精度をある程度上げたり、検出物体が小さすぎる場合は弾くことができる.

### 参考
https://github.com/jamjamjam888/DOC-kaken/blob/master/issue/ref_image.pdf
https://github.com/feynfeyn888/DOC-kaken/blob/master/issue/DOC-Diagram.png
