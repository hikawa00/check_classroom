import requests

cookies = {
    'JSESSIONID': 'AAD277DDA429B71CC89D21E622167922',
    '_ga': 'GA1.1.2009502105.1749023959',
    '_ga_LFG7NH3ZTX': 'GS2.1.s1749023959$o1$g1$t1749024465$j60$l0$h0',
    'route': '9a379300782a86f848686ae6b1ce2c8c',
    'JSESSIONID': '681B5647ADDC44DE19CB77E95F4CBC8B',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://jwgl.bupt.edu.cn',
    'Referer': 'https://jwgl.bupt.edu.cn/jsxsd/kbcx/kbxx_classroom',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
    'sec-ch-ua': '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'JSESSIONID=0FA3C1635F83D35D4FC447246A1A64FC; _ga=GA1.1.2009502105.1749023959; _ga_LFG7NH3ZTX=GS2.1.s1749023959$o1$g1$t1749024465$j60$l0$h0; route=9a379300782a86f848686ae6b1ce2c8c; JSESSIONID=681B5647ADDC44DE19CB77E95F4CBC8B',
}

data = {
    'xnxqh': '2025-2026-2',
    'kbjcmsid': '9475847A3F3033D1E05377B5030AA94D',
    'skyx': '',
    'xqid': '01',
    'jzwid': '21',
    'skjsid': '',
    'skjs': '',
    'zc1': '',
    'zc2': '',
    'skxq1': '',
    'skxq2': '',
    'jc1': '',
    'jc2': '',
}

response = requests.post('https://jwgl.bupt.edu.cn/jsxsd/kbcx/kbxx_classroom_ifr', cookies=cookies, headers=headers, data=data)
# 确保最后有这两行
print("状态码:", response.status_code)  # 看看是不是 200
print("网页内容:", response.text)