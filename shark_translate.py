#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : shark_translator.py
@Author  : Shark Translator Team
@Time    : 2025/05/14
@Desc    : 多平台翻译工具，支持有道、百度、金山词霸翻译接口
"""

import base64
import hashlib
import json
import math
import re
import time
import uuid
from abc import ABC, abstractmethod
from typing import List

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from PySide6.QtCore import Qt, QThread, Signal, QSize, QObject, QEvent
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QFrame,
    QSplitter, QStatusBar, QToolBar, QSpinBox
)


class TranslateEngine(ABC):
    """翻译引擎基类"""

    def __init__(self, text: str):
        """
        初始化翻译引擎

        Args:
            text: 需要翻译的文本
        """
        self.text = text
        self.result = ''

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

    def __init__(self, text: str):
        super().__init__(text)
        self.__sign = ""
        self.json_txt = {}

    def get_sign(self, query: str) -> None:
        """
        获取百度翻译签名

        Args:
            query: 查询文本
        """
        DEFAULT_TK = "320305.131321201"

        def cal_rlt(a: int, b: str) -> int:
            for c in range(0, len(b) - 2, 3):
                d = b[c + 2]
                d = ord(d) - 87 if 'a' <= d else int(d)
                d = a >> d if '+' == b[c + 1] else a << d
                a = (a + d) & 4294967295 if '+' == b[c] else a ^ d
            return a

        no_bmp_chars = re.findall(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', query)
        if not no_bmp_chars:
            q_len = len(query)
            if q_len > 30:
                query = query[0:10] + query[math.floor(q_len / 2) - 5:math.floor(q_len / 2) + 5] + query[-10:]
        else:
            bmp_parts = re.split(r'[\uD800-\uDBFF][\uDC00-\uDFFF]', query)
            q_array = []
            for i in range(len(bmp_parts)):
                if bmp_parts[i] != '':
                    q_array.extend(list(bmp_parts[i]))
                if i != len(bmp_parts) - 1:
                    q_array.append(no_bmp_chars[i])
            q_len = len(q_array)
            if q_len > 30:
                query = ''.join(q_array[0:10]) + ''.join(
                    q_array[math.floor(q_len / 2) - 5:math.floor(q_len / 2) + 5]) + ''.join(q_array[-10:])
            else:
                query = ''.join(q_array)

        tk_arr = DEFAULT_TK.split('.')
        tk0 = int(tk_arr[0]) or 0
        tk1 = int(tk_arr[1]) or 0
        e = []
        for c in query:
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
        self.__sign = str(rl) + '.' + str(rl ^ tk0)

    def translate(self) -> str:
        """执行百度翻译"""
        self.get_sign(self.text)

        url = "https://fanyi.baidu.com/v2transapi?from=en&to=zh"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Cookie": "BIDUPSID=529D72F795F09560A9A5CC1A17AE73A7; PSTM=1681276039; BAIDUID=529D72F795F09560D97567446104438A:FG=1; APPGUIDE_10_0_2=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1;",
            "Acs-Token": "1689345795708_1689345863597_xPEQ0yYO9xuYJALqfUGYmCm7dHKG0DEGbCblkAwh1SCKpnEvJN3c/YMxbks/pjxClpAkOaBGQek9DfTUflz7RE8XELKkLxwZy7RVwcpK+VZyMqmjiAbqv50pWAKDvqTU6fCoDb9wuqMeM5de+QHKZ7DCtzxAnHrDYNkdX3P+bT0pLOxh315gGZL4OoyU7XfesTAeCtXs4KOHFP6UTJPc2lJHxKwdC4nvAWLV+R+kKpGpDWzTXxxyusP/KFAF8O4JslX/LQ5nq0NyXyOlppZtgXqQv5FBACoCtrtH6OQ9AMB008yQdbj/vJ5pJ+Mxi5HWwk2LJLFXd9YF9Zk5KYisUOSeN3DHwtoOU/CalmQyKsNtHUYON4IYTEhYQX/0Qw9Ie/8mfmkWYqMBZ8V8P6hA2vGhWbHaE+Xb7GUV2EK6lU1nbES/GZn8bzp2DzDQjwRrEPFA5jjGFfvHih1rjcLwxeRS95lwJbzh4JQf8fPUpLY="
        }
        params = {
            "from": "auto",
            "to": "zh",
            "query": self.text,
            "simple_means_flag": "3",
            "sign": self.__sign,
            "token": "618e4f37cd15de2718962c27a17da2a4",
            "domain": "common",
            "ts": int(time.time() * 1000)
        }

        try:
            response = requests.post(url=url, headers=headers, params=params)
            response.encoding = 'utf-8'
            self.json_txt = response.json()

            self.result = '\n'.join([x['dst'] for x in self.json_txt['trans_result']['data']])
            return self.result
        except Exception as e:
            print(f"百度翻译出错: {e}")
            return "翻译出错，请稍后再试"


class YoudaoTranslator(TranslateEngine):
    """有道翻译引擎"""

    def __init__(self, text: str):
        super().__init__(text)

    def _decrypt(self, decrypt_str: str) -> bytes:
        """解密有道翻译的加密数据"""
        key = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
        iv = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
        key_md5 = hashlib.md5(key.encode('utf-8')).digest()
        iv_md5 = hashlib.md5(iv.encode('utf-8')).digest()
        aes = AES.new(key=key_md5, mode=AES.MODE_CBC, iv=iv_md5)
        code = aes.decrypt(base64.urlsafe_b64decode(decrypt_str))
        return unpad(code, AES.block_size)

    def translate(self) -> List[str]:
        """执行有道翻译"""
        time_id = int(time.time() * 1000)
        e = f"client=fanyideskweb&mysticTime={time_id}&product=webfanyi&key=fsdsogkndfokasodnaso"
        sign = hashlib.md5(e.encode()).hexdigest()

        cookies = {
            'OUTFOX_SEARCH_USER_ID': '700918787@10.110.96.153',
            'OUTFOX_SEARCH_USER_ID_NCOO': '192754076.3130601',
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://fanyi.youdao.com',
            'Pragma': 'no-cache',
            'Referer': 'https://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }
        data = {
            'i': self.text,
            'from': 'auto',
            'to': 'zh-CHS',
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
            encryption = response.text
            self.result = json.loads(self._decrypt(encryption))['translateResult'][0]['src']
            return self.result
        except Exception as e:
            print(f"有道翻译出错: {e}")
            return ["翻译出错，请稍后再试"]


class CibaTranslator(TranslateEngine):
    """金山词霸翻译引擎"""

    def __init__(self, text: str):
        super().__init__(text)
        self.__decode_key = None
        self.__sign = None
        self.__get_sign()

    def __get_sign(self) -> None:
        """获取金山词霸签名"""
        s = hashlib.md5(f"6key_web_new_fanyi6dVjYLFyzfkFkk{self.text}".encode()).hexdigest()[:16].encode()
        encode_key = "L4fBtD5fLC9FQw22".encode()
        self.__decode_key = "aahc3TfyfCEmER33".encode()
        cipher1 = AES.new(encode_key, AES.MODE_ECB)
        padded_data1 = pad(s, AES.block_size)
        encrypted = cipher1.encrypt(padded_data1)
        self.__sign = base64.b64encode(encrypted).decode('utf-8')

    def translate(self) -> List[str]:
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
            'from': 'zh',
            'to': 'en',
            'q': self.text,
        }
        params = {
            'c': 'trans',
            'm': 'fy',
            'client': '6',
            'auth_user': 'key_web_new_fanyi',
            'sign': self.__sign,
        }

        try:
            response = requests.post('https://ifanyi.iciba.com/index.php', params=params, headers=headers, data=data)
            response.encoding = 'utf-8'
            cipher2 = AES.new(self.__decode_key, AES.MODE_ECB)
            decrypt = unpad(cipher2.decrypt(base64.b64decode(response.json()['content'])), AES.block_size).decode(
                'utf-8')
            dict1 = json.loads(decrypt)
            self.result = dict1['out']
            return self.result
        except Exception as e:
            print(f"金山词霸翻译出错: {e}")
            return ["翻译出错，请稍后再试"]


class SougouTranslator(TranslateEngine):
    """搜狗翻译引擎"""
    __from_ = 'auto'
    __to_ = 'zh-CHS'
    __secret_code = '109984457'
    __cookies = {
        'ABTEST': '0|1747225250|v17',
        'SNUID': 'C6D3228B8086B49615E795F181D50316',
        'SUID': '4653A20B3850A20B0000000068248AA2',
        'wuid': '1747225250504',
        'FQV': 'c2f60136f423b4ec6a6c90d6eb2b682a',
        'translate.sess': '6b5d83a9-3efa-49f3-b1f2-d179e0b4f623',
        'SUV': '1747225251715',
        'SGINPUT_UPSCREEN': '1747225251748',
    }
    __headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    def __init__(self, text: str):
        self.__session = requests.session()
        super().__init__(text)

    def translate(self) -> str:
        s = hashlib.md5(f"{self.__from_}{self.__to_}{self.text}{self.__secret_code}".encode()).hexdigest()
        json_data = {
            'from': self.__from_,
            'to': self.__to_,
            'text': self.text,
            'client': 'pc',
            'fr': 'browser_pc',
            'needQc': 1,
            's': s,
            'uuid': 'd9a7d5d0-ed02-43b0-b7fc-dba258542c73',
            'exchange': False,
        }

        response = self.__session.post('https://fanyi.sogou.com/api/transpc/text/result', json=json_data,
                                       headers=self.__headers, cookies=self.__cookies)
        response.encoding = 'utf-8'
        print(response.json())
        return response.json()['data']['translate']['dit']


class TranslateWorker(QThread):
    """翻译工作线程"""

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, engine_name: str, text: str):
        super().__init__()
        self.engine_name = engine_name
        self.text = text

    def run(self) -> None:
        """运行翻译线程"""
        try:
            if not self.text.strip():
                self.finished.emit(["请输入要翻译的内容"])
                return

            # 根据引擎名称选择对应的翻译引擎
            translator = None
            if self.engine_name == "有道翻译":
                translator = YoudaoTranslator(self.text)
            elif self.engine_name == "百度翻译":
                translator = BaiduTranslator(self.text)
            elif self.engine_name == "金山词霸":
                translator = CibaTranslator(self.text)
            elif self.engine_name == "搜狗翻译":
                translator = SougouTranslator(self.text)

            if translator:
                results = translator.translate()
                self.finished.emit(results)
            else:
                self.error.emit("未知的翻译引擎")
        except Exception as e:
            self.error.emit(f"翻译出错: {str(e)}")


class ModernFrame(QFrame):
    """现代化的框架组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("鲨鱼翻译 v2.0")
        self.setup_ui()
        self.setup_connections()
        self.setup_styles()
        self.worker = None  # 保存当前翻译工作线程
        self.last_engine = ""  # 上次使用的翻译引擎

    def setup_ui(self) -> None:
        """设置 UI 界面"""
        # 主窗口设置
        self.setGeometry(100, 100, 960, 640)
        self.setMinimumSize(800, 500)

        # 创建中央小部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 创建顶部工具栏
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 引擎选择区域
        engine_layout = QHBoxLayout()

        self.engine_label = QLabel("翻译引擎:")
        self.engine_label.setFont(QFont("微软雅黑", 10))

        self.engine_combo = QComboBox()
        self.engine_combo.setFont(QFont("微软雅黑", 10))
        self.engine_combo.addItems(["金山词霸", "有道翻译", "搜狗翻译", "百度翻译"])
        self.engine_combo.setMinimumWidth(150)
        self.engine_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox:hover {
                border: 1px solid #80c0ff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left-width: 0px;
            }
        """)

        engine_layout.addWidget(self.engine_label)
        engine_layout.addWidget(self.engine_combo)
        engine_layout.addStretch()

        # 设置区域
        settings_layout = QHBoxLayout()

        self.font_size_label = QLabel("字体大小:")
        self.font_size_label.setFont(QFont("微软雅黑", 10))

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setFixedWidth(60)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 2px;
            }
        """)

        settings_layout.addWidget(self.font_size_label)
        settings_layout.addWidget(self.font_size_spin)
        settings_layout.addStretch()

        # 添加到顶部布局
        top_layout = QHBoxLayout()
        top_layout.addLayout(engine_layout)
        top_layout.addStretch()
        top_layout.addLayout(settings_layout)

        main_layout.addLayout(top_layout)

        # 创建输入输出区域
        content_layout = QHBoxLayout()

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 创建输入框架
        input_frame = ModernFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)

        input_header = QLabel("输入文本")
        input_header.setFont(QFont("微软雅黑", 11, QFont.Bold))

        self.text_input = QPlainTextEdit()
        self.text_input.setFont(QFont("微软雅黑", 12))
        self.text_input.setPlaceholderText("请输入要翻译的内容...")
        self.text_input.setStyleSheet("""
            QPlainTextEdit {
                border: none;
                background-color: #f0f0f0; /* 修改背景颜色为浅灰色 */
                color: #333333; /* 修改文字颜色为深灰色 */
            }
        """)

        input_layout.addWidget(input_header)
        input_layout.addWidget(self.text_input)

        # 创建输出框架
        output_frame = ModernFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(10, 10, 10, 10)

        output_header = QLabel("翻译结果")
        output_header.setFont(QFont("微软雅黑", 11, QFont.Bold))

        self.text_output = QPlainTextEdit()
        self.text_output.setFont(QFont("微软雅黑", 12))
        self.text_output.setPlaceholderText("翻译结果将显示在这里...")
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("""
            QPlainTextEdit {
                border: none;
                background-color: #f0f0f0; /* 修改背景颜色为浅灰色 */
                color: #333333; /* 修改文字颜色为深灰色 */
            }
        """)

        output_layout.addWidget(output_header)
        output_layout.addWidget(self.text_output)

        # 添加框架到分割器
        splitter.addWidget(input_frame)
        splitter.addWidget(output_frame)
        splitter.setSizes([400, 400])  # 设置初始大小

        content_layout.addWidget(splitter)
        main_layout.addLayout(content_layout, 1)

        # 创建翻译按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_button = QPushButton("清空")
        self.clear_button.setFont(QFont("微软雅黑", 10))
        self.clear_button.setFixedSize(100, 36)

        self.translate_button = QPushButton("翻译")
        self.translate_button.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.translate_button.setFixedSize(200, 36)

        button_layout.addWidget(self.clear_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.translate_button)

        main_layout.addLayout(button_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 设置右下角作者信息
        author_label = QLabel("By @鲨鱼爱兜兜")
        author_label.setFont(QFont("微软雅黑", 8))
        author_label.setStyleSheet("color: #888888;")
        self.status_bar.addPermanentWidget(author_label)

    def setup_connections(self) -> None:
        """设置信号连接"""
        self.translate_button.clicked.connect(self.translate_text)
        self.clear_button.clicked.connect(self.clear_text)
        self.engine_combo.currentTextChanged.connect(self.update_engine)
        self.font_size_spin.valueChanged.connect(self.update_font_size)

        # 输入框支持Ctrl+Enter快捷键翻译
        self.text_input.installEventFilter(self)

    def setup_styles(self) -> None:
        """设置UI样式"""
        # 设置全局风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6dad;
            }
            QPushButton#clear_button {
                background-color: #e0e0e0;
                color: #505050;
            }
            QPushButton#clear_button:hover {
                background-color: #d0d0d0;
            }
            QStatusBar {
                background-color: #f8f8f8;
                color: #606060;
                border-top: 1px solid #e0e0e0;
            }
            QPlainTextEdit {
                background-color: #f0f0f0; /* 修改背景颜色为浅灰色 */
                color: #333333; /* 修改文字颜色为深灰色 */
                border: none;
            }
        """)

        # 设置按钮对象名以便样式表识别
        self.clear_button.setObjectName("clear_button")
        self.translate_button.setObjectName("translate_button")

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """事件过滤器，用于拦截事件"""
        if obj == self.text_input and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            # Ctrl+Enter 快捷键翻译
            if key_event.key() == Qt.Key_Return and key_event.modifiers() & Qt.ControlModifier:
                self.translate_text()
                return True
        return super().eventFilter(obj, event)

    def update_engine(self, engine_name: str) -> None:
        """更新翻译引擎"""
        self.last_engine = engine_name
        self.status_bar.showMessage(f"当前使用: {engine_name}")

    def update_font_size(self, size: int) -> None:
        """更新字体大小"""
        font = QFont("微软雅黑", size)
        self.text_input.setFont(font)
        self.text_output.setFont(font)

    def clear_text(self) -> None:
        """清空输入和输出文本"""
        self.text_input.clear()
        self.text_output.clear()
        self.status_bar.showMessage("文本已清空")

    def translate_text(self) -> None:
        """执行翻译操作"""
        input_text = self.text_input.toPlainText().strip()
        engine_name = self.engine_combo.currentText()

        if not input_text:
            self.status_bar.showMessage("请输入要翻译的内容")
            return

        # 显示正在翻译提示
        self.text_output.setPlainText("正在翻译中...")
        self.status_bar.showMessage(f"正在使用 {engine_name} 翻译...")
        self.translate_button.setEnabled(False)

        # 创建并启动翻译线程
        self.worker = TranslateWorker(engine_name, input_text)
        self.worker.finished.connect(self.handle_translation_result)
        self.worker.error.connect(self.handle_translation_error)
        self.worker.start()

    def handle_translation_result(self, results: List[str]) -> None:
        """处理翻译结果"""
        self.text_output.clear()
        result = ''.join(results)
        self.text_output.appendPlainText(result)

        self.translate_button.setEnabled(True)
        self.status_bar.showMessage(f"翻译完成 ({self.engine_combo.currentText()})")

    def handle_translation_error(self, error_msg: str) -> None:
        """处理翻译错误"""
        self.text_output.setPlainText(f"翻译出错: {error_msg}")
        self.translate_button.setEnabled(True)
        self.status_bar.showMessage("翻译出错，请稍后再试")

    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        # 如果有正在运行的翻译线程，停止它
        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # 强制终止线程
            self.worker.wait()  # 等待线程结束
        event.accept()  # 允许关闭窗口


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
