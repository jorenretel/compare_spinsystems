from isotope_shift import correct_for_isotope_shift as correct
from ccpnmr.analysis.core.AssignmentBasic import makeResonanceGuiName


class ShiftedResonce(object):
    '''Contains all inforation about the protonated and deuterated
       chemical shift of a resonance and whether these chemical shifts
       are measured or estimated.

    '''

    def __init__(self, resonance, protonatedShiftList=None,
                 deuteratedShiftList=None, correct=True):
        '''Init.
           args:    resonance:    resonance that is described.
                    protonatedShiftList: shift list of protonated shifts
                    deuteratedShiftList: shift list of deuterated shifts

        '''

        self.correct = correct
        self.resonance = resonance
        self.shiftedShifts = []
        self.protonatedShiftList = protonatedShiftList
        self.deuteratedShiftList = deuteratedShiftList
        self.determine_shifts()

    def determine_shifts(self):
        '''Determine protonated and deuterated shift for the described
           resonance. If the resonance is present in one or both of the
           shift lists, the chemical shift value is taken directly from
           there. If
        '''

        if self.correct and self.protonatedShiftList \
           and self.deuteratedShiftList \
           and self.resonance.assignNames[0] in ('CA', 'CB'):

            protonated_shift = None
            deuterated_shift = None
            protonated_is_estimate = False
            deuterated_is_estimate = False

            shift_object = self.resonance.findFirstShift(parentList=self.protonatedShiftList)
            if shift_object:
                protonated_shift = shift_object.value
            shift_object = self.resonance.findFirstShift(parentList=self.deuteratedShiftList)
            if shift_object:
                deuterated_shift = shift_object.value

            # Find out amino acid type
            aa_name = self.resonance.resonanceGroup.ccpCode
            if not aa_name and self.resonance.resonanceGroup.residue:
                aa_name = self.resonance.resonanceGroup.residue.ccpCode
            if not aa_name:
                aa_name = 'Avg'

            if protonated_shift and not deuterated_shift:
                deuterated_shift = correct(aa_name=aa_name,
                                           atom_name=self.resonance.assignNames[0],
                                           shift=protonated_shift,
                                           deuterated=False)
                deuterated_is_estimate = True

            if deuterated_shift and not protonated_shift:
                protonated_shift = correct(aa_name=aa_name,
                                           atom_name=self.resonance.assignNames[0],
                                           shift=deuterated_shift,
                                           deuterated=True)

                self.protonated_is_estimate = True

            if not protonated_shift and not deuterated_shift:

                text = '''Resonance {} does not have a shift in either
                          of the two shift lists {} and {}.'''
                raise ValueError(text.format(self.resonance.serial,
                                             self.protonatedShiftList,
                                             self.deuteratedShiftList))

            self.shiftedShifts = [ShiftedShift(resonance=self.resonance,
                                               value=protonated_shift,
                                               estimated=protonated_is_estimate,
                                               deuterated=False),
                                  ShiftedShift(resonance=self.resonance,
                                               value=deuterated_shift,
                                               estimated=deuterated_is_estimate,
                                               deuterated=True)]

        else:
            shiftedShift = ShiftedShift(resonance=self.resonance,
                                        value=self.resonance.findFirstShift().value)
            self.shiftedShifts = [shiftedShift]


class ShiftedShift(object):
    """docstring for ShiftedShift"""
    def __init__(self, resonance, value, estimated=False, deuterated=False):
        super(ShiftedShift, self).__init__()
        self.resonance = resonance
        self.value = value
        self.estimated = estimated
        self.deuterated = deuterated

    def create_name(self, full=True):
        '''Returns a resonance name where deuterated and
           protonated are distinguishable.
           returns: str name description

        '''

        name = makeResonanceGuiName(self.resonance, fullName=full)

        if not self.deuterated:
            return name
        else:
            return '{} (D)'.format(name)

    def create_shift_description(self):
        '''Returns protonated or deuterated chemical shift with
           a question mark if the value is estimated.
           returns: str shift description

        '''

        if self.estimated:
            return '{}?'.format(round(self.value, 3))
        else:
            return str(round(self.value, 3))
