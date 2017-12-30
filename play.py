import os
import cv2
import numpy as np
import time


def get_screenshot(id):
    os.system('adb shell screencap -p /sdcard/%s.png' % str(id))
    os.system('adb pull /sdcard/%s.png .' % str(id))


def jump(distance):
    # 这个参数还需要针对屏幕分辨率进行优化
    press_time = int(distance * 1.35)
    cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    os.system(cmd)


# 第一次跳跃的距离是固定的
jump(530)
time.sleep(1)

# 匹配小跳棋的模板
temp1 = cv2.imread('temp_player.jpg', 0)
w1, h1 = temp1.shape[::-1]
# 匹配游戏结束画面的模板
temp_end = cv2.imread('temp_end.jpg', 0)
# 匹配中心小圆点的模板
temp_white_circle = cv2.imread('temp_white_circle.jpg', 0)
w2, h2 = temp_white_circle.shape[::-1]

# 循环直到游戏失败结束
for i in range(10000):
    get_screenshot(0)
    img_rgb = cv2.imread('%s.png' % 0, 0)

    # 如果在游戏截图中匹配到带"再玩一局"字样的模板，则循环中止
    res_end = cv2.matchTemplate(img_rgb, temp_end, cv2.TM_CCOEFF_NORMED)
    if (cv2.minMaxLoc(res_end)[1] > 0.95):
        print('Game over!')
        break

    # 模板匹配截图中小跳棋的位置
    res1 = cv2.matchTemplate(img_rgb, temp1, cv2.TM_CCOEFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    center1_loc = (max_loc1[0] + 39, max_loc1[1] + 189)

    # 先尝试匹配截图中的中心原点，
    # 如果匹配值没有达到0.95，则使用边缘检测匹配物块上沿
    res2 = cv2.matchTemplate(img_rgb, temp_white_circle, cv2.TM_CCOEFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
    if max_val2 > 0.95:
        print('found white circle!')
        x, y = max_loc2[0] + w2 // 2, max_loc2[1] + h2 // 2
    else:
        # 边缘检测
        img_rgb = cv2.GaussianBlur(img_rgb, (5, 5), 0)
        canny_img = cv2.Canny(img_rgb, 1, 10)

        # 消去小跳棋轮廓对边缘检测结果的干扰
        for k in range(max_loc1[1], max_loc1[1] + 189):
            for b in range(max_loc1[0], max_loc1[0] + 100):
                canny_img[k][b] = 0

        # 计算物块上沿的坐标
        y = np.nonzero([max(row) for row in canny_img[400:]])[0][0] + 400
        x = int(np.mean(np.nonzero(canny_img[y])))
        y += 50  # 偏移，需要设置得小一点，因为游戏到后面会出现非常小的物块
        img_rgb = canny_img

    # 将图片输出以供调试
    img_rgb = cv2.circle(img_rgb, (x, y), 10, 255, -1)
    # cv2.rectangle(canny_img, max_loc1, center1_loc, 255, 2)
    cv2.imwrite('last.png', img_rgb)

    distance = (center1_loc[0] - x) ** 2 + (center1_loc[1] - y) ** 2
    distance = distance ** 0.5
    jump(distance)
    time.sleep(3)
