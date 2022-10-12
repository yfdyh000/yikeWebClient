from yike import *
bdstoken=input("bdtoken:")
cookies=input("cookies:")
yi = yikeENV(cookies, bdstoken)

#v = yi.getvideos();
#link = [i.getdl() for i in v]


#g = yi.getgifs();
#g = yi.getvideos();
#g = yi.getall();
#g = yi.getscreenshots();
#g = yi.listrecent();

print('start downloading. items:', len(g))
for i in g:
    #i.dl("D:/yikedl/gifs/")
    #i.dl("D:/yikedl/videos/")
    #i.dl("D:/yikedl/")
    
#print(yi.delete(yi.getvideos())) #删除全部视频  

