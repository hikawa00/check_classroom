import asyncio
from playwright.async_api import async_playwright

# 你的教务系统账号和密码
USERNAME = "2024213403"
PASSWORD = "MciWhu@0327"

async def run():
    async with async_playwright() as p:
        # 启动浏览器（headless=True 表示在后台运行，不弹出浏览器窗口）
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("正在打开教务系统登录页...")
        # 替换成你学校教务系统的真实登录 URL
        await page.goto("https://jwgl.bupt.edu.cn/jsxsd/")

        # 1. 模拟真人输入账号和密码
        # 注：这里的 #userAccount 和 #userPassword 是根据你之前发给我的源码定位的
        await page.fill("#userAccount", USERNAME)
        await page.fill("#userPassword", PASSWORD)
        
        print("正在点击登录...")
        # 2. 点击登录按钮并等待页面加载完成
        # 混合处理：如果点击后会跳转，使用 wait_for_load_state
        await page.click("button.login_btn")
        await page.wait_for_load_state("networkidle")

        # 验证是否登录成功
        if "请先登录" in await page.content():
            print("❌ 登录失败，请检查账号密码或是否需要验证码！")
            await browser.close()
            return

        print("✅ 登录成功！正在跳转至教室课表页面...")

        # 3. 登录成功后，直接让浏览器跳转到课表数据接口页面
        # 这样浏览器会自动带着刚才登录成功的身份凭证（Cookie）去请求
        data_url = "https://jwgl.bupt.edu.cn/jsxsd/kbcx/kbxx_classroom_ifr"
        await page.goto(data_url)
        await page.wait_for_load_state("networkidle")

        # 4. 获取带有课表数据的 HTML 源码
        html_content = await page.content()
        
        print("================ 抓取成功 ================")
        print(f"成功拿到课表网页，内容长度：{len(html_content)} 字节")
        
        # 简单验证源码里有没有课表特征
        if "kbcontent1" in html_content:
            print("🎉 完美！网页中包含真实的课表数据格子（kbcontent1）！")
            
            # 把拿到的网页保存到本地，方便后续解析
            with open("classroom_kb.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("保存成功，文件名为：classroom_kb.html")
        else:
            print("❓ 成功进去了，但页面里好像没有课表格子，请检查默认页面是否有数据。")

        await browser.close()

# 运行脚本
asyncio.run(run())