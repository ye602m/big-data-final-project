#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  步骤3: Spark SQL 数据分析
  选题一: 基于Spark的电商用户行为分析与推荐系统
  分析内容: PV/UV统计、商品热度、转化漏斗、用户行为模式、RFM分析
=============================================================================
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, sum as spark_sum, avg, desc,
    when, hour, dayofweek, month, datediff, lit, to_date,
    row_number, rank, dense_rank, max as spark_max, round as spark_round
)
from pyspark.sql.window import Window

# ==================== 初始化Spark ====================
print("=" * 70)
print("  步骤3: Spark SQL 数据分析")
print("=" * 70)

spark = SparkSession.builder \
    .appName("E-commerce Spark SQL Analysis") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# ==================== 加载清洗后数据 ====================
CLEANED_FILE = "../data/ecommerce_cleaned.parquet"
df = spark.read.parquet(f"file://{os.path.abspath(CLEANED_FILE)}")
df.createOrReplaceTempView("behavior")

print(f"\n  数据加载完成: {df.count():,} 条记录")
print(f"  时间范围: 见下方分析")

# ==================== 分析1: 核心指标 ====================
print("\n" + "=" * 70)
print("  分析3.1: 平台核心指标概览")
print("=" * 70)

result1 = spark.sql("""
    SELECT
        COUNT(*) AS total_records,
        COUNT(DISTINCT user_id) AS total_users,
        COUNT(DISTINCT item_id) AS total_items,
        COUNT(DISTINCT category) AS total_categories,
        COUNT(DISTINCT date) AS total_days,
        ROUND(COUNT(*) / COUNT(DISTINCT date), 0) AS avg_daily_pv,
        ROUND(COUNT(*) / COUNT(DISTINCT user_id), 1) AS avg_actions_per_user
    FROM behavior
""")
result1.show(truncate=False)

# ==================== 分析2: PV/UV 趋势 ====================
print("=" * 70)
print("  分析3.2: 日均 PV/UV 趋势 (按月统计)")
print("=" * 70)

result2 = spark.sql("""
    SELECT
        month,
        COUNT(*) AS PV,
        COUNT(DISTINCT user_id) AS UV,
        ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 2) AS PV_UV_Ratio,
        COUNT(DISTINCT date) AS active_days
    FROM behavior
    GROUP BY month
    ORDER BY month
""")
result2.show(10)

# ==================== 分析3: 用户行为类型分布 ====================
print("=" * 70)
print("  分析3.3: 用户行为类型分布")
print("=" * 70)

result3 = spark.sql("""
    SELECT
        behavior_type,
        COUNT(*) AS count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM behavior), 2) AS percentage
    FROM behavior
    GROUP BY behavior_type
    ORDER BY count DESC
""")
result3.show()

# ==================== 分析4: 转化漏斗 ====================
print("=" * 70)
print("  分析3.4: 用户行为转化漏斗分析")
print("=" * 70)

funnel = spark.sql("""
    SELECT
        COUNT(DISTINCT CASE WHEN behavior_type = 'view' THEN user_id END) AS view_users,
        COUNT(DISTINCT CASE WHEN behavior_type = 'cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN behavior_type = 'fav' THEN user_id END) AS fav_users,
        COUNT(DISTINCT CASE WHEN behavior_type = 'buy' THEN user_id END) AS buy_users
    FROM behavior
""")
funnel_data = funnel.collect()[0]
view_u = funnel_data['view_users']
cart_u = funnel_data['cart_users']
fav_u = funnel_data['fav_users']
buy_u = funnel_data['buy_users']

print(f"""
  ┌──────────────┐
  │  浏览 (View)  │  {view_u:,} 人  (100.0%)
  └──────┬───────┘
         │  {cart_u/view_u*100:.1f}%
         ▼
  ┌──────────────┐
  │  加购 (Cart)  │  {cart_u:,} 人  ({cart_u/view_u*100:.1f}%)
  └──────┬───────┘
         │  {fav_u/cart_u*100:.1f}%
         ▼
  ┌──────────────┐
  │  收藏 (Fav)   │  {fav_u:,} 人  ({fav_u/view_u*100:.1f}%)
  └──────┬───────┘
         │  {buy_u/fav_u*100:.1f}%
         ▼
  ┌──────────────┐
  │  购买 (Buy)   │  {buy_u:,} 人  ({buy_u/view_u*100:.1f}%)
  └──────────────┘

  整体转化率: 浏览→购买 = {buy_u/view_u*100:.2f}%
""")

# ==================== 分析5: 商品热度排名 ====================
print("=" * 70)
print("  分析3.5: 商品热度排名 (Top 10)")
print("=" * 70)

result5 = spark.sql("""
    SELECT
        item_id,
        category,
        COUNT(*) AS total_views,
        SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_count,
        SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_count,
        ROUND(SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS conversion_rate
    FROM behavior
    GROUP BY item_id, category
    ORDER BY total_views DESC
    LIMIT 10
""")
result5.show(10, truncate=False)

