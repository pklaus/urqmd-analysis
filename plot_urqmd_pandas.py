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
    parser.add_argument('hdf5_file', metavar='HDF5_FILE', help="The HDF5 file containing the UrQMD events")
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--event-no', type=int, help='Total number of events (to scale histograms)')
    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity)

    hdf = pd.HDFStore(args.hdf5_file)
    df = hdf['particles']

    try:
        event_no = len(df['event_id'].unique())
    except:
        if args.event_no: event_no = args.event_no
        else: parser.error('The event_id is not included in the data. You must thus specify --event-no as param.')
    
    df['y'] = .5 * np.log((df.p0 + df.pz)/(df.p0 - df.pz))
    df['mT'] = np.sqrt(df.m**2 + df.px**2 + df.py**2)
    df['mT_weights'] = 1./df.mT**2
    nucleons = df[df.ityp == 1]
    pions = df[df.ityp == 101]
    kaons = df[abs(df.ityp) == 106]
    logging.info("{} particles of which {} pions or kaons".format(len(df), len(pions), len(pions)+len(kaons)))
    
    fig, ax = plt.subplots(1,2, figsize=(10,4))

    ### rapidity distribution
    ax[0].set_title('Rapidity Distribution')
    #fig.text(0.35, 0.04, 'rapidity', ha='center', va='center')
    ax[0].set_xlabel('rapidity y / GeV')
    #fig.text(0.10, 0.5, 'dN/dy', ha='center', va='center', rotation='vertical')
    ax[0].set_ylabel('dN/dy')
    bins_rapidity = np.linspace(-4.0, 4.0, num=81)
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
    prev_hist = hist
    # Nucleons
    hist, bins = np.histogram(nucleons.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='yellow', label='nucleons', bottom=prev_hist)
    prev_hist += hist
    # Kaons
    hist, bins = np.histogram(kaons.y, bins=bins_rapidity)
    #rescale histo:
    for i in range(len(hist)):
        bin_width = bins[1] - bins[0]
        hist[i] = hist[i] / bin_width / event_no
    ax[0].bar(bins[:-1], hist, width=(bins[1]-bins[0]), color='red', label='kaons', bottom=prev_hist)
    ax[0].legend()

    ### transverse mass distribution
    ax[1].set_title('Transverse Mass Distribution')
    #fig.text(0.70, 0.04, 'mT / GeV', ha='center', va='center')
    ax[1].set_xlabel('dN/dy')
    #fig.text(0.50, 0.5, '1/mT^2 dN/dmT', ha='center', va='center', rotation='vertical')
    ax[1].set_ylabel('1/mT^2 dN/dmT')
    # We use the rapidity cut: |y| < 1.0
    nucleons = nucleons[np.abs(nucleons.y) < 1.0]
    pions = pions[np.abs(pions.y) < 1.0]
    kaons = kaons[np.abs(kaons.y) < 1.0]
    bins_mT = np.linspace(0.0, 4.0, num=81)
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
    hdf.close()


if __name__ == "__main__":
    main()

