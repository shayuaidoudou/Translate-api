"""
-*- coding: utf-8 -*-
@File   : .py
@author : @鲨鱼爱兜兜
@Time   : 2024/06/25 22:23
"""

import math
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QLabel, QVBoxLayout, QWidget, \
    QComboBox
from PySide6.QtGui import QFont, QPixmap, QColor, QPalette
import requests
import base64
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import re
import time


class My_baidu_translate:
    def __init__(self, word):
        self.word = word

    def get_sing(self, query):
        DEFAULT_TK = "320305.131321201"

        def cal_rlt(a, b):
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

    def send_request(self):
        url = "https://fanyi.baidu.com/v2transapi?from=en&to=zh"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Cookie": "BIDUPSID=529D72F795F09560A9A5CC1A17AE73A7; PSTM=1681276039; BAIDUID=529D72F795F09560D97567446104438A:FG=1; APPGUIDE_10_0_2=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; H_WISE_SIDS=219946_219561_216852_213349_214806_219942_213028_230174_204917_110085_236308_243706_243873_244726_240590_245412_247148_250889_249892_253427_254294_254473_254734_254689_239150_253212_250882_255938_255981_253685_107315_254075_256083_253990_255660_255476_254076_256500_254831_256739_251971_256229_254317_256589_256996_257080_257290_256096_251059_251133_254299_257482_244253_257543_257656_257663_255177_257936_257167_257903_257823_257586_257403_255231_257790_257791_253900_258235_258257_257995_258344_258511_258373_258372_227146_256859_258724_258728_258305_258938_257303_255910_258982_258958_230288_259034_259047_259050_257016_252256_259186_259190_259193_256223_259200_259413_259285_259316_259430_259517_259569_259606_256998_259558_259409_259645_251786; H_WISE_SIDS_BFESS=219946_219561_216852_213349_214806_219942_213028_230174_204917_110085_236308_243706_243873_244726_240590_245412_247148_250889_249892_253427_254294_254473_254734_254689_239150_253212_250882_255938_255981_253685_107315_254075_256083_253990_255660_255476_254076_256500_254831_256739_251971_256229_254317_256589_256996_257080_257290_256096_251059_251133_254299_257482_244253_257543_257656_257663_255177_257936_257167_257903_257823_257586_257403_255231_257790_257791_253900_258235_258257_257995_258344_258511_258373_258372_227146_256859_258724_258728_258305_258938_257303_255910_258982_258958_230288_259034_259047_259050_257016_252256_259186_259190_259193_256223_259200_259413_259285_259316_259430_259517_259569_259606_256998_259558_259409_259645_251786; BDUSS=h6eG1qcGMyNG9FTkJuVGgwVHVPTXIwWEV-VVdIRW9qODhDM3NSMjhnUkhoY2RrRVFBQUFBJCQAAAAAAQAAAAEAAAAp5g1rRG91RG91QUlTSEFZVQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEf4n2RH-J9kUH; BDUSS_BFESS=h6eG1qcGMyNG9FTkJuVGgwVHVPTXIwWEV-VVdIRW9qODhDM3NSMjhnUkhoY2RrRVFBQUFBJCQAAAAAAQAAAAEAAAAp5g1rRG91RG91QUlTSEFZVQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEf4n2RH-J9kUH; BAIDUID_BFESS=529D72F795F09560D97567446104438A:FG=1; BA_HECTOR=2gah21a4258181ah21010g2m1ib2i9t1o; ZFY=:Bm5JPjPwyZ:A6lDbsF8UsRm1GTqHmNyMKbKywqthif:Bk:C; RT=\"z=1&dm=baidu.com&si=lh9ofaq79e8&ss=lk2ljtmb&sl=0&tt=0&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=2av&ul=2b9cj&hd=2b9cz\"; BDRCVFR[bPTzwF-RsLY]=mk3SLVN4HKm; PSINO=1; delPer=0; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1688543894,1688709758,1689345794,1689391036; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1689391036; H_PS_PSSID=36550_38643_38831_39027_39023_38959_38954_39009_38961_38820_38990_39086_38636_26350_39092_39052_39100_38951; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ab_sr=1.0.1_ODY4MzdjODliZjBmYjk3MDM0MGE1YTYyODEzZmNiNTFhNDVjNGVlY2Q2YjdhMzdjYmFmYmQ0NjM0NzY3NDk5ZWYzYjJhNjQ3MWY1MjZkOGE3NWQ5ODU4MDUwNDY0ZmE5MTM5NzEyZWUxMTU3MGVkNThlZDE5Mjc0MmI4NTBlZTcxZTNmM2Q2ZWFhZjYyN2ZhMGU2YTU4MDMxN2Q1MWFiYjhlYzQ5NmU5YjJkZWNlNjcwNTk5NGZiMzM0ZWZlZmMy",
            "Acs-Token": "1689345795708_1689345863597_xPEQ0yYO9xuYJALqfUGYmCm7dHKG0DEGbCblkAwh1SCKpnEvJN3c/YMxbks/pjxClpAkOaBGQek9DfTUflz7RE8XELKkLxwZy7RVwcpK+VZyMqmjiAbqv50pWAKDvqTU6fCoDb9wuqMeM5de+QHKZ7DCtzxAnHrDYNkdX3P+bT0pLOxh315gGZL4OoyU7XfesTAeCtXs4KOHFP6UTJPc2lJHxKwdC4nvAWLV+R+kKpGpDWzTXxxyusP/KFAF8O4JslX/LQ5nq0NyXyOlppZtgXqQv5FBACoCtrtH6OQ9AMB008yQdbj/vJ5pJ+Mxi5HWwk2LJLFXd9YF9Zk5KYisUOSeN3DHwtoOU/CalmQyKsNtHUYON4IYTEhYQX/0Qw9Ie/8mfmkWYqMBZ8V8P6hA2vGhWbHaE+Xb7GUV2EK6lU1nbES/GZn8bzp2DzDQjwRrEPFA5jjGFfvHih1rjcLwxeRS95lwJbzh4JQf8fPUpLY="
        }
        params = {
            "from": "auto",
            "to": "en",
            "query": self.word,
            "simple_means_flag": "3",
            "sign": self.__sign,
            "token": "618e4f37cd15de2718962c27a17da2a4",
            "domain": "common",
            "ts": "1689345863582"
        }
        print(self.__sign)
        response = requests.post(url=url, headers=headers, params=params)
        response.encoding = 'utf-8'
        self.json_txt = response.json()

    def parse(self):
        self.trans_start = self.json_txt['trans_result']['data'][0]['src']
        self.trans_result = [x['dst'] for x in self.json_txt['trans_result']['data']]
        return self.trans_result


