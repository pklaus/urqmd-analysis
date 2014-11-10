#!/usr/bin/env python

import argparse
import pickle
import logging
import pandas as pd

class Event(object):
    def __init__(self):
        self._particles = []
    def add_particle(self, particle):
        self._particles.append(particle)
    @property
    def particles(self):
        return self._particles

class Particle(object):
    pass

def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r'), help="Must be of type .f14")
    parser.add_argument('--output_file', metavar='OUT_FILE', type=argparse.FileType('wb'))
    args = parser.parse_args()

    f = args.urqmd_file

    new_event = False
    output = dict()
    events = []
    pd_events = pd.DataFrame()
    for line in f:
        parts = line.split()
        if not len(parts): continue
        if parts[0] == 'UQMD': new_event = True
        if new_event:
            event = Event()
            events.append(event)
            new_event = False
        if len(parts) == 15:
            logging.debug(parts)
            particle = Particle()
            particle.id = int(parts[9])
            particle.parts = parts
            event.add_particle(particle)
    output['events'] = events
    for event in events:
        pions = [particle for particle in event.particles if particle.id == 101]
        kaons = [particle for particle in event.particles if abs(particle.id) == 106]
        print("Event x: {} particles of which {} pions or kaons".format(len(event.particles), len(pions)+len(kaons)))
    if args.output_file:
        pickle.dump(output, args.output_file)

if __name__ == "__main__":
    main()
