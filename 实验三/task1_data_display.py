"""
实验三 任务1：数据集展示
使用 Python 展示 GCB2022v27_MtCO2_flat.csv 数据集
"""
import pandas as pd

# ========== 1. 读取数据 ==========
df = pd.read_csv("GCB2022v27_MtCO2_flat.csv")
print("=" * 60)
print("数据集基本信息")
print("=" * 60)
print(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")

# ========== 2. 列名及含义 ==========
print("\n列名及含义:")
col_desc = {
    "Country": "国家名称",
    "ISO 3166-1 alpha-3": "ISO三位字母国家代码",
    "Year": "年份",
    "Total": "总CO2排放量 (百万吨)",
    "Coal": "煤炭排放量",
    "Oil": "石油排放量",
    "Gas": "天然气排放量",
    "Cement": "水泥生产排放量",
    "Flaring": "火炬燃烧排放量",
    "Other": "其他排放量",
    "Per Capita": "人均CO2排放量 (吨/人)",
}
for col, desc in col_desc.items():
    print(f"  {col}: {desc}")

# ========== 3. 前10行展示 ==========
print("\n" + "=" * 60)
print("前10行数据:")
print("=" * 60)
print(df.head(10).to_string())

# ========== 4. 数据类型 ==========
print("\n" + "=" * 60)
print("数据类型:")
print("=" * 60)
print(df.dtypes.to_string())

# ========== 5. 基本统计信息 ==========
print("\n" + "=" * 60)
print("数值列统计描述:")
print("=" * 60)
print(df.describe().to_string())

# ========== 6. 缺失值统计 ==========
print("\n" + "=" * 60)
print("缺失值统计:")
print("=" * 60)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({"缺失数": missing, "缺失率(%)": missing_pct})
print(missing_df.to_string())

# ========== 7. 数据范围 ==========
print("\n" + "=" * 60)
print("数据范围:")
print("=" * 60)
print(f"年份范围: {df['Year'].min()} - {df['Year'].max()}")
print(f"国家数量: {df['Country'].nunique()}")
print(f"ISO代码数量: {df['ISO 3166-1 alpha-3'].nunique()}")
print(f"总排放量范围: {df['Total'].min():.2f} - {df['Total'].max():.2f} MtCO2")
print(f"人均排放量范围: {df['Per Capita'].min():.4f} - {df['Per Capita'].max():.2f} 吨/人")

print("\n任务1完成！")
