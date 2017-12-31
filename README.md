## 前言
最近微信小游戏跳一跳大热，自己也是中毒颇久，无奈手残最高分只拿到200分。无意间看到[教你用Python来玩微信跳一跳](https://zhuanlan.zhihu.com/p/32452473)一文，在电脑上利用adb驱动工具操作手机，详细的介绍以及如何安装adb驱动可以去看这篇文章，这里就不再介绍了。但是原文每次跳跃需要手动点击，于是想尝试利用图像处理的方法自动化。  
最重要的不是最终刷的分数，而是解决这个问题的过程。花了一个下午尝试各种方法，最终采用opencv的模板匹配+边缘检测，方法很简单但效果很好。  
本文主要分享如何用Opencv对游戏截图进行检测，自动找到小人和跳跃目标点的位置，计算跳跃距离，从而让电脑帮你玩跳一跳游戏！
本文的代码见https://github.com/moneyDboat/wechat_jump_jump，欢迎fork和star～

## 主要使用的Python库及对应版本：
python 3.6  
opencv-python 3.3.0  
numpy 1.13.3  

## Opencv  
首先介绍下opencv，是一个计算机视觉库，本文将用到opencv里的模板匹配和边缘检测功能。  

### 模板匹配
模板匹配是在一幅图像中寻找一个特定目标的方法之一。这种方法的原理非常简单，遍历图像中的每一个可能的位置，比较各处与模板是否“相似”，当相似度足够高时，就认为找到了我们的目标。  
例如提供小人的模板图片
![这里写图片描述](http://img.blog.csdn.net/20171231132928712?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbW9uZXlkYm9hdA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
```
import cv2
import numpy as np

# imread()函数读取目标图片和模板
img_rgb = cv2.imread("0.png", 0)
template = cv2.imread('temp1.jpg', 0) 

# matchTemplate 函数：在模板和输入图像之间寻找匹配,获得匹配结果图像 
# minMaxLoc 函数：在给定的矩阵中寻找最大和最小值，并给出它们的位置
res = cv2.matchTemplate(img_rgb,template,cv2.TM_CCOEFF_NORMED)
min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
```
使用OpenCV的matchTemplate函数，就能找到中小人的位置。小人的检测效果非常好，每次都能识别得很精确。
![这里写图片描述](http://img.blog.csdn.net/20171231133114181?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbW9uZXlkYm9hdA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
观察到小人跳到物块中心之后，下一个物块中心就会出现白色小圆点，同样可以匹配图中白色小圆点，从而获得跳跃目标点的坐标，计算跳跃的距离。
![这里写图片描述](http://img.blog.csdn.net/20171231133244302?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbW9uZXlkYm9hdA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
但是只匹配小圆点获得跳跃目标位置会出现问题，因为有些物块本身就是白色的，导致检测失败，所以我们在检测失败（模板匹配的相似度很低）的情况下采用边缘检测。

### 边缘检测
边缘检测顾名思义就是检测图片中的边缘，使用opencv中的cv2.Canny函数。
跳一跳的画面很简洁，所以边缘检测的效果很好。检测出边缘后，从上至下扫描图片就能找到下一个物块的大致位置。
```
img = cv2.imread('1.png', 0)

# 先做高斯模糊能够提高边缘检测的效果
img = cv2.GaussianBlur(img,(5,5),0)  
canny = cv2.Canny(img, 1, 10) 
```
![这里写图片描述](http://img.blog.csdn.net/20171231133343730?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbW9uZXlkYm9hdA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
# 总结
以上就是用OpenCV让电脑帮你玩跳一跳的整体思路，还有很多细节之后再补充，具体的流程见https://github.com/moneyDboat/wechat_jump_jump中的play.py文件，我已经尽力将代码注释写得详尽。  
电脑上安装好adb驱动和相关的Python库，手机通过数据线连接电脑，运行play.py，接下来你就可以刷刷剧吃吃零食，然后让电脑帮你刷分啦～  
这是我自己的结果截图，自动刷到1000分以上是没有问题的。  
![这里写图片描述](http://img.blog.csdn.net/20171231133441199?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbW9uZXlkYm9hdA==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
还有很多不完善的地方，例如屏幕分辨率适配等，如果有什么更好的想法和建议，欢迎评论共同探讨～～
