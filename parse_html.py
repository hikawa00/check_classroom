from bs4 import BeautifulSoup
import re
import json

# 读取你本地的 HTML 文件
with open("classroom_kb.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# 找到表格的主体行
tbody = soup.find("tbody")
if not tbody:
    # 如果没有 tbody，直接找所有的 tr
    all_rows = soup.find_all("tr")
else:
    all_rows = tbody.find_all("tr")

all_parsed_data = []

print("🚀 开始解析全校教室课表大表...")

for row in all_rows:
    cells = row.find_all("td", recursive=False)
    
    # 强智系统表格的一行如果有效，第一个单元格必须是教室名称
    if not cells:
        continue
        
    classroom_name = cells[0].get_text(strip=True)
    
    # 排除表头行（比如第一单元格叫 "教室\节次" 的行）
    if "教室" in classroom_name or not classroom_name:
        continue
    
    # 开始遍历这间教室后面的所有课程格子 (从索引 1 开始)
    for col_index in range(1, len(cells)):
        cell = cells[col_index]
        
        # 寻找单元格里所有 class 为 kbcontent1 的 div 标签
        divs = cell.find_all("div", class_="kbcontent1")
        
        if not divs:
            continue  # 说明这节课这间教室是空的
            
        # 根据列索引计算对应的星期和节次
        weekday = (col_index - 1) // 14 + 1
        period = (col_index - 1) % 14 + 1
        
        # 一个格子里可能有多个课（单双周轮替）
        for div in divs:
            text = div.get_text(" ", strip=True)
            if not text:
                continue
                
            # 使用正则表达式匹配周次，如 "(11周)" 或 "(1-8周)" 或 "(9-10,12,14-16周)"
            week_match = re.search(r'\((.*?)\s*周\)', text)
            weeks = week_match.group(1) if week_match else "全学期"
            
            # 清理出干净的课程名（通常是文本的前半段）
            # 也可以直接保留完整文本供查询展示
            all_parsed_data.append({
                "classroom": classroom_name,
                "weekday": weekday,
                "period": period,
                "weeks": weeks,
                "detail": text
            })

print(f"🎉 解析完成！全校共提取出 {len(all_parsed_data)} 条具体的排课记录。")

# 保存为规范的 JSON 文件
with open("school_timetable.json", "w", encoding="utf-8") as f:
    json.dump(all_parsed_data, f, ensure_ascii=False, indent=4)
print("💾 数据已成功写入：school_timetable.json")

# 预览前 3 条
if all_parsed_data:
    print("\n数据格式预览:")
    print(json.dumps(all_parsed_data[:3], ensure_ascii=False, indent=2))