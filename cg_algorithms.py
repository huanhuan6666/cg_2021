#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段
    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append([x0, y])
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append([x, int(y0 + k * (x - x0))])
    elif algorithm == 'DDA':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append([x0, y])
        elif y0 == y1:
            for x in range(x0, x1 + 1):
                result.append([x, y0])
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k) <= 1:
                if x0 > x1:  # make sure x is adding
                    x0, y0, x1, y1 = x1, y1, x0, y0
                yi = y0
                for x in range(x0, x1 + 1):
                    result.append([x, round(yi)])
                    yi += k
            else:
                if y0 > y1:  # make sure y is adding
                    x0, y0, x1, y1 = x1, y1, x0, y0
                xi = x0
                for y in range(y0, y1 + 1):
                    result.append([xi, round(y)])
                    xi += 1 / k
    elif algorithm == 'Bresenham':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append([x0, y])
        elif y0 == y1:
            for x in range(x0, x1 + 1):
                result.append([x, y0])
        else:
            dy, dx, ex = abs(y1 - y0), abs(x1 - x0), 0
            if dy > dx:  # the |k| > 1, need exchange x, y
                dx, dy = dy, dx
                ex = 1
                x0, y0, x1, y1 = y0, x0, y1, x1
            if x0 > x1:  # make sure x is adding
                x0, y0, x1, y1 = x1, y1, x0, y0
            s = (1 if y0 < y1 else -1)
            p = 2 * dy - dx
            y = y0
            for x in range(x0, x1 + 1):
                if ex == 1:  # exchange x, y
                    result.append([y, x])
                else:
                    result.append([x, y])
                if p > 0:
                    p = p + 2 * dy - 2 * dx
                    y += s
                else:
                    p = p + 2 * dy

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    a, b = abs(x1 - x0) / 2, abs(y0 - y1) / 2
    x, y = 0, b
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2  # vector need to be added
    p1k = b * b * (x + 1) ** 2 + a * a * (y - 1 / 2) ** 2 - a * a * b * b
    while b * b * x <= a * a * y:  # start in region 1
        if xc + x and yc + y:
            result += [[xc + x, yc + y], [xc + x, yc - y], [xc - x, yc + y], [xc - x, yc - y]]
        else:
            result += [[xc + x, yc + y]]
        if p1k >= 0:
            p1k += 2 * b * b * x - 2 * a * a * y + 2 * a * a + 3 * b * b
            x, y = x + 1, y - 1
        else:
            p1k += 2 * b * b * x + 3 * b * b
            x, y = x + 1, y

    p2k = b * b * (x + 1 / 2) ** 2 + a * a * (y - 1) ** 2 - a * a * b * b
    while y >= 0:  # start in region 2
        if xc + x and yc + y:
            result += [[xc + x, yc + y], [xc + x, yc - y], [xc - x, yc + y], [xc - x, yc - y]]
        else:
            result += [[xc + x, yc + y]]
        if p2k >= 0:
            p2k += -2 * a * a * y + 3 * a * a
            x, y = x, y - 1
        else:
            p2k += 2 * b * b * x - 2 * a * a * y + 2 * b * b + 3 * a * a
            x, y = x + 1, y - 1
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    res = []
    if algorithm == 'Bezier':
        n = len(p_list) - 1
        loc = [[[0, 0]] * (n + 1)] * (n + 1)  # 阶数r从0~n共(n+1)阶，每一阶的点数为(n+1-r)
        loc[0] = p_list  # 初始化0阶点为控制点
        for v in range(101):
            u = v / 100  # u取值(0, 1)
            for r in range(1, n + 1):  # 从上到下，阶数从1到n
                for i in range(0, n - r + 1):  # 从左到右
                    loc[r][i] = [(1 - u) * loc[r - 1][i][0] + u * loc[r - 1][i + 1][0],
                                 (1 - u) * loc[r - 1][i][1] + u * loc[r - 1][i + 1][1]]
            res.append([round(loc[n][0][0]), round(loc[n][0][1])])
        return res
    elif algorithm == 'B-spline':
        def curve_point(i, u):  # 第i条曲线上参数为u的点坐标
            t = []
            point = [0, 0]
            t += [-u ** 3 + 3 * u ** 2 - 3 * u + 1, 3 * u ** 3 - 6 * u ** 2 + 4,
                  -3 * u ** 3 + 3 * u ** 2 + 3 * u + 1, u ** 3]
            for j in range(4):  # 每条曲线涉及4个控制点
                point[0] += t[j] * p_list[i + j][0]
                point[1] += t[j] * p_list[i + j][0]
            point[0], point[1] = point[0] / 6, point[1] / 6
            return point

        n = len(p_list) - 1  # 控制点从0开始编号
        for i in range(n - 2):  # k=4为阶数，一共n+1-(k-1)=n-2条三次曲线
            for v in range(101):
                u = v / 100  # 每条曲线上u从(0, 1)
                p = curve_point(i, u)
                res += [round(p[0]), round(p[1])]
    return res


