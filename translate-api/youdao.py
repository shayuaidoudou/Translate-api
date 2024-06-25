"""
-*- coding: utf-8 -*-
@File   : .py
@author : @鲨鱼爱兜兜
@Time   : 2024/06/25 22:23
"""

import base64
import json
import requests
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt(decrypt_str):
    key = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    iv = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    key_md5 = hashlib.md5(key.encode('utf-8')).digest()
    iv_md5 = hashlib.md5(iv.encode('utf-8')).digest()
    aes = AES.new(key=key_md5, mode=AES.MODE_CBC, iv=iv_md5)
    code = aes.decrypt(base64.urlsafe_b64decode(decrypt_str))
    return unpad(code, AES.block_size).decode('utf8')


query = input()
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
response.encoding = 'utf-8'
decrypt = decrypt(response.text)
print(json.loads(decrypt))
