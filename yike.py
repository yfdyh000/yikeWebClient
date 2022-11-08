import base64
import requests
import time
import os
import sys
from urllib.parse import unquote
import traceback
from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle
from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time
from email.message import Message
import time
import hashlib

req = requests.Session()

printMaxChar = 0
def printProgress(message):
    global printMaxChar
    printMaxChar = max(printMaxChar, len(message))
    print(('\r' + message).ljust(printMaxChar + 4), end='')

class yikeENV():
    def __init__(self, cookies, bdstoken, limit=100):
        self.cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
        self.bdstoken = str(bdstoken)
        self.limit = limit
        self.ua = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.30"}
        self.s = {
            'videos': '1102',
            'gifs': '1103',
            'screenshots': '22'
        }

    def __cursor__(self, start, limit):
        if start == 0:
            return ''
        return '&cursor=' + str(base64.b64encode(('{\"start\":'+str(start)+',\"limit\":'+str(limit)+'}').encode('utf-8')))[2:-1]

    def __search__(self, method):
        url = 'https://photo.baidu.com/youai/iclass/index/v1/search?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken \
            + '&tag_id=' + self.s[method] \
            + '&need_thumbnail=1'
        l = []
        i = 0
        while True:
            tmp = req.get(url + self.__cursor__(i, self.limit),
                               cookies=self.cookies, headers=self.ua).json()['list']
            if tmp == []:
                break
            l += tmp
            i += self.limit
        result = []
        for i in l:
            result.append(yikePhoto(i, self.cookies, self.bdstoken))
        return result

    def __list_once__(self, method, extra = "", start = 0):
        url = 'https://photo.baidu.com/youai/file/v1/' + method + '?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken \
            + extra
        l = []
        resp = req.get(url + self.__cursor__(start, self.limit),
                        cookies=self.cookies, headers=self.ua).json()
        if 'list' not in resp: # r['errno'] == 2, no more result
            l = []
        else:
            l = resp['list']
        result = []
        for i in l:
            result.append(yikePhoto(i, self.cookies, self.bdstoken))
        return result, start + self.limit

    def __list__(self, method, extra = ""):
        i = 0
        result = []
        while True:
            resp, newStart = self.__list_once__(method, extra, i)
            if resp == []:
                break
            else:
                result += resp
                i = newStart
        return result

    def __fo__(self, method, list):
        result = []
        fsid_list = [i.fsid for i in list]
        url = 'https://photo.baidu.com/youai/file/v1/' + method + '?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken \
            + '&fsid_list='
        while True:
            if len(fsid_list) > 500:
                tmp = fsid_list[:500:]
                fsid_list = fsid_list[500::]
                while (True):
                    r = req.get(
                    url + str(tmp).replace(' ', '').replace('\'', ''), cookies=self.cookies, headers=self.ua).json()
                    if r['errno'] == 0:
                        break
                    else:
                        time.sleep(1)
                result.append(r)
            else:
                tmp = fsid_list
                while (True):
                    r = req.get(
                    url + str(tmp).replace(' ', '').replace('\'', ''), cookies=self.cookies, headers=self.ua).json()
                    if r['errno'] == 0:
                        break
                    else:
                        time.sleep(1)
                result.append(r)
                return result

    def getvideos(self):
        return self.__search__('videos')

    def getgifs(self):
        return self.__search__('gifs')

    def getscreenshots(self):
        return self.__search__('screenshots')

    def getall(self):
        return self.__list__('list')

    def getallonce(self, start = 0):
        return self.__list_once__('list', '', start)

    def getrecycled(self):
        return self.__list__('listrecycle')

    def listrecent(self):
        return self.__list__('listrecent', '&need_thumbnail=1&sort_field=ctime')

    def delete(self, list):
        return self.__fo__('delete', list)

    def restore(self, list):
        return self.__fo__('restore', list)

    def delrecycle(self, list):
        return self.__fo__('delrecycle', list)

    def clearrecycle(self):
        url = 'https://photo.baidu.com/youai/file/v1/clearrecycle?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken
        return req.get(url, cookies=self.cookies, headers=self.ua).json()
    
    def dlall(self, li, workdir):
        for i in li:
            i.dl(workdir)


