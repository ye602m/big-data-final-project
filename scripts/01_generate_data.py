#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  步骤1: 电商用户行为数据采集
  选题一: 基于Spark的电商用户行为分析与推荐系统
  数据来源: 模拟电商平台用户行为数据 (≥10万条)
=============================================================================
"""

import csv
import random
import os
from datetime import datetime, timedelta

# ==================== 配置参数 ====================
OUTPUT_FILE = "../data/ecommerce_behavior.csv"
NUM_USERS = 5000        # 用户数
NUM_ITEMS = 2000        # 商品数
NUM_RECORDS = 100000    # 行为记录总数 (10万条，满足 ≥1万要求)
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 6, 30)

# 行为类型及权重 (浏览:加购:收藏:购买 = 60:20:10:10)
BEHAVIOR_TYPES = ['view', 'cart', 'fav', 'buy']
BEHAVIOR_WEIGHTS = [0.60, 0.20, 0.10, 0.10]

# 商品类别
CATEGORIES = [
    '电子产品', '服装鞋帽', '食品饮料', '家居用品', '图书音像',
    '美妆护肤', '母婴用品', '运动户外', '汽车用品', '医药健康'
]

# 商品价格区间 (按类别)
PRICE_RANGES = {
    '电子产品': (50, 5000),
    '服装鞋帽': (30, 800),
    '食品饮料': (5, 200),
    '家居用品': (20, 1500),
    '图书音像': (10, 150),
    '美妆护肤': (20, 600),
    '母婴用品': (30, 1200),
    '运动户外': (40, 2000),
    '汽车用品': (30, 3000),
    '医药健康': (10, 500),
}

print("=" * 70)
print("  步骤1: 电商用户行为数据采集")
print("=" * 70)
print(f"  生成用户数: {NUM_USERS}")
print(f"  生成商品数: {NUM_ITEMS}")
print(f"  行为记录数: {NUM_RECORDS}")
print(f"  时间范围: {START_DATE.date()} ~ {END_DATE.date()}")
print(f"  行为类型: {BEHAVIOR_TYPES}")
print(f"  商品类别: {len(CATEGORIES)} 类")
print("=" * 70)

# ==================== 生成商品表 ====================
print("\n>>> 正在生成商品信息表...")
items = []
for i in range(1, NUM_ITEMS + 1):
    cat = random.choice(CATEGORIES)
    min_price, max_price = PRICE_RANGES[cat]
    item = {
        'item_id': f'ITEM_{i:05d}',
        'category': cat,
        'price': round(random.uniform(min_price, max_price), 2),
        'title': f'商品_{cat}_{i}',
    }
    items.append(item)
print(f"  生成 {len(items)} 个商品")

# ==================== 生成用户表 ====================
print("\n>>> 正在生成用户信息表...")
users = []
for i in range(1, NUM_USERS + 1):
    user = {
        'user_id': f'USER_{i:05d}',
        'region': random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京']),
        'age_group': random.choice(['18-24', '25-34', '35-44', '45-54', '55+']),
    }
    users.append(user)
print(f"  生成 {len(users)} 个用户")

# ==================== 生成行为数据 ====================
print("\n>>> 正在生成用户行为数据...")
records = []
date_range = (END_DATE - START_DATE).days

for _ in range(NUM_RECORDS):
    user = random.choice(users)
    item = random.choice(items)
    behavior = random.choices(BEHAVIOR_TYPES, weights=BEHAVIOR_WEIGHTS)[0]
    rand_days = random.randint(0, date_range)
    rand_seconds = random.randint(0, 86399)
    timestamp = START_DATE + timedelta(days=rand_days, seconds=rand_seconds)

    record = {
        'user_id': user['user_id'],
        'item_id': item['item_id'],
        'behavior_type': behavior,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'category': item['category'],
        'price': item['price'],
        'user_region': user['region'],
        'user_age_group': user['age_group'],
    }
    records.append(record)

print(f"  生成 {len(records)} 条行为记录")

# ==================== 保存数据 ====================
print(f"\n>>> 正在保存数据到 {OUTPUT_FILE}...")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'user_id', 'item_id', 'behavior_type', 'timestamp',
        'category', 'price', 'user_region', 'user_age_group'
    ])
    writer.writeheader()
    writer.writerows(records)

file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
print(f"  数据已保存: {OUTPUT_FILE}")
print(f"  文件大小: {file_size:.2f} MB")

# ==================== 数据概览 ====================
print("\n" + "=" * 70)
print("  数据采集完成! 数据概览:")
print("=" * 70)
print(f"  总记录数: {len(records):,} 条")
print(f"  用户数: {len(users):,} 人")
print(f"  商品数: {len(items):,} 个")
print(f"  商品类别: {len(CATEGORIES)} 类")
print(f"  时间跨度: {START_DATE.date()} ~ {END_DATE.date()}")

# 各类行为统计
print("\n  行为类型分布:")
for bt in BEHAVIOR_TYPES:
    count = sum(1 for r in records if r['behavior_type'] == bt)
    pct = count / len(records) * 100
    print(f"    {bt}: {count:,} 条 ({pct:.1f}%)")

# 展示前5条数据
print("\n  数据样本 (前5条):")
print("  " + "-" * 65)
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i <= 5:
            print(f"  {line.rstrip()}")
        else:
            break
print("  " + "-" * 65)
print("\n  数据集已就绪，可进入步骤2: 数据预处理")
