import json

# 1. 加载你刚刚解析成功的全校课表数据库
with open("school_timetable.json", "r", encoding="utf-8") as f:
    timetable = json.load(f)

# 2. 获取全校所有的教室名单（去重）
all_classrooms = sorted(list(set(item["classroom"] for item in timetable)))

def find_empty_classrooms(target_week, target_weekday, target_period):
    """
    寻找空教室的核心逻辑
    """
    # 先记录哪些教室在这一时刻是有课的
    busy_classrooms = set()
    
    for item in timetable:
        # 判断星期和节次是否吻合
        if item["weekday"] == target_weekday and item["period"] == target_period:
            
            # 解析周次字符串（处理 "1-8"、"11"、"9-10,12,14-16" 等复杂情况）
            weeks_str = item["weeks"]
            is_busy_this_week = False
            
            # 简单而强大的拆分逻辑
            for part in weeks_str.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start <= target_week <= end:
                        is_busy_this_week = True
                else:
                    if part.isdigit() and int(part) == target_week:
                        is_busy_this_week = True
            
            if is_busy_this_week:
                busy_classrooms.add(item["classroom"])
                
    # 全校教室 减去 有课的教室 = 空教室
    empty_classrooms = [rm for rm in all_classrooms if rm not in busy_classrooms]
    return empty_classrooms

# ================= 交互查询界面 =================
print("🏫 欢迎使用北邮(BUPT)空教室精细化查询系统 🏫")
print(f"当前数据库内总计包含教室：{len(all_classrooms)} 间\n")

try:
    week = int(input("请输入当前周次 (如 11): "))
    weekday = int(input("请输入星期几 (数字 1-7, 如周一输 1): "))
    period = int(input("请输入第几节课 (数字 1-14, 如第3节课输 3): "))
    
    empty_rooms = find_empty_classrooms(week, weekday, period)
    
    print("\n================ 查询结果 ================")
    print(f"在 第 {week} 周 | 星期 {weekday} | 第 {period} 节课，以下教室空闲：")
    print(f"总计找到 {len(empty_rooms)}间 空闲教室：\n")
    
    # 分行打印，方便查看
    for i, room in enumerate(empty_rooms, 1):
        print(f"[{i:02d}] {room}", end="\t")
        if i % 4 == 0:  # 每行打印4个教室
            print()
    print("\n==========================================")

except ValueError:
    print("输入错误，请输入纯数字！")