class yikePhoto:
    def __init__(self, js, cookies, bdstoken):
        self.fsid = str(js['fsid'])
        self.time = js['extra_info']['date_time'].replace('-',':')
        self.ctime = js['ctime']
        self.mtime = js['mtime']
        #self.shoot_time = js['shoot_time']
        self.md5 = js['md5']
        #self.server_md5 = js['server_md5']
        self.path = js['path'] # server_path, '/youa/web/filename.png'
        self.category = js['category']
        #self.face_info = js['face_info'] # {}
        #self.ext_status = js['ext_status'] #=1 如果有加入相册
        self.size = js['size'] #字节
        self.tags = js['tags']
        self.cookies = cookies
        self.bdstoken = str(bdstoken)
        self.ua = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.30"}

    def __fo__(self, method):
        url = 'https://photo.baidu.com/youai/file/v1/' + method + '?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken \
            + '&fsid_list=[' + self.fsid + ']'
        return req.get(url, cookies=self.cookies, headers=self.ua).json()

    # old code in git history
    def __modifyFileTime__(self, filePath):
        ctime = time.localtime(self.ctime)
        mtime = time.localtime(self.mtime)
        fh = CreateFile(filePath, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
        #createTimes, accessTimes, modifyTimes = GetFileTime(fh)
        #T = Time(time.mktime(Time_t))
        #SetFileTime(fh, T, T, T)
        try:
            SetFileTime(fh, Time(ctime), Time(time.time()), Time(mtime)) # must be a pywintypes time object
        except Exception as e:
            print('\n[Error] __modifyFileTime__ for ' + filePath + ' to ' + time.strptime(mtime, '%Y:%m:%d %H:%M:%S'))
            #print(traceback.format_exc())
            raise
        finally:
            CloseHandle(fh)

    def delrecycle(self):
        return self.__fo__('delrecycle')

    def restore(self):
        return self.__fo__('restore')

    def delete(self):
        return self.__fo__('delete')

    def getdl(self):
        try:
            url = 'https://photo.baidu.com/youai/file/v2/download?' \
                + 'clienttype=70' \
                + '&bdstoken=' + self.bdstoken \
                + '&fsid=' + self.fsid
            resp = req.get(url, cookies=self.cookies, headers=self.ua)
            if not resp.ok or not 'dlink' in resp.text: # 网络故障或服务器限制
                 raise KeyError
                #print('\n[Error]', resp.ok, resp.text)
                #return ''
            return resp.json()['dlink']
        except Exception as e:
            print('\n[Error] Failed to get download link of photo with fsid ' + self.fsid)
            print(traceback.format_exc())
            return ''

    def exif(self):
        url = 'https://photo.baidu.com/youai/file/v1/exif?' \
            + 'clienttype=70' \
            + '&bdstoken=' + self.bdstoken \
            + '&fsid=' + self.fsid
        return req.get(url, cookies=self.cookies, headers=self.ua).json()

    def __md5__(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname,"rb") as f:
            for chunk in iter(lambda :f.read(4096),b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def dl(self, workdir):
        try:
            url = self.getdl()
            if url == '':
                raise KeyError
            r = req.get(url, stream=True, headers=self.ua)
            filename = ''
            if 'Content-Disposition' in r.headers and r.headers['Content-Disposition']:
                m = Message()
                m['Content-Disposition'] = r.headers['Content-Disposition']
                file_name = m.get_param('filename', None, 'Content-Disposition')
                if file_name:
                    f = file_name.encode('ISO-8859-1').decode('utf8')
                    filename = unquote(f)
            if not filename and os.path.basename(url):
                filename = os.path.basename(url).split("?")[0]
            if not filename:
                raise ValueError()
            if filename == "温馨提示.txt": # 已屏蔽。跳过，避免反复写入和多线程写入冲突
                return
            filename = filename.strip('"')
            filePath = os.path.abspath(os.path.join(workdir, filename))
            if(os.path.isfile(filePath) and 
                'Content-Length' in r.headers and r.headers['Content-Length'] and
                'Content-MD5' in r.headers and r.headers['Content-MD5']): # sometime KeyError: 'content-length'
                if(os.path.getsize(filePath) != int(r.headers['Content-Length']) or 
                    self.__md5__(filePath) != r.headers['Content-MD5']):
                    # 考虑避免误覆盖已有或已损坏文件。
                    # 触发罕见。一刻服务器保存文件时可能会自动重命名同名文件。
                    # FIXME 多线程冲突的可能？
                    # time.sleep(2) # 避免杀软占用
                    filePath_ = os.path.splitext(filePath)
                    oldFileNewPath = filePath_[0] + '.old.' + str(int(time.time())) + filePath_[1]
                    os.rename(filePath, oldFileNewPath)
                else:
                    printProgress(os.path.basename(filePath) + ' already exists.')
                    # self.__modifyFileTime__(filePath) # 禁用此行，如果不需强制更新文件时间
                    return

            file = open(filePath, 'wb')
            for i in r.iter_content(chunk_size=4096):
                if i:
                    file.write(i)
            file.close()
            self.__modifyFileTime__(filePath)
            printProgress(os.path.basename(filePath) + ' done.')
        except Exception as e:
            print('\n[Error] Error downloading photo with fsid ', self.fsid)
            #print('The file path:', filePath) # local variable 'filePath' referenced before assignment
            print(traceback.format_exc())
        except KeyboardInterrupt as e: # FIXME
            print('\n[Exit] Keyboard interrupt. The last file:', filePath, "The fsid:", self.fsid)
            sys.exit()
