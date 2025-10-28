import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="退货运营可视化面板", layout="wide")

# === 读取并清理数据 ===
with open("data.csv", "r", encoding="utf-8", errors="ignore") as f:
    df = (
        pd.read_csv(f)      # 此时不再传入 encoding
          .dropna(how="all")
    )

# 去掉列名空格
df.columns = df.columns.str.strip()

# 仅保留 Date 不为空的行
df = df[df["Date"].notna()]

# === 转换日期 ===
year = datetime.now().year  # 或固定写 2024
# 仅对非空值拼接年份并解析
df["Date"] = pd.to_datetime(
    df["Date"].apply(lambda x: f"{year}{x.strip()}"),
    format="%Y%m月%d日"
)

# 按日期排序
df = df.sort_values("Date").reset_index(drop=True)

# === 侧边栏日期范围选择 ===
min_dt, max_dt = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input(
    "选择可视化时间范围",
    value=(min_dt.date(), max_dt.date()),
    min_value=min_dt.date(),
    max_value=max_dt.date()
)

# 解析选择结果
if isinstance(date_range, (list, tuple)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_dt.date(), max_dt.date()
else:
    start_date = end_date = date_range

mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
df_view = df.loc[mask].copy()

if df_view.empty:
    st.title("📊 退货运营可视化面板")
    st.warning("所选日期范围内无数据，请调整筛选条件。")
    with st.expander("查看原始数据"):
        st.dataframe(df)
    st.stop()

# === 计算 Total 并转成长格式 ===
value_cols = [c for c in df_view.columns if c not in ["Date", "Total"]]
df_view["Total"] = df_view[value_cols].sum(axis=1)

df_long = df_view.melt(
    id_vars="Date",
    value_vars=value_cols,
    var_name="Operation Type",
    value_name="Count"
)

# === 绘图 ===
title_range = f"{start_date} — {end_date}"
fig = px.bar(
    df_long,
    x="Date",
    y="Count",
    color="Operation Type",
    title=f"Stacked Daily Operations（{title_range}）",
    text="Count"
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Count",
    legend_title="Operation Type",
    legend=dict(x=1.02, y=1, bgcolor="rgba(0,0,0,0)"),
    barmode="stack",
    height=600
)
fig.update_traces(texttemplate="%{text}", textposition="inside", textfont=dict(size=10))

# 顶部显示每日总数
fig.add_trace(
    go.Scatter(
        x=df_view["Date"],
        y=df_view["Total"],
        mode="text",
        text=df_view["Total"],
        textposition="top center",
        textfont=dict(size=12, color="black"),
        showlegend=False
    )
)

# === 展示 ===
st.title("📊 退货运营可视化面板")
st.plotly_chart(fig, use_container_width=True)

with st.expander("查看原始数据"):
    st.dataframe(df)
