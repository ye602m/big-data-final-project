#!/bin/bash
# 实验三：基于CO2排放量数据集的数据分析及可视化
# 完整运行脚本（在虚拟机 Ubuntu 中执行）

echo "============================================"
echo "实验三：CO2排放数据分析及可视化"
echo "============================================"

# 创建输出目录
mkdir -p output

# 任务1：数据集展示
echo ""
echo ">>> 任务1：数据集展示..."
python3 task1_data_display.py

# 任务2：数据预处理
echo ""
echo ">>> 任务2：数据预处理..."
python3 task2_preprocess.py

# 任务3：Spark SQL数据查询分析
echo ""
echo ">>> 任务3：Spark SQL查询分析..."
spark-shell -i task3_spark_sql.scala 2>&1 | tail -30

# 任务4：Spark MLlib构建回归预测模型
echo ""
echo ">>> 任务4：Spark MLlib回归预测..."
spark-shell -i task4_spark_mllib.scala 2>&1 | tail -30

# 任务5：数据可视化
echo ""
echo ">>> 任务5：数据可视化..."
python3 task5_visualization.py

echo ""
echo "============================================"
echo "实验三所有任务完成！"
echo "结果文件："
echo "  GCB2022_cleaned.csv - 预处理后数据"
echo "  output/fig1~fig8.png - 可视化图表"
echo "  output/global_trend/ - 全球趋势数据"
echo "============================================"
