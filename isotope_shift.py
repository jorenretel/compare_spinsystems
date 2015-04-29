'''
Calculates isotope shifts for CA and CB nuclei in protonated and
deuterated samples.

Values are taken from two papers:

Venters, Ronald A., Bennett T. Farmer II, Carol A. Fierke,
and Leonard D. Spicer. "Characterizing the use of perdeuteration in NMR
studies of large proteins: 13 C, 15 N and 1 H assignments of human
carbonic anhydrase II." Journal of molecular biology 264, no. 5 (1996):
1101-1116.

Maltsev, Alexander S., Jinfa Ying, and Ad Bax. "Deuterium isotope shifts
for backbone 1H, 15N and 13C nuclei in intrinsically disordered protein
alpha-synuclein." Journal of biomolecular NMR 54, no. 2 (2012): 181-191.

The former paper describes how to predict the shift in chemical shift of
CA and CB nuclei due to deuteration of the sample. Also deviation from
the prediction of experimental values (which is significant in a few
cases)are described in the paper, which allows back calculation of the
original average isotope shift.

The latter paper directly lists the experimental isotope shift. These
are also the correction values used in the Talos+ software.


Copyright (C) 2015 Joren Retel

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see http://www.gnu.org/licenses/.

'''

groupA_deuterons = [(1, 2, 0), (2, 1, 0)]
groupB_deuterons = [(1, 2, 2), (2, 3, 2)]
groupC_deuterons = [(1, 2, 2), (2, 3, 0)]
leu_deuterons = [(1, 2, 1), (2, 2, 6)]
ile_deuterons = [(1, 1, 5), (1, 6, 3)]
val_deuterons = [(1, 1, 6), (1, 7, 0)]
thr_deuterons = [(1, 1, 3), (1, 4, 0)]
ala_deuterons = [(1, 3, 0), (3, 1, 0)]

all_groups = [groupA_deuterons, groupB_deuterons, groupC_deuterons,
              leu_deuterons, ile_deuterons, val_deuterons, thr_deuterons,
              ala_deuterons]


deuterons_aa_dict = {'Asn': groupA_deuterons,
                     'Asp': groupA_deuterons,
                     'Ser': groupA_deuterons,
                     'His': groupA_deuterons,
                     'Phe': groupA_deuterons,
                     'Trp': groupA_deuterons,
                     'Tyr': groupA_deuterons,
                     'Cys': groupA_deuterons,
                     'Lys': groupB_deuterons,
                     'Arg': groupB_deuterons,
                     'Pro': groupB_deuterons,
                     'Gln': groupC_deuterons,
                     'Glu': groupC_deuterons,
                     'Met': groupC_deuterons,
                     'Leu': leu_deuterons,
                     'Ile': ile_deuterons,
                     'Val': val_deuterons,
                     'Thr': thr_deuterons,
                     'Ala': ala_deuterons}

deviation_venter = {'Asn': (0.06, 0.15),
                    'Asp': (0.09, 0.16),
                    'Ser': (0.13, 0.3),
                    'His': (0.07, 0.03),
                    'Phe': (0.1, 0.34),
                    'Trp': (0.16, 0.17),
                    'Tyr': (0.14, 0.27),
                    'Cys': (0.11, -0.01),
                    'Lys': (-0.03, -0.06),
                    'Arg': (-0.01, 0.04),
                    'Pro': (0.01, -0.09),
                    'Gln': (-0.01, -0.07),
                    'Glu': (0.03, -0.09),
                    'Met': (0.05, -0.05),
                    'Leu': (0.07, 0.06),
                    'Ile': (-0.08, -0.08),
                    'Val': (-0.09, -0.04),
                    'Thr': (0.09, -0.04),
                    'Ala': (0.01, -0.01)}

talos_iso_corr = {'Asn': (-0.387, -0.617),
                  'Asp': (-0.387, -0.660),
                  'Ser': (-0.446, -0.706),
                  'His': (-0.453, -0.674),
                  'Phe': (-0.430, -0.846),
                  'Trp': (-0.433, -0.852),
                  'Tyr': (-0.435, -0.857),
                  'Cys': (-0.446, -0.706),
                  'Lys': (-0.461, -1.033),
                  'Arg': (-0.461, -1.033),
                  'Pro': (-0.447, -0.912),
                  'Gln': (-0.480, -0.858),
                  'Glu': (-0.489, -0.880),
                  'Met': (-0.443, -0.885),
                  'Leu': (-0.448, -1.104),
                  'Ile': (-0.470, -1.019),
                  'Val': (-0.507, -0.964),
                  'Thr': (-0.431, -0.574),
                  'Ala': (-0.473, -0.876),
                  'Gly': (-0.475, 0.0),
                  'Avg': (-0.448, -0.837)}


def predict_isotope_shifts(aa_name):
    '''Using the method described by Venters et al.'''

    delta1 = -0.29
    delta2 = -0.13
    delta3 = -0.07

    deuterons = deuterons_aa_dict[aa_name]

    ca_deuterons, cb_deuterons = deuterons

    ca_shift = (delta1 * ca_deuterons[0]) + (delta2 * ca_deuterons[1]) + (delta3 * ca_deuterons[2]) #- deviation_venter[aa_name][0]
    cb_shift = (delta1 * cb_deuterons[0]) + (delta2 * cb_deuterons[1]) + (delta3 * cb_deuterons[2]) #- deviation_venter[aa_name][1]

    return ca_shift, cb_shift


def correct_for_isotope_shift(aa_name, atom_name, shift, deuterated=False):
    '''Return the expected observed chemical shift in a deuterated
       sample, based on the shift in a protonated sample, or vise versa.
       args:    aa_name:     three letter amino acid code
                atom_name:   'CA' or 'CB'
                shift:       float measured shift
                deuterated:  Boolean, should be True if the given shift
                             corresponds to the deuterated sample.
    '''

    if atom_name not in ('CA', 'CB'):
        raise ValueError('''Only isotope correction data available
                            for CA and CB, not for {}'''.format(atom_name))

    atom_index = ['CA', 'CB'].index(atom_name)
    isotope_shift = talos_iso_corr[aa_name][atom_index]

    if deuterated:
        isotope_shift *= -1

    return shift + isotope_shift


if __name__ == '__main__':

    for aa in deuterons_aa_dict.keys():

        pred = predict_isotope_shifts(aa)[0]
        talos = talos_iso_corr[aa][0]

        t = '\t'

        print aa, t, pred, t, pred + deviation_venter[aa][0], t, talos, t, pred - talos, t, (pred + deviation_venter[aa][0]) -talos
