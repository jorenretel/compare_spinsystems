'''Classes SpinSystemComparison and ShiftComparison can be used to
   map the differences and
'''

from ccpn_isotope_shift import ShiftedResonce


class SpinSystemComparison(object):
    '''Contains all information about the differences and similarities
       of two spin systems.

    '''

    def __init__(self, spinSystem1, spinSystem2,
                 isotope_correction=True,
                 protonatedShiftList=None,
                 deuteratedShiftList=None):

        self.spinSystem1 = spinSystem1
        self.spinSystem2 = spinSystem2
        self.protonatedShiftList = protonatedShiftList
        self.deuteratedShiftList = deuteratedShiftList
        self.deviation = None
        self.intersection = []
        self.unique_to_1 = set()
        self.unique_to_2 = set()
        self.isotope_correction = isotope_correction

        self.compare()

    def divide_resonances(self):
        '''Divide resonances into 3 groups:
               A. Unique to spin system 1
               B. Unique to spin system 2
               C. Resonances that have assign names that are present in
                  both spin system 1 and 2.
           returns: [list A, list B, list of 2-tuples C.]

        '''

        shiftLists = [self.protonatedShiftList, self.deuteratedShiftList]
        resonances1 = self.spinSystem1.getResonances()
        resonances2 = self.spinSystem2.getResonances()
        combinations = []
        compared = set()
        bad = set()

        for res1 in resonances1:
            if not resonance_in_shiftLists(res1, shiftLists):
                bad.add(res1)
                continue
            if not res1.assignNames:
                continue

            for res2 in resonances2:
                if not resonance_in_shiftLists(res2, shiftLists):
                    bad.add(res2)
                    continue
                if not res2.assignNames:
                    continue
                if not res1.assignNames[0] == res2.assignNames[0]:
                    continue

                combinations.append((res1, res2))
                compared.update((res1, res2))

        difference1 = resonances1 - compared - bad
        difference2 = resonances2 - compared - bad

        return difference1, difference2, combinations

    def compare(self):
        '''Compares the two spin systems to each other and
           and thereby sets up some of the objects attributes
           like 'deviation', 'intersection', 'unique_to_1'
           and 'unique_to_2'.

        '''

        difference1, difference2, combinations = self.divide_resonances()

        for res1, res2 in combinations:

            shifted1 = ShiftedResonce(res1,
                                      self.protonatedShiftList,
                                      self.deuteratedShiftList,
                                      isotope_correction=self.isotope_correction)
            shifted2 = ShiftedResonce(res2,
                                      self.protonatedShiftList,
                                      self.deuteratedShiftList,
                                      isotope_correction=self.isotope_correction)

            average_delta = 0.0
            isotope_sorted_shifts = zip(shifted1.shiftedShifts,
                                        shifted2.shiftedShifts)
            for shiftedShifts in isotope_sorted_shifts:
                shiftComparison = ShiftComparison(shiftedShifts=shiftedShifts)
                self.intersection.append(shiftComparison)
                average_delta += shiftComparison.delta
            average_delta /= len(isotope_sorted_shifts)

            if not self.deviation:
                self.deviation = 0.0
            self.deviation += average_delta**2

        if self.deviation:
            self.deviation = self.deviation**0.5

        for resonances, difference_set in [(difference1, self.unique_to_1),
                                           (difference2, self.unique_to_2)]:

            for resonance in resonances:
                shiftedResonance = ShiftedResonce(resonance,
                                                  isotope_correction=self.isotope_correction)
                difference_set.update(shiftedResonance.shiftedShifts)

    @property
    def match(self):
        '''Bool, True if all overlapping shifts within the two spin
           systems 'match'.
        '''

        for resonance_comparison in self.intersection:
            if not resonance_comparison.match:
                return False
        return True


class ShiftComparison(object):
    """docstring for ShiftComparison"""
    def __init__(self, shiftedShifts):
        super(ShiftComparison, self).__init__()
        self.shiftedShifts = shiftedShifts

    @property
    def delta(self):
        '''Absolute difference between two shifts.

        '''
        return abs(self.shiftedShifts[0].value - self.shiftedShifts[1].value)

    @property
    def match(self):
        '''Boolean, True if shifts match under cut-off value.

        '''

        if self.delta < 0.5:
            return True
        return False

    @property
    def resonance_name(self):
        '''name describing resonance type including
           indication for deuterated shift.

        '''

        return self.shiftedShifts[0].create_name(full=False)

    @property
    def shifts_description(self):
        '''Describes chemical shift. If the exact chemical shift
           is estimated because of isotope correction, this is
           indicated by a question mark.

        '''

        return [self.shiftedShifts[0].create_shift_description(),
                self.shiftedShifts[1].create_shift_description()]


def find_all_shiftLists_for_resonanceGroup(resonanceGroup):
    '''Find all shift lists the resonance of a resonanceGroup (spin system)
       are represented in.
       args:    resonanceGroup:    spin system
       returns: list of shift lists

    '''

    shiftLists = set()

    for resonance in resonanceGroup.resonances:
        shiftLists.update([shift.parentList for shift in resonance.getShifts()])

    return sorted(list(shiftLists), reverse=True)


def resonance_in_shiftLists(resonance, shiftLists):
    '''Returns True if resonance is present in at least one of the
       shiftLists.
       args:    resonance:    Resonance object
                shiftLists:   iterable of shiftLists that should be
                              searched.
       returns: Boolean

    '''

    for shiftList in shiftLists:
        if resonance.findFirstShift(parentList=shiftList):
            return True
    return False
