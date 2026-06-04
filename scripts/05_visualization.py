#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  步骤5: 数据可视化 (Matplotlib + ECharts)
  选题一: 基于Spark的电商用户行为分析与推荐系统
  输出: 8张可视化图表 (PNG格式, 300DPI)
=============================================================================
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, desc, hour, month
import json

# ==================== 中文字体设置 ====================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['savefig.bbox'] = 'tight'

OUTPUT_DIR = "../output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("  步骤5: 数据可视化")
print("=" * 70)

# ==================== 加载数据 ====================
spark = SparkSession.builder \
    .appName("E-commerce Visualization") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

CLEANED_FILE = "../data/ecommerce_cleaned.parquet"
df = spark.read.parquet(f"file://{os.path.abspath(CLEANED_FILE)}")

# ==================== 图1: 全局趋势 - 日均PV/UV ====================
print("\n>>> [1/8] 日均PV/UV趋势图")
daily = df.groupBy('date').agg(
    count('*').alias('PV'),
    countDistinct('user_id').alias('UV')
).orderBy('date').toPandas()

fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.plot(daily['date'], daily['PV'], 'b-', alpha=0.7, linewidth=0.8, label='PV (浏览量)')
ax1.set_xlabel('日期')
ax1.set_ylabel('PV (浏览量)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.plot(daily['date'], daily['UV'], 'r-', alpha=0.7, linewidth=0.8, label='UV (访客数)')
ax2.set_ylabel('UV (访客数)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('图1: 日均 PV/UV 趋势', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig1_pv_uv_trend.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig1_pv_uv_trend.png")

# ==================== 图2: Top 15 商品热度 ====================
print("\n>>> [2/8] 商品热度排名图")
top_items = df.groupBy('item_id').agg(
    count('*').alias('views'),
    countDistinct('user_id').alias('unique_users')
).orderBy(desc('views')).limit(15).toPandas()

fig, ax = plt.subplots(figsize=(12, 7))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, 15))
bars = ax.barh(range(15), top_items['views'].values, color=colors[::-1])
ax.set_yticks(range(15))
ax.set_yticklabels([f"#{i}" for i in top_items['item_id'].values[:15]], fontsize=8)
ax.set_xlabel('浏览量')
ax.set_title('图2: 热门商品 Top 15', fontsize=14, fontweight='bold')
ax.invert_yaxis()
for i, (v, u) in enumerate(zip(top_items['views'].values, top_items['unique_users'].values)):
    ax.text(v + 10, i, f'{v:,}次 / {u}人', va='center', fontsize=7)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig2_top15_items.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig2_top15_items.png")

# ==================== 图3: 行为类型分布饼图 ====================
print("\n>>> [3/8] 用户行为类型分布饼图")
behavior_stats = df.groupBy('behavior_type').count().toPandas()
labels = behavior_stats['behavior_type'].values
sizes = behavior_stats['count'].values
colors_bt = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
explode = (0, 0, 0, 0.05)

fig, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))
ax3a.pie(sizes, explode=explode, labels=labels, colors=colors_bt,
         autopct='%1.1f%%', shadow=True, startangle=90)
ax3a.set_title('图3: 用户行为类型分布', fontsize=14, fontweight='bold')

