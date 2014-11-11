#!/usr/bin/env python

""" UrQMD File Reader """

import argparse
import logging
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Read a config file.')
    parser.add_argument('pandas_file', metavar='PANDAS_FILE', help="A pickle file created with pandas.")
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--event-no', type=int, help='Total number of events (to scale histograms)', required=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity)


    df = pd.read_pickle(args.pandas_file)
    
    df['y'] = .5 * np.log((df.p0 + df.pz)/(df.p0 - df.pz))
    df['mT'] = np.sqrt(df.m**2 + df.px**2 + df.py**2)
    df['mT_weights'] = 1./df.mT**2
    nucleons = df[df.ityp == 1]
    pions = df[df.ityp == 101]
    kaons = df[abs(df.ityp) == 106]
    logging.info("{} particles of which {} pions or kaons".format(len(df), len(pions), len(pions)+len(kaons)))
    
    fig, ax = plt.subplots(1,2, figsize=(10,4))
    event_no = args.event_no

    ### rapidity distribution
    ax[0].set_title('Rapidity Distribution')
    #fig.ylabel('dN/dy')
    #ax[0].xlabel('y / GeV')
    bins_rapidity = 50
    # All Particles
    hist, bins = np.histogram(df.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='grey', label='all particles')
    # Pions
    hist, bins = np.histogram(pions.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='blue', label='pions')
    # Nucleons
    hist, bins = np.histogram(nucleons.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='yellow', label='nucleons')
    # Kaons
    hist, bins = np.histogram(kaons.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='red', label='kaons')
    ax[0].legend()

    ### transverse mass distribution
    ax[1].set_title('Transverse Mass Distribution')
    # rapidity cut: |y| < 1.0
    #df_rapidity_cut = df[abs(df.y) < 1.0]
    nucleons = nucleons[abs(nucleons.y) < 1.0]
    pions = pions[abs(pions.y) < 1.0]
    kaons = kaons[abs(kaons.y) < 1.0]
    #ax[1].ylabel('1/mT^2 dN/dmT')
    #ax[1].xlabel('mT / GeV')
    bins_mT = 80
    # Nucleons
    hist, bins = np.histogram(nucleons.mT, weights=nucleons.mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='yellow', log=True, fill=True, label='nucleons')
    # Pions
    hist, bins = np.histogram(pions.mT, weights=pions.mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='blue', log=True, fill=True, label='pions')
    # Kaons
    hist, bins = np.histogram(kaons.mT, weights=kaons.mT_weights, bins=bins_mT)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[1].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='red', log=True, fill=True, label='kaons')
    ax[1].legend()
    fig.show()

    # Fitting the temperature
    def decay(x, x_p, y_p, y0, x0):
        return y0 + y_p * np.exp(-(x-x0)*x_p)


    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()

