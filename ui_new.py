#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：Translate-api 
@File    ：ui_new.py
@IDE     ：PyCharm 
@Author  ：shayuaidoudou
@Date    ：2025/5/23 10:20 
@explain : explain
"""
import base64
import hashlib
import json
import math
import re
import sys
import time
from abc import ABC, abstractmethod
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QComboBox,
                               QLabel, QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter, QPen


class MacOSButton(QPushButton):
    """仿macOS样式的按钮，带悬浮特效"""

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.is_hovered = False
        self.setFixedSize(12, 12)
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

        # 设置工具提示
        if color == "red":
            self.setToolTip("关闭")
        elif color == "yellow":
            self.setToolTip("最小化")
        else:
            self.setToolTip("最大化")

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆形按钮
        if self.color == "red":
            base_color = QColor(255, 95, 87)
            hover_color = QColor(255, 70, 60)
        elif self.color == "yellow":
            base_color = QColor(255, 189, 46)
            hover_color = QColor(255, 170, 20)
        else:  # green
            base_color = QColor(40, 201, 64)
            hover_color = QColor(20, 180, 44)

        color = hover_color if self.is_hovered else base_color

        # 绘制阴影效果
        if self.is_hovered:
            shadow_color = QColor(color)
            shadow_color.setAlpha(100)
            painter.setBrush(shadow_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(1, 1, 12, 12)

        painter.setBrush(color)
        painter.setPen(QPen(color.darker(110), 1))
        painter.drawEllipse(0, 0, 12, 12)

        # 悬浮时显示图标
        if self.is_hovered:
            painter.setPen(QPen(QColor(255, 255, 255), 1.5))
            center_x, center_y = 6, 6

            if self.color == "red":
                # 绘制 × 图标
                painter.drawLine(center_x - 2, center_y - 2, center_x + 2, center_y + 2)
                painter.drawLine(center_x - 2, center_y + 2, center_x + 2, center_y - 2)
            elif self.color == "yellow":
                # 绘制 - 图标
                painter.drawLine(center_x - 2, center_y, center_x + 2, center_y)
            else:  # green
                # 绘制 + 图标
                painter.drawLine(center_x - 2, center_y, center_x + 2, center_y)
                painter.drawLine(center_x, center_y - 2, center_x, center_y + 2)


class TitleBar(QWidget):
    """自定义标题栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None
        self.maximize_btn = None
        self.title_label = None
        self.minimize_btn = None
        self.close_btn = None
        self.parent_window = parent
        self.setMinimumHeight(40)
        self.setMaximumHeight(50)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)

        # macOS风格按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.close_btn = MacOSButton("red")
        self.minimize_btn = MacOSButton("yellow")
        self.maximize_btn = MacOSButton("green")

        # 连接信号
        self.close_btn.clicked.connect(self.close_window)
        self.minimize_btn.clicked.connect(self.minimize_window)
        self.maximize_btn.clicked.connect(self.maximize_window)

        button_layout.addWidget(self.close_btn)
        button_layout.addWidget(self.minimize_btn)
        button_layout.addWidget(self.maximize_btn)

        self.title_label = QLabel("✨ 鲨鱼翻译器2.0")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #be185d;
                font-size: 15px;
                font-weight: 600;
                background: transparent;
            }
        """)

        layout.addLayout(button_layout)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addSpacing(80)

        self.setLayout(layout)

        self.setStyleSheet("""
            TitleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #fdf2f8, stop:0.5 #fce7f3, stop:1 #fbcfe8);
                border-bottom: 1px solid #f3e8ff;
            }
        """)

    def close_window(self):
        if self.parent_window:
            self.parent_window.close()

    def minimize_window(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def maximize_window(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)


class StyledComboBox(QComboBox):
    """粉色主题的下拉框 - 修复黑色背景问题"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ffffff, stop:1 #fdf2f8);
                border: 2px solid #f9a8d4;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                color: #831843;
                font-weight: 500;
                min-height: 20px;
            }
            QComboBox:hover {
                background: #fef7ff;
            }
            QComboBox:focus {
                border-color: #be185d;
                outline: none;
            }
            QComboBox:on {
                border-color: #be185d;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #fef7ff, stop:1 #fae8ff);
            }
            QComboBox::drop-down {
                border: none;
                width: 35px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #ec4899;
                margin-right: 10px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #be185d;
            }

            QComboBox QAbstractItemView::item:selected:!active {
                background-color: #be185d !important;
                background: #be185d !important;
                color: white !important;
            }

            /* 按下时的项目样式 */
            QComboBox QAbstractItemView::item:pressed {
                background-color: #a21caf !important;
                background: #a21caf !important;
                color: white !important;
            }

            /* 焦点时的项目样式 */
            QComboBox QAbstractItemView::item:focus {
                background-color: #fce7f3 !important;
                background: #fce7f3 !important;
                color: #be185d !important;
                outline: none;
            }
        """)


class StyledTextEdit(QTextEdit):
    """粉色主题的文本编辑框"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(236, 72, 153, 50))
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ffffff, stop:1 #fefcff);
                border: 2px solid #f9a8d4;
                border-radius: 16px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.6;
                color: #1f2937;
                font-family: "SF Pro Display", "Helvetica Neue", sans-serif;
            }
            QTextEdit:hover {
                border-color: #ec4899;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #fefcff, stop:1 #faf5ff);
            }
            QTextEdit:focus {
                border-color: #be185d;
                outline: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ffffff, stop:1 #fefcff);
            }
        """)


class StyledButton(QPushButton):
    """粉色主题的按钮"""

    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        if primary:
            shadow.setColor(QColor(236, 72, 153, 60))
        else:
            shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #ec4899, stop:0.5 #db2777, stop:1 #be185d);
                    color: white;
                    border: none;
                    border-radius: 14px;
                    padding: 14px 28px;
                    font-size: 15px;
                    font-weight: 600;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #f472b6, stop:0.5 #ec4899, stop:1 #db2777);
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #be185d, stop:0.5 #a21551, stop:1 #831843);
                    transform: translateY(1px);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #ffffff, stop:1 #fdf2f8);
                    color: #be185d;
                    border: 2px solid #f9a8d4;
                    border-radius: 14px;
                    padding: 14px 28px;
                    font-size: 15px;
                    font-weight: 600;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #fefcff, stop:1 #fae8ff);
                    border-color: #ec4899;
                    color: #a21caf;
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #fae8ff, stop:1 #f3e8ff);
                    border-color: #be185d;
                    transform: translateY(1px);
                }
            """)


class TranslationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize_start_geometry = None
        self.resize_start_pos = None
        self.resize_edge = None
        self.clear_btn = None
        self.title_bar = None
        self.from_combo = None
        self.input_text = None
        self.service_combo = None
        self.output_text = None
        self.translate_btn = None
        self.to_combo = None
        self.translator_classes = {}
        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("鲨鱼翻译助手2.0")
        self.setMinimumSize(800, 600)
        self.resize(950, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #fefcff, stop:0.3 #fdf4ff, 
                                           stop:0.7 #fae8ff, stop:1 #f3e8ff);
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(236, 72, 153, 40))
        self.setGraphicsEffect(shadow)

    def setup_ui(self):
        """设置用户界面"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        service_layout = QHBoxLayout()
        service_label = QLabel("🌸 翻译服务:")
        service_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #be185d;
                background: transparent;
            }
        """)
        self.service_combo = StyledComboBox()
        # self.service_combo.setStyleSheet()
        self.service_combo.addItems(["请添加翻译服务 💕"])
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_combo)
        service_layout.addStretch()
        lang_container = QWidget()
        lang_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgba(255, 255, 255, 0.8), 
                                           stop:1 rgba(253, 242, 248, 0.8));
                border: 2px solid #f9a8d4;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        lang_layout = QHBoxLayout(lang_container)
        lang_layout.setSpacing(20)
        from_layout = QVBoxLayout()
        from_label = QLabel("💭 源语言:")
        from_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #be185d;
                margin-bottom: 8px;
                background: transparent;
            }
        """)
        self.from_combo = StyledComboBox()
        self.from_combo.addItems([
            "自动检测 🔍", "中文 🇨🇳", "英语 🇺🇸", "日语 🇯🇵", "韩语 🇰🇷",
            "法语 🇫🇷", "德语 🇩🇪", "西班牙语 🇪🇸", "俄语 🇷🇺", "阿拉伯语 🕌"
        ])

        from_layout.addWidget(from_label)
        from_layout.addWidget(self.from_combo)
        swap_btn = StyledButton("🔄")
        swap_btn.setFixedSize(50, 50)
        swap_btn.clicked.connect(self.swap_languages)
        swap_btn.setToolTip("交换语言")
        to_layout = QVBoxLayout()
        to_label = QLabel("🎯 目标语言:")
        to_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #be185d;
                margin-bottom: 8px;
                background: transparent;
            }
        """)
        self.to_combo = StyledComboBox()
        self.to_combo.addItems([
            "英语 🇺🇸", "中文 🇨🇳", "日语 🇯🇵", "韩语 🇰🇷",
            "法语 🇫🇷", "德语 🇩🇪", "西班牙语 🇪🇸", "俄语 🇷🇺", "阿拉伯语 🕌"
        ])

        to_layout.addWidget(to_label)
        to_layout.addWidget(self.to_combo)
        lang_layout.addLayout(from_layout)
        lang_layout.addWidget(swap_btn)
        lang_layout.addLayout(to_layout)
        translate_layout = QHBoxLayout()
        translate_layout.setSpacing(20)
        input_layout = QVBoxLayout()
        input_label = QLabel("📝 输入文本:")
        input_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #be185d;
                margin-bottom: 12px;
                background: transparent;
            }
        """)
        self.input_text = StyledTextEdit("请输入要翻译的文本... ✨")
        self.input_text.setMinimumHeight(150)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        output_layout = QVBoxLayout()
        output_label = QLabel("✨ 翻译结果:")
        output_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #be185d;
                margin-bottom: 12px;
                background: transparent;
            }
        """)
        self.output_text = StyledTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_text.setPlaceholderText("翻译结果将显示在这里... 💖")
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        translate_layout.addLayout(input_layout)
        translate_layout.addLayout(output_layout)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.clear_btn = StyledButton("🗑️ 清空")
        self.translate_btn = StyledButton("🌟 开始翻译", primary=True)
        self.clear_btn.clicked.connect(self.clear_text)
        self.translate_btn.clicked.connect(self.translate_text)
        button_layout.addWidget(self.clear_btn)
        button_layout.addSpacing(15)
        button_layout.addWidget(self.translate_btn)
        content_layout.addLayout(service_layout)
        content_layout.addWidget(lang_container)
        content_layout.addLayout(translate_layout, 1)
        content_layout.addStretch(0)
        content_layout.addLayout(button_layout)
        main_layout.addWidget(content_widget)

    def add_translator(self, name, translator_class):
        """添加翻译器类"""
        self.translator_classes[name] = translator_class
        if self.service_combo.count() == 1 and "请添加翻译服务" in self.service_combo.itemText(0):
            self.service_combo.clear()
        self.service_combo.addItem(name)

    def swap_languages(self):
        """交换源语言和目标语言"""
        from_text = self.from_combo.currentText()
        to_text = self.to_combo.currentText()

        if "自动检测" not in from_text:
            self.from_combo.setCurrentText(to_text)
        self.to_combo.setCurrentText(from_text if "自动检测" not in from_text else "中文 🇨🇳")

    def clear_text(self):
        """清空文本"""
        self.input_text.clear()
        self.output_text.clear()

    def translate_text(self):
        """执行翻译"""
        query = self.input_text.toPlainText().strip()
        if not query:
            self.output_text.setText("💡 请输入要翻译的文本哦～")
            return

        service_name = self.service_combo.currentText()
        if "请添加翻译服务" in service_name:
            self.output_text.setText("🚫 请先添加翻译服务")
            return
        clean_service_name = service_name.replace(" 💝", "")
        if clean_service_name not in self.translator_classes:
            self.output_text.setText("❌ 翻译服务不可用")
            return
        from_lang = self.from_combo.currentText().split()[0]
        to_lang = self.to_combo.currentText().split()[0]

        try:
            translator_class = self.translator_classes[clean_service_name]
            translator = translator_class(from_lang, to_lang, query)
            result = translator.translate()

            self.output_text.setText(f"{result}")

        except Exception as e:
            self.output_text.setText(f"😱 翻译出错啦: {str(e)}")

    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于窗口边缘拖拽"""
        if event.button() == Qt.LeftButton:
            self.resize_edge = self.get_resize_edge(event.position().toPoint())
            if self.resize_edge != 0:
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geometry = self.geometry()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于调整窗口大小"""
        if hasattr(self, 'resize_edge') and self.resize_edge != 0:
            self.resize_window(event.globalPosition().toPoint())
        else:
            # 更新鼠标指针样式
            self.update_cursor(event.position().toPoint())

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if hasattr(self, 'resize_edge'):
            self.resize_edge = 0
        self.setCursor(Qt.ArrowCursor)

    def get_resize_edge(self, pos):
        """获取鼠标位置对应的窗口边缘"""
        edge_size = 10
        rect = self.rect()
        edge = 0
        if pos.x() <= edge_size:
            edge |= 1
        elif pos.x() >= rect.width() - edge_size:
            edge |= 2
        if pos.y() <= edge_size:
            edge |= 4
        elif pos.y() >= rect.height() - edge_size:
            edge |= 8
        return edge

    def update_cursor(self, pos):
        """根据鼠标位置更新光标样式"""
        edge = self.get_resize_edge(pos)

        if edge == 0:
            self.setCursor(Qt.ArrowCursor)
        elif edge in [1, 2]:
            self.setCursor(Qt.SizeHorCursor)
        elif edge in [4, 8]:
            self.setCursor(Qt.SizeVerCursor)
        elif edge in [5, 10]:
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge in [6, 9]:
            self.setCursor(Qt.SizeBDiagCursor)

    def resize_window(self, global_pos):
        """调整窗口大小"""
        if not hasattr(self, 'resize_start_pos') or not hasattr(self, 'resize_start_geometry'):
            return

        delta = global_pos - self.resize_start_pos
        new_geo = QRect(self.resize_start_geometry)
        if self.resize_edge & 1:
            new_geo.setLeft(new_geo.left() + delta.x())
        if self.resize_edge & 2:
            new_geo.setRight(new_geo.right() + delta.x())
        if self.resize_edge & 4:
            new_geo.setTop(new_geo.top() + delta.y())
        if self.resize_edge & 8:
            new_geo.setBottom(new_geo.bottom() + delta.y())
        min_size = self.minimumSize()
        if new_geo.width() >= min_size.width() and new_geo.height() >= min_size.height():
            self.setGeometry(new_geo)


