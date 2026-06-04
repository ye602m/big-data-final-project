/*
 * 实验三 任务4：Spark MLlib 构建回归预测模型
 * 预测全球CO2排放量趋势
 * 用法: spark-shell -i task4_spark_mllib.scala
 */
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.ml.feature.{VectorAssembler, StandardScaler}
import org.apache.spark.ml.regression.{LinearRegression, RandomForestRegressor, GBTRegressor}
import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.Pipeline

val spark = SparkSession.builder()
  .appName("CO2 Regression Prediction")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

// ========== 1. 加载数据并聚合全球年度总排放 ==========
val df = spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .csv("GCB2022v27_MtCO2_flat.csv")

// 全球年度总排放
val globalDF = df.filter($"Year" >= 1950)
  .groupBy("Year")
  .agg(
    round(sum("Total"), 2).as("Total"),
    round(sum("Coal"), 2).as("Coal"),
    round(sum("Oil"), 2).as("Oil"),
    round(sum("Gas"), 2).as("Gas"),
    round(sum("Cement"), 2).as("Cement"),
    round(sum("Flaring"), 2).as("Flaring")
  )
  .orderBy("Year")

globalDF.show(10, false)
println(s"全球年度数据: ${globalDF.count()} 行")

// ========== 2. 特征工程 ==========
// 添加滞后特征和前N年趋势
val windowSpec = org.apache.spark.sql.expressions.Window.orderBy("Year")

val featureDF = globalDF
  .withColumn("Year_Norm", $"Year" - 1950)
  .withColumn("Year_Sq", pow($"Year" - 1950, 2))
  .withColumn("Prev_Total", lag("Total", 1, 0).over(windowSpec))
  .withColumn("Prev_Coal", lag("Coal", 1, 0).over(windowSpec))
  .withColumn("Prev_Oil", lag("Oil", 1, 0).over(windowSpec))
  .withColumn("Prev_Gas", lag("Gas", 1, 0).over(windowSpec))
  .withColumn("Coal_Ratio", $"Coal" / $"Total")
  .withColumn("Oil_Ratio", $"Oil" / $"Total")
  .withColumn("Gas_Ratio", $"Gas" / $"Total")

featureDF.show(10, false)

// ========== 3. 组装特征向量 ==========
val assembler = new VectorAssembler()
  .setInputCols(Array(
    "Year_Norm", "Year_Sq",
    "Prev_Total", "Prev_Coal", "Prev_Oil", "Prev_Gas",
    "Coal_Ratio", "Oil_Ratio", "Gas_Ratio"
  ))
  .setOutputCol("raw_features")

// 特征标准化
val scaler = new StandardScaler()
  .setInputCol("raw_features")
  .setOutputCol("features")
  .setWithStd(true)
  .setWithMean(true)

// ========== 4. 划分训练集和测试集 ==========
val Array(trainData, testData) = featureDF.randomSplit(Array(0.8, 0.2), seed=42)

println(s"训练集: ${trainData.count()} 行")
println(s"测试集: ${testData.count()} 行")

// ========== 5. 线性回归模型 ==========
println("\n===== 线性回归模型 =====")
val lr = new LinearRegression()
  .setFeaturesCol("features")
  .setLabelCol("Total")
  .setMaxIter(100)
  .setRegParam(0.1)

val lrPipeline = new Pipeline().setStages(Array(assembler, scaler, lr))
val lrModel = lrPipeline.fit(trainData)

val lrPredictions = lrModel.transform(testData)
lrPredictions.select("Year", "Total", "prediction").show(20, false)

val evaluatorRMSE = new RegressionEvaluator()
  .setLabelCol("Total")
  .setPredictionCol("prediction")
  .setMetricName("rmse")

val evaluatorR2 = new RegressionEvaluator()
  .setLabelCol("Total")
  .setPredictionCol("prediction")
  .setMetricName("r2")

