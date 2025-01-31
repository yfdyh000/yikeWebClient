## 这是一个开源的百度一刻相册客户端，仅供学习使用，通过逆向网页版API实现；并遵循[GPL-3.0 license](https://github.com/hexin-lin-1024/yikeWebClientPython/blob/main/LICENSE)。  

### Fork说明

文档有待更新。

开发迭代顺序（越后越新，功能和代码逻辑越全，但也更复杂）：dl.py、dl_all.py、dl_all_fast.py、dl_all_in_album.py。

### 拓展阅读

1. https://alist-doc.nn.ci/docs/driver/baidu.photo
2. https://github.com/alist-org/alist/tree/main/drivers/baidu_photo
3. https://photo.baidu.com/union/doc/jksjzuv5r

### 走过路过，不要错过。只要您是在研究一刻相册网页版的API，[Wiki](https://github.com/hexin-lin-1024/yikeWebClientPython/wiki) 里的东西您就大概率会感兴趣。  

|依赖|  
|---
|requests  
|pywin32  
|Python3|
  
`pip3 install requests`
`pip3 install pywin32` (备选 `py -3 -m pip install pywin32` 或 `python3 -m pip install pywin32` 或 `python -m pip install pywin32`)

### 使用教程：
引入：`from yike import *`，  
并实例化`yi = yikeENV(cookies, bdstoken)`。  
cookie字符串可以在浏览器开发人员工具中寻得，bdstoken同理，设置筛选条件为XHR寻找。  
  
### yikeENV类：  
yikeENV有几个实现其功能的成员方法：  
以下方法都不接受参数，且返回一个包含yikePhoto类的列表。  

|方法名称|方法作用|
|---|---
|getvideos()|获取全部视频
|getgifs()|获取全部动图
|getscreenshots()|获取全部截图
|getall()|获取全部
|getrecycled()|获取回收站全部
|clearrecycle()|清空回收站|
  
特别地，以下三个方法接受一个参数：  
该参数为包含了yikePhoto类的列表，且三个方法都返回包含所有应答JSON(字典)的列表。  
|方法名称|方法作用|
|---|---
|delete()|移入回收站
|restore()|从回收站恢复
|delrecycle()|从回收站删除|
  
特别的，该方法不仅接受一个上述的列表，还接受一个字符串（工作目录，以/结尾）：  
|方法名称|方法作用|  
|---|---  
|dlall() 不推荐使用该方法，因为速度太慢，在之后版本中将改写为多线程下载。 （此方法通过调用yikePhoto.dl()实现）|将给出的媒体全部下载到工作目录中|  
  
  
### yikePhoto类：  
yikePhoto是实现功能的基本单位，含有以下几个成员方法：  
以下方法都不接受参数，且返回一个JSON(字典)。  
  
|方法名称|方法作用|
|---|---
|delrecycle()|从回收站删除自身
|restore()|从回收站恢复自身
|delete()|将自身移入回收站
|exif()|获取自身EXIF|
  
特别的，该方法返回字符串（Url）。  
  
|方法名称|方法作用|
|---|---
|getdl()|获取自身下载链接|  
  
以下方法接受一个字符串（工作目录，要以/结尾）,且没有返回。  
  
|方法名称|方法作用|  
|---|---  
|dl() （在下载过程中会自动将丢失的创建时间等元信息写入）|将自身下载到工作目录|  
  
yikePhoto有一个可能有用的属性：  `yikePhoto.time`。  
该属性为一个字符串，记录了其在一刻中显示的时间（在主页时间轴上）且格式为YYYY:MM:DD HH:MM:SS。  
由于Png，Webp等图片在传输过程中丢失了创建时间信息，而通常情况此类文件没有被写入元信息，故该属性可作为补充。  

### 使用例：

```Python
from yike import *  
bdstoken=input("bdtoken:")  
cookies=input("cookies:")  
yi = yikeENV(cookies, bdstoken)  
print(yi.delete(yi.getvideos())) #删除全部视频  
```
  
### 请注意：  
一刻相册的task需要一段时间执行，如果界面无反应请耐心等待，返回的errno为0就说明一定会生效了。
