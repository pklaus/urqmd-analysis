#!/usr/bin/env python

""" UrQMD File Reader """

from read_urqmd import F14_Reader
import argparse
import pickle
import logging
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np


class Particle(object):

    def __init__(self, properties):
        self._properties = properties
        # precalculate expensive values:
        self._mT = math.sqrt(self.m0**2 + self.px**2 + self.py**2)

    @property
    def id(self):
        return int(self._properties[9])

    @property
    def time(self):
        return float(self._properties[0])

    @property
    def E(self):
        return float(self._properties[4])

    @property
    def px(self):
        return float(self._properties[5])

    @property
    def py(self):
        return float(self._properties[6])

    @property
    def pz(self):
        return float(self._properties[7])

    @property
    def m0(self):
        return float(self._properties[8])

    @property
    def mT(self):
        return self._mT

    @property
    def y(self):
        """ rapidity """
        return .5 * math.log((self.E + self.pz)/(self.E - self.pz))


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('urqmd_file', metavar='URQMD_FILE', type=argparse.FileType('r'), help="Must be of type .f14")
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity)

    events = []
    event_number = []
    particle_number = []
    particle_y = []
    nucleon_y = []
    nucleon_number = []
    pion_number = []
    kaon_number = []
    pion_y = []
    pion_mT = []
    pion_mT_weights = []
    kaon_y = []
    kaon_mT = []
    kaon_mT_weights = []
    particle_mT = []
    particle_mT_weights = []
    nucleon_mT = []
    nucleon_mT_weights = []
    for event in F14_Reader(args.urqmd_file).get_events():
        events.append(event)
        event_number.append(event['id'])
        particles = [Particle(particle_properties) for particle_properties in event['particle_properties']]
        particle_y += [particle.y for particle in particles]
        particle_mT += [particle.mT for particle in particles if abs(particle.y) < 1.0]
        particle_mT_weights += [1/particle.mT**2 for particle in particles if abs(particle.y) < 1.0]
        nucleons = [particle for particle in particles if particle.id == 1]
        pions = [particle for particle in particles if particle.id == 101]
        kaons = [particle for particle in particles if abs(particle.id) == 106]
        nucleon_number.append(len(nucleons))
        pion_number.append(len(pions))
        kaon_number.append(len(kaons))
        for nucleon in nucleons:
            nucleon_y.append(nucleon.y)
            if abs(nucleon.y) < 1.0:
                nucleon_mT.append(nucleon.mT)
                # weights for the histogram
                # http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
                nucleon_mT_weights.append(1/nucleon.mT**2)
        for pion in pions:
            pion_y.append(pion.y)
            if abs(pion.y) < 1.0:
                pion_mT.append(pion.mT)
                # weights for the histogram
                # http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
                pion_mT_weights.append(1/pion.mT**2)
        for kaon in kaons:
            kaon_y.append(kaon.y)
            if abs(kaon.y) < 1.0:
                kaon_mT.append(kaon.mT)
                # weights for the histogram
                # http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
                kaon_mT_weights.append(1/kaon.mT**2)
        particle_number.append(len(particles))
        logging.info("Event #{}: {} particles of which {} pions or kaons".format(event['id'], len(particles), len(pions)+len(kaons)))
    
    df_physics = pd.DataFrame({'particles': particle_number, 'pions': pion_number, 'kaons': kaon_number}, index=event_number)

    df_events = pd.DataFrame({'particles': particle_number, 'pions': pion_number, 'kaons': kaon_number}, index=event_number)
    print(df_events.describe())

    event_no = len(events)

    fig, ax = plt.subplots(1,2, figsize=(10,4))

    ### rapidity distribution
    ax[0].set_title('Rapidity Distribution')
    #fig.ylabel('dN/dy')
    #ax[0].xlabel('y / GeV')
    bins_rapidity = 50
    # All Particles
    hist, bins = np.histogram(particle_y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='grey', label='all particles')
    # Pions
    hist, bins = np.histogram(pion_y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='blue', label='pions')
    # Nucleons
    hist, bins = np.histogram(nucleon_y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='yellow', label='nucleons')
    # Kaons
    hist, bins = np.histogram(kaon_y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='red', label='kaons')
    ax[0].legend()

    ### transverse mass distribution
    ax[1].set_title('Transverse Mass Distribution')
    #ax[1].ylabel('1/mT^2 dN/dmT')
    #ax[1].xlabel('mT / GeV')
    bins_mT = 80
    # Nucleons
    hist, bins = np.histogram(nucleon_mT, weights=nucleon_mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='yellow', log=True, fill=True, label='nucleons')
    # Pions
    hist, bins = np.histogram(pion_mT, weights=pion_mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='blue', log=True, fill=True, label='pions')
    # Kaons
    hist, bins = np.histogram(kaon_mT, weights=kaon_mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='red', log=True, fill=True, label='kaons')
    ax[1].legend()
    fig.show()
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()

