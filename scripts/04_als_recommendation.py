#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  步骤4: ALS 协同过滤推荐算法 (Spark MLlib)
  选题一: 基于Spark的电商用户行为分析与推荐系统
  算法: ALS (Alternating Least Squares) 矩阵分解
  评价指标: RMSE (均方根误差)
  输出: Top-N 推荐结果
=============================================================================
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, desc, expr, explode, collect_list, row_number
)
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
from pyspark.sql.window import Window
from pyspark.sql.types import FloatType

# ==================== 初始化Spark ====================
print("=" * 70)
print("  步骤4: ALS 协同过滤推荐算法")
print("=" * 70)

spark = SparkSession.builder \
    .appName("ALS Recommendation System") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# ==================== 加载数据并构建评分矩阵 ====================
CLEANED_FILE = "../data/ecommerce_cleaned.parquet"
df = spark.read.parquet(f"file://{os.path.abspath(CLEANED_FILE)}")

print("\n>>> 构建用户-商品评分矩阵")
print("  评分规则: view=1, cart=2, fav/collect=3, buy=5")

# 构建评分数据: 将行为转换为评分
ratings_df = df.select('user_id', 'item_id', 'behavior_type') \
    .withColumn('rating',
        expr("""
            CASE behavior_type
                WHEN 'view' THEN 1.0
                WHEN 'cart' THEN 2.0
                WHEN 'fav' THEN 3.0
                WHEN 'buy' THEN 5.0
                ELSE 1.0
            END
        """)
    )

# 同一用户对同一商品可能有多次行为, 取最高评分
ratings_df = ratings_df.groupBy('user_id', 'item_id') \
    .agg({'rating': 'max'}) \
    .withColumnRenamed('max(rating)', 'rating')

print(f"  评分矩阵: {ratings_df.count():,} 条 (user_id × item_id × rating)")

# 评分分布
print("\n  评分分布:")
ratings_df.groupBy('rating').count().orderBy('rating').show()

# ==================== 编码用户和商品ID为整数 ====================
print("\n>>> 编码用户和商品ID为整数索引")

user_indexer = StringIndexer(inputCol='user_id', outputCol='user_idx')
item_indexer = StringIndexer(inputCol='item_id', outputCol='item_idx')

ratings_df = user_indexer.fit(ratings_df).transform(ratings_df)
ratings_df = item_indexer.fit(ratings_df).transform(ratings_df)

ratings_df = ratings_df.withColumn('user_idx', col('user_idx').cast('int')) \
                       .withColumn('item_idx', col('item_idx').cast('int')) \
                       .withColumn('rating', col('rating').cast('float'))

num_users = ratings_df.agg({'user_idx': 'max'}).collect()[0][0] + 1
num_items = ratings_df.agg({'item_idx': 'max'}).collect()[0][0] + 1
print(f"  用户数: {num_users:,}, 商品数: {num_items:,}")
print(f"  评分矩阵密度: {ratings_df.count() / (num_users * num_items) * 100:.4f}%")

# ==================== 划分训练集和测试集 ====================
print("\n>>> 划分训练集/测试集 (80%/20%)")
train, test = ratings_df.randomSplit([0.8, 0.2], seed=42)
print(f"  训练集: {train.count():,} 条")
print(f"  测试集: {test.count():,} 条")

# ==================== ALS 模型训练 ====================
print("\n" + "=" * 70)
print("  ALS 模型训练")
print("=" * 70)
print("""
  参数说明:
    rank=10        - 隐因子维度 (用户/商品特征向量长度)
    maxIter=10     - 最大迭代次数
    regParam=0.1   - 正则化参数 (防止过拟合)
    alpha=1.0      - 隐式反馈置信参数
    coldStartStrategy='drop' - 冷启动策略(评估时丢弃未见过的用户/商品)
""")

als = ALS(
    maxIter=10,
    rank=10,
    regParam=0.1,
    userCol='user_idx',
    itemCol='item_idx',
    ratingCol='rating',
    coldStartStrategy='drop',
    seed=42
)

