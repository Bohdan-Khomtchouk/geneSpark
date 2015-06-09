# Copyright (C) 2015 Bohdan Khomtchouk and Mohamed Sordo

# Before running this program, install Spark on your machine: https://spark.apache.org/downloads.html

# Usage: /path/to/spark-1.3.1/bin/spark-submit --master local[2] geneXtender_spark.py ../Input/NAME_OF_FILE.gtf 

# Apache Spark geneXtender runs approximately 5X faster (relative to geneXtender with only big data Pandas and Numpy libraries) in a local machine with 2 cores.

# geneXtender is a software program written in the Python programming language
# that extends the boundaries of every gene in a genome by a user-specified
# distance (in DNA base pairs) for the purpose of flexibly incorporating cis-
# regulatory elements (CREs) such as enhancers and promoters as well as
# downstream elements that are important to the function of the gene.
# By performing a computational expansion of this nature, ChIP-seq reads that
# would initially not map strictly to a specific gene can now be mapped to the
# regulatory regions of the gene, thereby implicating the gene as a potential
# candidate, and thereby making the ChIP-seq experiment more successful.
# Such an approach becomes particularly important when working with epigenetic
# histone modifications that have inherently broad peaks.
# geneXtender is designed to handle the opposite orientations inherent to
# positive and negative DNA strands.

# geneXtender is an ongoing bioinformatics software project fully financially
# supported by the United States Department of Defense (DoD) through the
# National Defense Science and Engineering Graduate Fellowship Program.
# This research was conducted with Government support under and awarded
# by DoD, Army Research Office (ARO), National Defense Science and
# Engineering Graduate (NDSEG) Fellowship, 32 CFR 168a.


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -------------------------------------------------------------------------------------------

import os
import argparse

from functools import partial
from fileinput import input
from glob import glob
from tempfile import NamedTemporaryFile

from pyspark import SparkContext


def parse_line(line):
    '''
    Parses a line from the GTF file

    Parameters
    ----------

    line : List
        a line of the GTF file as a list of elements

    Returns
    -------

    a tuple w/ format: (Gene_id, (Chr, Start, End, Strand))
    '''
    start = int(line[3])
    end = int(line[4])
    gene_name = None
    for col in line[8].strip().split(";"):
        col = col.split()
        if len(col) > 0:
            if col[0] == "gene_name":
                gene_name = col[1][1:-1]
            if col[0] == "gene_id":
                gene_id = col[1][1:-1]
    if gene_name is not None:
        gene_id += "_" + gene_name
    return (gene_id, (line[0], start, end, line[6]))


def min_and_max(geneA_val, geneB_val):
    '''
    Computes the minimum start and maximum end for each exon gene

    Parameters
    ----------

    geneA_val : Tuple
        a tuple w/ format: (Chr, Start, End, Strand)

    geneB_val : Tuple
        a tuple w/ format: (Chr, Start, End, Strand)

    Returns
    -------

    a tuple w/ format: (Chr, Start, End, Strand)
    '''
    return (geneA_val[0],
            min(geneA_val[1], geneB_val[1]),
            max(geneA_val[2], geneB_val[2]),
            geneA_val[3])


def geneXtension(gene, upstream_bp, downstream_bp):
    '''
    Performs geneXtender extensions of an exon

    Parameters
    ----------

    gene : Tuple
        a tuple w/ format: (Gene_id, (Chr, Start, End, Strand))

    upstream_bp : Spark broadcast variable, int (default=2000)
        Extend upstream of first exon of each gene

    dowstream_bp : Spark broadcast variable, int (default=500).
        Extend dowstream of last exon of each gene

    Returns
    -------

    a tuple w/ format: (Chr, Start, End, Gene_id)
    '''
    if gene[1][-1] == '+':
        return "{}\t{}\t{}\t{}".format(gene[1][0],
                                       gene[1][1]-upstream_bp.value,
                                       gene[1][2]+downstream_bp.value,
                                       gene[0])
    else:
        return "{}\t{}\t{}\t{}".format(gene[1][0],
                                       gene[1][1]-downstream_bp.value,
                                       gene[1][2]+upstream_bp.value,
                                       gene[0])


def geneXtender(input_filename, output_filename,
                upstream_bp=2000, downstream_bp=500):
    '''
    Performs geneXtender extensions given a `input_filename`
    and stores the output in `output_filename`

    Parameters
    ----------

    input_filename : string
        path to the GTF file

    output_filename : string
        path to the output extended GTF file

    upstream_bp : int (default=2000):
        Extend upstream of first exon of each gene

    dowstream_bp : int (default=500):
        Extend dowstream of last exon of each gene
    '''
    # create spark context
    sc = SparkContext(appName="geneXtender")

    # set up broadcasting variables
    upstream_bp_var = sc.broadcast(upstream_bp)
    downstream_bp_var = sc.broadcast(downstream_bp)

    # create temporary folder where to store the output chunks
    tempFile = NamedTemporaryFile(delete=True)
    tempFile.close()

    # define the spark pipeline
    (sc.textFile(input_filename)
     .map(lambda x: x.split('\t'))
     .filter(lambda x: x[2] == 'exon')
     .map(parse_line)
     .reduceByKey(min_and_max)
     .sortByKey()
     .map(partial(geneXtension,
                  upstream_bp=upstream_bp_var,
                  downstream_bp=downstream_bp_var))
     .saveAsTextFile(tempFile.name))

    # merge output chunks to single output_filename
    with open(output_filename, 'w') as fw:
        for line in input(sorted(glob(tempFile.name + "/part-000*"))):
            fw.write(line)

    sc.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compute gene extensions (in DNA base pairs)\
                    from first and last exon of every gene in a GTF file')
    parser.add_argument('input_file', metavar='INPUT_FILE',
                        help='GTF input filename')
    parser.add_argument('-o', '--output-file',
                        help='Extended GTF output filename')
    parser.add_argument('-u', '--upstream-base-pairs', type=int,
                        default=2000, help='Extend upstream of \
                                first exon of each gene')
    parser.add_argument('-d', '--downstream-base-pairs', type=int,
                        default=500, help='Extend downstream of \
                                last exon of each gene')
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    if output_file is None:
        filename, extension = os.path.splitext(input_file)
        output_file = filename + "_output" + extension

    geneXtender(input_file, output_file,
                args.upstream_base_pairs, args.downstream_base_pairs)
