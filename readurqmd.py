#!/usr/bin/env python

import argparse
import pickle
import logging
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

class Event(object):
    def __init__(self):
        self._particles = []
    def add_particle(self, particle):
        self._particles.append(particle)
    @property
    def particles(self):
        return self._particles

class Particle(object):
    @property
    def parts(self):
        return _parts
    @property
    def E(self):
        return float(self._parts[4])
    @property
    def px(self):
        return float(self._parts[5])
    @property
    def py(self):
        return float(self._parts[6])
    @property
    def pz(self):
        return float(self._parts[7])
    @property
    def m0(self):
        return float(self._parts[8])
    @property
    def mT(self):
        return math.sqrt(self.m0**2 + self.px**2 + self.py**2)
    @property
    def y(self):
        """ rapidity """
        return .5 * math.log((self.E + self.pz)/(self.E - self.pz))

def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r'), help="Must be of type .f14")
    parser.add_argument('--output_file', metavar='OUT_FILE', type=argparse.FileType('wb'))
    args = parser.parse_args()

    f = args.urqmd_file

    new_event = False
    output = dict()
    events = []
    for line in f:
        parts = line.split()
        if not len(parts): continue
        if parts[0] == 'UQMD': new_event = True
        if new_event:
            event = Event()
            events.append(event)
            new_event = False
        if parts[0] == 'event#': event.number = int(parts[1])
        if len(parts) == 15:
            logging.debug(parts)
            particle = Particle()
            particle.id = int(parts[9])
            particle._parts = parts
            event.add_particle(particle)
    output['events'] = events
    event_number = []
    particle_number = []
    pion_number = []
    kaon_number = []
    pion_y = []
    pion_mT = []
    kaon_y = []
    kaon_mT = []
    for event in events:
        event_number.append(event.number)
        pions = [particle for particle in event.particles if particle.id == 101]
        kaons = [particle for particle in event.particles if abs(particle.id) == 106]
        pion_number.append(len(pions))
        kaon_number.append(len(kaons))
        for pion in pions:
            pion_y.append(pion.y)
            if abs(pion.y) < 1.0:
                pion_mT.append(pion.mT)
        for kaon in kaons:
            kaon_y.append(1/kaon.y)
            if abs(kaon.y) < 1.0:
                kaon_mT.append(kaon.mT)
        particle_number.append(len(event.particles))
        logging.info("Event #{}: {} particles of which {} pions or kaons".format(event.number, len(event.particles), len(pions)+len(kaons)))
    
    df_physics = pd.DataFrame({'particles': particle_number, 'pions': pion_number, 'kaons': kaon_number}, index=event_number)

    df_events = pd.DataFrame({'particles': particle_number, 'pions': pion_number, 'kaons': kaon_number}, index=event_number)
    output['df_events'] = df_events
    print(df_events.describe())

    event_no = len(events)

    ## Pions

    fig, ax = plt.subplots(1,2, figsize=(10,4))

    # rapidity distribution
    s_y = pd.Series(pion_y)
    hist, bins = np.histogram(pion_y)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='grey')
    #ax[0].hist(s_y, normed=True, color='grey')

    # transverse mass distribution
    s_mT = pd.Series(pion_mT)
    hist, bins = np.histogram(pion_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / (bins[i+1] - bins[i])**2 / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='grey')
    #ax[1].hist(s_mT, normed=True, color='grey')
    fig.show()
    import pdb; pdb.set_trace()

    if args.output_file:
        pickle.dump(output, args.output_file)

if __name__ == "__main__":
    main()
