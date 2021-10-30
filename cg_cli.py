#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

import numpy as np
from PIL import Image

import cg_algorithms as alg

input_file = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)
item_dict = {}
pen_color = np.zeros(3, np.uint8)
width = 0
height = 0


def reset_canvas(line):
    global width, height, item_dict
    width = int(line[1])
    height = int(line[2])
    item_dict = {}


def save_canvas(line):
    global height, width, item_dict
    save_name = line[1]
    canvas = np.zeros([height, width, 3], np.uint8)
    canvas.fill(255)
    for item_type, p_list, algorithm, color in item_dict.values():
        if item_type == 'line':
            pixels = alg.draw_line(p_list, algorithm)
            for x, y in pixels:
                canvas[height - 1 - y, x] = color
        elif item_type == 'polygon':
            pass
        elif item_type == 'ellipse':
            pass
        elif item_type == 'curve':
            pass
    Image.fromarray(canvas).save(os.path.join(output_dir, save_name + '.bmp'), 'bmp')


def set_color(line):
    global pen_color
    pen_color[0] = int(line[1])
    pen_color[1] = int(line[2])
    pen_color[2] = int(line[3])


def draw_line(line):
    global item_dict
    item_id = line[1]
    x0 = int(line[2])
    y0 = int(line[3])
    x1 = int(line[4])
    y1 = int(line[5])
    algorithm = line[6]
    item_dict[item_id] = ['line', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]


def draw_polygon(line):
    pass


def draw_ellipse(line):
    pass


def draw_curve(line):
    pass


def translate(line):
    pass


def rotate(line):
    pass


def scale(line):
    pass


def clip(line):
    pass


func_dict = {
    'resetCanvas': reset_canvas,
    'saveCanvas': save_canvas,
    'setColor': set_color,
    'drawLine': draw_line,
    'drawPolygon': draw_polygon,
    'drawEllipse': draw_ellipse,
    'drawCurve': draw_curve,
    'translate': translate,
    'rotate': rotate,
    'scale': scale,
    'clip': clip,
}

if __name__ == '__main__':

    with open(input_file, 'r') as fp:
        line = fp.readline()
        while line:
            line = line.strip().split(' ')
            try:
                func_dict[line[0]](line)
            except KeyError:
                print(f'[ERROR] :You call the nonexistent func: {line[0]}!!!')
                exit()
            # print(width, height, item_dict, pen_color)
            line = fp.readline()
