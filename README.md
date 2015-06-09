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
* Spark / PySpark (if you use the spark version of geneXtender)
  * https://spark.apache.org/downloads.html
  
###ÊHow to run

* Regular version:
  * python src/geneXtender.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
  
* Spark version:
  * /PATH/TO/spark-VERSION/bin/spark-submit --master local[2] src/geneXtender_spark.py [-o OUTPUT_FILE] [-u UPSTREAM_BASE_PAIRS] [-d DOWNSTREAM_BASE_PAIRS] INPUT_FILE
  * This is just an example using . For more options, please have a look at [Spark documentation](https://spark.apache.org/docs/latest/index.html)

The Apache Spark version geneXtender runs approximately 5X faster (relative to geneXtender with only big data Pandas and Numpy libraries) in a local machine with 2 cores.
