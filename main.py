'''
Tkinterを用いて、画像もしくはpdfからOCRを用いてテキストファイルに変換するプログラムです。
プログラムを起動するとウィンドウが開かれるので、ウィンドウに対してテキストを抽出したい画像もしくはpdfをドラッグ&ドロップしてください。

作成時環境一覧
- Python 3.9.12
- glob2 0.7
- pdf2image 1.16.0
- Pillow 9.0.1
- pyocr 0.8.2
- tkinterdnd2 0.3.0
- tesseract 5.1.0

作成日： 2022/6/10 (金)
'''

import os
import glob
import pyocr
import shutil
import pathlib
from PIL import Image
import tkinter as tk
import tkinterdnd2 as tkdnd
from pathlib import Path
from pdf2image import convert_from_path

def drop_enter(event):
    event.widget.focus_force()
    return event.action

def drop_leave(event):
    event.widget._root().focus_force()
    return event.action

def drop_position(event):
    return event.action

def drop(event):
    # jpn:横書き、jpn_vert:縦書き
    lang = 'jpn'
    # 出力用ディレクトリ作成
    new_dir = 'TextFiles'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        
    # OCRエンジンを取得
    engines = pyocr.get_available_tools()
    engine = engines[0]
    
    # path修正
    file = event.data.replace('{', '').replace('}', '')
    # ファイルの拡張子を取得
    sf = pathlib.PurePath(file).suffix
    if sf == '.pdf':
        pdf(file, engine, new_dir, lang)
    else:
        image(file, engine, sf, new_dir, lang)
    
    return event.action

'''
画像の場合の関数
引数：ファイルの絶対パス, OCRエンジン, ファイルの拡張子, テキストファイル保存用ディレクトリ, 言語設定
戻り値：なし
'''
def image(file, engine, sf, new_dir, lang):
    # ファイル名抽出
    file_name = file.split('/')[-1]
    # ファイルの内容を読み込み
    txt = engine.image_to_string(Image.open(file), lang=lang)
    
    # ファイルの拡張子を.txtに変更
    write_file = open(new_dir + '/' + file_name.replace(sf, '.txt'), 'w')
    # 取得した文字をファイルに書き込み
    write_file.write(txt)
    # ファイルを閉じる
    write_file.close()
    
'''
pdfの場合の関数
引数：ファイルの絶対パス, OCRエンジン, テキストファイル保存用ディレクトリ, 言語設定
戻り値：なし
'''
def pdf(path, engine, new_dir, lang):
    # pdf -> jpgに変換した際の作業用フォルダ作成
    work_dir = 'Work'
    
    # フォルダの中身を空にするため、一旦削除->作成
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    
    # PDFファイルのパス
    pdf_path = Path(path)
    #outputのファイルパス
    img_path = Path(work_dir)
    # pdfをjpg形式に変換
    convert_from_path(pdf_path, output_folder=img_path, fmt='jpeg', output_file=pdf_path.stem)
    # 任意のディレクトリ以下のファイル一覧取得
    files = glob.glob('./work/*')
    for file in files:
        # ファイルの内容を読み込み
        text = engine.image_to_string(Image.open(file), lang=lang)
        # ファイル名を取得
        file_name = file.split('/')[-1]
        # ファイルの拡張子を取得
        sf = pathlib.PurePath(file).suffix
        # ファイルの拡張子を.txtに変更
        write_file = open(new_dir + '/' + file_name.replace(sf, '.txt'), 'w')
        # 取得した文字をファイルに書き込み
        write_file.write(text)
        # ファイルを閉じる
        write_file.close()
    
    # 作業用フォルダの削除
    shutil.rmtree(work_dir)
    
def main():
    app = tkdnd.TkinterDnD.Tk()
    app.drop_target_register(tkdnd.DND_FILES)
    
    # ドラッグした状態のカーソルがウィジェット上にのったとき
    app.dnd_bind('<<DropEnter>>', drop_enter)
    # ドラッグした状態のカーソルがウィジェット上にのっているとき
    app.dnd_bind('<<DropLeave>>', drop_leave)
    # ドラックした状態のカーソルがウィジェットから離れたとき
    app.dnd_bind('<<DropPosition>>', drop_position)
    # ウィジェット上でドロップしたとき
    app.dnd_bind('<<Drop>>', drop)
    
    app.mainloop()

if __name__ == '__main__':
    main()