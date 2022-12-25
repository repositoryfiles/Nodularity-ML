# coding: utf-8
from pycaret.classification import *
import cv2
import tkinter
from tkinter import filedialog
import numpy as np
import io
import os
import sys
import datetime
import math

# VSCで日本語表示するためのおまじない
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 環境設定
iDir = "C:/Data"  # 画像ファイルが格納されているフォルダ
pic_width = 1920  # 入力画像のサイズによらず、画像処理や出力画像はこの幅に設定
# pic_height（高さ）は入力画像の幅と高さの比から計算
min_grainsize = 0.0071  # 画像の幅に対する黒鉛の最小長さ（撮影した画像に応じて設定が必要）
# min_grainsize=0.007はサンプル画像に対する値である。
# サンプル画像は幅142mmに表示させると、倍率100倍の組織画像になる。
# この場合、黒鉛の最小長さ（10μm）は1mmとなる。1mm÷142mm=0.007→min_grainsize
width = 64  # 個々の黒鉛を画像処理するときの幅
Col = 3  # コラム数（3または9）

if Col != 3 and Col != 9:
    print("Col は 3 または 9 としてください")
    sys.exit()

# ダイアログ形式によるファイル選択
def get_picture_filenames():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("jpg", "*.jpg"), ("BMP", "*.bmp"), ("png", "*.png"), ("tiff", "*.tif")]
    filenames = filedialog.askopenfilenames(
        title="画像ファイルを選んでください", filetypes=fTyp, initialdir=iDir
    )
    return filenames


# contoursからmin_grainsize未満の小さい輪郭と、画像の端に接している輪郭を除いてcoutours1に格納
def select_contours(contours, pic_width, pic_height, min_grainsize):
    contours1 = []
    for e, cnt in enumerate(contours):
        x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(cnt)
        (x_circle, y_circle), radius_circle = cv2.minEnclosingCircle(cnt)
        if (
            int(pic_width * min_grainsize) <= 2 * radius_circle
            and 0 < int(x_rect)
            and 0 < int(y_rect)
            and int(x_rect + w_rect) < pic_width
            and int(y_rect + h_rect) < pic_height
        ):
            contours1.append(cnt)
    return contours1


def get_graphite_length(hull):
    max_distance = 0
    for i, hull_x in enumerate(hull):
        for j, hull_y in enumerate(hull):
            if j + 1 < len(hull) and i != j + 1:
                dis_x = hull[j + 1][0][0] - hull[i][0][0]
                dis_y = hull[j + 1][0][1] - hull[i][0][1]
                dis = math.sqrt(dis_x**2 + dis_y**2)
                if dis > max_distance:
                    max_distance = dis
                    x = dis_x * 0.5 + hull[i][0][0]
                    y = dis_y * 0.5 + hull[i][0][1]
    return (x, y, max_distance)


def get_max_circle(contour):
    dist = 0
    dia = 0
    x, y, w, h = cv2.boundingRect(contour)
    for k in range(x, x + w):
        for l in range(y, y + h):
            dist = cv2.pointPolygonTest(contour, (k, l), True)
            if dist > dia:
                dia = dist
                x1 = k
                y1 = l
    dia *= 2  # 半径から直径に変換
    return x1, y1, dia