# ==================== 分析6: 类目分析 ====================
print("=" * 70)
print("  分析3.6: 商品类别销售分析")
print("=" * 70)

result6 = spark.sql("""
    SELECT
        category,
        COUNT(*) AS total_actions,
        SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS total_sales,
        ROUND(AVG(CASE WHEN behavior_type = 'buy' THEN price END), 2) AS avg_order_value,
        ROUND(SUM(CASE WHEN behavior_type = 'buy' THEN price END), 2) AS total_revenue
    FROM behavior
    GROUP BY category
    ORDER BY total_sales DESC
""")
result6.show(10, truncate=False)

# ==================== 分析7: 用户活跃时段分析 ====================
print("=" * 70)
print("  分析3.7: 用户活跃时段分析")
print("=" * 70)

result7 = spark.sql("""
    SELECT
        hour,
        COUNT(*) AS actions,
        COUNT(DISTINCT user_id) AS active_users,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM behavior), 2) AS percentage
    FROM behavior
    GROUP BY hour
    ORDER BY hour
""")
result7.show(24)

print("\n  ★ 高峰时段提示:")
peak = result7.orderBy(desc('actions')).first()
print(f"    最高峰出现在 {peak['hour']}:00, 共 {peak['actions']:,} 条行为")

# ==================== 分析8: 地域分析 ====================
print("=" * 70)
print("  分析3.8: 用户地域分布分析")
print("=" * 70)

result8 = spark.sql("""
    SELECT
        user_region,
        COUNT(DISTINCT user_id) AS user_count,
        COUNT(*) AS total_actions,
        SUM(CASE WHEN behavior_type = 'buy' THEN price ELSE 0 END) AS total_gmv,
        ROUND(SUM(CASE WHEN behavior_type = 'buy' THEN price ELSE 0 END) /
              NULLIF(COUNT(DISTINCT CASE WHEN behavior_type = 'buy' THEN user_id END), 0), 2) AS arpu
    FROM behavior
    GROUP BY user_region
    ORDER BY total_gmv DESC
""")
result8.show(10, truncate=False)

# ==================== 分析9: 用户价值分层 ====================
print("=" * 70)
print("  分析3.9: 用户价值分层 (基于购买次数)")
print("=" * 70)

result9 = spark.sql("""
    SELECT
        CASE
            WHEN buy_count >= 10 THEN '高价值用户'
            WHEN buy_count >= 5 THEN '中等价值用户'
            WHEN buy_count >= 2 THEN '普通用户'
            WHEN buy_count = 1 THEN '单次购买用户'
            ELSE '未购买用户'
        END AS user_level,
        COUNT(*) AS user_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT user_id) FROM behavior), 2) AS percentage
    FROM (
        SELECT
            user_id,
            SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS buy_count
        FROM behavior
        GROUP BY user_id
    )
    GROUP BY
        CASE
            WHEN buy_count >= 10 THEN '高价值用户'
            WHEN buy_count >= 5 THEN '中等价值用户'
            WHEN buy_count >= 2 THEN '普通用户'
            WHEN buy_count = 1 THEN '单次购买用户'
            ELSE '未购买用户'
        END
    ORDER BY user_count DESC
""")
result9.show()

# ==================== 分析10: 商品关联分析 ====================
print("=" * 70)
print("  分析3.10: 商品类别关联分析 (同用户购买的不同类别)")
print("=" * 70)

result10 = spark.sql("""
    SELECT
        a.category AS category_a,
        b.category AS category_b,
        COUNT(DISTINCT a.user_id) AS co_users
    FROM
        (SELECT DISTINCT user_id, category FROM behavior WHERE behavior_type = 'buy') a
    JOIN
        (SELECT DISTINCT user_id, category FROM behavior WHERE behavior_type = 'buy') b
    ON a.user_id = b.user_id AND a.category < b.category
    GROUP BY a.category, b.category
    ORDER BY co_users DESC
    LIMIT 10
""")
result10.show(10, truncate=False)

# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  步骤3 完成! 数据分析总结:")
print("=" * 70)
print(f"""
  ① 平台核心指标: PV/UV/商品数 均已统计
  ② 转化漏斗: 浏览→加购→收藏→购买, 转化率已计算
  ③ 商品热度: Top商品及转化率已输出
  ④ 类别分析: 各类目销售额、客单价已统计
  ⑤ 时段分析: 用户活跃高峰时段已识别
  ⑥ 地域分析: 各地区用户数、GMV、ARPU值已计算
  ⑦ 用户分层: 高/中/普通/单次/未购买 用户分布已统计
  ⑧ 关联分析: 商品类别共现关系已挖掘
""")

spark.stop()
print("  步骤3完成! 可进入步骤4: ALS协同过滤推荐算法")
