import streamlit as st
import pandas as pd
import requests
import altair as alt

# ===================== 这里是后端给你的 Apifox Mock 地址，后面填在这里 =====================
API_URL = ""   # 例如 "https://xxx.apifox.cn/api/recognize_bill"
# =======================================================================================

# ---------------------- 页面基础设置 ----------------------
st.set_page_config(
    page_title="AI记账助手",
    page_icon="📒",
    layout="wide"
)

# 侧边栏菜单
menu = st.sidebar.selectbox(
    "功能菜单",
    ["一句话记账", "自然语言查账", "账单与统计"]
)

# 侧边栏项目说明
st.sidebar.divider()
st.sidebar.subheader("📖 项目说明")
st.sidebar.markdown("""
智能记账AI系统
- ✍️ 文字记账：输入消费描述自动识别
- 📷 小票识别：上传截图AI提取账单
- 📊 自动统计：柱状图+饼图分析消费
""")
st.sidebar.markdown("版本：前端演示版（对接Apifox）")

# 初始化账单数据
if "bill_data" not in st.session_state:
    st.session_state.bill_data = pd.DataFrame([
        {"日期": "2026-11-10", "类别": "餐饮", "金额": 24, "备注": "午饭"},
        {"日期": "2026-11-11", "类别": "交通", "金额": 12, "备注": "打车"},
        {"日期": "2026-11-12", "类别": "购物", "金额": 89, "备注": "文具"}
    ])

# ====================== 页面1：AI智能识别记账（合并文字+图片） ======================
if menu == "一句话记账":
    st.header("📒 AI智能识别记账")
    st.info("提示：文字描述 / 上传小票截图，AI自动识别账单")
    st.divider()

    # 初始化表单缓存
    if "text_input_cache" not in st.session_state:
        st.session_state.text_input_cache = ""
    if "money_cache" not in st.session_state:
        st.session_state.money_cache = 0.0
    if "category_cache" not in st.session_state:
        st.session_state.category_cache = "其他"
    if "remark_cache" not in st.session_state:
        st.session_state.remark_cache = ""

    # 卡片容器
    st.markdown("""
    <div style="background-color:#262730; padding:20px; border-radius:12px">
    """, unsafe_allow_html=True)
    st.subheader("🧾 输入文字或者上传小票")
    text_input = st.text_input("文字记账，例子：晚饭30、打车15、奶茶18", value=st.session_state.text_input_cache)
    upload_img = st.file_uploader("上传小票、微信/支付宝截图", type=["png", "jpg", "jpeg"])
    st.markdown("</div>", unsafe_allow_html=True)

    mock_money = st.session_state.money_cache
    mock_category = st.session_state.category_cache
    remark = st.session_state.remark_cache

    # ---------------- 调用Apifox接口函数 ----------------
    def call_recognize_api(text=None, img_file=None):
        if not API_URL:
            return None
        try:
            if img_file is not None:
                res = requests.post(API_URL, files={"image": img_file})
            else:
                res = requests.post(API_URL, data={"text": text})
            if res.status_code == 200:
                return res.json()
            else:
                return None
        except Exception as e:
            st.warning(f"接口调用失败，使用本地模拟识别。错误：{e}")
            return None

    # 文字识别
    if text_input and text_input != st.session_state.text_input_cache:
        st.session_state.text_input_cache = text_input
        api_result = call_recognize_api(text=text_input)
        if api_result:
            mock_money = api_result.get("money", 0)
            mock_category = api_result.get("category", "其他")
            remark = api_result.get("remark", "")
            st.success(f"✅【AI接口识别成功】识别为：{mock_category}，{mock_money}元")
        else:
            if "午饭" in text_input or "晚饭" in text_input or "奶茶" in text_input or "吃饭" in text_input:
                mock_money = 25
                mock_category = "餐饮"
                st.success("✅【本地模拟识别成功】识别为：餐饮，25元")
            elif "打车" in text_input or "地铁" in text_input or "公交" in text_input:
                mock_money = 12
                mock_category = "交通"
                st.success("✅【本地模拟识别成功】识别为：交通，12元")
            elif "文具" in text_input or "买" in text_input:
                mock_money = 60
                mock_category = "购物"
                st.success("✅【本地模拟识别成功】识别为：购物，60元")
            else:
                mock_money = 0
                mock_category = "其他"
                st.info("ℹ️ 暂时无法识别，请手动填写下面信息")
        # 更新缓存
        st.session_state.money_cache = mock_money
        st.session_state.category_cache = mock_category
        st.session_state.remark_cache = remark

    # 图片识别
    if upload_img is not None:
        st.image(upload_img, width=400)
        if st.button("开始识别小票"):
            api_result = call_recognize_api(img_file=upload_img)
            if api_result:
                mock_money = api_result.get("money", 0)
                mock_category = api_result.get("category", "其他")
                remark = api_result.get("remark", "")
                st.success(f"✅【AI接口识别成功】识别为：{mock_category}，{mock_money}元")
            else:
                mock_money = 30
                mock_category = "餐饮"
                remark = "小票识别模拟"
                st.warning("⚠️ 接口未就绪，本地模拟识别：餐饮 30元")
            st.session_state.money_cache = mock_money
            st.session_state.category_cache = mock_category
            st.session_state.remark_cache = remark

    st.divider()
    st.subheader("📝 解析预览（可修改）")
    money = st.number_input("金额（元）", value=mock_money, min_value=0.0, step=0.1)
    category = st.text_input("消费类别", value=mock_category)
    date = st.date_input("消费日期")
    remark = st.text_input("备注", value=remark)

    # 保存 和 清空按钮并排
    col_save, col_clear = st.columns([1,1])
    with col_save:
        save_btn = st.button("💾 保存账单", use_container_width=True)
    with col_clear:
        clear_btn = st.button("🗑️ 清空表单", use_container_width=True)

    if save_btn:
        if money > 0:
            new_row = pd.DataFrame([{
                "日期": str(date),
                "类别": category,
                "金额": money,
                "备注": remark
            }])
            st.session_state.bill_data = pd.concat([st.session_state.bill_data, new_row], ignore_index=True)
            st.success("✅ 账单保存成功！")
        else:
            st.error("❌ 金额必须大于0")

    # 清空逻辑：重置所有缓存，刷新页面
    if clear_btn:
        st.session_state.text_input_cache = ""
        st.session_state.money_cache = 0.0
        st.session_state.category_cache = "其他"
        st.session_state.remark_cache = ""
        st.rerun()

