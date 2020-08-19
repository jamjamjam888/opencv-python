## parameter_info

カメラのpxl:```480*640pxl```

差分ではじくノイズのしきい値。差分で検出した面積が一定値以下のものをはじくようにする。検出する物体サイズにもとづいてパラメータチューニングを行う:```area_size = 500```

膨張処理・収縮処理回数(デノイジング):```noize_iters = 3```

## text_info

書き込み情報:```[id, [x,y], frame_number, timestamp]```

※id = None→検出物体なし
