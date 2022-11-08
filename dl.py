from yike import *
bdstoken=input("bdtoken:")
cookies=input("cookies:")
yi = yikeENV(cookies, bdstoken)

#v = yi.getvideos();
#link = [i.getdl() for i in v]


#g = yi.getgifs()
#g = yi.getvideos()
g = yi.getall()
#g = yi.getscreenshots()
#g = yi.listrecent()

print('start downloading. items:', len(g))
for i in g:
    tagids=[tag['tag_id'] for tag in i.tags]
    if(1102 in tagids or 1103 in tagids):
        continue
    #i.dl("D:/yikedl/gifs/")
    #i.dl("D:/yikedl/videos/")
    i.dl("D:/yikedl/all")
    
#print(yi.delete(yi.getvideos())) #删除全部视频

