"""
实验三 任务5：数据可视化
使用 Python matplotlib/seaborn 完成 CO2 排放数据可视化
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 非交互后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# ========== 中文字体设置 ==========
fm._rebuild()
plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Noto Sans CJK SC",
                                    "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
sns.set_style("whitegrid")

# ========== 加载数据 ==========
df = pd.read_csv("GCB2022v27_MtCO2_flat.csv")
# 加载预处理后的数据
df_clean = pd.read_csv("GCB2022_cleaned.csv")

output_dir = "output/"

# ========== 图1：全球CO2排放年度趋势(1950-2021) ==========
print("绘制图1: 全球CO2排放年度趋势...")
fig, ax = plt.subplots(figsize=(12, 6))
global_trend = df[df["Year"] >= 1950].groupby("Year")["Total"].sum() / 1000  # 转换为Gt
ax.fill_between(global_trend.index, global_trend.values, alpha=0.3, color="steelblue")
ax.plot(global_trend.index, global_trend.values, color="steelblue", linewidth=2)
ax.set_xlabel("Year (年份)", fontsize=12)
ax.set_ylabel("CO2 Emissions (GtCO2 / 十亿吨)", fontsize=12)
ax.set_title("Global CO2 Emissions Trend (1950-2021)\n全球CO2排放趋势", fontsize=14)
ax.annotate(f"{global_trend.values[-1]:.1f} Gt",
            xy=(2021, global_trend.values[-1]),
            xytext=(2010, global_trend.values[-1] + 2),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=11, color="red")
plt.tight_layout()
plt.savefig(output_dir + "fig1_global_trend.png", dpi=150)
plt.close()

# ========== 图2：2021年CO2排放量TOP15国家 ==========
print("绘制图2: 2021年TOP15排放国家...")
fig, ax = plt.subplots(figsize=(12, 7))
df_2021 = df[(df["Year"] == 2021) & (df["Total"] > 0)]
top15 = df_2021.nlargest(15, "Total")[["Country", "Total"]].sort_values("Total")
colors = plt.cm.Reds_r(np.linspace(0.3, 0.9, 15))
bars = ax.barh(range(15), top15["Total"].values, color=colors)
ax.set_yticks(range(15))
ax.set_yticklabels(top15["Country"].values, fontsize=10)
ax.set_xlabel("CO2 Emissions (MtCO2 / 百万吨)", fontsize=12)
ax.set_title("Top 15 Countries by CO2 Emissions (2021)\n2021年CO2排放量TOP15国家", fontsize=14)
for i, (v, c) in enumerate(zip(top15["Total"].values, top15["Country"].values)):
    ax.text(v + 50, i, f"{v:.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(output_dir + "fig2_top15_countries.png", dpi=150)
plt.close()

# ========== 图3：2021年全球碳排放源占比 ==========
print("绘制图3: 排放源占比...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
df_2021_global = df[df["Year"] == 2021]
sources = ["Coal", "Oil", "Gas", "Cement", "Flaring"]
source_totals = [df_2021_global[s].sum() for s in sources]
source_labels = ["Coal (煤炭)", "Oil (石油)", "Gas (天然气)", "Cement (水泥)", "Flaring (火炬)"]
source_colors = ["#2c3e50", "#e74c3c", "#3498db", "#95a5a6", "#f39c12"]

# 饼图
wedges, texts, autotexts = ax1.pie(
    source_totals, labels=source_labels, autopct="%1.1f%%",
    colors=source_colors, explode=(0.02, 0.02, 0.02, 0.02, 0.02)
)
ax1.set_title("Global CO2 Emission Sources (2021)\n全球CO2排放源占比", fontsize=13)

# 柱状图
ax2.bar(source_labels, [s / 1000 for s in source_totals], color=source_colors)
ax2.set_ylabel("Emissions (GtCO2 / 十亿吨)", fontsize=12)
ax2.set_title("CO2 Emissions by Source (2021)\n各排放源排放量", fontsize=13)
ax2.tick_params(axis="x", rotation=30)
for i, v in enumerate(source_totals):
    ax2.text(i, v / 1000 + 0.3, f"{v/1000:.1f}", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig(output_dir + "fig3_emission_sources.png", dpi=150)
plt.close()

# ========== 图4：主要国家人均排放对比 ==========
print("绘制图4: 人均排放对比...")
fig, ax = plt.subplots(figsize=(12, 6))
countries = ["China", "United States", "India", "Russia", "Japan",
             "Germany", "United Kingdom", "France", "Brazil", "South Africa",
             "Canada", "Australia", "Saudi Arabia", "Indonesia", "South Korea"]
df_sub = df_2021[df_2021["Country"].isin(countries)].dropna(subset=["Per Capita"])
df_sub = df_sub.sort_values("Per Capita", ascending=True)
colors = ["#e74c3c" if c in ["China", "United States", "India"]
          else "#3498db" for c in df_sub["Country"]]
ax.barh(df_sub["Country"], df_sub["Per Capita"], color=colors)
ax.set_xlabel("Per Capita CO2 Emissions (tons/person / 吨/人)", fontsize=12)
ax.set_title("Per Capita CO2 Emissions by Country (2021)\n各国人均CO2排放对比", fontsize=14)
for i, (v, c) in enumerate(zip(df_sub["Per Capita"].values, df_sub["Country"].values)):
    ax.text(v + 0.2, i, f"{v:.2f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(output_dir + "fig4_per_capita.png", dpi=150)
plt.close()

# ========== 图5：中国、美国、印度排放趋势对比(1950-2021) ==========
print("绘制图5: 中美印排放趋势...")
fig, ax = plt.subplots(figsize=(12, 6))
countries_compare = ["China", "United States", "India"]
colors_comp = ["#e74c3c", "#3498db", "#2ecc71"]
for country, color in zip(countries_compare, colors_comp):
    country_data = df[(df["Country"] == country) & (df["Year"] >= 1950)]
    ax.plot(country_data["Year"], country_data["Total"],
            color=color, linewidth=2.5, label=country)

ax.set_xlabel("Year (年份)", fontsize=12)
ax.set_ylabel("CO2 Emissions (MtCO2 / 百万吨)", fontsize=12)
ax.set_title("CO2 Emissions: China vs USA vs India (1950-2021)\n中美印CO2排放趋势对比", fontsize=14)
ax.legend(fontsize=12, loc="upper left")
china_2021_val = df[(df["Country"] == "China") & (df["Year"] == 2021)]["Total"].values[0]
ax.annotate(f"{china_2021_val:.0f}",
            xy=(2021, china_2021_val),
            xytext=(2005, 12000), arrowprops=dict(arrowstyle="->"), fontsize=9, color="#e74c3c")
plt.tight_layout()
plt.savefig(output_dir + "fig5_china_usa_india.png", dpi=150)
plt.close()

# ========== 图6：2000-2021年排放增速最快国家 ==========
print("绘制图6: 排放增速TOP10...")
df_2000 = df[(df["Year"] == 2000) & (df["Total"] > 1)].set_index("Country")
df_2021_c = df[(df["Year"] == 2021) & (df["Total"] > 1)].set_index("Country")
common = df_2000.index.intersection(df_2021_c.index)
growth = pd.DataFrame({
    "Country": common,
    "Growth": ((df_2021_c.loc[common, "Total"].values - df_2000.loc[common, "Total"].values)
               / df_2000.loc[common, "Total"].values * 100)
}).nlargest(10, "Growth")

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(growth["Country"][::-1], growth["Growth"].values[::-1],
        color=plt.cm.Oranges(np.linspace(0.4, 0.9, 10)))
ax.set_xlabel("Growth Rate (%), 2000-2021", fontsize=12)
ax.set_title("Top 10 Countries by CO2 Emission Growth (2000-2021)\nCO2排放增速最快国家", fontsize=14)
for i, (v, c) in enumerate(zip(growth["Growth"].values[::-1], growth["Country"].values[::-1])):
    ax.text(v + 5, i, f"{v:.0f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(output_dir + "fig6_growth_top10.png", dpi=150)
plt.close()

# ========== 图7：排放源年度堆叠面积图 ==========
print("绘制图7: 排放源年度趋势...")
fig, ax = plt.subplots(figsize=(12, 6))
yearly = df[df["Year"] >= 1950].groupby("Year")[["Coal", "Oil", "Gas", "Cement", "Flaring"]].sum()
yearly_gas = yearly / 1000  # 转换为Gt
ax.stackplot(yearly_gas.index,
             yearly_gas["Coal"], yearly_gas["Oil"], yearly_gas["Gas"],
             yearly_gas["Cement"], yearly_gas["Flaring"],
             labels=["Coal (煤炭)", "Oil (石油)", "Gas (天然气)",
                     "Cement (水泥)", "Flaring (火炬)"],
             colors=["#2c3e50", "#e74c3c", "#3498db", "#95a5a6", "#f39c12"],
             alpha=0.85)
ax.set_xlabel("Year (年份)", fontsize=12)
ax.set_ylabel("CO2 Emissions (GtCO2 / 十亿吨)", fontsize=12)
ax.set_title("Global CO2 Emissions by Source Over Time\n全球各排放源CO2趋势", fontsize=14)
ax.legend(loc="upper left", fontsize=10)
plt.tight_layout()
plt.savefig(output_dir + "fig7_source_stack.png", dpi=150)
plt.close()

# ========== 图8：相关系数热力图 ==========
print("绘制图8: 相关性热力图...")
fig, ax = plt.subplots(figsize=(10, 8))
corr_cols = ["Total", "Coal", "Oil", "Gas", "Cement", "Flaring", "Per Capita"]
corr_matrix = df[corr_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, mask=mask, square=True, linewidths=0.5,
            cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title("Correlation Heatmap of CO2 Emission Sources\nCO2排放源相关性热力图", fontsize=14)
plt.tight_layout()
plt.savefig(output_dir + "fig8_correlation.png", dpi=150)
plt.close()

print(f"\n所有图表已保存至 {output_dir} 目录")
print("任务5完成！")
print("\n生成的图表:")
print("  fig1_global_trend.png       - 全球CO2排放趋势")
print("  fig2_top15_countries.png    - 2021年TOP15排放国家")
print("  fig3_emission_sources.png   - 排放源占比")
print("  fig4_per_capita.png         - 人均排放对比")
print("  fig5_china_usa_india.png    - 中美印排放趋势")
print("  fig6_growth_top10.png       - 排放增速TOP10")
print("  fig7_source_stack.png       - 排放源年度堆叠")
print("  fig8_correlation.png        - 相关性热力图")
