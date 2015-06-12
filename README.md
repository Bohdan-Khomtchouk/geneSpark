# geneXtender

## About

geneXtender is a software program that extends the
boundaries of every gene in a genome by a user-specified distance (in DNA base pairs) for the
purpose of flexibly incorporating cis-regulatory elements (CREs) such as enhancers and
promoters as well as downstream elements that are important to the function of the gene. By
performing a computational expansion of this nature, ChIP-seq reads that would initially not
map strictly to a specific gene can now be mapped to the regulatory regions of the
gene, thereby implicating the gene as a potential candidate, and thereby making the ChIP-seq
experiment more successful. Such an approach becomes particularly important when working with
epigenetic histone modifications that have inherently broad peaks.  geneXtender is designed to
handle the opposite orientations inherent to positive and negative DNA strands.

geneXtender is an ongoing bioinformatics software project fully financially supported by the
United States Department of Defense (DoD) through the National Defense Science and Engineering
Graduate Fellowship (NDSEG) Program. This research was conducted with Government support under
and awarded by DoD, Army Research Office (ARO), National Defense Science and Engineering
Graduate (NDSEG) Fellowship, 32 CFR 168a.

## Installation

### Requirements

* Python >= 2.7
* Pandas >= 0.14.1 (if you use the regular version of geneXtender)
* Spark / PySpark (if you use the Spark version of geneXtender)
  * https://spark.apache.org/downloads.html

## How to run

##### Regular version:
* python src/geneXtender.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
  
##### Spark version:
* /PATH/TO/spark-VERSION/bin/spark-submit --master local[2] src/geneXtender_spark.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
* This is just an example using 2 cores of a local machine. Change local[2] to customize to the number of cores in your machine. To learn how many cores your machine has, type `sysctl -n hw.ncpu` in the Terminal (command-line). For more options, please have a look at [Spark documentation](https://spark.apache.org/docs/latest/index.html)

The Apache Spark version of geneXtender runs approximately 5X faster (relative to geneXtender using only the Pandas and Numpy library of Python) in a local machine with 2 cores.  In a local machine with 8 cores, the Spark version of geneXtender runs 11X faster.  The more cores your system has, the faster Spark geneXtender finishes its run.  

Apache Spark geneXtender is designed to scale up and leverage the power of thousands of computing cores of any HPC environment via the MapReduce framework.