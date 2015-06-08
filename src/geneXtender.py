#!/usr/bin/env python
# Copyright (C) 2015 Bohdan Khomtchouk and Mohamed Sordo

# geneXtender is a software program written in the Python programming language that extends the
# boundaries of every gene in a genome by a user-specified distance (in DNA base pairs) for the
# purpose of flexibly incorporating cis-regulatory elements (CREs) such as enhancers and
# promoters as well as downstream elements that are important to the function of the gene. By
# performing a computational expansion of this nature, ChIP-seq reads that would initially not
# map strictly to a specific gene can now be mapped to the regulatory regions of the
# gene, thereby implicating the gene as a potential candidate, and thereby making the ChIP-seq
# experiment more successful. Such an approach becomes particularly important when working with
# epigenetic histone modifications that have inherently broad peaks.  geneXtender is designed to
# handle the opposite orientations inherent to positive and negative DNA strands.

# geneXtender is an ongoing bioinformatics software project fully financially supported by the
# United States Department of Defense (DoD) through the National Defense Science and Engineering
# Graduate Fellowship (NDSEG) Program. This research was conducted with Government support under
# and awarded by DoD, Army Research Office (ARO), National Defense Science and Engineering
# Graduate (NDSEG) Fellowship, 32 CFR 168a.


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
import sys
import argparse
import pandas as pd
import numpy as np

#@profile
def load_dataset(input_filename):
    '''
    Parsing a GTF file

    Parameters
    ----------

    input_filename : string
        path to the GTF file

    Returns
    -------
    df : pandas.DataFrame
        A pandas DataFrame
    '''
    dataset = []
    i = 0
    with open(input_filename) as f:
        for line in f:
            line = line.strip().split("\t")
            chro = line[0]
            feature_type = line[2]
            start = int(line[3])
            end = int(line[4])
            strand = line[6]
            gene_col = line[8]
            if feature_type == "exon":
                gene_name = None
                gene_id = None
                for col in gene_col.strip().split(";"):
                    col = col.split()
                    if len(col) > 0:
                        if col[0] == "gene_name":
                            gene_name = col[1][1:-1]
                        if col[0] == "gene_id":
                            gene_id = col[1][1:-1]
                gene = gene_id
                if gene_name is not None:
                    gene += "_" + gene_name
                dataset.append((chro, start, end, strand, gene))
                #df.append([chro, start, end, strand, gene])
            i += 1
            if i % 100000 == 0:
                print i, "lines processed"
    df = pd.DataFrame(data=dataset,
                      columns=['Chr', 'Start', 'End', 'Strand', 'Gene'])
    return df


#@profile
def geneXtender(df, upstrean_bp=2000, downstream_bp=500):
    '''
    Performe geneXtender extensions

    Parameters
    ----------

    df : pandas.DataFrame
        A pandas DataFrame

    Returns
    -------
    gtf : List of Tuples
        extended GTF
    '''

    # get the indexes of the minimum value for each gene
    minValues = df.loc[(df.groupby('Gene'))['Start'].idxmin()]
    # substract/add the coordinates of the minimum value by 2000
    for i in minValues.index:
        if minValues.ix[i, 'Strand'] == '+':
            minValues.ix[i, 'Start'] -= upstrean_bp
        else:
            minValues.ix[i, 'Start'] -= downstream_bp

    # get the indexes of the maximum value for each gene
    maxValues = df.loc[(df.groupby('Gene'))['End'].idxmax()]
    # add/subtract the coordinates of the maximum value by 500
    for i in maxValues.index:
        if maxValues.ix[i, 'Strand'] == '+':
            maxValues.ix[i, 'End'] += downstream_bp
        else:
            maxValues.ix[i, 'End'] += upstrean_bp

    # re-index the dataframes by gene name
    minValues = minValues.set_index('Gene')
    maxValues = maxValues.set_index('Gene')

    # select extended GTFs
    gtf = []
    for gene in minValues.index:
        ming = minValues.loc[gene]
        maxg = maxValues.loc[gene]
        gtf.append((ming.Chr, ming.Start, maxg.End, gene))

    return gtf

#@profile
def write_output(gtf, output_filename):
    '''
    Write extended GTF to output

    Parameters
    ----------

    gtf : List of Tuples
        extended GTF

    output_filename : string
        path to the output extended GTF file
    '''
    with open(output_filename, "w") as fw:
        for line in gtf:
            fw.write("%s\t%s\t%s\t%s\n" % line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compute gene extensions (in DNA base pairs)\
                    from first and last exon of every gene in a GTF file')
    parser.add_argument('input_file', metavar='INPUT_FILE',
                        help='GTF input filename')
    parser.add_argument('-o', '--output-file',
                        help='Extended GTF output filename')
    parser.add_argument('-u', '--upstream-base-pairs', type=int,
                        default=2000, help='Extend upstream of first exon of each gene')
    parser.add_argument('-d', '--downstream-base-pairs', type=int,
                        default=500, help='Extend downstream of last exon of each gene')
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    if output_file is None:
        filename, extension = os.path.splitext(input_file)
        output_file = filename + "_output" + extension

    df = load_dataset(input_file)
    gtf = geneXtender(df, args.upstream_base_pairs, args.downstream_base_pairs)
    write_output(gtf, output_file)
