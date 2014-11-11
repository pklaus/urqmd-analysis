#!/usr/bin/env python

""" UrQMD File Reader """

import argparse
import pickle
import logging
import pandas as pd
import numpy as np


class TextCleaner(object):
    def __init__(self, in_file):
        self.in_file = in_file
        self.new_event = False
        self.event_id = 0
        #f = io.StringIO("some initial text data")

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            # raises StopIteration when reached EOF
            line = next(self.in_file)
            parts = line.split()
            if not len(parts): continue
            if parts[0] == 'event#': self.event_id = int(parts[1])
            if len(parts) == 15:
                return str(self.event_id) + ' ' + line

    def read(self, bytes=-1):
        return self.next()

class F_Reader(object):

    def __init__(self, data_file):
        self.data_file = data_file

    def get_events(self):
        pass


class F14_Reader(F_Reader):

    def get_events(self):
        new_event = False
        event = None
        first_line = next(self.data_file)
        #assert(first_line.startswith('UQMD'))
        for i in range(18):
            next(self.data_file)
        names = ['r0', 'rx', 'ry', 'rz', 'p0', 'px', 'py', 'pz', 'm', 'ityp', '2i3', 'chg', 'lcl#', 'ncl', 'or']
        df = pd.read_table(self.data_file, names=names, delim_whitespace=True)
        df = df[df['or'].notnull()]
        df = df.convert_objects(convert_numeric=True)
        df.dropna(how='any', inplace=True)
        df['ityp'] = df['ityp'].astype(np.int64)
        df['2i3'] = df['2i3'].astype(np.int64)
        df['chg'] = df['chg'].astype(np.int64)
        df['lcl#'] = df['lcl#'].astype(np.int64)
        df['ncl'] = df['ncl'].astype(np.int64)
        df['or'] = df['or'].astype(np.int64)
        return df


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r'), help="Must be of type .f14")
    parser.add_argument('--output_file', metavar='OUT_FILE')
    args = parser.parse_args()

    #tc = TextCleaner(args.urqmd_file)
    #F14_Reader(tc).get_events()
    df = F14_Reader(args.urqmd_file).get_events()
    #import pdb; pdb.set_trace()

    if args.output_file:
        df.to_pickle(args.output_file)

if __name__ == "__main__":
    main()

