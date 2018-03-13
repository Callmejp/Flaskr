# -*- coding: utf-8 -*-
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

# 打开本体TXT文件
text = open('try.txt').read()

# 结巴分词 cut_all=True 设置为全模式
wordlist = jieba.cut(text, cut_all=True)

# 使用空格连接 进行中文分词
wl_space_split = " ".join(wordlist)
print(wl_space_split)

# 对分词后的文本生成词云
my_wordcloud = WordCloud().generate(wl_space_split)

WordCloud.to_file(my_wordcloud, "4.jpg")

"""# 显示词云图
plt.imshow(my_wordcloud)
# 是否显示x轴、y轴下标
plt.axis("off")
plt.show()"""