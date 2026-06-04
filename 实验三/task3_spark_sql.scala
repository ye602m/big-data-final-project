/*
 * 实验三 任务3：Spark SQL 数据查询分析
 * 用法: spark-shell -i task3_spark_sql.scala
 */
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

val spark = SparkSession.builder()
  .appName("CO2 Emissions Analysis")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

// ========== 1. 加载数据 ==========
val df = spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .csv("GCB2022v27_MtCO2_flat.csv")

println(s"数据加载完成: ${df.count()} 行")
df.printSchema()
df.show(10, false)

// 注册临时视图
df.createOrReplaceTempView("co2")

// ========== 2. 查询1: 2021年CO2排放量TOP10国家 ==========
println("\n===== 2021年CO2排放量TOP10国家 =====")
spark.sql("""
  SELECT Country, Year, Total, `Per Capita`
  FROM co2
  WHERE Year = 2021 AND Total > 0
  ORDER BY Total DESC
  LIMIT 10
""").show(false)

// ========== 3. 查询2: 全球CO2排放量年度趋势(1950年后) ==========
println("\n===== 全球CO2排放年度趋势 =====")
spark.sql("""
  SELECT Year, ROUND(SUM(Total), 2) AS Global_Total,
         ROUND(SUM(Coal), 2) AS Global_Coal,
         ROUND(SUM(Oil), 2) AS Global_Oil,
         ROUND(SUM(Gas), 2) AS Global_Gas
  FROM co2
  WHERE Year >= 1950
  GROUP BY Year
  ORDER BY Year
""").show(10, false)

// ========== 4. 查询3: 2021年各排放源占比 ==========
println("\n===== 2021年各排放源全球占比 =====")
spark.sql("""
  SELECT
    ROUND(SUM(Coal)/SUM(Total)*100, 2) AS Coal_Pct,
    ROUND(SUM(Oil)/SUM(Total)*100, 2) AS Oil_Pct,
    ROUND(SUM(Gas)/SUM(Total)*100, 2) AS Gas_Pct,
    ROUND(SUM(Cement)/SUM(Total)*100, 2) AS Cement_Pct,
    ROUND(SUM(Flaring)/SUM(Total)*100, 2) AS Flaring_Pct
  FROM co2
  WHERE Year = 2021 AND Total > 0
""").show(false)

// ========== 5. 查询4: 2021年主要国家人均排放对比 ==========
println("\n===== 2021年主要国家人均排放对比 =====")
spark.sql("""
  SELECT Country, `Per Capita`, Total, Year
  FROM co2
  WHERE Year = 2021
    AND Country IN ('China','United States','India','Russia',
                    'Japan','Germany','United Kingdom','France',
                    'Brazil','South Africa')
  ORDER BY `Per Capita` DESC
""").show(false)

// ========== 6. 查询5: 2000-2021年排放增速TOP10 ==========
println("\n===== 2000-2021年排放增速TOP10国家 =====")
spark.sql("""
  SELECT a.Country,
         ROUND(a.Total, 2) AS Emission_2000,
         ROUND(b.Total, 2) AS Emission_2021,
         ROUND((b.Total-a.Total)/a.Total*100, 2) AS Growth_Pct
  FROM (SELECT * FROM co2 WHERE Year = 2000 AND Total > 1) a
  JOIN (SELECT * FROM co2 WHERE Year = 2021 AND Total > 1) b
    ON a.Country = b.Country
  ORDER BY Growth_Pct DESC
  LIMIT 10
""").show(false)

// ========== 7. 查询6: 化石燃料依赖度 ==========
println("\n===== 2021年化石燃料占排放比例(TOP10排放国) =====")
spark.sql("""
  SELECT Country, Total,
         ROUND((Coal+Oil+Gas)/Total*100, 2) AS Fossil_Pct,
         ROUND(Coal/Total*100, 2) AS Coal_Pct
  FROM co2
  WHERE Year = 2021 AND Total > 100
  ORDER BY Total DESC
  LIMIT 10
""").show(false)

// ========== 8. 保存全球年度趋势 ==========
val globalTrend = spark.sql("""
  SELECT Year, ROUND(SUM(Total), 2) AS Global_Total
  FROM co2 WHERE Year >= 1950
  GROUP BY Year ORDER BY Year
""")
globalTrend.coalesce(1).write
  .option("header", "true")
  .mode("overwrite")
  .csv("output/global_trend")

println("\nSpark SQL 分析完成！")
spark.stop()
