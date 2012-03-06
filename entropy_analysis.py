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

import os
import sys
import operator
from scipy import log2 as log
import numpy as np

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import fastalib as u

class EntropyError(Exception):
    def __init__(self, e = None):
        Exception.__init__(self)
        self.e = e
        return
    def __str__(self):
        return 'Error: %s' % self.e

COLORS = {'A': 'red',
          'T': 'blue', 
          'C': 'green', 
          'G': 'purple', 
          'N': 'white', 
          '-': '#CACACA'}

def entropy(l):
    P = lambda n: (len([x for x in l if x.upper() == n.upper()]) * 1.0 / len(l)) + 0.0000000000000000001
    return -(sum([P(N) * log(P(N)) for N in ['A', 'T', 'C', 'G', '-']]))


def entropy_analysis(alignment_path, output_file = None, verbose = True, uniqued = False, freq_from_defline = None):
    if freq_from_defline == None:
        freq_from_defline = lambda x: int([t.split(':')[1] for t in x.split('|') if t.startswith('freq')][0])

    lines = []
    
    alignment = u.SequenceSource(alignment_path)
    if not uniqued:
        while alignment.next():
            lines.append(alignment.seq)
    else:
        while alignment.next():
            frequency = freq_from_defline(alignment.id)
            for i in range(0, frequency):
                lines.append(alignment.seq)

    alignment.close()

    if len(list(set([len(line) for line in lines]))) != 1:
        raise EntropyError, "Not all sequences have the same length."

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

def get_unique_sequences(alignment, limit = 10):
    unique_sequences = []

    fasta = u.SequenceSource(alignment, unique = True)

    while fasta.next() and fasta.pos < limit:
        unique_sequences.append(fasta.seq)

    return unique_sequences


def visualize_distribution(alignment, entropy_values, output_file, display = True):
    import matplotlib.pyplot as plt
    import numpy as np

    y_maximum = max(entropy_values) + (max(entropy_values) / 10.0)
    number_of_uniques_to_show = int(y_maximum * 100)
    unique_sequences = get_unique_sequences(alignment, limit = number_of_uniques_to_show)

    fig = plt.figure(figsize = (len(unique_sequences[0]) / 20, 10))

    plt.rcParams.update({'axes.linewidth' : 0.1})
    plt.rc('grid', color='0.70', linestyle='-', linewidth=0.1)
    plt.grid(True)

    plt.subplots_adjust(hspace = 0, wspace = 0, right = 0.995, left = 0.050, top = 0.92, bottom = 0.10)

    ax = fig.add_subplot(111)

    current = 0
    for y in range(number_of_uniques_to_show, 0, -3):
        unique_sequence = unique_sequences[current]
        for i in range(0, len(unique_sequence)):
            plt.text(i, y / 100.0, unique_sequence[i],  \
                                fontsize = 5, color = COLORS[unique_sequence[i]])
        current += 1
        if current + 1 > len(unique_sequences):
            break

    ind = np.arange(len(entropy_values))
    ax.bar(ind, entropy_values, color = 'black', lw = 0.5)
    ax.set_xlim([0, len(unique_sequences[0])])
    ax.set_ylim([0, y_maximum])
    plt.xlabel('Nucleotide Position')
    plt.ylabel('Shannon Entropy')
    plt.savefig(output_file)

    if display:
        plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Entropy Analysis')
    parser.add_argument('alignment', metavar = 'ALIGNMENT', help = 'Alignment file\
                         that contains all datasets and sequences in FASTA format')

    alignment = parser.parse_args().alignment
    entropy_values = entropy_analysis(alignment, output_file = alignment + '-ENTROPY.txt')
    visualize_distribution(alignment, entropy_values, output_file = alignment + '-ENTROPY.png')