class TranslateEngine(ABC):
    """翻译引擎基类"""

    def __init__(self, from_, to_, query):
        """
        初始化翻译引擎

        Args:
            from_: 源语言
            to_: 目标语言
            query: 翻译的文本
        """
        self.__from = from_
        self.__to = to_
        self.__query = query

    @abstractmethod
    def translate(self) -> str:
        """
        执行翻译操作

        Returns:
            翻译结果列表
        """
        pass


class BaiduTranslator(TranslateEngine):
    """百度翻译引擎"""
    __DEFAULT_TK = "320305.131321201"
    __language_map = {
        '自动检测': 'auto',
        '中文': 'zh',
        '英语': 'en',
        '日语': 'jp',
        '韩语': 'kor',
        '法语': 'fra',
        '德语': 'de',
        '西班牙语': 'es',
        '俄语': 'ru',
        '阿拉伯语': 'ar',
    }

    def __init__(self, from_, to_, query):
        super().__init__(from_, to_, query)
        self.__query, self.__from, self.__to = query, self.__language_map[from_], self.__language_map[to_]

    def get_sign(self) -> str:
        """
        获取百度翻译签名
        """

        def cal_rlt(a: int, b: str) -> int:
            for c in range(0, len(b) - 2, 3):
                d = b[c + 2]
                d = ord(d) - 87 if 'a' <= d else int(d)
                d = a >> d if '+' == b[c + 1] else a << d
                a = (a + d) & 4294967295 if '+' == b[c] else a ^ d
            return a

        no_bmp_chars = re.findall(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', self.__query)
        if not no_bmp_chars:
            q_len = len(self.__query)
            if q_len > 30:
                self.__query = self.__query[0:10] + self.__query[
                                                    math.floor(q_len / 2) - 5:math.floor(q_len / 2) + 5] + self.__query[
                                                                                                           -10:]
        else:
            bmp_parts = re.split(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', self.__query)
            q_array = []
            for i in range(len(bmp_parts)):
                if bmp_parts[i] != '':
                    q_array.extend(list(bmp_parts[i]))
                if i != len(bmp_parts) - 1:
                    q_array.append(no_bmp_chars[i])
            q_len = len(q_array)
            if q_len > 30:
                self.__query = ''.join(q_array[0:10]) + ''.join(
                    q_array[math.floor(q_len / 2) - 5:math.floor(q_len / 2) + 5]) + ''.join(q_array[-10:])
            else:
                self.__query = ''.join(q_array)

        tk_arr = self.__DEFAULT_TK.split('.')
        tk0 = int(tk_arr[0]) or 0
        tk1 = int(tk_arr[1]) or 0
        e = []
        for c in self.__query:
            if ord(c) < 128:
                e.append(ord(c))
            else:
                char_bytes = c.encode('utf-8')
                for b in char_bytes:
                    e.append(b)
        rl = tk0
        rule1 = "+-a^+6"
        rule2 = "+-3^+b+-f"
        for i in range(len(e)):
            rl = cal_rlt(rl + e[i], rule1)
        rl = cal_rlt(rl, rule2)
        rl ^= tk1
        if rl < 0:
            rl = (rl & 2147483647) + 2147483648
        rl %= 1000000
        return str(rl) + '.' + str(rl ^ tk0)

    def translate(self) -> str:
        """执行百度翻译"""
        url = "https://fanyi.baidu.com/v2transapi?from=en&to=zh"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Cookie": "BIDUPSID=529D72F795F09560A9A5CC1A17AE73A7; PSTM=1681276039; BAIDUID=529D72F795F09560D97567446104438A:FG=1; APPGUIDE_10_0_2=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1;",
            "Acs-Token": "1689345795708_1689345863597_xPEQ0yYO9xuYJALqfUGYmCm7dHKG0DEGbCblkAwh1SCKpnEvJN3c/YMxbks/pjxClpAkOaBGQek9DfTUflz7RE8XELKkLxwZy7RVwcpK+VZyMqmjiAbqv50pWAKDvqTU6fCoDb9wuqMeM5de+QHKZ7DCtzxAnHrDYNkdX3P+bT0pLOxh315gGZL4OoyU7XfesTAeCtXs4KOHFP6UTJPc2lJHxKwdC4nvAWLV+R+kKpGpDWzTXxxyusP/KFAF8O4JslX/LQ5nq0NyXyOlppZtgXqQv5FBACoCtrtH6OQ9AMB008yQdbj/vJ5pJ+Mxi5HWwk2LJLFXd9YF9Zk5KYisUOSeN3DHwtoOU/CalmQyKsNtHUYON4IYTEhYQX/0Qw9Ie/8mfmkWYqMBZ8V8P6hA2vGhWbHaE+Xb7GUV2EK6lU1nbES/GZn8bzp2DzDQjwRrEPFA5jjGFfvHih1rjcLwxeRS95lwJbzh4JQf8fPUpLY="
        }
        params = {
            "from": self.__from,
            "to": self.__to,
            "query": self.__query,
            "simple_means_flag": "3",
            "sign": self.get_sign(),
            "token": "618e4f37cd15de2718962c27a17da2a4",
            "domain": "common",
            "ts": int(time.time() * 1000)
        }

        try:
            response = requests.post(url=url, headers=headers, params=params)
            response.encoding = 'utf-8'
            return '\n'.join([x['dst'] for x in response.json()['trans_result']['data']])
        except Exception as e:
            print(f"百度翻译出错: {e}")
            return "翻译出错，请稍后再试"


class YoudaoTranslator(TranslateEngine):
    """有道翻译引擎"""
    __language_map = {
        '自动检测': 'auto',
        '中文': 'zh-CHS',
        '俄语': 'ru',
        '德语': 'de',
        '阿拉伯语': 'ar',
        '日语': 'ja',
        '法语': 'fr',
        '西班牙语': 'es',
        '英语': 'en',
        '韩语': 'ko',
    }
    __KEY_SIGN = 'Vy4EQ1uwPkUoqvcP1nIu6WiAjxFeA3Y3'
    __KEY = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    __IV = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"

    def __init__(self, from_, to_, query):
        super().__init__(from_, to_, query)
        self.__query, self.__from, self.__to = query, self.__language_map[from_], self.__language_map[to_]

    def __decrypt(self, decrypt_str: str) -> bytes:
        """解密有道翻译的加密数据"""
        key_md5 = hashlib.md5(self.__KEY.encode('utf-8')).digest()
        iv_md5 = hashlib.md5(self.__IV.encode('utf-8')).digest()
        aes = AES.new(key=key_md5, mode=AES.MODE_CBC, iv=iv_md5)
        code = aes.decrypt(base64.urlsafe_b64decode(decrypt_str))
        return unpad(code, AES.block_size)

    def translate(self) -> str:
        """执行有道翻译"""
        time_id = int(time.time() * 1000)
        e = f"client=fanyideskweb&mysticTime={time_id}&product=webfanyi&key={self.__KEY_SIGN}"
        sign = hashlib.md5(e.encode()).hexdigest()
        cookies = {
            'OUTFOX_SEARCH_USER_ID': '-1789987592@115.231.234.228',
            'OUTFOX_SEARCH_USER_ID_NCOO': '473934733.26327544',
            '_uetsid': '7a148670378211f08d2a97dbc4c81e40',
            '_uetvid': 'b1bb6bf015df11f0acc0d7d89da45378',
            'DICT_DOCTRANS_SESSION_ID': 'YzlmMGYyOGMtYTg1ZS00ZmRhLTg4NWQtYTQxM2Q0YjNmOGI4',
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://fanyi.youdao.com',
            'Pragma': 'no-cache',
            'Referer': 'https://fanyi.youdao.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data = {
            'i': self.__query,
            'from': self.__from,
            'to': self.__to,
            'useTerm': 'false',
            'domain': '0',
            'dictResult': 'true',
            'keyid': 'webfanyi',
            'sign': sign,
            'client': 'fanyideskweb',
            'product': 'webfanyi',
            'appVersion': '1.0.0',
            'vendor': 'web',
            'pointParam': 'client,mysticTime,product',
            'mysticTime': time_id,
            'keyfrom': 'fanyi.web',
            'mid': '1',
            'screen': '1',
            'model': '1',
            'network': 'wifi',
            'abtest': '0',
            'yduuid': 'abcdefg',
        }
        try:
            response = requests.post('https://dict.youdao.com/webtranslate', cookies=cookies, headers=headers,
                                     data=data)
            response.encoding = 'utf-8'
            res_json = json.loads(self.__decrypt(response.text))
            return ''.join([_[0]['tgt'] for _ in res_json['translateResult']])
        except Exception as e:
            print(f"有道翻译出错: {e}")
            return "翻译出错，请稍后再试"


class CibaTranslator(TranslateEngine):
    """金山词霸翻译引擎"""
    __language_map = {
        '自动检测': 'auto',
        '中文': 'zh-CHS',
        '英语': 'en',
        '日语': 'ja',
        '德语': 'de',
        '法语': 'fr',
        '西班牙语': 'es',
        '韩语': 'ko',
        '阿拉伯语': 'ar',
        '俄语': 'ru'
    }
    __ENCODE_KEY = "L4fBtD5fLC9FQw22".encode()
    __DECODE_KEY = "aahc3TfyfCEmER33".encode()

    def __init__(self, from_, to_, query):
        super().__init__(from_, to_, query)
        self.__query, self.__from, self.__to = query, self.__language_map[from_], self.__language_map[to_]

    def __get_sign(self) -> str:
        """获取金山词霸签名"""
        s = hashlib.md5(f"6key_web_new_fanyi6dVjYLFyzfkFkk{self.__query}".encode()).hexdigest()[:16].encode()
        cipher1 = AES.new(self.__ENCODE_KEY, AES.MODE_ECB)
        padded_data1 = pad(s, AES.block_size)
        encrypted = cipher1.encrypt(padded_data1)
        return base64.b64encode(encrypted).decode('utf-8')

    def translate(self) -> str:
        """执行金山词霸翻译"""
        headers = {
            'authority': 'ifanyi.iciba.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.iciba.com',
            'referer': 'https://www.iciba.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        data = {
            'from': self.__from,
            'to': self.__to,
            'q': self.__query,
        }
        params = {
            'c': 'trans',
            'm': 'fy',
            'client': '6',
            'auth_user': 'key_web_new_fanyi',
            'sign': self.__get_sign(),
        }
        try:
            response = requests.post('https://ifanyi.iciba.com/index.php', params=params, headers=headers, data=data)
            response.encoding = 'utf-8'
            cipher2 = AES.new(self.__DECODE_KEY, AES.MODE_ECB)
            decrypt = unpad(cipher2.decrypt(base64.b64decode(response.json()['content'])), AES.block_size).decode(
                'utf-8')
            return json.loads(decrypt)['out']
        except Exception as e:
            print(f"金山词霸翻译出错: {e}")
            return "翻译出错，请稍后再试"


def main():
    app = QApplication(sys.argv)

    # 创建主窗口
    window = TranslationGUI()

    # 添加示例翻译器
    window.add_translator("百度翻译", BaiduTranslator)
    window.add_translator("有道翻译", YoudaoTranslator)
    window.add_translator("金山词霸", CibaTranslator)

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
