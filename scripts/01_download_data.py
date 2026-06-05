#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  步骤1: 采集 Kaggle RetailRocket 电商真实数据集
  选题一: 基于Spark的电商用户行为分析与推荐系统
  数据来源: Kaggle - RetailRocket E-commerce Dataset
  网址: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
  文件: events.csv (275 万条真实用户行为记录)

  字段说明:
    timestamp     - Unix 毫秒时间戳
    visitorid     - 访客ID (用户标识)
    event         - 行为类型: view / addtocart / transaction
    itemid        - 商品ID
    transactionid - 交易ID (仅 transaction 事件有值)
=============================================================================
"""

import os
import sys

print("=" * 70)
print("  步骤1: 采集 Kaggle RetailRocket 电商真实用户行为数据")
print("=" * 70)
print(f"  数据来源: Kaggle - RetailRocket E-commerce Dataset")
print(f"  网址: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset")

# ==================== 下载数据集 ====================
print("\n>>> 正在下载数据集 (约 28MB)...")

OUTPUT_DIR = "../data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    import kagglehub
    print("  使用 kagglehub 下载...")
    path = kagglehub.dataset_download("retailrocket/ecommerce-dataset")
    print(f"  下载路径: {path}")

    # 复制到项目 data 目录
    import shutil
    for f in os.listdir(path):
        src = os.path.join(path, f)
        dst = os.path.join(OUTPUT_DIR, f)
        shutil.copy2(src, dst)
        size_mb = os.path.getsize(dst) / (1024 * 1024)
        print(f"  已复制: {f} ({size_mb:.2f} MB)")

except ImportError:
    print("  kagglehub 未安装，尝试 pip 安装...")
    print("  请在终端执行: pip install kagglehub")
    print("  然后重新运行此脚本")
    sys.exit(1)
except Exception as e:
    print(f"  kagglehub 下载失败: {e}")
    print("")
    print("  备选方案 - 手动下载:")
    print("  1. 浏览器打开: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset")
    print("  2. 点击 Download 按钮下载 zip 文件")
    print("  3. 解压到 data/ 目录下")
    print("  4. 确保 data/events.csv 存在")
    sys.exit(1)

# ==================== 数据概览 ====================
print("\n" + "=" * 70)
print("  数据集概览")
print("=" * 70)

events_file = os.path.join(OUTPUT_DIR, "events.csv")

import csv
total_lines = 0
event_counts = {}
unique_visitors = set()
unique_items = set()

with open(events_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_lines += 1
        event = row.get('event', '')
        event_counts[event] = event_counts.get(event, 0) + 1
        unique_visitors.add(row.get('visitorid', ''))
        unique_items.add(row.get('itemid', ''))

print(f"  文件名: events.csv")
print(f"  总记录数: {total_lines:,} 条 (≥1万条 ✓)")
print(f"  独立访客: {len(unique_visitors):,} 人")
print(f"  独立商品: {len(unique_items):,} 件")
print(f"  文件大小: {os.path.getsize(events_file) / (1024*1024):.2f} MB")

print(f"\n  行为类型分布:")
for event, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
    pct = count / total_lines * 100
    print(f"    {event}: {count:,} ({pct:.1f}%)")

# 转化漏斗
view_users = set()
cart_users = set()
buy_users = set()
with open(events_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        vid = row.get('visitorid', '')
        event = row.get('event', '')
        if event == 'view':
            view_users.add(vid)
        elif event == 'addtocart':
            cart_users.add(vid)
        elif event == 'transaction':
            buy_users.add(vid)

print(f"\n  转化漏斗:")
print(f"    浏览(view):      {len(view_users):>10,} 人")
print(f"    加购(addtocart): {len(cart_users):>10,} 人 ({len(cart_users)/max(len(view_users),1)*100:.1f}%)")
print(f"    购买(transaction):{len(buy_users):>10,} 人 ({len(buy_users)/max(len(view_users),1)*100:.1f}%)")

# 数据样本
print(f"\n  数据样本 (前5条):")
print("  " + "-" * 80)
with open(events_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i <= 5:
            print(f"  {line.rstrip()}")
print("  " + "-" * 80)

print(f"\n  ✓ 数据采集完成! 真实电商数据，{total_lines:,} 条记录")
print(f"  来源: Kaggle RetailRocket 公开数据集")
print(f"  可进入步骤2: 数据预处理")
