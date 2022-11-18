from yike import *
import concurrent.futures
from threading import Lock
import csv
import config

class ENVClass():
    CONNECTIONS = 5
    #TIMEOUT = 30
    def __init__(self, bdcookie='', bdstoken=''):
        if bdstoken and bdstoken:
            self.yi = yikeENV(bdcookie, bdstoken)
        self.albumTitle = ''
        self.albumIdName = ''
        self.albumDlDir = ''
        self.globalLock = Lock()
        self.respJsonKeys = {}

    @staticmethod
    def makedir(dir):
        os.makedirs(dir, exist_ok = True)

    def init(self):
        config.bdstoken = config.bdstoken or input("bdtoken: ")
        config.bdcookie = config.bdcookie or input("cookies: ")
        self.yi = yikeENV(config.bdcookie, config.bdstoken)
    def album_init(self):
        self.init()
        config.album_id = config.album_id or input("album_id: ")
    def albumDl_init(self):
        self.album_init()
        ids = config.album_id.split(',')
        for id in ids:
            self.albumDl_process(id.strip())
    def albumDl_process(self, album_id):
        resp = self.yi.getAlbumDetail(album_id)
        self.albumTitle = resp['title'] or ""
        self.albumIdName = album_id + "_" + self.albumTitle
        self.albumDlDir = os.path.abspath(os.path.join(config.dldir, album_id + "_" + self.albumTitle))
        self.makedir(config.dldir)
        self.makedir(self.albumDlDir)

def dl_sub(i, dldir, lock):
    #tagids = [tag['tag_id'] for tag in i.tags]
    i.lock = ENV.globalLock
    i.dl(dldir)
    return 1

def thumb_dl_sub(i, dldir, lock, csv):
    #tagids = [tag['tag_id'] for tag in i.tags]
    i.lock = ENV.globalLock
    i.csvWriter = csv
    i.csvHeader = ENV.respJsonKeys # 传入对象指针，确保每次不被清除
    i.dlThumb(dldir)
    return 1

def bulk_sub(g, dldir):
    # TODO: 基于完整路径的互斥
    lock = ENV.globalLock
    with concurrent.futures.ThreadPoolExecutor(max_workers=ENV.CONNECTIONS) as executor:
        result = (executor.submit(dl_sub, i, dldir, lock) for i in g)
        concurrent.futures.as_completed(result)
        for future in concurrent.futures.as_completed(result):
            if(future.result() < 0): # TODO?
                print('bad')
def thumbbulk_sub(g, dldir, csv):
    lock = ENV.globalLock
    with concurrent.futures.ThreadPoolExecutor(max_workers=ENV.CONNECTIONS) as executor:
        result = (executor.submit(thumb_dl_sub, i, dldir, lock, csv) for i in g)
        concurrent.futures.as_completed(result)
        for future in concurrent.futures.as_completed(result):
            if(future.result() < 0): # TODO?
                print('bad')

ENV = ENVClass()

def dl_album_id():
    ENV.album_init()
    cursor = ''
    while True:
        postedcursor = cursor
        g, resp = ENV.yi.getalbumfiles(config.album_id, cursor)
        cursor = resp['cursor']
        if g == []:
            print('no more, exiting.')
            break

        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) +
            'start downloading. amount:', str(len(g)) + ', cursor:', postedcursor)
        bulk_sub(g, os.path.join(config.dldir + "_raw" ))
        print('\n') # due to printProgress's end=''

def dl_album_thumb():
    ENV.albumDl_init()
    
    csvpath = os.path.abspath(os.path.join(ENV.albumDlDir, ENV.albumIdName + '.csv'))
    csv_file = open(csvpath, 'a', buffering=1, newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    cursor = ''
    print(ENV.albumIdName, 'started.')
    while True:
        postedcursor = cursor
        g, resp = ENV.yi.getalbumfiles(config.album_id, cursor)
        cursor = resp['cursor']
        if g == []:
            print('no more, exiting.')
            break

        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()) +
            'start downloading. amount:', str(len(g)) + ', cursor:', postedcursor)
        thumbbulk_sub(g, ENV.albumDlDir, csv_writer)
        print('\n')
        csv_file.flush()
    csv_file.close()

dl_album_thumb()

def save_album_list():
    ENV.init()
    csvpath = os.path.abspath(os.path.join('my-albums.csv'))
    csv_file = open(csvpath, 'w', buffering=-1, newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    cursor = ''
    print('started.')
    hasHeader = False
    while True:
        postedcursor = cursor
        g, resp = ENV.yi.getalbumlist(cursor)
        cursor = resp['cursor']
        if not g:
            print('no more, done.')
            break
        if not hasHeader:
            header = list(g[0].keys())
            #header.insert(0, time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()))
            csv_writer.writerow(header)
            hasHeader = True
        for i in g:
            csv_writer.writerow(i.values())
        csv_file.flush()
        time.sleep(1)
    csv_file.close()
#save_album_list()

