#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 - 2012, A. Murat Eren
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import sys
import operator
from scipy import log2 as log
import numpy as np

sys.path.append('lib')
import fastalib as u

COLORS = {'A': 'red',
          'T': 'blue', 
          'C': 'green', 
          'G': 'purple', 
          'N': 'white', 
          '-': '#CACACA'}

def entropy(l):
    P = lambda n: (len([x for x in l if x.upper() == n.upper()]) * 1.0 / len(l)) + 0.0000000000000000001
    return -(sum([P(N) * log(P(N)) for N in ['A', 'T', 'C', 'G', '-']]))


def get_consensus_sequence(alignment_file):
    consensus_sequence = ''
    fasta = u.SequenceSource(alignment_file)
    
    fasta.next()
    alignment_length = len(fasta.seq)
    
    consensus_dict = {}
    
    for i in range(0, alignment_length):
        consensus_dict[i] = {'A': 0, 'T': 0, 'C': 0, 'G': 0, '-': 0}
    
    fasta.reset()
    
    while fasta.next():
        seq = fasta.seq.upper()
        for pos in range(0, alignment_length):
            if seq[pos] in ['A', 'T', 'C', 'G', '-']:
                consensus_dict[pos][seq[pos]] += 1
    
    for pos in range(0, alignment_length):
        consensus_sequence += sorted(consensus_dict[pos].iteritems(), key=operator.itemgetter(1), reverse=True)[0][0]
    
    return consensus_sequence


def entropy_analysis(alignment, output_file = None, verbose = True):
    lines = [l for l in open(alignment) if not l.startswith('>')]
    
    entropy_tpls = [] 
    
    for i in range(0, len(lines[0])):
        if verbose:
            sys.stderr.write('\rPerforming entropy analysis: %d%%' % (int((i + 1) * 100.0 / len(lines[0]))))
            sys.stderr.flush()
    
        if set([x[i] for x in lines]) == set(['.']) or set([x[i] for x in lines]) == set(['-']):
            entropy_tpls.append((i, 0.0),)
        else:
            column = "".join([x[i] for x in lines])
            e = entropy(column)
            if e < 0.00001:
                entropy_tpls.append((i, 0.0),)
            else:
                entropy_tpls.append((i, e),)
    
    if verbose:
        print
   
    if output_file:
        entropy_output = open(output_file, 'w')
        for _component, _entropy in sorted(entropy_tpls, key=operator.itemgetter(1), reverse=True):
            entropy_output.write('%d\t%.4f\n' % (_component, _entropy))
        entropy_output.close()
    
    return [x[1] for x in entropy_tpls]


def visualize_distribution(alignment, entropy_values, output_file, display = True):
    import matplotlib.pyplot as plt
    import numpy as np

    consensus_sequence = get_consensus_sequence(alignment)
    fig = plt.figure(figsize = (len(consensus_sequence) / 20, 10))

    plt.rcParams.update({'axes.linewidth' : 0.1})
    plt.rc('grid', color='0.70', linestyle='-', linewidth=0.1)
    plt.grid(True)

    plt.subplots_adjust(hspace = 0, wspace = 0, right = 0.995, left = 0.050, top = 0.92, bottom = 0.10)

    ax = fig.add_subplot(111)

    y_maximum = max(entropy_values) + (max(entropy_values) / 10.0)
    for i in range(0, len(consensus_sequence)):
        for y in range(int(y_maximum * 100), 0, -3):
            plt.text(i, y / 100.0, consensus_sequence[i],  alpha = y / (y_maximum * 100.0),\
                                fontsize = 5, color = COLORS[consensus_sequence[i]])

    ind = np.arange(len(entropy_values))
    ax.bar(ind, entropy_values, color = 'black', lw = 0.5)
    ax.set_xlim([0, len(consensus_sequence)])
    ax.set_ylim([0, y_maximum])
    plt.xlabel('Nucleotide Position')
    plt.ylabel('Shannon Entropy')
    plt.savefig(output_file)

    if display:
        plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert FastQ to FASTA')
    parser.add_argument('alignment', metavar = 'ALIGNMENT', help = 'Alignment file\
                         that contains all samples and sequences in FASTA format')

    alignment = parser.parse_args().alignment
    entropy_values = entropy_analysis(alignment, output_file = alignment + '-ENTROPY.txt')
    visualize_distribution(alignment, entropy_values, output_file = alignment + '-ENTROPY.png')

