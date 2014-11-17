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

    def __init__(self, data_file, add_event_columns=False, renumber_event_ids=True):
        self.data_file = data_file
        self.add_event_columns = add_event_columns
        self.renumber_event_ids = renumber_event_ids

    def get_dataframe(self):
        return pd.concat(list(self.iter_dataframes()), ignore_index=True)

    def iter_dataframes(self, chunksize=100000):
        curr_event_id = 0
        curr_impact = 0.0
        names = ['r0', 'rx', 'ry', 'rz', 'p0', 'px', 'py', 'pz', 'm', 'ityp', '2i3', 'chg', 'lcl#', 'ncl', 'or']
        for df in pd.read_table(self.data_file, names=names, delim_whitespace=True, chunksize=chunksize):
            logging.info('Read {} lines from {}.'.format(len(df), self.data_file.name))
            # -- add additional event_* columns
            if self.add_event_columns:
                #total_event_no = len(df[df.r0 == 'UQMD'])
                df['event_id'] = curr_event_id
                df['event_ip'] = curr_impact
                event_start = None
                for idx in df[df.r0 == 'UQMD'].index:
                    # remember the index where the event started
                    if event_start == None:
                        event_start = idx
                        continue
                    curr_impact = df.loc[event_start+3, 'rx']
                    # set curr_event_id
                    if self.renumber_event_ids:
                        curr_event_id += 1
                    else:
                        curr_event_id = df.loc[event_start+5, 'rx']
                    # update event_id and event_ip for the event from event_start (the current event) to idx (the new event)
                    df.loc[event_start:idx, 'event_ip'] = curr_impact
                    df.loc[event_start:idx, 'event_id'] = curr_event_id
                    event_start = idx
                # update particles belonging to the last event
                curr_impact = df.loc[event_start+3, 'rx']
                if self.renumber_event_ids:
                    curr_event_id += 1
                else:
                    curr_event_id = df.loc[event_start + 5, 'rx']
                df.loc[event_start:, 'event_id'] = curr_event_id
                df.loc[event_start:, 'event_ip'] = curr_impact
                # -- end add event_* columns
            df = df[df['or'].notnull()]
            df = df.convert_objects(convert_numeric=True)
            df.dropna(how='any', inplace=True)
            if self.add_event_columns:
                df['event_id'] = df['event_id'].astype(np.uint32)
                df['event_ip'] = df['event_ip'].astype(np.float32)
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


class HDF_Worker(multiprocessing.Process):

    def __init__(self, h5_path, queue):
        self.h5_path = h5_path
        self.queue = queue
        self.block_period = .01
        super(HDF_Worker, self).__init__()

    def run(self):
        self.hdf = pd.HDFStore(self.h5_path)
        original_warnings = list(warnings.filters)
        warnings.simplefilter('ignore', tables.NaturalNameWarning)
        while True:
            try:
                # get queue content
                qc = self.queue.get(timeout=self.block_period)
            except queue.Empty:
                continue
            if type(qc) == str and qc == 'EOF': break
            self.hdf.append('particles', qc, data_columns=True, index=False)
        self.hdf.close()
        warnings.filters = original_warnings


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r', encoding='ascii'), help="Must be of type .f14")
    parser.add_argument('out_file', metavar='OUT_FILE', help='The HDF5 (.h5) file to store the information in')
    parser.add_argument('--no-event-columns', action='store_true', help="Don NOT include columns for the event number and event impact parameter.")
    parser.add_argument('--chunksize', type=int, default = 100000, help='The number of lines to read in one go.')
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help="How verbose should the output be")
    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity, format='%(asctime)s.%(msecs)d %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    queue = multiprocessing.Queue()
    worker = HDF_Worker(args.out_file, queue)
    worker.start()
    for df in F14_Reader(args.urqmd_file, not args.no_event_columns).iter_dataframes(chunksize = args.chunksize):
        logging.debug("DataFrame ready to be written to file.")
        if not queue.empty(): time.sleep(0.05)
        logging.debug("Queue empty. DataFrame will be put into write queue now.")
        queue.put(df.copy())
    queue.put('EOF')
    queue.close()
    queue.join_thread()
    worker.join()

if __name__ == "__main__":
    main()