def main():
    Num1 = []
    Num2 = []
    Num3 = []
    Num4 = []
    Num5 = []
    Num6 = []

    # 画像ファイルごとの球状化率はこの変数に格納
    Nodularity_ISO = []
    if Col == 9:
        model_path = "C:/Data/3-4Data_final_et_model_9columns"  # モデルファイル名
    elif Col == 3:
        model_path = "C:/Data/3-4Data_final_gbc_model_3columns"  # モデルファイル名

    # 保存したモデルをロードする
    model = load_model(model_path)

    # 画像ファイル名の取り込み
    filenames = get_picture_filenames()
    if filenames == "":
        sys.exit()

    for filename in filenames:
        if Col == 9:
            columns = ["CSF", "Round", "CSFm", "CSFg", "AR", "MR", "BF", "Conv", "Sol"]
        elif Col == 3:
            columns = ["Round", "CSFg", "MR"]

        X_test = pd.DataFrame(columns=[columns])

        # 画像ファイルの読み込み、サイズ取得（パス名に全角があるとエラーになる）
        img_color = cv2.imread(filename)  # カラーで出力表示させるためカラーで読み込み
        img_height, img_width, channel = img_color.shape  # 画像のサイズ取得

        # 画像処理や出力画像のサイズ計算（pic_width, pic_height）
        pic_height = int(pic_width * img_height / img_width)
        img_color = cv2.resize(img_color, (pic_width, pic_height))  # 読み込んだ画像ファイルのサイズ変換

        # カラー→グレー変換、白黒反転の二値化、輪郭の検出、球状化率の評価に用いる輪郭の選別
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        ret, img_inv_binary = cv2.threshold(
            img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        contours, hierarchy = cv2.findContours(
            img_inv_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        contours1 = select_contours(
            contours, pic_width, pic_height, min_grainsize
        )  # 球状化率の評価に用いる輪郭をcoutours1に格納

        # 輪郭を大きい順にソート
        contours1.sort(key=lambda x: cv2.contourArea(x), reverse=True)

        contourArea_all = 0
        contourArea_5and6 = 0
        num_1 = num_2 = num_3 = num_4 = num_5 = num_6 = 0
        for i, cnt in enumerate(contours1):  # すべての輪郭に対して実施

            A = cv2.contourArea(cnt)
            contourArea_all += A
            hull = cv2.convexHull(cnt)
            Ac = cv2.contourArea(hull)
            Pc = cv2.arcLength(hull, True)
            P = cv2.arcLength(cnt, True)

            # 黒鉛の長軸（maxFeret)
            feret_x, feret_y, Fmax = get_graphite_length(
                hull
            )  # 輪郭の長軸の中心座標（x, y）と長軸の半分の長さ

            rect = cv2.minAreaRect(cnt)
            (x, y), (wid, hei), angle = rect

            if hei <= wid:
                Fmin = hei
            elif wid < hei:
                Fmin = wid

            # 黒鉛の最大内接円
            x1, y1, W = get_max_circle(cnt)

            # 各パラメータの計算
            CSF = (4 * math.pi * A) / (P**2)
            Round = (4 * A) / (math.pi * (Fmax**2))
            CSFm = (4 * A) / (P * Fmax)
            CSFg = (16 * (A**2)) / (math.pi * P * (Fmax**3))
            AR = Fmin / Fmax
            MR = W / Fmax
            BF = W / Fmin
            Conv = Pc / P
            Sol = A / Ac
            # 推論のためのデータ作成
            if Col == 9:
                X_data = [[CSF, Round, CSFm, CSFg, AR, MR, BF, Conv, Sol]]
            elif Col == 3:
                X_data = [[Round, CSFg, MR]]
            X_test = pd.DataFrame(X_data, columns=columns)

            # 推論
            predict = predict_model(model, data=X_test)

            # Labelは0～5で出力されるので1を足す
            if predict.Label[0] + 1 == 1:
                num_1 = num_1 + 1
                cv2.drawContours(img_color, contours1, i, (128, 0, 0), -1)  # 紺
            if predict.Label[0] + 1 == 2:
                num_2 = num_2 + 1
                cv2.drawContours(img_color, contours1, i, (255, 0, 0), -1)  # 青
            if predict.Label[0] + 1 == 3:
                num_3 = num_3 + 1
                cv2.drawContours(img_color, contours1, i, (0, 0, 128), -1)  # 茶
            if predict.Label[0] + 1 == 4:
                num_4 = num_4 + 1
                cv2.drawContours(img_color, contours1, i, (128, 0, 128), -1)  # 紫
            if predict.Label[0] + 1 == 5:
                num_5 = num_5 + 1
                cv2.drawContours(img_color, contours1, i, (0, 0, 255), -1)  # 赤
                contourArea_5and6 += A
            if predict.Label[0] + 1 == 6:
                num_6 = num_6 + 1
                cv2.drawContours(img_color, contours1, i, (128, 128, 0), -1)  # 青緑
                contourArea_5and6 += A

        # ISO法による球状化率の計算
        Nodularity_ISO.append(contourArea_5and6 / contourArea_all * 100)

        # 黒鉛をタイプⅠ～Ⅵに塗分けた画像の保存
        src = filename
        idx = src.rfind(r".")
        if Col == 9:
            result_ISO_filename = (
                src[:idx]
                + "_nodularity(Machine Learning)_3-4Data_9columns."
                + src[idx + 1 :]
            )
        elif Col == 3:
            result_ISO_filename = (
                src[:idx]
                + "_nodularity(Machine Learning)_3-4Data_3columns."
                + src[idx + 1 :]
            )
        cv2.imwrite(result_ISO_filename, img_color)

        # Num1～6：各画像ファイルのタイプⅠ～Ⅵの個数
        Num1.append(num_1)
        Num2.append(num_2)
        Num3.append(num_3)
        Num4.append(num_4)
        Num5.append(num_5)
        Num6.append(num_6)

    # Num1～6をファイル保存
    now = datetime.datetime.now()
    if Col == 9:
        f2 = open(
            str(os.path.dirname(filenames[0]))
            + "/result_{0:%Y%m%d%H%M}_nodularity(Machine Learning)_3-4Data_9columns".format(
                now
            )
            + ".csv",
            "w",
        )
    elif Col == 3:
        f2 = open(
            str(os.path.dirname(filenames[0]))
            + "/result_{0:%Y%m%d%H%M}_nodularity(Machine Learning)_3-4Data_3columns".format(
                now
            )
            + ".csv",
            "w",
        )
    if f2 != "":
        print("ファイル名, Ⅰの個数, Ⅱの個数, Ⅲの個数, Ⅳの個数, Ⅴの個数, Ⅵの個数, 球状化率(%)", file=f2)  # ファイル名
        for i in range(len(filenames)):
            print(
                "{}, {}, {}, {}, {}, {}, {}, {:.2f}".format(
                    filenames[i],
                    Num1[i],
                    Num2[i],
                    Num3[i],
                    Num4[i],
                    Num5[i],
                    Num6[i],
                    Nodularity_ISO[i],
                ),
                file=f2,
            )  # ファイル名


if __name__ == "__main__":
    main()
