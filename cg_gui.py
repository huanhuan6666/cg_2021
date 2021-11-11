#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from typing import Optional

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QSpinBox,
    QLabel,
    QStyleOptionGraphicsItem, QColorDialog, QDialog, QMessageBox, QDialogButtonBox, QSlider, QFormLayout)

import cg_algorithms as alg


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.begin = []  # 图形变换时选中的第一个控制点
        self.rawList = []  # 图形变换时原图元控制参数

        self.rotate_angel = 0  # 旋转角度
        self.scale_factor = 1  # 缩放比例

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = 'line'+item_id

    # TODO: 以下内容为11月新修改
    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = 'polygon'+item_id
        self.temp_item = None # 防止p_list沿用上个多边形或者曲线的p_list

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = 'ellipse'+item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = 'curve'+item_id
        self.temp_item = None

    def start_translate(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请现在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.status = 'translate'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def start_rotate(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请现在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        if  self.item_dict[self.selected_id].item_type == 'ellipse':  # 还没有选图元或者选椭圆不做任何动作
            QMessageBox.warning(self, '注意', '椭圆不提供旋转功能', QMessageBox.Yes, QMessageBox.Yes)
            return
        # self.begin = []
        self.rotate_angel = 0 # 从0开始防止上次旋转角度的叠加
        self.status = 'rotate'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def start_scale(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请现在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.scale_factor = 1 # 防止上次操作的叠加
        self.status = 'scale'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def finish_draw(self):
        self.temp_item = None
        self.temp_id = str(self.status) + self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        if len(self.item_dict) == 0:
            return
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        print(f"the graph is {self.status}, the id is {self.temp_id}")
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.pen_color)
            self.scene().addItem(self.temp_item)

        elif self.status == 'polygon':
            if self.temp_item is None:
                print('a new polygon')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.pen_color)
                self.scene().addItem(self.temp_item)
                self.setMouseTracking(True) # 实时追踪鼠标位置
            else:
                print(f"the p_list is {self.temp_item.p_list}")
                if event.button() == QtCore.Qt.RightButton:  # 按下鼠标右键停止绘制多边形
                    self.add_item()
                    self.setMouseTracking(False)
                else:
                    self.temp_item.p_list.append([x, y])  # 按左键表示继续增加本多边形的参数点

        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], None, self.main_window.pen_color)
            self.scene().addItem(self.temp_item)

        elif self.status == 'curve':
            if self.temp_item is None:
                print('a new curve')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.main_window.pen_color)
                self.scene().addItem(self.temp_item)
                self.setMouseTracking(True)  # 实时追踪鼠标位置
            else:
                print(f"the p_list is {self.temp_item.p_list}")
                if event.button() == QtCore.Qt.RightButton:  # 按下鼠标右键停止绘制多边形
                    self.add_item()
                    self.setMouseTracking(False)
                else:
                    self.temp_item.p_list.append([x, y])  # 按左键表示继续增加本曲线的控制点

        elif self.status == 'translate':
            self.begin = [x, y]
        elif self.status == 'rotate':
            self.begin = [x, y]
            self.rotate_angel = 0  # 每次选择新的旋转中心角度清零
        elif self.status == 'scale':
            self.begin = [x, y]
            self.scale_factor = 1  # 每次选择新的旋转中心角度清零

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        # TODO: 11月修改
        elif self.status == 'polygon':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            if self.temp_item is not None:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            self.temp_item.p_list = alg.translate(self.rawList, x - self.begin[0], y - self.begin[1])
            print(f"the p_list is {self.temp_item.p_list}")
        elif self.status == 'rotate':
            pass
        elif self.status == 'scale':
            pass
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def add_item(self):
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.finish_draw()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.add_item()
        # TODO: 11月修改
        elif self.status == 'polygon':
            pass
        elif self.status == 'ellipse':
            self.add_item()
        elif self.status == 'curve':
            pass
        elif self.status == 'translate':
            self.rawList = self.temp_item.p_list
        elif self.status == 'rotate':
            self.rawList = self.temp_item.p_list
        elif self.status == 'scale':
            self.rawList = self.temp_item.p_list
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:  # 鼠标滚轮
        if self.begin == []: # 还没有选择参考点
            return
        if self.status == 'rotate':
            if event.angleDelta().y() > 0:
                self.rotate_angel -= 1
            elif event.angleDelta().y() < 0:
                self.rotate_angel += 1
            self.temp_item.p_list = alg.rotate(self.rawList, self.begin[0], self.begin[1], self.rotate_angel)
        elif self.status == 'scale':
            if event.angleDelta().y() > 0:
                self.scale_factor += 0.1
            elif event.angleDelta().y() < 0:
                self.scale_factor -= 0.1
            self.temp_item.p_list = alg.scale(self.rawList, self.begin[0], self.begin[1], self.scale_factor)
        self.updateScene([self.sceneRect()])

    def clearCanvas(self):
        '''清空画布的所有图元，以及画布上的所有参数，用于重置画布时调用'''
        for id in self.item_dict:
            self.scene().removeItem(self.item_dict[id])
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.begin = []  # 图形变换时选中的第一个控制点
        self.rawList = []  # 图形变换时原图元控制参数
        self.rotate_angel = 0  # 旋转角度
        self.scale_factor = 1  # 缩放比例


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color=QColor(0, 0, 0), parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color #画笔颜色

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect(item_pixels))

    def boundingRect(self, item_pixels=None) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon':
            x_list = [p[0] for p in self.p_list]
            y_list = [p[1] for p in self.p_list]
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)

        elif self.item_type == 'curve':
            x_list = [p[0] for p in self.p_list]
            y_list = [p[1] for p in self.p_list]
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        self.set_bezier_num = 4
        self.set_bspline_num = 3
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)
        # 设置画布大小
        self.weight = 800
        self.height = 800

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.weight, self.height)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.weight, self.height)
        # self.canvas_widget.resize(self.weight, self.height)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        # 设置画笔
        self.pen_color = QColor(0, 0, 0)

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')
        save_canvas_act = file_menu.addAction('保存画布')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        line_naive_act.triggered.connect(self.line_naive_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        # TODO: 以下内容在11月修改
        save_canvas_act.triggered.connect(self.save_canvas_action)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(self.weight, self.height)
        self.setWindowTitle('CG Demo')

        # self.setbar = QToolBar()
        # self.addToolBar(Qt.LeftToolBarArea, self.setbar)
        #
        # self.bezier_box = QSpinBox()
        # self.bezier_box.setRange(3, 20)
        # self.bezier_box.setSingleStep(1)
        # self.bezier_box.setValue(1)
        # self.setbar.addWidget(QLabel("Bezier控制点数"))
        # self.setbar.addWidget(self.bezier_box)
        # self.setbar.addSeparator()
        # self.bspline_box = QSpinBox()
        # self.bspline_box.setRange(4, 20)
        # self.bspline_box.setSingleStep(1)
        # self.bspline_box.setValue(2)
        # self.setbar.addWidget(QLabel("B样条阶数"))
        # self.setbar.addWidget(self.bspline_box)
        # self.bezier_box.valueChanged.connect(self.set_bezier_num)
        # self.bspline_box.valueChanged.connect(self.set_bspline_num)

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def save_canvas_action(self):
        pass

    def reset_canvas_action(self):
        self.statusBar().showMessage('重置画布')
        # 设置弹出窗口布局
        dialog = QDialog()
        dialog.setWindowTitle('重置画布')
        formlayout = QFormLayout(dialog)
        # 宽度和高度对话框及其对应的滑块
        box1 = QSpinBox(dialog)
        box1.setRange(100, 800) # 范围在[100, 800]
        box1.setSingleStep(1)
        box1.setValue(self.weight)
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(100, 800)
        slider1.setSingleStep(1)
        slider1.setValue(self.weight)
        slider1.setTickPosition(QSlider.TicksBelow)
        slider1.setTickInterval(100)
        box2 = QSpinBox(dialog)
        box2.setRange(100, 800)
        box2.setSingleStep(1)
        box2.setValue(self.height)
        slider2 = QSlider(Qt.Horizontal)
        slider2.setRange(100, 800)
        slider2.setSingleStep(1)
        slider2.setValue(self.height)
        slider2.setTickPosition(QSlider.TicksBelow)
        slider2.setTickInterval(100)
        slider1.valueChanged.connect(box1.setValue) # 滑块和box关联
        box1.valueChanged.connect(slider1.setValue)
        slider2.valueChanged.connect(box2.setValue)
        box2.valueChanged.connect(slider2.setValue)
        formlayout.addRow('宽度 ', box1)
        formlayout.addRow(slider1)
        formlayout.addRow('高度 ', box2)
        formlayout.addRow(slider2)
        # 确定取消按钮
        box3 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box3.accepted.connect(dialog.accept)
        box3.rejected.connect(dialog.reject)
        formlayout.addRow(box3)

        if dialog.exec():
            self.weight = box1.value()
            self.height = box2.value()
            self.item_cnt = 0  # 清空图元
            self.canvas_widget.clearCanvas() # 清空画布图元
            self.list_widget.clearSelection() # 清除图元列表的选择
            self.canvas_widget.clear_selection() # 清除画布的选择
            self.list_widget.clear() # 清除图元列表
            self.scene = QGraphicsScene(self)
            self.scene.setSceneRect(0, 0, self.weight, self.height)
            self.canvas_widget.resize(self.weight, self.height)
            self.canvas_widget.setFixedSize(self.weight, self.height)
            self.statusBar().showMessage('空闲')
            self.setMaximumSize(self.weight, self.height)
            self.resize(self.weight, self.height)
            self.show()


    def set_pen_action(self):
        self.pen_color = QColorDialog.getColor()
        # print(f"color is : {self.pen_color}")
        self.statusBar().showMessage('设置画笔')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('绘制B-spline曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移操作')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转操作')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放操作')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip_cohen_sutherland()
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪操作')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip_liang_barsky()
        self.statusBar().showMessage('Liang-Barsky算法裁剪操作')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
