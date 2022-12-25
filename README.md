# AllData_Classification.py, 3-4Data_Classification.py

## 概要

球状黒鉛鋳鉄品（FCD）の組織画像について、機械学習によって判定した黒鉛形状を基にして黒鉛球状化率を求めるプログラムです。

## 使い方

1. **AllData_Classification.py, 3-4Data_Classification.py**を適当なフォルダに置きます。
2. **AllData_Classification.py, 3-4Data_Classification.py**の19行目以降の環境設定の**iDir**と**min_grainsize**の値を設定します。<br>
ここで、**iDir**はダイアログ「画像ファイルを選んでください」で最初に表示させたいフォルダを設定し、**min_grainsize**は「最小黒鉛のサイズ」÷「画像の幅」の値を設定します。
3. **拡張子がpklのファイル**も適当なフォルダに置きます。
4. **AllData_Classification.pyと3-4Data_Classification.py**の27行目のコラム数を3または9に設定し、pklファイルのパス名を102と104行目で設定します。
5. 上記2.の**iDir**に設定したフォルダに上図のような組織画像を格納して**AllData_Classification.pyまたは3-4Data_Classification.py**を実行します。上記のファイルは全角文字を含まないフォルダに格納してください。
6. プログラムを実行すると最初にダイアログ「画像ファイルを選んでください」が表示されるので、球状化率を求める組織画像を選択します。**min_grainsize**が同じ組織画像でしたら複数選択しても構いません。画像ファイルを選択して開くをクリックして少し待つと、球状化率を計算して以下のファイルを作成します。

- **result_日付時刻_nodularity(Machine Learning)_データの割合_コラム数**...ファイル名や球状化率などのデータ
- **画像ファイル名_nodularity(Machine Learning)_データの割合Data_コラム数.jpg**... 黒鉛形状の判定結果

ここで、黒鉛形状の判定結果は次の色で表示されます。
Ⅰ：紺
Ⅱ：青
Ⅲ：茶
Ⅳ：紫
Ⅴ：赤
Ⅵ：青緑

また、データの割合やコラム数は、機械学習の際に用いたデータセットの種類に関する情報となります。
データの割合やコラム数によって、用いるpklファイルが異なります。pyファイルの27、102、104行目の変更は気を付けて行ってください。

## pklファイルについて

- AllData_final_lda_model_9columns.pkl...ISO945-1 Fig.1のⅠ～Ⅵの各図の全ての黒鉛の画像の形状データをデータセットにして学習したモデル（ldaモデル）です。
- AllData_final_lightgbm_model_3columns.pkl...ISO945-1 Fig.1のⅠ～Ⅵの各図の全ての黒鉛の画像の形状データのうち3個のパラメータ（Conv, AR, CSFm）をデータセットにして学習したモデル（lightgbmモデル）です。
- 3-4Data_final_et_model_9columns...ISO945-1 Fig.1のⅠ～Ⅵの各図の大きい順に3/4の黒鉛の画像の形状データをデータセットにして学習したモデル（etモデル）です。
- 3-4Data_final_gbc_model_3columns.pkl...ISO945-1 Fig.1のⅠ～Ⅵの各図の大きい順に3/4の黒鉛の画像の形状データのうち3個のパラメータ（Round, CSFg, MR）をデータセットにして学習したモデル（bgcモデル）です。

## ご利用に関して

使用結果について当方は責任は負いません。

## 開発環境
- Windows11
- VSC 1.7.3.1
- Python 3.8.10
- OpenCV 4.5.4




## 注意点
JIS G5502-2007では、黒鉛形状ⅤとⅥを識別するためのしきい値は規定していません。評価者が決める必要があります。
nodularity-G5502(2007).pyでは、この値を0.45としていますが、この値はJISの規定値ではありませんのでご注意ください。

## ご利用に関して

使用結果について当方は責任は負いません。

## 開発環境
- Windows11
- VSC 1.7.3.1
- Python 3.8.10
- OpenCV 4.6.0.66
- Pycaret 2.3.5
