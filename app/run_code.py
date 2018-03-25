# -*- coding: utf-8 -*-
import jieba
from wordcloud import *
from urllib import request, parse
from config import url, headers
import matplotlib.pyplot as plt
from PIL import Image
import os

basedir = os.path.abspath(os.path.dirname(__file__))
font = "C:/Windows/Fonts/STFANGSO.ttf"



def pa_chong(d):
    data = bytes(parse.urlencode(d), encoding='utf8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    response = request.urlopen(req)
    dic = response.read().decode('utf-8')
    return dic


def get_txt(st, ed, data):
    print(st, ed)
    tmp = st
    st = min(st, ed)
    ed = max(tmp, ed)
    txt = ""
    for d in data:
        #day = str(d.timestamp)
        day = d.timestamp.date()
        #day = day.split(' ')[0]
        if st <= day and day <= ed:
            txt = txt + " " + d.body
    print(txt)
    with open(basedir + '\\static\\try.txt', 'w') as f:
        f.write(txt)


def make_wc(st, ed, data):
    get_txt(st, ed, data)

    # 打开本体TXT文件
    text = open(basedir + '\\static\\try.txt').read()

    # 结巴分词 cut_all=True 设置为全模式
    wordlist = jieba.cut(text, cut_all=True)

    # 使用空格连接 进行中文分词
    wl_space_split = " ".join(wordlist)
    print(wl_space_split)

    # 对分词后的文本生成词云

    my_wordcloud = WordCloud(
        background_color='white',
        font_path=font
    ).generate(wl_space_split)
    #调整大小
    file = basedir + '\\static\\try.jpg'
    im = Image.open(file)
    (x, y) = im.size
    x_s = 1280
    y_s = y * x_s // x
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    out.save(file)

    backgroud_Image = plt.imread(file)
    img_colors = ImageColorGenerator(backgroud_Image)

    WordCloud.to_file(my_wordcloud.recolor(color_func=img_colors), file)


def make_judge_wc_picture(tid):
    text = open(basedir + '\\static\\try' + str(tid) + '.txt').read()

    # 结巴分词 cut_all=True 设置为全模式
    wordlist = jieba.cut(text, cut_all=True)

    # 使用空格连接 进行中文分词
    wl_space_split = " ".join(wordlist)
    print(wl_space_split)

    my_wordcloud = WordCloud(
        background_color='white',
        font_path=font
    ).generate(wl_space_split)
    # 调整大小
    file = basedir + '\\static\\1.jpg'
    tofile = basedir + '\\static\\try' + str(tid) + '.jpg'

    im = Image.open(file)
    (x, y) = im.size
    x_s = 1280
    y_s = y * x_s // x
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    out.save(file)

    backgroud_Image = plt.imread(file)
    img_colors = ImageColorGenerator(backgroud_Image)

    WordCloud.to_file(my_wordcloud.recolor(color_func=img_colors), tofile)


def make_judge_wc(rst):
    txt1 = ""
    txt2 = ""
    txt3 = ""
    for r in rst:
        arr = str(r.comment).split('*')
        txt1 = txt1 + " " + arr[0]
        txt2 = txt2 + " " + arr[1]
        txt3 = txt3 + " " + arr[2]
    ###########
    txt1 = txt1 + " " + "规整 " + "规整"
    txt2 = txt2 + " " + "几乎正确 " + "scanf()错误"
    txt3 = txt3 + " " + "思路复杂 " + "思路繁琐"
    ###########
    with open(basedir + '\\static\\try1.txt', 'w') as f:
        f.write(txt1)
    with open(basedir + '\\static\\try2.txt', 'w') as f:
        f.write(txt2)
    with open(basedir + '\\static\\try3.txt', 'w') as f:
        f.write(txt3)

    make_judge_wc_picture(1)
    make_judge_wc_picture(2)
    make_judge_wc_picture(3)

