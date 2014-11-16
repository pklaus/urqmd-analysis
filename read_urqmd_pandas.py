#!/usr/bin/env python

""" UrQMD File Reader """

import pandas as pd
import numpy as np
import tables
import argparse
import logging
import warnings
import multiprocessing
import time
import queue


class F14_Reader(object):

    def __init__(self, data_file, add_event_id_column=False):
        self.data_file = data_file
        self.add_event_id_column = add_event_id_column

    def get_dataframe(self):
        return pd.concat(list(self.iter_dataframes()), ignore_index=True)

    def iter_dataframes(self, chunksize=100000):
        last_event_id = 0
        names = ['r0', 'rx', 'ry', 'rz', 'p0', 'px', 'py', 'pz', 'm', 'ityp', '2i3', 'chg', 'lcl#', 'ncl', 'or']
        for df in pd.read_table(self.data_file, names=names, delim_whitespace=True, chunksize=chunksize):
            logging.info('Read in {} lines.'.format(len(df)))
            if self.add_event_id_column:
                #total_event_no = len(df[df.r0 == 'UQMD'])
                df['event_id'] = last_event_id
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
                df['event_id'] = df['event_id'].astype(np.int32)
            df['r0'] = df['r0'].astype(np.float32)
            df['rx'] = df['rx'].astype(np.float32)
            df['ry'] = df['ry'].astype(np.float32)
            df['rz'] = df['rz'].astype(np.float32)
            df['p0'] = df['p0'].astype(np.float32)
            df['px'] = df['px'].astype(np.float32)
            df['py'] = df['py'].astype(np.float32)
            df['pz'] = df['pz'].astype(np.float32)
            df['m'] = df['m'].astype(np.float32)
            df['ityp'] = df['ityp'].astype(np.int16)
            df['2i3'] = df['2i3'].astype(np.int8)
            df['chg'] = df['chg'].astype(np.int8)
            df['lcl#'] = df['lcl#'].astype(np.uint32)
            df['ncl'] = df['ncl'].astype(np.uint16)
            df['or'] = df['or'].astype(np.uint16)
            yield df


class Worker(multiprocessing.Process):

    def __init__(self, q, f):
        self.q = q # queue
        self.f = f # function
        super(Worker, self).__init__()

    def run(self):
        while True:
            try:
                # get queue content
                qc = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            if type(qc) == str and qc == 'EOF': break
            self.f(qc) # call function on queue content


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r', encoding='ascii'), help="Must be of type .f14")
    parser.add_argument('out_file', metavar='OUT_FILE', help='The HDF5 (.h5) file to store the information in')
    parser.add_argument('--no-event-id-column', action='store_false', help='Include a column event_id in the pandas DataFrame.')
    parser.add_argument('--chunksize', type=int, default = 1000000, help='The number of lines to read in one go.')
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help="How verbose should the output be")
    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity)
    pool = multiprocessing.Pool()

    hdf = pd.HDFStore(args.out_file)
    original_warnings = list(warnings.filters)
    warnings.simplefilter('ignore', tables.NaturalNameWarning)

    queue = multiprocessing.Queue()
    append_func = lambda df: hdf.append('particles', df, format='table', data_columns=True)
    worker = Worker(queue, append_func)
    worker.start()
    for df in F14_Reader(args.urqmd_file, args.no_event_id_column).iter_dataframes(chunksize = args.chunksize):
        if not queue.empty(): time.sleep(0.05)
        queue.put(df)
    queue.put('EOF')
    queue.close()
    queue.join_thread()
    worker.join()

    warnings.filters = original_warnings
    hdf.close()

if __name__ == "__main__":
    main()

