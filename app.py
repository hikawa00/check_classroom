import streamlit as st
import json
import datetime

# 页面配置
st.set_page_config(page_title="BUPT空教室", page_icon="🏫", layout="wide")

# ================= 1. 初始化会话状态 (Session State) =================
# 用来记住全选按钮的状态，实现"全选/全清"切换
if "all_selected" not in st.session_state:
    st.session_state.all_selected = False

# ================= 2. 数据加载与区域划分 =================
@st.cache_data
def load_data():
    with open("school_timetable.json", "r", encoding="utf-8") as f:
        return json.load(f)

timetable = load_data()
all_classrooms = sorted(list(set(item["classroom"] for item in timetable)))

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

# ================= 3. 完美北京时间计算 (最新标准) =================
ANCHOR_DATE = datetime.date(2026, 5, 29)
ANCHOR_WEEK = 13

PERIOD_TIMING = {
    1:  ("08:00", "08:45"), 2:  ("08:50", "09:35"), 3:  ("09:50", "10:35"),
    4:  ("10:40", "11:25"), 5:  ("11:30", "12:15"), 6:  ("13:00", "13:45"),
    7:  ("13:50", "14:35"), 8:  ("14:45", "15:30"), 9:  ("15:40", "16:25"),
    10: ("16:35", "17:20"), 11: ("17:25", "18:10"), 12: ("18:30", "19:15"),
    13: ("19:20", "20:05"), 14: ("20:10", "20:55"),
}

def get_bj_now():
    """获取精准无警告的北京时间"""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.replace(tzinfo=None) + datetime.timedelta(hours=8)

def get_current_school_time():
    bj_today = get_bj_now().date()
    delta_days = (bj_today - ANCHOR_DATE).days
    current_weekday = (4 + delta_days) % 7 + 1
    anchor_monday = ANCHOR_DATE - datetime.timedelta(days=4)
    delta_weeks = (bj_today - anchor_monday).days // 7
    return max(1, ANCHOR_WEEK + delta_weeks), current_weekday

def get_current_period_index():
    now_str = get_bj_now().strftime("%H:%M")
    for period, (start, end) in PERIOD_TIMING.items():
        if start <= now_str <= end:
            return period
    return None

auto_week, auto_weekday = get_current_school_time()
current_live_period = get_current_period_index()

# ================= 4. 过滤算法 =================
def find_empty_rooms_multi_periods(target_week, target_weekday, selected_periods, selected_buildings):
    if not selected_periods: return []
    busy_rooms = set()
    for item in timetable:
        if item["weekday"] == target_weekday and item["period"] in selected_periods:
            weeks_str = item["weeks"]
            is_busy = False
            for part in weeks_str.split(','):
                if '-' in part:
                    s, e = map(int, part.split('-'))
                    if s <= target_week <= e: is_busy = True
                else:
                    if part.isdigit() and int(part) == target_week: is_busy = True
            if is_busy: busy_rooms.add(item["classroom"])
                    
    filtered_empty = []
    for room in all_classrooms:
        _, b_name = get_classroom_location(room)
        if b_name in selected_buildings and room not in busy_rooms:
            filtered_empty.append(room)
    return filtered_empty

# ================= 5. 前端 GUI 渲染 =================
st.title("🏫 BUPT空教室查询系统")
now_time_display = get_bj_now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"🕒 北京时间：{now_time_display} | 推荐课表：第 {auto_week} 周 星期{['一','二','三','四','五','六','日'][auto_weekday-1]}")
st.markdown("---")

layout_left, layout_right = st.columns([1, 2])