# ====================== 页面2：自然语言查账 ======================
elif menu == "自然语言查账":
    st.header("🔍 自然语言查账")
    st.info("用口语提问，查询账单")
    st.divider()

    question = st.text_input("输入你的问题，示例：这个月吃饭花了多少钱")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("这个月餐饮一共花多少")
    with col2:
        st.button("哪一类消费最多")
    with col3:
        st.button("查看最近3条账单")

    st.divider()
    st.subheader("📌 查询结果")
    if question:
        st.info("⚠️ 查询接口等待后端开发，目前仅占位演示")
    else:
        st.info("请输入问题，点击查询")

# ====================== 页面3：账单与统计（新增删除功能） ======================
elif menu == "账单与统计":
    st.header("📊 账单列表 & 消费统计")
    st.divider()
    st.subheader("📋 全部账单")

    # 展示账单+选择删除行
    if not st.session_state.bill_data.empty:
        # 增加序号列，方便选择
        df_show = st.session_state.bill_data.copy()
        df_show.insert(0, "序号", list(range(len(df_show))))
        st.dataframe(df_show, use_container_width=True)

        # 删除区域
        st.divider()
        st.subheader("🗑️ 删除账单")
        del_index = st.number_input("输入要删除账单的序号", min_value=0, max_value=len(st.session_state.bill_data)-1, step=1)
        delete_btn = st.button("确认删除这条账单")
        if delete_btn:
            st.session_state.bill_data = st.session_state.bill_data.drop(del_index).reset_index(drop=True)
            st.success(f"✅ 序号{del_index}账单已删除！")
            st.rerun()
    else:
        st.info("暂无账单数据")

    st.divider()
    st.subheader("📈 消费分类统计")
    group_data = st.session_state.bill_data.groupby("类别")["金额"].sum().reset_index()
    if not group_data.empty:
        col_left, col_right = st.columns(2)
        with col_left:
            st.bar_chart(group_data, x="类别", y="金额")
        with col_right:
            pie = alt.Chart(group_data).mark_arc().encode(
                theta="金额",
                color="类别"
            )
            st.altair_chart(pie, use_container_width=True)
    else:
        st.info("暂无账单数据")
