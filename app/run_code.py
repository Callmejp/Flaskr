import jieba
from wordcloud import *
from urllib import request, parse
from config import url, headers
import matplotlib.pyplot as plt
import Image
import os

basedir = os.path.abspath(os.path.dirname(__file__))


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
    font = r'C:\Windows\Fonts\simfang.ttf'
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