def translate(p_list, dx, dy):
    """平移变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return [[x + dx, y + dy] for [x, y] in p_list]


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    res = []
    theta = math.radians(r)
    cos = math.cos(theta)
    sin = math.sin(theta)
    for p in p_list:
        x1 = x + (p[0] - x) * cos - (p[1] - y) * sin
        y1 = y + (p[0] - x) * sin + (p[1] - y) * cos
        res.append([round(x1), round(y1)])
    return res


def scale(p_list, x, y, s):
    """缩放变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    res = []
    for p in p_list:
        res.append([round(x + (p[0] - x) * s), round(y + (p[1] - y) * s)])
    return res


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x1, y1 = p_list[0]
    x2, y2 = p_list[1]

    if y_min > y_max:
        y_max, y_min = y_min, y_max

    def encode(x, y):  # 给定点[x, y]返回编码
        code = 0
        if y > y_max:
            code |= 8
        elif y < y_min:
            code |= 4
        if x > x_max:
            code |= 2
        elif x < x_min:
            code |= 1
        return code


    if algorithm == 'Cohen-Sutherland':
        c1, c2 = encode(x1, y1), encode(x2, y2)
        if c1 == 0 and c2 == 0:  # 全部保留
            return p_list

        while True:  # 不断裁剪知道全部保留或舍弃
            if c1 & c2 != 0:  # 全部舍弃
                return []
            elif c1 == 0 and c2 == 0:  # 全部保留
                return [[round(x1), round(y1)], [round(x2), round(y2)]]

            if c1 == 0:  # 找到边界外的那个点
                x1, x2, y1, y2 = x2, x1, y2, y1
                c1, c2 = c2, c1

            if c1 & 8 == 8:  # 上边界外
                x1 = x1 + (y_max - y1) * (x2 - x1) / (y2 - y1)
                y1 = y_max
            elif c1 & 4 == 4:  # 下边界外
                x1 = x1 + (y_min - y1) * (x2 - x1) / (y2 - y1)
                y1 = y_min
            elif c1 & 2 == 2:  # 右边界外
                y1 = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x1 = x_max
            elif c1 & 1 == 1:  # 左边界外
                y1 = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x1 = x_min
            c1 = encode(x1, y1)  # 更新c1和c2的编码
            c2 = encode(x2, y2)

    elif algorithm == 'Liang-Barsky':
        dx, dy = x2 - x1, y2 - y1
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        u1, u2 = 0, 1
        for k in range(4):
            if p[k] == 0 and q[k] < 0:  # 全部舍弃
                return []
            elif p[k] < 0:  # 入边
                u1 = max(u1, q[k] / p[k])
            elif p[k] > 0:  # 出边
                u2 = min(u2, q[k] / p[k])
        if u1 > u2:  # 全部舍弃
            return []
        return [[round(x1 + u1 * (x2 - x1)), round(y1 + u1 * (y2 - y1))],
                [round(x1 + u2 * (x2 - x1)), round(y1 + u2 * (y2 - y1))]]
