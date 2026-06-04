#!/bin/bash
# ============================================================================
#  一键运行脚本 - 电商用户行为分析与推荐系统
#  选题一: 基于Spark的电商用户行为分析与推荐系统
#  广州商学院 大数据技术综合实验 期末大作业
#
#  使用方法:
#    方式1 (逐步截图):  bash run_all.sh step      # 逐步骤运行
#    方式2 (全部运行):  bash run_all.sh all        # 一次性运行所有
#    方式3 (单独步骤):  bash run_all.sh 1          # 只运行步骤1
# ============================================================================

set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_input() {
    echo -e "${YELLOW}  [输入] $1${NC}"
}

print_output() {
    echo -e "${GREEN}  [输出] $1${NC}"
}

pause() {
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  请截图以上内容，然后按 Enter 继续...${NC}"
    echo -e "${RED}============================================${NC}"
    read -p ""
}

# ============================================================================
# 步骤1: 数据采集
# ============================================================================
step1() {
    print_header "步骤1/5: 电商用户行为数据采集"
    echo "  生成模拟电商平台的用户行为数据"
    echo "  数据量: ≥10万条 (满足课程要求 ≥1万)"
    echo "  包含: 用户ID、商品ID、行为类型、时间戳、类别、价格等"
    echo ""

    print_input "Python脚本: scripts/01_generate_data.py"
    echo ""
    python3 scripts/01_generate_data.py

    echo ""
    print_input "查看生成的数据文件"
    ls -lh data/ecommerce_behavior.csv
    echo ""
    echo "数据行数统计:"
    wc -l data/ecommerce_behavior.csv
    echo ""
    echo "前10行数据展示:"
    head -10 data/ecommerce_behavior.csv

    pause
}

# ============================================================================
# 步骤2: 数据预处理 (PySpark)
# ============================================================================
step2() {
    print_header "步骤2/5: 数据预处理 (PySpark)"

    echo "  功能说明:"
    echo "    ① 数据加载与Schema推断"
    echo "    ② 数据质量检查 (缺失值、重复值、异常值)"
    echo "    ③ 数据清洗 (去重、缺失值处理、异常价格过滤)"
    echo "    ④ 特征工程 (时间特征、行为编码)"
    echo "    ⑤ 存储为 Parquet 列式格式"
    echo ""

    print_input "PySpark脚本: scripts/02_preprocess.py"
    echo ""
    spark-submit scripts/02_preprocess.py 2>/dev/null || python3 scripts/02_preprocess.py

    echo ""
    print_input "查看清洗后的 Parquet 文件"
    ls -lh data/ecommerce_cleaned.parquet/ 2>/dev/null || echo "  (Parquet 目录)"

    pause
}

# ============================================================================
# 步骤3: Spark SQL 数据分析
# ============================================================================
step3() {
    print_header "步骤3/5: Spark SQL 数据分析 (10项分析)"

    echo "  分析清单:"
    echo "    3.1  平台核心指标 (PV/UV/商品数)"
    echo "    3.2  日均PV/UV趋势"
    echo "    3.3  用户行为类型分布"
    echo "    3.4  转化漏斗分析 (浏览→加购→收藏→购买)"
    echo "    3.5  商品热度排名 Top10"
    echo "    3.6  商品类别销售分析"
    echo "    3.7  用户活跃时段分析"
    echo "    3.8  地域分布分析"
    echo "    3.9  用户价值分层"
    echo "    3.10 商品关联分析"
    echo ""

    print_input "PySpark SQL脚本: scripts/03_spark_sql_analysis.py"
    echo ""
    spark-submit scripts/03_spark_sql_analysis.py 2>/dev/null || python3 scripts/03_spark_sql_analysis.py

    pause
}

