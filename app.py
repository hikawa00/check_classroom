import streamlit as st
import json
import datetime

# 页面配置
st.set_page_config(page_title="北邮(BUPT) 空教室查询", page_icon="🏫", layout="wide")

# ================= 1. 数据加载与区域划分 =================
@st.cache_data
def load_data():
    with open("school_timetable.json", "r", encoding="utf-8") as f:
        return json.load(f)

timetable = load_data()
all_classrooms = sorted(list(set(item["classroom"] for item in timetable)))

# 完美的精准匹配字典
CAMPUS_DATA = {
    "西土城本部": {
        "教二": ["2-"],        
        "教三": ["3-"],        
        "教四": ["4-"],        
        "未来学习大楼": ["未来学习", "未来", "WL"] 
    },
    "沙河校区": {
        "教学实验综合楼N": ["综合楼-N", "实验楼-N"],  
        "教学实验综合楼S": ["综合楼-S", "实验楼-S"],  
        "智慧教学楼（S1）": ["智慧", "S1"]
    }
}

def get_classroom_location(room_name):
    for campus, buildings in CAMPUS_DATA.items():
        for b_name, keywords in buildings.items():
            if any(kw in room_name for kw in keywords):
                return campus, b_name
    return "其他", "其他"

# ================= 2. 时间与精准节次配置 =================
ANCHOR_DATE = datetime.date(2026, 5, 29)
ANCHOR_WEEK = 13

# 14个小节的时间映射（用于自动高亮）
PERIOD_TIMING = {
    1:  ("08:00", "08:45"),
    2:  ("08:50", "09:35"),
    3:  ("09:50", "10:35"),
    4:  ("10:40", "11:25"),
    5:  ("11:30", "12:15"),
    6:  ("13:00", "13:45"),
    7:  ("13:50", "14:35"),
    8:  ("14:45", "15:30"),
    9:  ("15:40", "16:25"),
    10: ("16:35", "17:20"),
    11: ("17:25", "18:10"),
    12: ("18:30", "19:15"),
    13: ("19:20", "20:05"),
    14: ("20:10", "20:55"),
}

def get_current_school_time():
    today = datetime.date.today()
    delta_days = (today - ANCHOR_DATE).days
    current_weekday = (4 + delta_days) % 7 + 1
    anchor_monday = ANCHOR_DATE - datetime.timedelta(days=4)
    delta_weeks = (today - anchor_monday).days // 7
    return max(1, ANCHOR_WEEK + delta_weeks), current_weekday

def get_current_period_index():
    """实时计算现在几点几分，命中第几节课"""
    now_str = datetime.datetime.now().strftime("%H:%M")
    for period, (start, end) in PERIOD_TIMING.items():
        if start <= now_str <= end:
            return period
    return None # 此时不在任何一节课的时间段内

auto_week, auto_weekday = get_current_school_time()
current_live_period = get_current_period_index()

# ================= 3. 核心多节次过滤算法 =================
def find_empty_rooms_multi_periods(target_week, target_weekday, selected_periods, selected_buildings):
    if not selected_periods:
        return []
        
    busy_rooms = set()
    for item in timetable:
        if item["weekday"] == target_weekday:
            # 只要这节课在用户勾选的【任意一个节次】中，就需要检查
            if item["period"] in selected_periods:
                weeks_str = item["weeks"]
                is_busy = False
                for part in weeks_str.split(','):
                    if '-' in part:
                        s, e = map(int, part.split('-'))
                        if s <= target_week <= e: is_busy = True
                    else:
                        if part.isdigit() and int(part) == target_week: is_busy = True
                if is_busy:
                    busy_rooms.add(item["classroom"])
                    
    filtered_empty = []
    for room in all_classrooms:
        _, b_name = get_classroom_location(room)
        if b_name in selected_buildings and room not in busy_rooms:
            filtered_empty.append(room)
    return filtered_empty

# ================= 4. 前端 GUI 渲染 =================
st.title("🏫 北邮(BUPT) 智能空教室查询系统")

