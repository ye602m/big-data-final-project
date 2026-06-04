#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  Flask Web 可视化系统
  选题一: 基于Spark的电商用户行为分析与推荐系统
  功能: 展示推荐结果、数据分析图表、实时仪表盘
  端口: 5000
=============================================================================
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import random

app = Flask(__name__)

# 加载数据
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
with open(os.path.join(DATA_DIR, 'echarts_data.json'), 'r', encoding='utf-8') as f:
    echarts_data = json.load(f)

@app.route('/')
def index():
    """主页面 - 仪表盘"""
    return render_template('index.html')

@app.route('/api/dashboard')
def api_dashboard():
    """仪表盘数据API"""
    return jsonify({
        'status': 'ok',
        'data': echarts_data
    })

@app.route('/api/recommendations')
def api_recommendations():
    """推荐结果API"""
    user_id = request.args.get('user_id', 'USER_00001')
    # 模拟推荐结果 (实际生产环境从 Parquet 读取)
    recs = generate_mock_recommendations(user_id)
    return jsonify({
        'status': 'ok',
        'user_id': user_id,
        'recommendations': recs
    })

@app.route('/recommend')
def recommend_page():
    """推荐页面"""
    return render_template('recommend.html')

def generate_mock_recommendations(user_id):
    """生成模拟推荐结果"""
    items = []
    for i in range(5):
        items.append({
            'item_id': f'ITEM_{random.randint(1, 2000):05d}',
            'category': random.choice(['电子产品', '服装鞋帽', '食品饮料', '家居用品']),
            'predicted_rating': round(random.uniform(3.5, 5.0), 2),
            'reason': random.choice(['与你购买过的商品相似', '浏览过同类商品的用户也喜欢',
                                      '热门推荐', '基于你的收藏记录', '与你兴趣相似的用户的购买'])
        })
    return items

if __name__ == '__main__':
    print("=" * 50)
    print("  Flask Web 可视化系统启动中...")
    print("  访问地址: http://127.0.0.1:5000")
    print("  API接口: /api/dashboard")
    print("  推荐查询: /recommend?user_id=USER_00001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
