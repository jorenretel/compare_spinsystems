from isotope_shift import correct_for_isotope_shift as correct


class ShiftedResonce(object):
    '''Contains all inforation about the protonated and deuterated
       chemical shift of a resonance and whether these chemical shifts
       are measured or estimated.

    '''

    def __init__(self, resonance, protonatedShiftList, deuteratedShiftList):
        '''Init.
           args:    resonance:    resonance that is described.
                    protonatedShiftList: shift list of protonated shifts
                    deuteratedShiftList: shift list of deuterated shifts

        '''

        self.resonance = resonance
        self.protonatedShiftList = protonatedShiftList
        self.deuteratedShiftList = deuteratedShiftList
        self.protonated_shift = None
        self.deuterated_shift = None
        self.protonated_is_estimate = False
        self.deuterated_is_estimate = False
        self.determine_shifts()

    def determine_shifts(self):
        '''Determine protonated and deuterated shift for the described
           resonance. If the resonance is present in one or both of the
           shift lists, the chemical shift value is taken directly from
           there. If
        '''

        shift_object = self.resonance.findFirstShift(parentList=self.protonatedShiftList)
        if shift_object:
            self.protonated_shift = shift_object.value
        shift_object = self.resonance.findFirstShift(parentList=self.deuteratedShiftList)
        if shift_object:
            self.deuterated_shift = shift_object.value

        # Find out amino acid type
        aa_name = self.resonance.resonanceGroup.ccpCode
        if not aa_name and self.resonance.resonanceGroup.residue:
            aa_name = self.resonance.resonanceGroup.residue.ccpCode
        if not aa_name:
            aa_name = 'Avg'

        if self.protonated_shift and not self.deuterated_shift:
            self.deuterated_shift = correct(aa_name=aa_name,
                                            atom_name=self.resonance.assignNames[0],
                                            shift=self.protonated_shift,
                                            deuterated=False)
            self.deuterated_is_estimate = True

        if self.deuterated_shift and not self.protonated_shift:
            self.protonated_shift = correct(aa_name=aa_name,
                                            atom_name=self.resonance.assignNames[0],
                                            shift=self.deuterated_shift,
                                            deuterated=True)
            self.protonated_is_estimate = True

        if not self.protonated_shift and not self.deuterated_shift:

            text = '''Resonance {} does not have a shift in either
                      of the two shift lists {} and {}.'''
            raise ValueError(text.format(self.resonance.serial,
                                         self.protonatedShiftList,
                                         self.deuteratedShiftList))

    def make_resonance_name(self, protonated=True):
        return 'replace this'


class ShiftedShift(object):
    """docstring for ShiftedShift"""
    def __init__(self, value, estimated=False, deuterated=False):
        super(ShiftedShift, self).__init__()
        self.value = value
        self.estimated = estimated
        self.deuterated = deuterated

    @property
    def name(self):
        '''Returns a resonance name where deuterated and
           protonated are distinguishable.
           returns: str name description

        '''

        if self.protonated:
            return makeResonanceGuiName(self.resonance)
        else:
            return '{} (D)'.format(makeResonanceGuiName(self.resonance))

    def make_shift_description(self):
        '''Returns protonated or deuterated chemical shift with
           a question mark if the value is estimated.
           returns: str shift description

        '''

        if self.estimated:
            return '{}?'.format(round(self.value, 3))
        else:
            return str(round(self.value, 3))
