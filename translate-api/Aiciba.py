"""
-*- coding: utf-8 -*-
@File   : .py
@author : @鲨鱼爱兜兜
@Time   : 2024/06/25 22:23
"""

import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import requests

word = input()
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
    'q': word
}
s = hashlib.md5(f"6key_web_new_fanyi6dVjYLFyzfkFkk{word}".encode()).hexdigest()[:16].encode()
encode_key = "L4fBtD5fLC9FQw22".encode()
decode_key = "aahc3TfyfCEmER33".encode()
cipher1 = AES.new(encode_key, AES.MODE_ECB)
padded_data1 = pad(s, AES.block_size)
encrypted = cipher1.encrypt(padded_data1)
sign = base64.b64encode(encrypted).decode('utf-8')
params = {
    'c': 'trans',
    'm': 'fy',
    'client': '6',
    'auth_user': 'key_web_new_fanyi',
    'sign': sign
}
response = requests.post('https://ifanyi.iciba.com/index.php', params=params, headers=headers, data=data)
response.encoding = 'utf-8'
cipher2 = AES.new(decode_key, AES.MODE_ECB)
decrypt = unpad(cipher2.decrypt(base64.b64decode(response.json()['content'])), AES.block_size).decode('utf-8')
res = json.loads(decrypt)
print(res['out'])