# ============================================================================
# 步骤4: ALS 协同过滤推荐
# ============================================================================
step4() {
    print_header "步骤4/5: ALS 协同过滤推荐算法 (Spark MLlib)"

    echo "  算法说明:"
    echo "    算法: ALS (Alternating Least Squares) 矩阵分解"
    echo "    参数: rank=10, maxIter=10, regParam=0.1"
    echo "    评分: view=1, cart=2, fav=3, buy=5"
    echo "    评价: RMSE (均方根误差)"
    echo "    输出: 每个用户 Top-5 推荐商品"
    echo ""

    print_input "PySpark MLlib脚本: scripts/04_als_recommendation.py"
    echo ""
    spark-submit scripts/04_als_recommendation.py 2>/dev/null || python3 scripts/04_als_recommendation.py

    echo ""
    print_input "查看生成的推荐结果"
    ls -lh output/recommendations.parquet/ 2>/dev/null || echo "  (Parquet 目录)"
    ls -lh output/als_model/ 2>/dev/null || echo "  (模型目录)"

    pause
}

# ============================================================================
# 步骤5: 数据可视化
# ============================================================================
step5() {
    print_header "步骤5/5: 数据可视化 (8张图表)"

    echo "  图表清单:"
    echo "    图1: 日均PV/UV趋势"
    echo "    图2: 热门商品 Top15"
    echo "    图3: 用户行为类型分布"
    echo "    图4: 各类别销售额"
    echo "    图5: 用户活跃时段"
    echo "    图6: 转化漏斗"
    echo "    图7: 地域GMV"
    echo "    图8: 用户价值分层"
    echo ""

    print_input "可视化脚本: scripts/05_visualization.py"
    echo ""
    spark-submit scripts/05_visualization.py 2>/dev/null || python3 scripts/05_visualization.py

    echo ""
    print_input "查看生成的图表文件"
    ls -lh output/fig*.png

    pause
}

# ============================================================================
# 步骤6: Flask Web 可视化 (可选)
# ============================================================================
step6() {
    print_header "步骤6 (可选): 启动 Flask Web 可视化系统"

    echo "  启动 Flask 应用, 可通过浏览器访问仪表盘"
    echo "  访问地址: http://127.0.0.1:5000"
    echo ""
    echo -e "${RED}  按 Ctrl+C 可停止服务${NC}"
    echo ""

    cd web
    python3 app.py
}

# ============================================================================
# 主入口
# ============================================================================
case "${1:-step}" in
    all)
        print_header "一键运行全部步骤 (截图模式)"
        echo "  每个步骤完成后会暂停，请截图后按 Enter 继续"
        step1
        step2
        step3
        step4
        step5
        print_header "所有步骤完成! 🎉"
        echo ""
        echo "  产出文件清单:"
        echo "    data/ecommerce_behavior.csv        - 原始数据"
        echo "    data/ecommerce_cleaned.parquet/    - 清洗后数据"
        echo "    output/fig1~fig8_*.png             - 8张可视化图表"
        echo "    output/als_model/                  - ALS推荐模型"
        echo "    output/recommendations.parquet/    - 推荐结果"
        echo "    output/echarts_data.json           - ECharts前端数据"
        echo ""
        echo "  下一步: 运行 'bash run_all.sh web' 启动Web可视化系统"
        ;;
    step)
        print_header "逐步运行模式 - 每个步骤可单独截图"
        echo "  此模式会逐步执行，每步完成后暂停供截图"
        echo ""
        step1
        step2
        step3
        step4
        step5
        print_header "所有步骤完成! 🎉"
        ;;
    web|6)
        step6
        ;;
    1) step1 ;;
    2) step2 ;;
    3) step3 ;;
    4) step4 ;;
    5) step5 ;;
    *)
        echo "使用方法:"
        echo "  bash run_all.sh         逐步运行 (每步暂停，可截图)"
        echo "  bash run_all.sh all     一次性运行"
        echo "  bash run_all.sh 1       仅运行步骤1"
        echo "  bash run_all.sh 2       仅运行步骤2"
        echo "  bash run_all.sh 3       仅运行步骤3"
        echo "  bash run_all.sh 4       仅运行步骤4"
        echo "  bash run_all.sh 5       仅运行步骤5"
        echo "  bash run_all.sh web     启动Web可视化"
        ;;
esac
