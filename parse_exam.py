import pandas as pd
import json
import datetime

# 1. 读取 Excel 文件（如果是 .xls 请用 read_excel；如果是 .csv 请用 read_csv）
# 确保文件名和你的本地文件名一字不差
try:
    df = pd.read_excel("test_classroom.xls")
except:
    df = pd.read_csv("附件1：北京邮电大学2025-2026学年第二学期本科生期末考试考表.xls - 093313748.csv", encoding="utf-8")

# 节次时间映射
PERIOD_TIMING = {
    1:  ("08:00", "08:45"), 2:  ("08:50", "09:35"), 3:  ("09:50", "10:35"),
    4:  ("10:40", "11:25"), 5:  ("11:30", "12:15"), 6:  ("13:00", "13:45"),
    7:  ("13:50", "14:35"), 8:  ("14:45", "15:30"), 9:  ("15:40", "16:25"),
    10: ("16:35", "17:20"), 11: ("17:25", "18:10"), 12: ("18:30", "19:15"),
    13: ("19:20", "20:05"), 14: ("20:10", "20:55"),
}

def time_to_periods(exam_time_str):
    """把类似 '08:00~10:00' 的时间段，转换成受影响的节次列表"""
    # 兼容波浪号 ~ 和短横线 -
    exam_time_str = exam_time_str.replace('~', '-')
    try:
        start_str, end_str = exam_time_str.split('-')
        start_str, end_str = start_str.strip(), end_str.strip()
    except:
        return []
        
    affected_periods = []
    for p, (p_start, p_end) in PERIOD_TIMING.items():
        if not (end_str <= p_start or start_str >= p_end):
            affected_periods.append(p)
    return affected_periods

exam_list = []

# 2. 遍历考表，精准提取你表格里的字段
for index, row in df.iterrows():
    try:
        # 如果“考试地点”为空，说明是由教师自行安排或者没排考场，直接跳过
        if pd.isna(row['考试地点']) or str(row['考试地点']).strip() == "" or "自行安排" in str(row['考试地点']):
            continue
            
        date_str = str(row['考试日期']).strip()  # 提取考试日期
        time_str = str(row['考试时间']).strip()  # 提取考试时间 (如 08:00~10:00)
        room_str = str(row['考试地点']).strip()  # 提取真实教室 (如 3-333)
        
        # 转换成 14 节课对应的编号
        periods = time_to_periods(time_str)
        
        exam_list.append({
            "date": date_str,
            "periods": periods,
            "classroom": room_str
        })
    except Exception as e:
        print(f"解析第 {index+2} 行失败: {e}")

# 3. 保存为结构化的 exam_timetable.json
with open("exam_timetable.json", "w", encoding="utf-8") as f:
    json.dump(exam_list, f, ensure_ascii=False, indent=4)

print(f"🎉 成功清洗考试数据！共成功导入 {len(exam_list)} 场考试。")