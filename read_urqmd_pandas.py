#!/usr/bin/env python

""" UrQMD File Reader """

import argparse
import pickle
import logging
import pandas as pd
import numpy as np


class F14_Reader(object):

    def __init__(self, data_file, add_event_id_column=False):
        self.data_file = data_file
        self.add_event_id_column = add_event_id_column

    def get_dataframe(self):
        event = None
        names = ['r0', 'rx', 'ry', 'rz', 'p0', 'px', 'py', 'pz', 'm', 'ityp', '2i3', 'chg', 'lcl#', 'ncl', 'or']
        df = pd.read_table(self.data_file, names=names, delim_whitespace=True)
        if self.add_event_id_column:
            #total_event_no = len(df[df.r0 == 'UQMD'])
            df['event_id'] = 0
            event_start = None
            for idx in df[df.r0 == 'event#'].index:
                if event_start == None:
                    event_start = idx
                    continue
                df.loc[event_start:idx, 'event_id'] = df.loc[event_start, 'rx']
                event_start = idx
            df.loc[event_start:, 'event_id'] = df.loc[event_start, 'rx']
        df = df[df['or'].notnull()]
        df = df.convert_objects(convert_numeric=True)
        df.dropna(how='any', inplace=True)
        if self.add_event_id_column:
            df['event_id'] = df['event_id'].astype(np.int64)
        df['ityp'] = df['ityp'].astype(np.int64)
        df['2i3'] = df['2i3'].astype(np.int64)
        df['chg'] = df['chg'].astype(np.int64)
        df['lcl#'] = df['lcl#'].astype(np.int64)
        df['ncl'] = df['ncl'].astype(np.int64)
        df['or'] = df['or'].astype(np.int64)
        return df


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r', encoding='ascii'), help="Must be of type .f14")
    parser.add_argument('--output-file', metavar='OUT_FILE', help='The .pkl file to store the information in')
    parser.add_argument('--no-event-id-column', action='store_false', help='Include a column event_id in the pandas DataFrame.')
    args = parser.parse_args()

    df = F14_Reader(args.urqmd_file, args.no_event_id_column).get_dataframe()

    if args.output_file:
        df.to_pickle(args.output_file)

if __name__ == "__main__":
    main()

