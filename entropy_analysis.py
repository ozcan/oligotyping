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

from utils import parsers
from lib.entropy import entropy_analysis
from utils.utils import process_command_line_args_for_quality_files
from visualization.entropy_distribution_bar import entropy_distribution_bar

if __name__ == '__main__':
    parser = parsers.entropy()
    args = parser.parse_args()

    # process qual scores if provided
    qual_stats_dict = process_command_line_args_for_quality_files(args, _return = 'qual_stats_dict')       

    output_text_path = args.alignment + '%s-ENTROPY' % ('-WEIGHTED' if args.weighted else '')
    output_img_path = args.alignment + '%s-ENTROPY.png' % ('-WEIGHTED' if args.weighted else '')

    entropy_values = entropy_analysis(args.alignment,
                                      output_file = output_text_path,
                                      weighted = args.weighted,
                                      qual_stats_dict = qual_stats_dict)

    entropy_distribution_bar(args.alignment,
                             entropy_values,
                             output_file = output_img_path,
                             quick = args.quick,
                             no_display = args.no_display,
                             qual_stats_dict = qual_stats_dict,
                             weighted = args.weighted)

