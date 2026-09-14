import requests

# 1. 填入你刚刚在浏览器里看到的最新 Cookie
cookies = {
    'JSESSIONID': 'AAD277DDA429B71CC89D21E622167922' 
}

# 2. 强智系统对 User-Agent 有基础要求，模仿浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://jwgl.bupt.edu.cn/jsxsd/kbcx/kbxx_classroom',
}

# 3. 发送请求（先查默认的初始页面）
url = 'https://jwgl.bupt.edu.cn/jsxsd/kbcx/kbxx_classroom_ifr'

try:
    response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
    
    print("================ 结果验证 ================")
    if "请先登录" in response.text or "登录" in response.text:
        print("❌ 结果：依然被拦截了！说明 Cookie 还是不对或已过期。")
    elif "kbcontent1" in response.text or "教室" in response.text:
        print("✅ 成功！！！拿到了真正的课表网页结构！")
    else:
        print("❓ 拿到了网页，但既不是登录页也不是课表，前100个字是：")
        print(response.text.strip()[:100])

except Exception as e:
    print(f"请求发生错误: {e}")