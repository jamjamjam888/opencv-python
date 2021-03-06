# 概要
このリポジトリでは、科研の研究プロジェクトの一環として行った水路の流速推定のコードを扱う。
この研究プロジェクトは本専攻の複数研究室に渡るプロジェクトであり、
```
1. 下水道を流れる汚物の速度を非接触に測定
2. 汚物の速度から水路の流速、流量を推定。解析結果から下水道の欠陥の発生有無を検出
3. ベイズ推定を用いて欠陥箇所の特定
```
を一連の流れとする。

今回は```1の下水道を流れる汚物の速度を非接触に測定```を担当した。

## 参考
研究プロジェクト:「多次元光センサー群によるネットワーク構造物の診断と強化」

リンク:https://kaken.nii.ac.jp/ja/grant/KAKENHI-PROJECT-16KT0105/

## 目的と実装 
最終的な目的は水面を流れる物体(ペットボトル)から流速を推定することである。
ただし、流速推定は画像の移動量と現実の移動量の対応付は行っていない(ImageJ等で画像のペットボトルの直径画素値から推定することはできる)。
また、より一般的かつ正確に流速を推定する手法としてTOF(Time of Flight)を用いることもできる。

今回は背景差分法を用いて物体検出、以下のような拘束条件のもとフレーム間での検出物体の同定をし、モーショントラッキングを行った。

モーショントラッキングを行う上で肝になるのが
```
1. いつ視野内に入ってきたのか?
2. 視野内に検出物体が2つ以上存在する場合、フレームの前後でどのように紐付けすればいいのか？
3. いつ視野外に出るのか？
```
の3つを想定する必要がある。
以上の条件を踏まえた上で実装することは以下のようになる。

カメラの視野内に水路があり、左から右に物体が流れていくと仮定する。
現在のフレームをframe,直前のフレームをframe_preとして

```
1.フレームの前後で、frameで検出した重心座標に対して対応する重心がframe_preが存在するか?
⇒if frameの重心座標のx座標　> frame_preのx座標だったら直前のフレームでも検出している。つまり初めて視野内に入ってきた物体ではない。

2.フレームの前後で、各検出物体は直前の座標から最近傍に存在する点に移動する(オプティカルフローを参照)
⇒O(N^2)で総当りで重心座標の最近傍を計算する。

3.フレームの前後で、frame_preで検出した重心座標に対して対応する重心がframeに存在するか？
⇒if frameの重心座標のx座標 > frame_preのx座標だったらOK。対応する点が存在しない場合、その検出物体は視野外に移動している。
```

厳密にはペットボトルの追い越しが発生すると上記の拘束条件は機能しない。
ただし今回は測定対象が水流というベルトコンベアに乗って一様に移動することから、そのようなケースは発生しないこととした。

## directory tree
```
README.md
|-capture_video # 画像解析ファイル管理フォルダ
|-issue         # 解析参考情報
|-txt_data      # 書き込んだ解析データの例
```

```capture_video_timelapse_id_allocation_tracking.py```ファイルが最終的なソースコード。