val lrRmse = evaluatorRMSE.evaluate(lrPredictions)
val lrR2 = evaluatorR2.evaluate(lrPredictions)
println(s"线性回归 RMSE: ${"%.4f".format(lrRmse)}")
println(s"线性回归 R2: ${"%.4f".format(lrR2)}")

// ========== 6. 随机森林模型 ==========
println("\n===== 随机森林模型 =====")
val rf = new RandomForestRegressor()
  .setFeaturesCol("features")
  .setLabelCol("Total")
  .setNumTrees(50)
  .setMaxDepth(5)
  .setSeed(42)

val rfPipeline = new Pipeline().setStages(Array(assembler, scaler, rf))
val rfModel = rfPipeline.fit(trainData)

val rfPredictions = rfModel.transform(testData)
rfPredictions.select("Year", "Total", "prediction").show(20, false)

val rfRmse = evaluatorRMSE.evaluate(rfPredictions)
val rfR2 = evaluatorR2.evaluate(rfPredictions)
println(s"随机森林 RMSE: ${"%.4f".format(rfRmse)}")
println(s"随机森林 R2: ${"%.4f".format(rfR2)}")

// ========== 7. GBT模型 ==========
println("\n===== GBT 梯度提升树模型 =====")
val gbt = new GBTRegressor()
  .setFeaturesCol("features")
  .setLabelCol("Total")
  .setMaxIter(50)
  .setMaxDepth(5)
  .setSeed(42)

val gbtPipeline = new Pipeline().setStages(Array(assembler, scaler, gbt))
val gbtModel = gbtPipeline.fit(trainData)

val gbtPredictions = gbtModel.transform(testData)
gbtPredictions.select("Year", "Total", "prediction").show(20, false)

val gbtRmse = evaluatorRMSE.evaluate(gbtPredictions)
val gbtR2 = evaluatorR2.evaluate(gbtPredictions)
println(s"GBT RMSE: ${"%.4f".format(gbtRmse)}")
println(s"GBT R2: ${"%.4f".format(gbtR2)}")

// ========== 8. 模型对比 ==========
println("\n===== 模型性能对比 =====")
println(s"| 模型       | RMSE        | R2          |")
println(s"|------------|-------------|-------------|")
println(s"| 线性回归   | ${"%.4f".format(lrRmse)}     | ${"%.4f".format(lrR2)}     |")
println(s"| 随机森林   | ${"%.4f".format(rfRmse)}     | ${"%.4f".format(rfR2)}     |")
println(s"| GBT        | ${"%.4f".format(gbtRmse)}     | ${"%.4f".format(gbtR2)}     |")

// ========== 9. 预测未来5年排放 ==========
println("\n===== 预测2022-2026年全球CO2排放 =====")
val lastYear = featureDF.orderBy(desc("Year")).limit(1).collect()(0)
var prevTotal = lastYear.getAs[Double]("Total")
var prevCoal = lastYear.getAs[Double]("Coal")
var prevOil = lastYear.getAs[Double]("Oil")
var prevGas = lastYear.getAs[Double]("Gas")

val futureData = (2022 to 2026).map { year =>
  val yn = (year - 1950).toDouble
  val cr = prevCoal / prevTotal
  val or = prevOil / prevTotal
  val gr = prevGas / prevTotal
  val row = (year, yn, yn*yn, prevTotal, prevCoal, prevOil, prevGas, cr, or, gr)
  // 更新prev值（用预测值作为下一年输入）
  row
}

val futureDF = futureData.toDF("Year", "Year_Norm", "Year_Sq",
  "Prev_Total", "Prev_Coal", "Prev_Oil", "Prev_Gas",
  "Coal_Ratio", "Oil_Ratio", "Gas_Ratio")

val futurePred = gbtModel.transform(futureDF)
println("全球CO2排放预测 (MtCO2):")
futurePred.select($"Year", round($"prediction", 2).as("Predicted_Total")).show()

spark.stop()