class My_sougou_translate:
    def __init__(self, word):
        self.word = word

    def spider(self):
        cookies = {
            'ABTEST': '1|1698379142|v17',
            'SUID': '8C178CDE8486A20A00000000653B3586',
            'wuid': '1698379142374',
            'SUV': '1698379141757',
            'SGINPUT_UPSCREEN': '1698379141770',
            'SNUID': 'BA1F85D7080F03D7B50E25C0094C36AB',
            'translate.sess': '52c734e0-35af-4633-9141-fdbc551dc41f',
            'FQV': '2452f1d34753ec176f373573f060b058',
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://fanyi.sogou.com',
            'Referer': 'https://fanyi.sogou.com/text?keyword=spiders&transfrom=auto&transto=zh-CHS&model=general',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        params = {
            'from': 'auto',
            'to': 'zh-CHS',
            'text': self.word,
            'client': 'pc',
            'fr': 'browser_pc',
            'needQc': 1,
            's': hashlib.md5(f'autozh-CHS{self.word}109984457'.encode()).hexdigest(),
            'uuid': '2e1c2124-2d2e-4e97-a313-dc907b543140'
        }
        response = requests.post('https://fanyi.sogou.com/api/transpc/text/result', cookies=cookies, headers=headers,
                                 params=params)
        response.encoding = 'utf-8'
        return response.json()['data']['translate']['dit']


class My_ali_translate:
    def __init__(self, word):
        self.word = word

    def get_csrf(self):
        cookies = {
            'xman_us_f': 'x_l=1',
            'xman_f': 'H8IHt+HNqvvQKaMOkkdIrDAIP9+4ESHj09k72MRUN2zqoXCVJmE8Fs4xUP7ptxMHkhRq4zuyGslxhdf5AvjVn5nauI1B/lMv/lfeWl780sdblL9sB5AlOg==',
            '__itrace_wid': '41319dd0-4c92-48ab-b175-fde4aeb96b85',
            'cna': 'mzZ2HQdTZxUCAd6MF67E2ekK',
            'xlly_s': '1',
            'xman_t': 'uhNfscv563JVygBKAa14Y17UlBgHDXhWE4DtCTjZDpkxovQsf4uid/ZPRzAJkp+I',
            'acs_usuc_t': 'acs_rt=d420076bb2fd45b2a3589804c36c7066',
            'acs_t': 'Ipu/zC6x696oNEHTmA2SC0rDmMyeUY/2YvhBapW9StCT2FEBzJTLldaiGP200+Lb',
            'tfstk': 'drnveDMNhQAD0V2MSRLk77XhZ-9krmHqojkCj5Vc5bh-LAv4SScgXRG3ZKrioFrTWfVomSD0cturtvsmmErGXorafBAHxHDm3lr62n9yr72RhsABtHxn3Ew4jYOH_ymLOG1MftLJ3M2nA-TZL3INBo1a3rFIeeSFxbI3uWMbwGOi2OPnxDL3X6VLIZ9JeN7al8RLGdzf.',
            'l': 'fBjv27lrNttEvz9QBOfaFurza77ORIR4ouPzaNbMi9fPOU5p5HLCB1T4K289CnGVes6w73-WjmOpBA8dPyCVE5CTpdMCE80mFdhyN3pR.',
            'isg': 'BMbGrGzt3iOhaIraqMMqbRhrF7xIJwrhRGUw7rDvkunEs2TNH7e_8f8Bi-9_HQL5',
        }
        headers = {
            'authority': 'translate.alibaba.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        response = requests.get('https://translate.alibaba.com/', cookies=cookies, headers=headers)
        csrf = re.findall("_csrf : '(.*?)'", response.text)[0]
        return csrf

    def send_requests(self):
        cookies = {
            'xman_us_f': 'x_l=1',
            'xman_f': 'H8IHt+HNqvvQKaMOkkdIrDAIP9+4ESHj09k72MRUN2zqoXCVJmE8Fs4xUP7ptxMHkhRq4zuyGslxhdf5AvjVn5nauI1B/lMv/lfeWl780sdblL9sB5AlOg==',
            '__itrace_wid': '41319dd0-4c92-48ab-b175-fde4aeb96b85',
            'cna': 'mzZ2HQdTZxUCAd6MF67E2ekK',
            'xlly_s': '1',
            'xman_t': 'uhNfscv563JVygBKAa14Y17UlBgHDXhWE4DtCTjZDpkxovQsf4uid/ZPRzAJkp+I',
            'acs_usuc_t': 'acs_rt=d420076bb2fd45b2a3589804c36c7066',
            'acs_t': '6jD/VRPCoQIc18eTW+Z73BcT+ty9Y9cPkV0CCMgpg8LSGrNA6Nwk4sarJRLPVrIC',
            'l': 'fBjv27lrNttEvMXNBO5Bhurza779nIdffrVzaNbMiIEGa6pPMUZKSNC6uJkWydtjgTCEedxyVhmX9dh6JLadgTVO6JpsdT2onxvtaQtJe',
            'tfstk': 'dmj2eJsyUoEVYFLGSe-NLmKCNf-vVHFQ7GO6IOXMhIAD1FtN7OfuHcwAIhyNG1wYBrBM_15Ww18THCOM_16Gl8ZQAtBvXhAaOkZQ4HHebmjiNw6dHhKgOYigRkWA9AtnTGpFKqHSHU0hQQjXu8u1FflvicmGmlpJTxOWeKjy3ERHlCWNSfplnojOuf0woLpyO8yPHf8Q-',
            'isg': 'BCQknUjiHGUWSWg0pqmo646R9SIWvUgnku_SwD5EM--P6cOzQM3ut2kPqUFxN4B_',
        }
        headers = {
            'authority': 'translate.alibaba.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.1',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundarytk8Fu0tafy2Fmk54',
            'origin': 'https://translate.alibaba.com',
            'referer': 'https://translate.alibaba.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'x-xsrf-token_property_item': '0cd9041e-bd85-491e-a17e-86d7be5f6f27',
        }
        csrf = self.get_csrf()
        data = f'------WebKitFormBoundarytk8Fu0tafy2Fmk54\r\nContent-Disposition: form-data; name="srcLang"\r\n\r\nauto\r\n------WebKitFormBoundarytk8Fu0tafy2Fmk54\r\nContent-Disposition: form-data; name="tgtLang"\r\n\r\nen\r\n------WebKitFormBoundarytk8Fu0tafy2Fmk54\r\nContent-Disposition: form-data; name="domain"\r\n\r\ngeneral\r\n------WebKitFormBoundarytk8Fu0tafy2Fmk54\r\nContent-Disposition: form-data; name="query"\r\n\r\n{self.word}\r\n------WebKitFormBoundarytk8Fu0tafy2Fmk54\r\nContent-Disposition: form-data; name="_csrf"\r\n\r\n{csrf}\r\n------WebKitFormBoundarytk8Fu0tafy2Fmk54--\r\n'.encode()
        response = requests.post('https://translate.alibaba.com/api/translate/text', cookies=cookies, headers=headers,
                                 data=data)
        result = response.json()['data']['translateText']
        return result


class My_youdao_translate:
    def __init__(self, word):
        self.word = word

    def decrypt(self, decrypt_str):
        key = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
        iv = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
        key_md5 = hashlib.md5(key.encode('utf-8')).digest()
        iv_md5 = hashlib.md5(iv.encode('utf-8')).digest()
        aes = AES.new(key=key_md5, mode=AES.MODE_CBC, iv=iv_md5)
        code = aes.decrypt(base64.urlsafe_b64decode(decrypt_str))
        return unpad(code, AES.block_size)

    def spider(self):
        query = self.word
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
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        data = {
            'i': query,
            'from': 'auto',
            'to': '',
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
        response = requests.post('https://dict.youdao.com/webtranslate', cookies=cookies, headers=headers, data=data)
        encryption = response.text
        decrypt_list = [x[0]['tgt'] for x in json.loads(self.decrypt(encryption))['translateResult']]
        return decrypt_list


class My_ciba_translate:
    def __init__(self, word):
        self.__decode_key = None
        self.__sign = None
        self.__word = word
        self.__get_sign()

    def __get_sign(self):
        s = hashlib.md5(f"6key_web_new_fanyi6dVjYLFyzfkFkk{self.__word}".encode()).hexdigest()[:16].encode()
        encode_key = "L4fBtD5fLC9FQw22".encode()
        self.__decode_key = "aahc3TfyfCEmER33".encode()
        cipher1 = AES.new(encode_key, AES.MODE_ECB)
        padded_data1 = pad(s, AES.block_size)
        encrypted = cipher1.encrypt(padded_data1)
        self.__sign = base64.b64encode(encrypted).decode('utf-8')

    def decode_data(self):
        headers = {
            'authority': 'ifanyi.iciba.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.iciba.com',
            'referer': 'https://www.iciba.com/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        data = {
            'from': 'en',
            'to': 'zh',
            'q': self.__word,
        }
        params = {
            'c': 'trans',
            'm': 'fy',
            'client': '6',
            'auth_user': 'key_web_new_fanyi',
            'sign': self.__sign,
        }
        response = requests.post('https://ifanyi.iciba.com/index.php', params=params, headers=headers, data=data)
        response.encoding = 'utf-8'
        cipher2 = AES.new(self.__decode_key, AES.MODE_ECB)
        decrypt = unpad(cipher2.decrypt(base64.b64decode(response.json()['content'])), AES.block_size).decode('utf-8')
        dict1 = json.loads(decrypt)
        return dict1['out']


def handle():
    choice = combo_box.currentText()
    print(f"当前接口源：{choice[:4]}")


def fff():
    if combo_box.currentText() == "百度翻译":
        text = textEdit_input.toPlainText()
        baidu_trans = My_baidu_translate(text)
        baidu_trans.get_sing(text)
        baidu_trans.send_request()
        result_list = baidu_trans.parse()
        textEdit_result.clear()
        for result in result_list:
            textEdit_result.appendPlainText(result)
    elif combo_box.currentText() == '有道翻译':
        text = textEdit_input.toPlainText()
        youdao = My_youdao_translate(text)
        my_list = youdao.spider()
        textEdit_result.clear()
        for x in my_list:
            textEdit_result.appendPlainText(x.strip())
    elif combo_box.currentText() == '金山词霸':
        text = textEdit_input.toPlainText()
        ciba = My_ciba_translate(text)
        result = ciba.decode_data()
        textEdit_result.clear()
        textEdit_result.setPlainText(result)


if __name__ == '__main__':
    app = QApplication([])
    window = QMainWindow()
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(152, 251, 152))
    window.setPalette(palette)
    window.setAutoFillBackground(True)
    layout = QVBoxLayout()
    window.setLayout(layout)
    window.setGeometry(100, 100, 880, 600)
    window.setWindowTitle("Shark Translate")
    textEdit_input = QPlainTextEdit(window)
    textEdit_input.setPlaceholderText("请输入要翻译的内容")
    textEdit_input.move(20, 80)
    textEdit_input.resize(400, 450)
    layout.addWidget(textEdit_input)
    label_text = QLabel("翻译接口源：", window)
    label_text.resize(75, 30)
    label_text.move(15, 10)
    combo_box = QComboBox(window)
    font = QFont()
    font.setPointSize(8)
    combo_box.setFont(font)
    combo_box.move(100, 10)
    combo_box.resize(220, 30)
    layout.addWidget(combo_box)
    item = ['有道翻译', '百度翻译', '金山词霸']
    for it in item:
        combo_box.addItem(it)
    combo_box.currentIndexChanged.connect(handle)
    button = QPushButton("翻译", window)
    button.setFixedSize(400, 40)
    button.move(20, 540)
    button.clicked.connect(fff)
    layout.addWidget(button)
    textEdit_result = QPlainTextEdit(window)
    textEdit_result.setPlaceholderText("译文")
    textEdit_result.setReadOnly(True)
    textEdit_result.move(450, 10)
    textEdit_result.resize(400, 560)
    layout.addWidget(textEdit_result)
    window.show()
    app.exec()
