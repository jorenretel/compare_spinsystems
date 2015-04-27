'''
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

#DC(D) = 1 DC(D)d 1b + 2 DC(D)d 2b + 3 DC(D)d 3b


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


Delta1 = -0.29
Delta2 = -0.13
Delta3 = -0.07


def predict_isotope_shifts(aa_name):

    deuterons = deuterons_aa_dict[aa_name]

    ca_deuterons, cb_deuterons = deuterons

    ca_shift = (Delta1 * ca_deuterons[0]) + (Delta2 * ca_deuterons[1]) + (Delta3 * ca_deuterons[2]) #- deviation_venter[aa_name][0]
    cb_shift = (Delta1 * cb_deuterons[0]) + (Delta2 * cb_deuterons[1]) + (Delta3 * cb_deuterons[2]) #- deviation_venter[aa_name][1]

    return ca_shift, cb_shift


def correct_for_isotope_shift(aa_name, atom_name, shift, deuterated=False):

    if atom_name not in ('CA', 'CB'):
        raise ValueError('''Only isotope correction data available
                            for CA and CB, not for {}'''.format(atom_name))

    atom_index = ['CA', 'CB'].index(atom_name)
    isotope_shift = talos_iso_corr[aa_name][atom_index]

    if deuterated:
        isotope_shift *= -1

    return shift + isotope_shift


if __name__ == '__main__':

    for aa_name, deuterons in deuterons_aa_dict.items():

        pred = predict_isotope_shifts(aa_name)[0]
        talos = talos_iso_corr[aa_name][0]

        t = '\t'

        print aa_name, t, pred, t, pred + deviation_venter[aa_name][0], t, talos, t, pred - talos, t, (pred + deviation_venter[aa_name][0]) -talos