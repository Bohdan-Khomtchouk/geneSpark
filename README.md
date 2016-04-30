# geneSpark

## Installation

### Requirements

* Python >= 2.7
* Pandas >= 0.14.1
* Spark / PySpark
  * https://spark.apache.org/downloads.html

## How to run

##### Regular version:
* python src/geneSpark.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
  
##### Spark version:
* /PATH/TO/spark-VERSION/bin/spark-submit --master local[2] src/geneSpark_spark.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
* This is just an example using 2 cores of a local machine. Change local[2] to customize to the number of cores in your machine. To learn how many cores your machine has, type `sysctl -n hw.ncpu` in the Terminal (command-line). For more options, please have a look at [Spark documentation](https://spark.apache.org/docs/latest/index.html)

The Apache Spark version of geneSpark runs approximately 5X faster (relative to geneSpark using only the Pandas and Numpy library of Python) in a local machine with 2 cores.  In a local machine with 8 cores, the Spark version of geneSpark runs 11X faster.  The more cores your system has, the faster Spark geneSpark finishes its run.  

Apache Spark geneSpark is designed to scale up and leverage the power of thousands of computing cores of any HPC environment via the MapReduce framework.