with layout_left:
    st.subheader("⚙️ 基础筛选")
    selected_campuses = st.multiselect("📍 选择校区", options=list(CAMPUS_DATA.keys()), default=["西土城本部"])
    available_buildings = []
    for campus in selected_campuses:
        available_buildings.extend(list(CAMPUS_DATA[campus].keys()))
    selected_buildings = st.multiselect("🏢 选择教学楼", options=available_buildings, default=available_buildings[:2])
    
    with st.expander("📅 教学周/星期微调"):
        week = st.number_input("教学周次", min_value=1, max_value=25, value=auto_week)
        weekday = st.selectbox("星期几", options=[1,2,3,4,5,6,7], index=auto_weekday-1,
                               format_func=lambda x: f"星期{['一','二','三','四','五','六','日'][x-1]}")

# ================= ⏱️ 核心时间面板区域 =================
st.markdown("### ⏱️ 选择上课时间段")

# 1. 确定"当前节次及以后"的范围
# 注意：中午没有当前课节，此时current_live_period为None
#   - 如果当前在午休（12:15-13:00），应该从下午第6节开始选
#   - 否则从头开始选
now_str = get_bj_now().strftime("%H:%M")
if current_live_period is None:
    if "12:15" <= now_str < "13:00":
        start_from_period = 6
    else:
        start_from_period = 1
else:
    start_from_period = current_live_period
all_future_periods = list(range(start_from_period, 15))

# 2. 真正的"全选/取消全选"按钮交互（强行同步前端开关的 Value）
btn_label = "❌ 取消全选" if st.session_state.all_selected else "📅 全选当前及后续节次"
if st.button(btn_label):
    st.session_state.all_selected = not st.session_state.all_selected
    
    # 暴力同步：直接修改 Streamlit 内部管辖组件状态的 session_state
    for p in range(1, 15):
        if st.session_state.all_selected:
            # 如果是全选，只把"当前及以后"的开关置为 True，过去的置为 False
            st.session_state[f"period_{p}"] = (p in all_future_periods)
        else:
            # 如果是取消全选，恢复默认：只把当前这一节置为 True
            st.session_state[f"period_{p}"] = (p == current_live_period if current_live_period else p in [1, 2])
            
    st.rerun() # 强制页面重新渲染，让开关视觉状态立刻刷新

st.write("点击下方方块选择一节或多节课（支持跨节多选）。带有 🔥 标识的为**当前实时进行中**的节次：")

# 3. 渲染 14 个平铺开关（移动端列数动态调整，保证顺序正确）
selected_periods = []
user_agent = str(st.context.headers.get("User-Agent", ""))
is_mobile = "Mobi" in user_agent or "Android" in user_agent
cols_count = 2 if is_mobile else 5
grid_cols = st.columns(cols_count)

for p in range(1, 15):
    start_t, end_t = PERIOD_TIMING[p]
    is_current = (p == current_live_period)
    label_prefix = "🔥 " if is_current else ""
    button_text = f"{label_prefix}第 {p:02d} 节\n({start_t} ~ {end_t})"

    # 初始化兜底状态（仅在应用第一次打开、session_state 里还没这个开关时生效）
    if f"period_{p}" not in st.session_state:
        st.session_state[f"period_{p}"] = (p == current_live_period if current_live_period else p in [1, 2])

    with grid_cols[(p-1) % cols_count]:
        # 注意：这里去掉了 value= 属性，改用完全由 key 绑定的 session_state 接管
        if st.toggle(button_text, key=f"period_{p}"):
            selected_periods.append(p)

# ================= 6. 结果渲染展示 =================
st.markdown("---")
st.subheader("🟢 实时空闲教室面板")

if not selected_buildings:
    st.warning("⚠️ 请在左侧选择至少一栋教学楼！")
elif not selected_periods:
    st.info("💡 请至少点击上方激活一个时间节次方块！")
else:
    result_rooms = find_empty_rooms_multi_periods(week, weekday, selected_periods, selected_buildings)
    sorted_periods = sorted(selected_periods)
    st.markdown(f"📊 正在查询：**第 {week} 周** | **星期{['一','二','三','四','五','六','日'][weekday-1]}** | 选定节次: `第 {sorted_periods} 节`")
    
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
                for room in rooms: st.success(f"📍 {room}")
            else:
                st.caption("无空闲教室")