from cmath import inf
from yike import *

dldir = "D:/yikedl/all"
def makedir():
    if not os.path.exists(dldir):
        os.makedirs(dldir)
makedir()

bdstoken=input("bdtoken:")
cookies=input("cookies:")
yi = yikeENV(cookies, bdstoken)

index = 0
while True:
    postedIndex = index
    g, index = yi.getallonce(index)
    if g == []:
        print('no more, exiting.')
        break

    print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) +
        'start downloading. amount:', len(g), ', index:', postedIndex)
    for i in g:
        tagids = [tag['tag_id'] for tag in i.tags]
        if(1102 in tagids or 1103 in tagids): # 跳过特定标签的文件（例如已下载过）。
            continue
        i.dl(dldir)
    print('\n') # due to printProgress's end=''