print("  正在训练 ALS 模型...")
model = als.fit(train)
print("  ✓ 模型训练完成!")

# ==================== 模型评估 ====================
print("\n" + "=" * 70)
print("  模型评估")
print("=" * 70)

predictions = model.transform(test)

evaluator = RegressionEvaluator(
    metricName='rmse',
    labelCol='rating',
    predictionCol='prediction'
)
rmse = evaluator.evaluate(predictions)
print(f"\n  ★ RMSE (均方根误差): {rmse:.4f}")
print(f"     RMSE 越小越好, 表示预测评分与实际评分越接近")
print(f"     通常 RMSE < 1.0 表示模型效果良好")

# 预测示例
print("\n  预测评分 vs 实际评分 (前10条):")
predictions.select('user_idx', 'item_idx', 'rating', 'prediction') \
    .withColumn('prediction', expr('ROUND(prediction, 2)')) \
    .show(10)

# ==================== 生成推荐 ====================
print("=" * 70)
print("  生成 Top-N 推荐")
print("=" * 70)

# 为每个用户推荐 Top-5 商品
print("\n>>> 为用户生成 Top-5 推荐...")
user_recs = model.recommendForAllUsers(5)
print(f"  为 {user_recs.count():,} 个用户生成了推荐")

# 为每个商品推荐 Top-5 用户 (可用于营销)
print("\n>>> 为商品推荐 Top-5 目标用户...")
item_recs = model.recommendForAllItems(5)
print(f"  为 {item_recs.count():,} 个商品匹配了目标用户")

# ==================== 推荐结果展示 ====================
print("\n" + "=" * 70)
print("  推荐结果展示")
print("=" * 70)

# 展开推荐结果 (取5个用户作为示例)
print("\n  示例用户推荐结果 (5个用户, 每人Top 5):")
sample_recs = user_recs.orderBy('user_idx').limit(5) \
    .withColumn('rec', explode('recommendations')) \
    .select('user_idx', 'rec.item_idx', 'rec.rating')

# 构建ID映射表用于还原
id_mapping = ratings_df.select('user_idx', 'user_id', 'item_idx', 'item_id').distinct()
user_id_map = id_mapping.select('user_idx', 'user_id').distinct()
item_id_map = id_mapping.select('item_idx', 'item_id').distinct()

sample_with_names = sample_recs \
    .join(user_id_map, 'user_idx') \
    .join(item_id_map, 'item_idx') \
    .select('user_id', 'item_id', col('rating').alias('predicted_rating')) \
    .orderBy('user_id', desc('predicted_rating'))

sample_with_names.show(25, truncate=False)

# ==================== 保存模型和推荐结果 ====================
print("\n>>> 保存模型...")
MODEL_PATH = "../output/als_model"
model.write().overwrite().save(f"file://{os.path.abspath(MODEL_PATH)}")
print(f"  模型已保存: {MODEL_PATH}")

# 保存推荐结果
print("\n>>> 保存推荐结果...")
RECS_PATH = "../output/recommendations.parquet"
sample_with_names.write.mode('overwrite').parquet(f"file://{os.path.abspath(RECS_PATH)}")
print(f"  推荐结果已保存: {RECS_PATH}")

# ==================== 总结 ====================
print("\n" + "=" * 70)
print("  步骤4 完成! ALS推荐算法总结:")
print("=" * 70)
print(f"""
  ① 算法: ALS (Alternating Least Squares) 协同过滤
  ② 隐因子维度: rank=10
  ③ 训练集/测试集: 80% / 20%
  ④ 模型RMSE: {rmse:.4f}
  ⑤ 生成推荐:
     - 为 {user_recs.count():,} 个用户各推荐 Top-5 商品
     - 为 {item_recs.count():,} 个商品各匹配 Top-5 目标用户
  ⑥ 模型已保存到: {MODEL_PATH}
  ⑦ 推荐结果已保存到: {RECS_PATH}
""")

spark.stop()
print("  步骤4完成! 可进入步骤5: 数据可视化")
