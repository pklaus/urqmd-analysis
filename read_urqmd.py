#!/usr/bin/env python

""" UrQMD File Reader """

import argparse
import pickle
import logging


class F_Reader(object):

    def __init__(self, data_file):
        self.data_file = data_file

    def get_events(self):
        pass


class F14_Reader(F_Reader):

    def get_events(self):
        new_event = False
        event = None
        for line in self.data_file:
            parts = line.split()
            if not len(parts): continue
            if parts[0] == 'UQMD': new_event = True
            if new_event:
                if event: yield event
                event = dict()
                event['particle_properties'] = []
                new_event = False
            if parts[0] == 'event#': event['id'] = int(parts[1])
            if len(parts) == 15:
                event['particle_properties'].append(parts)
        if event: yield event


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r'), help="Must be of type .f14")
    args = parser.parse_args()

    for event in F14_Reader(args.urqmd_file).get_events():
        print("Event #{} containing {} particles".format(event['id'], len(event['particle_properties'])))


if __name__ == "__main__":
    main()