ax3b.bar(labels, sizes, color=colors_bt, edgecolor='white', linewidth=1.5)
ax3b.set_ylabel('行为次数')
ax3b.set_title('行为类型柱状图')
for i, v in enumerate(sizes):
    ax3b.text(i, v + max(sizes)*0.01, f'{v:,}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig3_behavior_distribution.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig3_behavior_distribution.png")

# ==================== 图4: 类别销售额 ====================
print("\n>>> [4/8] 商品类别销售分析图")
cat_sales = df.filter(col('behavior_type') == 'buy') \
    .groupBy('category').agg(
        spark_sum('price').alias('total_sales')
    ).orderBy(desc('total_sales')).toPandas()

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(cat_sales['category'], cat_sales['total_sales'],
              color=plt.cm.Set2(np.linspace(0, 1, len(cat_sales))),
              edgecolor='white', linewidth=1.5)
ax.set_xlabel('商品类别')
ax.set_ylabel('销售额')
ax.set_title('图4: 各类别销售总额', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
for bar, val in zip(bars, cat_sales['total_sales']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cat_sales['total_sales'])*0.01,
            f'{val:,.0f}', ha='center', fontsize=8, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig4_category_sales.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig4_category_sales.png")

# ==================== 图5: 用户活跃时段热力 ====================
print("\n>>> [5/8] 用户活跃时段分析图")
hourly = df.groupBy('hour').agg(count('*').alias('actions')).orderBy('hour').toPandas()

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(hourly['hour'], hourly['actions'], alpha=0.3, color='steelblue')
ax.plot(hourly['hour'], hourly['actions'], 'b-', linewidth=2, marker='o', markersize=5)
ax.set_xlabel('小时 (24小时制)')
ax.set_ylabel('行为次数')
ax.set_title('图5: 用户活跃时段分布 (24小时)', fontsize=14, fontweight='bold')
ax.set_xticks(range(0, 24))
ax.grid(axis='y', alpha=0.3)
# 标注峰值
peak_idx = hourly['actions'].idxmax()
ax.annotate(f"峰值 {hourly['actions'][peak_idx]:,}次\n{hourly['hour'][peak_idx]}:00",
            xy=(hourly['hour'][peak_idx], hourly['actions'][peak_idx]),
            xytext=(hourly['hour'][peak_idx] + 3, hourly['actions'][peak_idx] * 1.1),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10, fontweight='bold', color='red')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig5_hourly_activity.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig5_hourly_activity.png")

# ==================== 图6: 转化漏斗 ====================
print("\n>>> [6/8] 转化漏斗图")
funnel_data = df.groupBy('behavior_type').agg(
    countDistinct('user_id').alias('users')
).toPandas()

behavior_order = {'view': 0, 'cart': 1, 'fav': 2, 'buy': 3}
funnel_data['order'] = funnel_data['behavior_type'].map(behavior_order)
funnel_data = funnel_data.sort_values('order')

fig, ax = plt.subplots(figsize=(10, 8))
max_users = funnel_data['users'].max()
colors_funnel = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
for i, (_, row) in enumerate(funnel_data.iterrows()):
    width = row['users'] / max_users
    left = (1 - width) / 2
    ax.barh(i, width, left=left, height=0.6,
            color=colors_funnel[i], edgecolor='white', linewidth=2)
    ax.text(0.5, i, f"{row['behavior_type']}\n{row['users']:,} 人\n{row['users']/max_users*100:.1f}%",
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

ax.set_yticks(range(4))
ax.set_yticklabels([])
ax.set_xlim(0, 1)
ax.set_title('图6: 用户行为转化漏斗', fontsize=14, fontweight='bold')
ax.set_xlabel('用户占比')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig6_conversion_funnel.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig6_conversion_funnel.png")

# ==================== 图7: 地域GMV ====================
print("\n>>> [7/8] 地域GMV贡献图")
region_data = df.filter(col('behavior_type') == 'buy') \
    .groupBy('user_region').agg(
        spark_sum('price').alias('GMV'),
        countDistinct('user_id').alias('buyers')
    ).orderBy(desc('GMV')).toPandas()

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(region_data['user_region'], region_data['GMV'],
              color=plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(region_data))),
              edgecolor='white', linewidth=1.5)
ax.set_xlabel('地区')
ax.set_ylabel('GMV (销售额)')
ax.set_title('图7: 各地区 GMV 贡献', fontsize=14, fontweight='bold')
plt.xticks(rotation=30)
for bar, gmv in zip(bars, region_data['GMV']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(region_data['GMV'])*0.01,
            f'{gmv:,.0f}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig7_region_gmv.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig7_region_gmv.png")

# ==================== 图8: 用户价值分层 ====================
print("\n>>> [8/8] 用户价值分层图")
user_buys = df.filter(col('behavior_type') == 'buy') \
    .groupBy('user_id').agg(count('*').alias('buy_count')).toPandas()

bins = [0, 1, 2, 5, 10, float('inf')]
labels = ['未购买(0)', '单次购买(1)', '普通(2-4)', '中等(5-9)', '高价值(10+)']
user_buys['level'] = pd.cut(user_buys['buy_count'], bins=bins, labels=labels, right=True)
level_counts = user_buys['level'].value_counts().reindex(labels).fillna(0)

# 添加未购买用户
total_users = df.select('user_id').distinct().count()
buy_users = df.filter(col('behavior_type') == 'buy').select('user_id').distinct().count()
not_buy = total_users - buy_users
level_counts['未购买(0)'] = not_buy

fig, ax = plt.subplots(figsize=(10, 8))
colors_level = ['#ecf0f1', '#3498db', '#2ecc71', '#f39c12', '#e74c3c']
wedges, texts, autotexts = ax.pie(
    level_counts.values, labels=level_counts.index,
    autopct='%1.1f%%', colors=colors_level,
    explode=(0, 0, 0, 0.05, 0.1),
    startangle=90, shadow=True
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_fontweight('bold')
ax.set_title('图8: 用户价值分层', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fig8_user_value_levels.png")
plt.close()
print(f"  ✓ 已保存: {OUTPUT_DIR}/fig8_user_value_levels.png")

# ==================== 生成ECharts JSON数据 ====================
print("\n>>> 生成 ECharts 前端数据...")
echarts_data = {
    'daily_pv_uv': daily.to_dict('records'),
    'top_items': top_items.to_dict('records'),
    'category_sales': cat_sales.to_dict('records'),
    'hourly_activity': hourly.to_dict('records'),
}

with open(f"{OUTPUT_DIR}/echarts_data.json", 'w', encoding='utf-8') as f:
    json.dump(echarts_data, f, ensure_ascii=False, default=str)
print(f"  ✓ ECharts数据已保存: {OUTPUT_DIR}/echarts_data.json")

# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  步骤5 完成! 可视化总结:")
print("=" * 70)
print(f"""
  已生成 8 张可视化图表:
    ① fig1_pv_uv_trend.png       - 日均PV/UV趋势
    ② fig2_top15_items.png        - 热门商品Top15
    ③ fig3_behavior_distribution.png - 用户行为类型分布
    ④ fig4_category_sales.png     - 各类别销售额
    ⑤ fig5_hourly_activity.png    - 用户活跃时段
    ⑥ fig6_conversion_funnel.png  - 转化漏斗
    ⑦ fig7_region_gmv.png         - 地域GMV
    ⑧ fig8_user_value_levels.png  - 用户价值分层

  图表保存在: {os.path.abspath(OUTPUT_DIR)}/

  另有 ECharts JSON数据 供 Web 前端使用
""")

spark.stop()
print("  步骤5完成! 可进入步骤6: Flask Web 可视化系统")
