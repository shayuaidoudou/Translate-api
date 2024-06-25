"""
-*- coding: utf-8 -*-
@File   : .py
@author : @鲨鱼爱兜兜
@Time   : 2024/06/25 22:23
"""

import requests

query = input()
cookies = {
    'QiHooGUID': 'CD711E29AF0DDB2AE2AC5174A21A78CB.1700807377894',
    '__guid': '15484592.2679069343796695600.1709564733332.9546',
    'so_huid': '11lieFZAMo62jQiVEFxiNyAWxL87vX%2FIKfjJyM05M%2BElg%3D',
    '__huid': '11lieFZAMo62jQiVEFxiNyAWxL87vX%2FIKfjJyM05M%2BElg%3D',
    'Q_UDID': 'e5653a0c-9642-8871-17d6-0097687f5429',
    'count': '1',
}
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://fanyi.so.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'pro': 'fanyi',
    'referer': 'https://fanyi.so.com/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}
params = {
    'eng': '1',
    'validate': '',
    'ignore_trans': '0',
    'query': query,
}
response = requests.post('https://fanyi.so.com/index/search', params=params, cookies=cookies, headers=headers)
response.encoding = 'utf-8'
print(response.json())
