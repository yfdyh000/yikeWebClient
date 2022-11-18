from yike import *
import concurrent.futures
from threading import Lock

CONNECTIONS = 4
#TIMEOUT = 30

def dl_sub(i, dldir, lock):
    tagids = [tag['tag_id'] for tag in i.tags]
    if(1102 in tagids or 1103 in tagids): # 跳过特定标签的文件（例如已下载过）。
        return 0
    i.lock = lock
    i.dl(dldir)
    return 1

def bulk_sub(g, dldir):
    lock = Lock() # TODO: 基于完整路径的互斥
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        result = (executor.submit(dl_sub, i, dldir, lock) for i in g)
        concurrent.futures.as_completed(result)
        for future in concurrent.futures.as_completed(result):
            if(future.result() < 0): # TODO?
                print('bad')
            #try:
            #    data = future.result()
            #except Exception as exc:
            #    data = str(type(exc))
            #finally:
                #out.append(data)
                #print(data)

def main():
    dldir = "D:/yikedl/all"
    def makedir():
        if not os.path.exists(dldir):
            os.makedirs(dldir)
    makedir()

    bdstoken = input("bdtoken: ")
    cookies = input("cookies: ")
    yi = yikeENV(cookies, bdstoken)

    index = 0
    while True:
        postedIndex = index
        g, index = yi.getallonce(index)
        if g == []:
            print('no more, exiting.')
            break

        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) +
            'start downloading. amount:', str(len(g)) + ', index:', postedIndex)
        bulk_sub(g, dldir)
        print('\n') # due to printProgress's end=''

main()
