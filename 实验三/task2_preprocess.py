"""
实验三 任务2：数据预处理
对 CO2 排放数据集进行清洗和预处理
"""
import pandas as pd
import numpy as np

df = pd.read_csv("GCB2022v27_MtCO2_flat.csv")
print(f"原始数据: {df.shape[0]} 行 x {df.shape[1]} 列")
print(f"原始缺失值总数: {df.isnull().sum().sum()}")

# ========== 1. 缺失值处理 ==========
print("\n" + "=" * 60)
print("1. 缺失值处理")
print("=" * 60)

# ISO代码缺失，用国家名填充
df["ISO 3166-1 alpha-3"] = df["ISO 3166-1 alpha-3"].fillna("WLD")

# 各排放源的缺失值：早期年份分源数据可能缺失，用0填充
for col in ["Coal", "Oil", "Gas", "Cement", "Flaring", "Other"]:
    df[col] = df[col].fillna(0)

# Total 缺失处理：先尝试用分源之合填充，剩余填0
df["Total"] = df["Total"].fillna(
    df["Coal"] + df["Oil"] + df["Gas"] + df["Cement"] + df["Flaring"] + df["Other"]
)
df["Total"] = df["Total"].fillna(0)

# Per Capita 缺失处理：用同国家中位数填充，剩余填0
df["Per Capita"] = df.groupby("Country")["Per Capita"].transform(
    lambda x: x.fillna(x.median())
)
df["Per Capita"] = df["Per Capita"].fillna(0)

print(f"处理后缺失值总数: {df.isnull().sum().sum()}")

# ========== 2. 异常值处理 ==========
print("\n" + "=" * 60)
print("2. 异常值处理")
print("=" * 60)

# 检查负值
for col in ["Total", "Coal", "Oil", "Gas", "Cement", "Flaring", "Other", "Per Capita"]:
    neg_count = (df[col] < 0).sum()
    if neg_count > 0:
        print(f"  {col} 负值: {neg_count} 条, 已置为0")
        df.loc[df[col] < 0, col] = 0

# 使用IQR法观察Total列极端值分布
Q1 = df["Total"].quantile(0.25)
Q3 = df["Total"].quantile(0.75)
IQR = Q3 - Q1
upper = Q3 + 3 * IQR
outliers = (df["Total"] > upper).sum()
print(f"  Total IQR上界: {upper:.2f}, 超出记录数: {outliers}")
print("  未删除极端值（高排放国如中国、美国数据为正常大值）")

# ========== 3. 数据筛选与特征工程 ==========
print("\n" + "=" * 60)
print("3. 数据筛选与特征工程")
print("=" * 60)

df_recent = df[df["Year"] >= 1950].copy()
print(f"  1950年后数据: {df_recent.shape[0]} 行")

# 化石燃料排放总量
df["Fossil_Fuel"] = df["Coal"] + df["Oil"] + df["Gas"]
df["Fossil_Ratio"] = np.where(df["Total"] > 0, df["Fossil_Fuel"] / df["Total"], 0)

# 主要排放源标签
def main_source(row):
    sources = {"Coal": row["Coal"], "Oil": row["Oil"], "Gas": row["Gas"]}
    if max(sources.values()) == 0:
        return "None"
    return max(sources, key=sources.get)

df["Main_Source"] = df.apply(main_source, axis=1)
print(f"  新增列: Fossil_Fuel, Fossil_Ratio, Main_Source")

# ========== 4. 保存处理后的数据 ==========
output_file = "GCB2022_cleaned.csv"
df.to_csv(output_file, index=False)
print(f"\n预处理完成，已保存至: {output_file}")
print(f"最终数据: {df.shape[0]} 行 x {df.shape[1]} 列")