# 头部加入实时时间锚点状态栏
now_time_display = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"🕒 服务器当前实时时间：{now_time_display} | 推荐课表：第 {auto_week} 周 星期{['一','二','三','四','五','六','日'][auto_weekday-1]}")
st.markdown("---")

# 界面两栏布局
layout_left, layout_right = st.columns([1, 2])

with layout_left:
    st.subheader("⚙️ 基础筛选")
    
    selected_campuses = st.multiselect(
        "📍 选择校区", 
        options=list(CAMPUS_DATA.keys()), 
        default=["西土城本部"] # 默认勾选西土城，体验丝滑
    )
    
    available_buildings = []
    for campus in selected_campuses:
        available_buildings.extend(list(CAMPUS_DATA[campus].keys()))
        
    selected_buildings = st.multiselect(
        "🏢 选择教学楼", 
        options=available_buildings, 
        default=available_buildings[:2] # 默认帮选前两个楼
    )
    
    with st.expander("📅 教学周/星期微调"):
        week = st.number_input("教学周次", min_value=1, max_value=25, value=auto_week)
        weekday = st.selectbox("星期几", options=[1,2,3,4,5,6,7], index=auto_weekday-1,
                               format_func=lambda x: f"星期{['一','二','三','四','五','六','日'][x-1]}")

# 跨栏或者放在右侧上方的：14 节次大平铺选择面板
st.markdown("### ⏱️ 选择上课时间段")
st.write("点击下方方块选择一节或多节课（支持跨节多选）。带有 🔥 标识的为**当前实时进行中**的节次：")

# 复刻原版的平铺大网格（分成 5 列展示 14 个小节）
selected_periods = []
grid_cols = st.columns(5)

for p in range(1, 15):
    start_t, end_t = PERIOD_TIMING[p]
    
    # 判断当前实时时间是否处于这一节课
    is_current = (p == current_live_period)
    label_prefix = "🔥 " if is_current else ""
    
    # 构造卡片上的文本描述
    button_text = f"{label_prefix}第 {p:02d} 节\n({start_t} ~ {end_t})"
    
    # 放入网格中，使用 st.checkbox 伪装成平铺块，或者用 st.toggle 更有高级感
    with grid_cols[(p-1) % 5]:
        if st.toggle(button_text, value=(p in [1, 2] if not is_current else True), key=f"period_{p}"):
            selected_periods.append(p)

# 全选快捷键
if st.button("全选所有节次 📅"):
    st.info("提示：如需全选，请直接将上方需要的方块顺次点亮即可。")

# ================= 5. 结果渲染展示 =================
st.markdown("---")
st.subheader("🟢 实时空闲教室面板")

if not selected_buildings:
    st.warning("⚠️ 请在上方选择至少一栋教学楼！")
elif not selected_periods:
    st.info("💡 请至少点击上方激活一个时间节次方块！")
else:
    # 执行多节次联合查询
    result_rooms = find_empty_rooms_multi_periods(week, weekday, selected_periods, selected_buildings)
    
    sorted_periods = sorted(selected_periods)
    st.markdown(f"📊 正在查询：**第 {week} 周** | **星期{['一','二','三','四','五','六','日'][weekday-1]}** | 选定节次: `第 {sorted_periods} 节`")
    
    # 按楼归类展示
    rooms_by_building = {b: [] for b in selected_buildings}
    for room in result_rooms:
        _, b_name = get_classroom_location(room)
        if b_name in rooms_by_building:
            rooms_by_building[b_name].append(room)
            
    res_cols = st.columns(len(selected_buildings) if len(selected_buildings) > 0 else 1)
    
    for i, b_name in enumerate(selected_buildings):
        with res_cols[i]:
            st.markdown(f"#### 🏢 {b_name} (`{len(rooms_by_building[b_name])}` 间空闲)")
            rooms = rooms_by_building[b_name]
            if rooms:
                for room in rooms:
                    st.success(f"📍 {room}")
            else:
                st.caption("无空闲教室")