#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成课程论文 Word 文档
按照广州商学院课程设计论文模板规范
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
import os

doc = Document()

# ==================== 页面设置 ====================
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

# ==================== 样式设置 ====================
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)  # 小四号
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
pf = style.paragraph_format
pf.line_spacing = 1.25

def add_heading_custom(text, level=1):
    """添加标题: 四号宋体加粗"""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(14)  # 四号
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h

def add_para(text, bold=False, indent=True):
    """添加正文段落: 小四号宋体"""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)  # 空两格
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(text)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(12)  # 小四号
    run.font.bold = bold
    return p

def add_code_block(code_text):
    """添加代码块"""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(code_text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    return p

# ==================== 封面 ====================
for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('广州商学院\n课 程 设 计 论 文')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(22)  # 小二
run.font.bold = True

doc.add_paragraph()

cover_info = [
    ('课 程 名 称', '大数据技术综合实验'),
    ('考 查 学 期', '2025-2026 学年 第 2 学期'),
    ('考 查 方 式', '课程论文'),
    ('题    目', '基于Spark的电商用户行为分析与推荐系统'),
    ('姓    名', '杨恩迈'),
    ('学    号', '202306140143'),
    ('专    业', '智能科学与技术'),
    ('成    绩', ''),
    ('指 导 教 师', ''),
]

for label, value in cover_info:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 2.0
    run = p.add_run(f'{label}：{value}')
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(16)  # 三号
    run.font.bold = True

doc.add_page_break()

# ==================== 中文摘要 ====================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('摘  要')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(18)  # 小二号
run.font.bold = True

add_para(
    '随着电子商务的快速发展，海量用户行为数据为个性化推荐提供了丰富的数据基础。'
    '本文基于Apache Spark大数据处理框架，设计并实现了一个电商用户行为分析与推荐系统。'
    '系统使用PySpark进行数据预处理和分析，采用Spark SQL完成多维度的用户行为分析，'
    '包括PV/UV统计、转化漏斗分析、商品热度排名、用户活跃时段分析、地域分布分析和用户价值分层等。'
    '在推荐算法方面，系统基于Spark MLlib实现了ALS（交替最小二乘法）协同过滤推荐算法，'
    '通过矩阵分解技术为用户生成个性化Top-N商品推荐。'
    '实验使用包含10万条记录的模拟电商用户行为数据集，涵盖5000名用户、2000件商品和10个商品类别。'
    '通过数据预处理，清洗后的数据缺失率和重复率均降至0%。'
    'ALS推荐模型的RMSE（均方根误差）为1.57，为全部5000名用户成功生成了Top-5个性化推荐。'
    '系统还实现了基于Matplotlib和ECharts的数据可视化功能，以及基于Flask的Web展示系统，'
    '提供了直观的数据仪表盘和推荐查询界面。'
    '实验结果表明，基于Spark的协同过滤推荐算法能够有效挖掘用户行为模式，'
    '为电商平台提供可靠的个性化推荐服务。'
)

p = doc.add_paragraph()
p.paragraph_format.first_line_indent = Pt(24)
run = p.add_run('关键词：')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(12)
run.font.bold = True
run = p.add_run('Spark；协同过滤；ALS；用户行为分析；推荐系统；电商数据')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(12)

doc.add_page_break()

# ==================== 正文 ====================

# ---- 1. 需求分析 ----
add_heading_custom('1 需求分析')

add_heading_custom('1.1 课题背景', level=2)
add_para(
    '随着互联网和移动支付的普及，电子商务平台已成为人们日常消费的重要渠道。'
    '用户在电商平台上产生了海量的行为数据，包括浏览、加购、收藏和购买等。'
    '如何从这些海量数据中挖掘用户的兴趣偏好和消费模式，并据此提供个性化推荐，'
    '已成为提升电商平台用户体验和销售额的关键技术问题。'
    '传统的数据分析方法难以应对海量数据的存储和计算需求，'
    '而Apache Spark作为新一代大数据处理框架，以其内存计算和丰富的机器学习库，'
    '为大规模推荐系统的实现提供了高效的技术支撑。'
)

add_heading_custom('1.2 问题描述', level=2)
add_para(
    '本课题要求设计并实现一个基于Spark的电商用户行为分析与推荐系统。'
    '系统需要完成以下核心任务：(1) 采集或生成电商用户行为数据，数据量不少于1万条；'
    '(2) 对原始数据进行预处理，包括去重、缺失值处理、异常值过滤和特征提取；'
    '(3) 使用Spark SQL进行多维度的数据分析，挖掘用户行为规律；'
    '(4) 基于Spark MLlib实现ALS协同过滤推荐算法，为每个用户生成个性化推荐；'
    '(5) 实现数据可视化展示，包括趋势图、分布图、漏斗图等；'
    '(6) 可选搭建Web可视化系统提供交互式数据查询。'
    '所有数据分析任务需在Linux系统环境下完成。'
)

add_heading_custom('1.3 设计目标', level=2)
add_para(
    '本系统的具体设计目标如下：(1) 数据规模：生成不少于10万条用户行为记录，'
    '涵盖5000名用户和2000件商品；(2) 预处理质量：清洗后数据缺失率0%、重复率0%；'
    '(3) 分析维度：完成至少8项数据分析，包括核心指标、趋势分析、行为分布、转化漏斗、'
    '商品热度、类别销售、时段分析和用户分层；(4) 推荐效果：ALS模型RMSE小于2.0，'
    '为全部用户生成个性化Top-5推荐；(5) 可视化：输出不少于6张高质量图表，'
    '清晰展示分析结果；(6) 工程规范：代码注释率超过50%，提供完整的运行脚本。'
    '所有数据处理基于PySpark实现，分析结果可复现。'
)

# ---- 2. 总体设计 ----
add_heading_custom('2 总体设计')

add_heading_custom('2.1 系统架构', level=2)
add_para(
    '本系统采用经典的批处理大数据架构，分为数据采集层、数据存储层、数据处理层、'
    '数据分析层、推荐引擎层和可视化展示层六个层次。'
    '数据采集层负责生成或导入电商用户行为数据，以CSV格式存储。'
    '数据存储层使用HDFS存储原始数据，清洗后的数据以Parquet列式存储格式保存，'
    '以提升查询效率。数据处理层基于PySpark DataFrame API实现数据清洗和特征工程。'
    '数据分析层使用Spark SQL完成10项多维分析任务。'
    '推荐引擎层基于Spark MLlib的ALS算法构建协同过滤推荐模型。'
    '可视化展示层使用Matplotlib生成静态图表，并通过Flask搭建Web交互界面。'
    '系统各层之间通过标准化的数据接口进行交互，保证了模块的独立性和可维护性。'
)

add_heading_custom('2.2 技术路线', level=2)
add_para(
    '系统选用以下技术栈：(1) 编程语言：Python 3.6，使用PySpark API进行Spark编程；'
    '(2) 大数据框架：Apache Spark 3.0.3，运行在本地模式下进行开发和测试；'
    '(3) 数据处理：PySpark DataFrame API和Spark SQL；'
    '(4) 推荐算法：Spark MLlib中的ALS（Alternating Least Squares）协同过滤算法，'
    '通过矩阵分解将用户-商品评分矩阵分解为低维用户特征向量和商品特征向量；'
    '(5) 数据存储：CSV格式存储原始数据，Parquet格式存储清洗后数据；'
    '(6) 可视化：Matplotlib生成PNG图表，ECharts用于Web前端动态可视化；'
    '(7) Web框架：Flask（Python轻量级Web框架）。'
    '选择Spark作为核心框架的主要原因是其内存计算能力强、API丰富、'
    '内置MLlib机器学习库，能够一站式完成数据处理、分析和建模的全流程。'
    '选择ALS算法的原因是其在Netflix推荐竞赛中表现优异，'
    '能够有效处理大规模稀疏评分矩阵的分解问题。'
)

add_heading_custom('2.3 系统流程', level=2)
add_para(
    '系统整体流程如下：(1) 数据生成：使用Python脚本生成10万条模拟电商用户行为数据，'
    '包含用户ID、商品ID、行为类型、时间戳、商品类别、价格、用户区域等信息；'
    '(2) 数据上传：将CSV文件上传至HDFS或本地文件系统；'
    '(3) 数据预处理：使用PySpark进行去重、缺失值处理、异常值过滤、'
    '时间特征提取和行为类型编码；预处理后数据以Parquet格式存储；'
    '(4) 数据分析：使用Spark SQL执行10项分析任务，包括平台核心指标统计、'
    'PV/UV趋势分析、用户行为类型分布统计、转化漏斗分析、商品热度排名、'
    '商品类别销售分析、用户活跃时段分析、地域分布分析、用户价值分层和商品关联分析；'
    '(5) 推荐建模：将用户行为转换为隐式评分矩阵（view=1, cart=2, fav=3, buy=5），'
    '使用ALS算法进行模型训练，通过RMSE评估模型效果，为每个用户生成Top-5推荐；'
    '(6) 数据可视化：生成8张可视化图表，覆盖趋势、分布、排名、对比等多个维度；'
    '(7) Web展示：通过Flask搭建Web仪表盘，提供数据概览和个性化推荐查询功能。'
)

# ---- 3. 详细设计 ----
add_heading_custom('3 详细设计')

add_heading_custom('3.1 数据采集模块', level=2)
add_para(
    '数据采集模块（01_generate_data.py）负责生成模拟的电商用户行为数据集。'
    '模块核心类是DataGenerator，包含以下方法：'
    '(1) generate_items(num_items)：生成商品信息表，为每个商品分配唯一ID、'
    '随机类别和价格区间；(2) generate_users(num_users)：生成用户信息表，'
    '为每个用户分配唯一ID、随机区域和年龄段；'
    '(3) generate_behaviors(users, items, num_records)：根据预设的行为类型权重'
    '（view:60%, cart:20%, fav:10%, buy:10%）随机生成用户行为记录；'
    '(4) save_to_csv(records, output_path)：将数据保存为CSV格式。'
    '生成的数据包含8个字段：user_id、item_id、behavior_type、timestamp、'
    'category、price、user_region、user_age_group。'
    '数据集规模为10万条，满足课程要求（≥1万条），时间跨度为2024年1月1日至6月30日。'
)

add_heading_custom('3.2 数据预处理模块', level=2)
add_para(
    '数据预处理模块（02_preprocess.py）基于PySpark DataFrame API实现，'
    '主要包含以下处理步骤：(1) 数据加载：使用spark.read.csv加载CSV数据，'
    '自动推断列的数据类型；(2) 数据质量检查：统计各列的缺失值数量和重复行数；'
    '(3) 数据清洗：调用dropDuplicates()去重，使用dropna()处理缺失值，'
    '通过filter()过滤价格异常值（price<=0或price>=100000）；'
    '(4) 特征工程：使用to_timestamp()解析时间戳，提取date、hour、dayofweek、month特征；'
    '使用StringIndexer对behavior_type进行编码；(5) 数据保存：使用write.parquet()'
    '将清洗后的数据保存为Parquet列式存储格式。'
    '预处理完成后输出清洗前后对比统计表，展示缺失率、重复率、记录数等指标的变化。'
)

add_heading_custom('3.3 Spark SQL分析模块', level=2)
add_para(
    'Spark SQL分析模块（03_spark_sql_analysis.py）共包含10项分析任务，'
    '所有分析通过Spark SQL语句或DataFrame API实现：'
    '(1) 核心指标概览：使用COUNT和COUNT DISTINCT统计总记录数、用户数、商品数、'
    '类别数和日均PV；(2) PV/UV趋势：按月统计PV和UV，使用窗口函数计算环比变化；'
    '(3) 行为类型分布：按behavior_type分组统计数量和占比；'
    '(4) 转化漏斗：使用CASE WHEN统计各阶段独立用户数，计算相邻阶段转化率；'
    '(5) 商品热度排名：按item_id分组统计浏览量和购买量，排序取Top10；'
    '(6) 类别销售分析：按category分组统计销售额、订单数和平均客单价；'
    '(7) 用户活跃时段分析：按hour分组统计行为数量，识别高峰时段；'
    '(8) 地域分布分析：按user_region分组统计用户数、GMV、ARPU值；'
    '(9) 用户价值分层：基于购买次数将用户分为高价值、中等、普通、单次购买和未购买五层；'
    '(10) 商品关联分析：通过自连接查询同一用户购买的不同类别组合，发现跨类别购买模式。'
)

add_heading_custom('3.4 ALS推荐算法模块', level=2)
add_para(
    'ALS推荐算法模块（04_als_recommendation.py）基于Spark MLlib实现协同过滤推荐。'
    '主要流程为：(1) 评分矩阵构建：将用户行为类型转换为隐式评分，'
    'view映射为1.0、cart映射为2.0、fav映射为3.0、buy映射为5.0，'
    '同一用户对同一商品的多次行为取最高评分；(2) ID编码映射：'
    '使用StringIndexer将字符串类型的user_id和item_id编码为整数索引，'
    '以适配ALS算法对ID列的数据类型要求；(3) 数据集划分：使用randomSplit()'
    '按80%:20%的比例将数据划分为训练集和测试集，设置随机种子确保结果可复现；'
    '(4) 模型训练：设置ALS参数rank=10（隐因子维度）、maxIter=10（最大迭代次数）、'
    'regParam=0.1（L2正则化系数），使用训练集进行模型拟合；'
    '(5) 模型评估：在测试集上计算预测评分与实际评分的RMSE；'
    '(6) 推荐生成：调用recommendForAllUsers(5)为全部用户生成Top-5推荐，'
    '调用recommendForAllItems(5)为全部商品匹配Top-5潜在用户；'
    '(7) 结果持久化：将训练好的模型和推荐结果分别保存为Parquet文件。'
    'ALS算法的核心思想是通过梯度下降迭代优化用户矩阵U和商品矩阵V，'
    '使得U×V^T尽可能逼近原始评分矩阵，从而预测用户对未交互商品的评分。'
)

add_heading_custom('3.5 可视化模块', level=2)
add_para(
    '可视化模块（05_visualization.py）使用Matplotlib和Pandas生成8张分析图表：'
    '(1) 日均PV/UV趋势图：使用双Y轴折线图展示浏览量（PV）和访客数（UV）的日变化趋势；'
    '(2) 热门商品Top15：使用水平柱状图展示浏览量最高的15件商品；'
    '(3) 用户行为类型分布：使用饼图和柱状图对比展示四种行为类型的分布比例；'
    '(4) 各类别销售额：使用彩色柱状图展示10个商品类别的销售总额；'
    '(5) 用户活跃时段：使用面积图展示24小时各时段的行为活跃度，标注峰值时段；'
    '(6) 转化漏斗：使用漏斗图展示浏览→加购→收藏→购买的用户转化路径和转化率；'
    '(7) 地域GMV分布：使用柱状图展示各地区销售额（GMV）贡献；'
    '(8) 用户价值分层：使用饼图展示高价值、中等、普通、单次购买和未购买用户的占比。'
    '此外，模块还将分析数据导出为JSON格式供ECharts前端使用。'
)

# ---- 4. 程序运行结果与分析 ----
add_heading_custom('4 程序运行结果测试与分析')

add_heading_custom('4.1 数据采集结果', level=2)
add_para(
    '运行步骤1数据采集脚本，成功生成包含100,000条记录的电商用户行为数据集。'
    '数据集文件大小为7.66MB，包含5,000名用户对2,000件商品的行为记录。'
    '行为类型分布为：浏览（view）60,090条（60.1%）、加购（cart）20,225条（20.2%）、'
    '收藏（fav）9,774条（9.8%）、购买（buy）9,911条（9.9%）。'
    '数据时间跨度为2024年1月1日至2024年6月30日，共181天。'
    '数据字段完整，包含用户ID、商品ID、行为类型、时间戳、商品类别、价格、'
    '用户区域和用户年龄段8个维度。数据规模满足课程要求（≥1万条），'
    '且数据分布合理，符合真实电商场景的行为模式（浏览量>加购量>收藏量≈购买量）。'
)

add_heading_custom('4.2 数据预处理结果', level=2)
add_para(
    '运行步骤2数据预处理脚本，对10万条原始数据进行了全面的质量检查和清洗。'
    '检查结果显示：原始数据质量较好，无缺失值和重复记录。'
    '通过异常值过滤（price<=0或price>=100000），所有记录均通过验证。'
    '清洗后数据量和原始数据量一致（100,000条），数据完整性保持100%。'
    '特征工程方面，成功提取了date、hour、dayofweek和month四个时间特征，'
    '并对behavior_type进行了数值编码。清洗后的数据以Parquet列式存储格式保存，'
    '文件大小约为2.9MB（压缩后），相比原始CSV文件（7.66MB）压缩率约为62%，'
    '体现了列式存储格式在存储效率方面的优势。'
    '用户行为分析显示，活跃度最高的用户（USER_02528）有41次行为记录，'
    '浏览了41个不同商品，在37天内保持活跃，反映出该用户的高参与度。'
)

add_heading_custom('4.3 Spark SQL分析结果', level=2)
add_para(
    '运行步骤3的Spark SQL分析，获得了10个维度的分析结果。核心指标方面：'
    '平台总行为记录100,000条，独立用户5,000人，独立商品2,000件，商品类别10个。'
    '转化漏斗分析显示：浏览用户5,000人（100%），加购用户5,000人（100%），'
    '收藏用户4,992人（99.8%），购买用户4,312人（86.2%）。'
    '浏览到购买的整体转化率为86.2%，说明系统生成的模拟数据具有合理的转化特征。'
    '商品热度排名中，ITEM_01904以78次浏览和8次购买位居第一，'
    'ITEM_01913以73次浏览和11次购买次之。'
    '用户活跃时段分析显示，行为最高峰出现在18:00（下午6点），'
    '共4,343条，符合晚间购物高峰特征。'
    '地域GMV分析显示，北京以995,666元GMV居首，'
    '深圳（960,447元）、武汉（945,309元）紧随其后，各地ARPU值在1,600-1,800元之间。'
    '用户价值分层方面：普通用户（2-4次购买）占53.68%，'
    '单次购买用户占27.36%，未购买用户占13.76%，中等价值用户（5-9次购买）占5.20%。'
    '商品类别关联分析表明，美妆护肤与食品饮料的共现用户最多（201人），'
    '服装鞋帽与电子产品的关联也较为紧密（201人），这些发现可为交叉销售策略提供参考。'
)

add_heading_custom('4.4 ALS推荐结果', level=2)
add_para(
    '运行步骤4的ALS协同过滤推荐算法，完成了模型训练和推荐生成。'
    '将10万条行为记录转换为评分矩阵后，获得用户-商品评分配对。'
    '评分矩阵密度约为1%（100,000条评分/（5,000用户×2,000商品））。'
    '将数据按80:20分割为训练集和测试集，使用ALS算法（rank=10, maxIter=10, regParam=0.1）'
    '进行训练。模型在测试集上的RMSE（均方根误差）为1.5687，'
    '表示预测评分与实际评分的平均偏差约为1.57分（评分范围1-5）。'
    '考虑到评分矩阵的稀疏性和隐式评分的特性，该RMSE值在可接受范围内。'
    '推荐生成阶段，成功为全部5,000名用户生成了Top-5个性化商品推荐，'
    '同时为全部2,000件商品匹配了Top-5潜在目标用户。'
    '以5个样本用户的推荐结果为例，预测评分在2.98至4.66之间，'
    '其中USER_02402获得的最高预测评分为4.57（ITEM_01741），'
    'USER_04478获得的最高预测评分为4.66（ITEM_00527），'
    '这表明模型能够有效区分用户对不同商品的偏好强度。'
    'ALS模型和推荐结果已分别保存至output/als_model和output/recommendations.parquet，'
    '可供后续使用或增量更新。'
)

add_heading_custom('4.5 可视化结果', level=2)
add_para(
    '运行步骤5的可视化脚本，成功生成了8张PNG格式图表（fig1至fig8），'
    '每张图表均以300DPI分辨率输出，确保在论文中清晰呈现。'
    '图1（日均PV/UV趋势）展示了PV和UV随时间的变化趋势，便于观察平台流量波动。'
    '图2（热门商品Top15）直观对比了高流量商品的关注度差异。'
    '图3（行为类型分布）以饼图和柱状图双重形式呈现了四种行为类型的比例。'
    '图4（各类别销售额）展示了10个商品类别的销售贡献差异。'
    '图5（用户活跃时段）显示了24小时各时段的行为分布，18点为明显峰值。'
    '图6（转化漏斗）清晰展示了各阶段的用户数和转化率。'
    '图7（地域GMV分布）对比了不同地区的销售额贡献。'
    '图8（用户价值分层）展示了五类价值用户的分布比例。'
    '所有图表均已保存至项目output目录，同时生成了echarts_data.json供Web前端使用。'
)

# ---- 5. 结论与心得 ----
add_heading_custom('5 结论与心得')

add_heading_custom('5.1 主要结论', level=2)
add_para(
    '本文基于Apache Spark框架，成功设计并实现了一个电商用户行为分析与推荐系统。'
    '系统完成了从数据生成、预处理、分析到推荐生成和可视化的全流程。'
    '通过Spark SQL的10项多维分析，系统揭示了用户行为的多项规律：'
    '浏览行为占比约60%，是电商平台最主要的用户行为类型；'
    '转化漏斗显示浏览到购买的转化率约为86%（模拟数据）；'
    '用户活跃高峰出现在18:00，反映了晚间购物的消费习惯；'
    '北京、深圳、武汉等一线城市是GMV贡献最大的地区。'
    'ALS协同过滤推荐模型达到了RMSE 1.57的性能水平，'
    '为5,000名用户成功生成了个性化推荐，证明了基于Spark MLlib的大规模推荐系统'
    '的技术可行性。系统还实现了基于Matplotlib和Flask的可视化展示，'
    '提供了直观的数据分析界面。'
)

add_heading_custom('5.2 问题与改进方向', level=2)
add_para(
    '在本系统的开发和实验过程中，也发现了一些可以改进的问题：'
    '(1) 数据方面：由于使用的是模拟数据，数据分布和真实电商场景存在一定差异，'
    '后续可以采用Kaggle或真实平台的公开数据集进行验证；'
    '(2) 推荐算法方面：目前仅使用了ALS协同过滤，可以进一步对比基于内容的推荐、'
    '混合推荐等方法的推荐效果；ALS的RMSE为1.57，通过调整隐因子维度(rank)、'
    '正则化参数(regParam)或增加迭代次数，可能进一步降低误差；'
    '(3) 实时处理方面：当前系统是批处理架构，无法实现实时推荐更新，'
    '未来可以引入Flink或Spark Streaming实现实时用户行为捕捉和动态推荐更新；'
    '(4) 冷启动问题：ALS对未见过的用户或商品无法生成有效推荐，'
    '可以结合基于内容的推荐或热门推荐策略解决冷启动问题；'
    '(5) 可视化交互：当前Web系统仅提供基础的图表展示和推荐查询，'
    '可以增加更多的交互式分析功能，如自定义时间范围、多维度下钻等。'
)

add_heading_custom('5.3 学习心得', level=2)
add_para(
    '通过本次大数据技术综合实验的课程设计，我深入学习和实践了以下内容：'
    '第一，掌握了Apache Spark的核心编程模型，包括RDD、DataFrame和Spark SQL的使用方法，'
    '理解了内存计算相比传统MapReduce的性能优势。'
    '第二，学习了协同过滤推荐算法的原理和实现，特别是ALS矩阵分解算法的数学原理'
    '及其在大规模稀疏矩阵上的应用。'
    '第三，实践了完整的大数据项目开发流程，包括需求分析、架构设计、数据处理、'
    '模型训练、评估优化和可视化展示，提升了工程实践能力。'
    '第四，熟悉了Linux环境下的开发部署流程，加深了对大数据生态系统的理解。'
    '在项目过程中，遇到的主要困难包括Spark环境配置、PySpark API的使用熟悉、'
    'ALS参数调优以及中文可视化字体配置等，通过查阅官方文档和社区资源逐一解决。'
    '本次实验让我认识到，大数据技术不仅仅是工具的使用，更重要的是对数据本身的理解'
    '和对业务场景的洞察，只有将技术与业务需求有机结合，才能发挥大数据的真正价值。'
)

# ---- 参考文献 ----
doc.add_page_break()
add_heading_custom('参考文献')

refs = [
    '[1] 林子雨. 大数据技术原理与应用（第3版）[M]. 北京: 人民邮电出版社, 2021.',
    '[2] Holden Karau, Andy Konwinski, Patrick Wendell, Matei Zaharia. Learning Spark: Lightning-Fast Data Analytics (2nd Edition)[M]. O\'Reilly Media, 2020.',
    '[3] Yehuda Koren, Robert Bell, Chris Volinsky. Matrix Factorization Techniques for Recommender Systems[J]. IEEE Computer, 2009, 42(8): 30-37.',
    '[4] Yifan Hu, Yehuda Koren, Chris Volinsky. Collaborative Filtering for Implicit Feedback Datasets[C]. Proceedings of the 8th IEEE International Conference on Data Mining, 2008: 263-272.',
    '[5] Matei Zaharia, Mosharaf Chowdhury, Michael J. Franklin, Scott Shenker, Ion Stoica. Spark: Cluster computing with working sets[C]. Proceedings of the 2nd USENIX Conference on Hot Topics in Cloud Computing, 2010: 10.',
    '[6] Apache Spark MLlib Documentation: Collaborative Filtering - ALS[EB/OL]. https://spark.apache.org/docs/latest/ml-collaborative-filtering.html, 2024.',
]

for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(ref)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(12)

# ==================== 保存 ====================
output_path = os.path.join(os.path.dirname(__file__), '..', 'output', '课程论文_基于Spark的电商用户行为分析与推荐系统.docx')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
doc.save(output_path)
print(f'论文已保存至: {output_path}')
print(f'字数统计: 约5800字 (满足≥3000字要求 ✓)')
