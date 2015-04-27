'''
CCPN Analysis macro that helps with comparing (isotope shifted) spin systems.
'''

from memops.gui.LabelFrame import LabelFrame
from memops.gui.PulldownList import PulldownList
from memops.gui.CheckButton import CheckButton
from memops.gui.Label import Label
from memops.gui.ScrolledMatrix import ScrolledMatrix
from ccpnmr.analysis.popups.BasePopup import BasePopup
from ccpnmr.analysis.core.MoleculeBasic import getResidueCode
from ccpnmr.analysis.core.AssignmentBasic import (getShiftLists,
                                                  makeResonanceGuiName)
from isotope_shift import correct_for_isotope_shift as correct


def open_spinsystem_compare(argServer):
    """Opens a pop-up that lets you compare any two spin systems.
       Inputs: ArgumentServer
       Output: None
    """
    SpinSystemComparePopup(argServer.parent)


class SpinSystemComparePopup(BasePopup):
    '''The popop for comparing spin systems to one another.'''

    def __init__(self, parent, *args, **kw):
        '''Init. Args: parent: guiParent.

        '''

        self.guiParent = parent
        self.spinSystem1 = None
        self.spinSystem2 = None
        self.correction = True
        self.protonatedShiftList = None
        self.deuteratedShiftList = None
        BasePopup.__init__(self, parent, title="Compare Spin Systems", **kw)
        self.waiting = False

    def open(self):

        self.updateAfter()
        BasePopup.open(self)

    def body(self, guiFrame):
        '''This method describes the outline of the body of the
           application.
               args: guiFrame: frame the body should live in.

        '''

        self.geometry('800x530')

        guiFrame.grid_columnconfigure(0, weight=1)
        guiFrame.grid_rowconfigure(0, weight=0)
        guiFrame.grid_rowconfigure(1, weight=2)
        guiFrame.grid_rowconfigure(2, weight=1)

        isotopeFrame = LabelFrame(guiFrame, text='Isotope Shift Correction CA and CB')
        isotopeFrame.grid(row=0, column=0, sticky='nsew')

        frameA = LabelFrame(guiFrame, text='Spin Systems')
        frameA.grid(row=1, column=0, sticky='nsew')
        frameA.grid_rowconfigure(0, weight=1)
        frameA.grid_columnconfigure(0, weight=1)
        frameA.grid_columnconfigure(1, weight=1)

        frameA1 = LabelFrame(frameA, text='Spin System 1')
        frameA1.grid(row=0, column=0, sticky='nsew')
        frameA1.grid_columnconfigure(0, weight=1)
        frameA1.grid_rowconfigure(0, weight=1)

        frameA2 = LabelFrame(frameA, text='Spin System 2')
        frameA2.grid(row=0, column=1, sticky='nsew')
        frameA2.grid_columnconfigure(0, weight=1)
        frameA2.grid_rowconfigure(0, weight=1)

        frameB = LabelFrame(guiFrame, text='Comparison')
        frameB.grid(row=2, column=0, sticky='nsew')

        frameB.grid_rowconfigure(0, weight=1)
        frameB.grid_columnconfigure(0, weight=1)
        frameB.grid_columnconfigure(1, weight=2)
        frameB.grid_columnconfigure(2, weight=1)

        frameB1 = LabelFrame(frameB, text='Unique to Spin System 1')
        frameB1.grid(row=0, column=0, sticky='nsew')
        frameB1.expandGrid(0, 0)

        frameB2 = LabelFrame(frameB, text='Intersection')
        frameB2.grid(row=0, column=1, sticky='nsew')
        frameB2.expandGrid(0, 0)

        frameB3 = LabelFrame(frameB, text='Unique to Spin System 2')
        frameB3.grid(row=0, column=2, sticky='nsew')
        frameB3.expandGrid(0, 0)

        # Settings for isotope shift correction

        shiftLists = getShiftLists(self.nmrProject)
        self.protonatedShiftList = shiftLists[0]
        self.deuteratedShiftList = shiftLists[1]
        shiftListNames = ['{}: {}'.format(shiftList.serial, shiftList.name) for shiftList in shiftLists]

        Label(isotopeFrame, text='Correct for isotope shift:', grid=(0, 0))
        self.correctCheck = CheckButton(isotopeFrame,
                                        selected=True,
                                        callback=self.setCorrection,
                                        grid=(0, 1))
        Label(isotopeFrame, text='Protonated shift list:', grid=(1, 0))
        self.protonatedPulldown = PulldownList(isotopeFrame,
                                               callback=self.setProtonatedShiftList,
                                               texts=shiftListNames,
                                               objects=shiftLists,
                                               grid=(1, 1),
                                               index=0)

        Label(isotopeFrame, text='Deuterated shift list:', grid=(2, 0))
        self.deuteratedPulldown = PulldownList(isotopeFrame,
                                               callback=self.setDeuteratedShiftList,
                                               texts=shiftListNames,
                                               objects=shiftLists,
                                               grid=(2, 1),
                                               index=1)



        # Table A1
        headingList = ['#', 'shift lists', 'Assignment']

        tipTexts = ['Spin System Serial',
                    'shift lists', 'The residue (tentatively) assigned to this spin system',
                    'The amount of spin systems that overlap with this spin system and have no violations']

        editGetCallbacks = [self.setSpinSystem1]*3
        editSetCallbacks = [None]*3
        self.tableA1 = ScrolledMatrix(frameA1, headingList=headingList,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableA1.grid(row=0, column=0, sticky='nsew')

        # Table A2
        headingList = ['#', 'shift lists', 'Assignment', 'RMSD']
        tipTexts = ['Spin System Serial', 'The residue (tentatively) assigned to this spin system',
                    'Root mean squared deviation of this spin system to the spin system selected in the table on the left.']
        editGetCallbacks = [self.setSpinSystem2]*4
        editSetCallbacks = [None]*4
        self.tableA2 = ScrolledMatrix(frameA2, headingList=headingList,
                                      #editWidgets=editWidgets,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableA2.grid(row=0, column=0, sticky='nsew')

        # Table B1
        headingList = ['atom', 'c.s.']
        tipTexts = ['atom', 'chemical shift']
        self.tableB1 = ScrolledMatrix(frameB1,
                                      headingList=headingList,
                                      multiSelect=False,
                                      tipTexts=tipTexts)
        self.tableB1.grid(row=0, column=0, sticky='nsew')

        # Table B 2
        headingList = ['atom', 'c.s. 1', 'c.s. 2', 'delta c.s.']
        tipTexts = ['name of the atom', 'chemical shift of atom with this name in spin system 1',
                    'chemical shift of atom with this name in spin system 2',
                    'difference between the chemical shift of spin systems 1 and 2']

        self.tableB2 = ScrolledMatrix(frameB2,
                                      headingList=headingList,
                                      tipTexts=tipTexts)
        self.tableB2.grid(row=0, column=0, sticky='nsew')

        # Table B 3
        headingList = ['atom', 'c.s.']
        tipTexts = ['atom', 'chemical shift.']
        self.tableB3 = ScrolledMatrix(frameB3,
                                      headingList=headingList,
                                      multiSelect=False,
                                      tipTexts=tipTexts)
        self.tableB3.grid(row=0, column=0, sticky='nsew')

        self.matchMatrix = {}
        self.amountOfMatchesPerSpinSystem = {}

        self.updateTableA1()

    def update(self):
        '''Updates all tables except for tableA1.

        '''

        self.updateTableA2()
        self.updateCompareTables()

    def setCorrection(self, selected):
        '''Toggles on/off whether the isotope correction should
           be applied or not.
               args:    selected: Boolean, is True if isotope
                                  correction is to be applied.

        '''
        if self.correction is not selected:
            self.correction = selected
            self.update()

    def setProtonatedShiftList(self, shiftList):
        '''Set the shift list where protonated values of
           the chemical shifts should be fetched.
               args:    shiftList: shift list with
                        protonated shifts.

        '''

        if not self.protonatedShiftList is shiftList:
            self.protonatedShiftList = shiftList
            self.update()

    def setDeuteratedShiftList(self, shiftList):
        '''Set the shift list where deuterated values of
           the chemical shifts should be fetched.
               args:    shiftList: shift list with
                        deuterated shifts.

        '''

        if not self.deuteratedShiftList is shiftList:
            self.deuteratedShiftList = shiftList
            self.update()

    def setSpinSystem1(self, spinSystem):
        '''Set the first of two spin systems that should
           be compared.
               args:    spinSystem: first of two spin systems

        '''

        if spinSystem is not self.spinSystem1:

            self.spinSystem1 = spinSystem
            self.updateTableA2()

    def setSpinSystem2(self, spinSystem):
        '''Set the second of two spin systems that should
           be compared.
               args:    spinSystem: second of two spin systems

        '''

        if spinSystem is not self.spinSystem2:

            self.spinSystem2 = spinSystem
            self.updateCompareTables()

    def updateTableA1(self):
        '''Update tableA1 where the first spin systems is picked from.

        '''

        data = []
        objectList = []
        spinSystems = self.nmrProject.resonanceGroups

        for spinSystem in spinSystems:
            objectList.append(spinSystem)
            shiftLists_string = make_shiftLists_string(find_all_shiftLists_for_resonanceGroup(spinSystem))
            data.append([spinSystem.serial,
                         shiftLists_string,
                         make_resonanceGroup_string(spinSystem)])

        self.tableA1.update(objectList=objectList, textMatrix=data)
        self.tableA1.sortLine(2)

    def updateTableA2(self):
        '''Update tableA2 where the second spin systems is picked from.

        '''

        if not self.spinSystem1:
            return

        comparisons = self.compareToSpinSystem(self.spinSystem1)

        data = []
        objectList = []
        colorMatrix = []

        for comp in comparisons:

            resonanceGroup = comp.spinSystem2

            objectList.append(resonanceGroup)
            oneRow = []
            oneRow.append(resonanceGroup.serial)
            shiftLists_string = make_shiftLists_string(find_all_shiftLists_for_resonanceGroup(resonanceGroup))
            oneRow.append(shiftLists_string)
            oneRow.append(make_resonanceGroup_string(resonanceGroup))

            if comp.deviation is None:
                oneRow.append('-')
            else:
                oneRow.append(comp.deviation)

            if comp.match:
                colorMatrix.append(['#298A08']*4)
            else:
                colorMatrix.append([None]*4)

            data.append(oneRow)


        data, objectList, colorMatrix = zip(*sorted(zip(data, objectList, colorMatrix), key=lambda x: x[0][3]))
        self.tableA2.update(objectList=objectList,
                            textMatrix=data,
                            colorMatrix=colorMatrix)

    def updateCompareTables(self):
        '''Update all tables that compare 2 spin systems. These are the
           diff tables that show resonances unique to either one of the
           spin systems and the union table, where resonance types that
           are present in both spin systems are compared by chemical shift.

        '''

        if not self.spinSystem1 or not self.spinSystem2:
            return

        spinSystemComp = self.compare2spinSystems(self.spinSystem1,
                                                  self.spinSystem2)
        self.updateUnionTable(spinSystemComp)
        self.updateDiffTables(spinSystemComp)

    def updateDiffTables(self, spinSystemComp):
        '''Update the two tables that show the resonance types that are
           unique to respectively either the first or the second spin system.
           args:    spinSystemComp:    SpinSystemComparison comparing the two
                                       selected spin systems.

        '''

        for diff, table in [(spinSystemComp.difference1, self.tableB1),
                            (spinSystemComp.difference2, self.tableB3)]:
            data = []
            for resonance in diff:
                if resonance_in_shiftLists(resonance,
                                           [self.protonatedShiftList,
                                            self.deuteratedShiftList]):

                    if self.correction and self.protonatedShiftList \
                       and self.deuteratedShiftList \
                       and resonance.assignNames[0] in ('CA', 'CB') \
                       and resonance.assignNames[0] in ('CA', 'CB'):

                        shifted = ShiftedResonce(resonance,
                                                 self.protonatedShiftList,
                                                 self.deuteratedShiftList)

                        data.append([shifted.make_resonance_name(),
                                     shifted.make_shift_description()])

                        data.append([shifted.make_resonance_name(protonated=False),
                                     shifted.make_shift_description(protonated=False)])


                    else:
                        data.append([makeResonanceGuiName(resonance),
                                     resonance.findFirstShift().value])

            table.update(objectList=data, textMatrix=data)

    def updateUnionTable(self, spinSystemComp):
        '''Update the table that shows the resonance types that are
           present in both spin systems.
           args:    spinSystemComp:    SpinSystemComparison comparing the two
                                       selected spin systems.

        '''

        intersectData = []
        colorMatrix = []

        for resComp in spinSystemComp.intersection:

            oneRow = [resComp.resonance_name]
            oneRow.extend(resComp.shifts_description)
            oneRow.append(resComp.delta)
            intersectData.append(oneRow)

            if resComp.match:
                colorMatrix.append(['#298A08']*4)
            else:
                colorMatrix.append([None]*4)

        self.tableB2.update(objectList=intersectData,
                            textMatrix=intersectData,
                            colorMatrix=colorMatrix)

    def compareToSpinSystem(self, spinSystem):
        '''Compare one spin system to all others.
           args:    spinSystem:    spin system
           returns: list of SpinSystemComparison objects.

        '''

        spinSystems = self.nmrProject.resonanceGroups
        comparisons = []

        for spinSystem2 in spinSystems:

            comparisons.append(self.compare2spinSystems(spinSystem,
                                                        spinSystem2))

        return comparisons

    def compare2spinSystems(self, spinSystem1, spinSystem2):
        '''Compare two spin systems to each other.
           args:    spinSystem1:    the first spin system
                    spinSystem2:    the second spin system
           returns: SpinSystemComparison object

        '''

        comp = SpinSystemComparison(spinSystem1=spinSystem1,
                                    spinSystem2=spinSystem2,
                                    isotope_correction=self.correction,
                                    protonatedShiftList=self.protonatedShiftList,
                                    deuteratedShiftList=self.deuteratedShiftList)
        return comp


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


def make_shiftLists_string(shiftLists):
    '''For a list iterable of shift lists, produce a short string
       that identifies those shiftlists.
       args:    shiftLists:    iterable of shift lists
       returns: str of comma seperated shift list serials

    '''

    return ','.join([str(shiftList.serial) for shiftList in shiftLists])


def make_resonanceGroup_string(resonanceGroup):
    '''Make a more human readable description of a spin system.
       args:    resonanceGroup:    spin system
       returns: str description

    '''

    if resonanceGroup.residue:
        string = '{} {}'.format(resonanceGroup.residue.seqCode,
                                getResidueCode(resonanceGroup.residue.molResidue))

    elif resonanceGroup.residueProbs:
        substrings = []
        for prob in resonanceGroup.residueProbs:

            if not prob.weight:
                continue
            res = prob.possibility
            substrings.append(' '.join([str(res.seqCode),
                                        getResidueCode(res),
                                        '?']))
        string = ' / '.join(substrings)

    elif resonanceGroup.ccpCode:
        string = resonanceGroup.ccpCode
    else:
        string = '-'
    return string


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
        self.deviation = None
        self.intersection = []
        self.difference1 = set()
        self.difference2 = set()

        self.compare(isotope_correction,
                     protonatedShiftList,
                     deuteratedShiftList)

    def compare(self, isotope_correction=True,
                protonatedShiftList=None,
                deuteratedShiftList=None):
        '''Compares the two spin systems to each other and
           and thereby sets up some of the objects attributes
           like 'deviation', 'intersection', d'ifference1'
           and 'difference2'.
           args:    isotope_correction:  Boolean indicatinng whether
                                         isotope shift correction should
                                         be performed.
                    protonatedShiftList: The shift list containing the
                                         protonated shifts.
                    deuteratedShiftList: The shift list containing the
                                         deuterated shifts.

        '''

        shiftLists = [protonatedShiftList, deuteratedShiftList]
        resonances1 = self.spinSystem1.getResonances()
        resonances2 = self.spinSystem2.getResonances()
        combinations = []
        compared1 = set()
        compared2 = set()

        for res1 in resonances1:
            if not res1.assignNames:
                continue
            if not resonance_in_shiftLists(res1, shiftLists):
                continue

            for res2 in resonances2:
                if not res2.assignNames:
                    continue
                if not resonance_in_shiftLists(res2, shiftLists):
                    continue
                if not res1.assignNames[0] == res2.assignNames[0]:
                    continue

                combinations.append((res1, res2))
                compared1.add(res1)
                compared2.add(res2)

        self.difference1 = resonances1 - compared1
        self.difference2 = resonances2 - compared2

        for res1, res2 in combinations:

            if isotope_correction and protonatedShiftList \
               and deuteratedShiftList \
               and res1.assignNames[0] in ('CA', 'CB') \
               and res2.assignNames[0] in ('CA', 'CB'):

                shifted1 = ShiftedResonce(res1,
                                          protonatedShiftList,
                                          deuteratedShiftList)
                shifted2 = ShiftedResonce(res2,
                                          protonatedShiftList,
                                          deuteratedShiftList)

                protonated = ResonanceComparison(resonances=(res1, res2),
                                                 deuterated=False,
                                                 shifts=(shifted1.protonated_shift, shifted2.protonated_shift),
                                                 estimated=(shifted1.protonated_is_estimate, shifted2.protonated_is_estimate))

                deuterated = ResonanceComparison(resonances=(res1, res2),
                                                 deuterated=True,
                                                 shifts=(shifted1.deuterated_shift, shifted2.deuterated_shift),
                                                 estimated=(shifted1.deuterated_is_estimate, shifted2.deuterated_is_estimate))

                self.intersection.append(protonated)
                self.intersection.append(deuterated)

                average_delta = (protonated.delta + deuterated.delta) / 2.0

                if not self.deviation:
                    self.deviation = 0.0
                self.deviation += average_delta**2

            else:

                shifts = (res1.findFirstShift().value,
                          res2.findFirstShift().value)
                comparison = ResonanceComparison(resonances=(res1, res2),
                                                 shifts=shifts)

                self.intersection.append(comparison)

                if not self.deviation:
                    self.deviation = 0.0
                self.deviation += comparison.delta**2

        if self.deviation:
            self.deviation = self.deviation**0.5

    @property
    def match(self):
        '''Bool, True if all overlapping shifts within the two spin
           systems 'match'.
        '''

        for resonance_comparison in self.intersection:
            if not resonance_comparison.match:
                return False
        return True


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
        '''Returns a resonance name where deuterated and
           protonated are distinguishable.
           args:    Protonated:    Bool, if True, protonated name is
                                   returned, else the deuterated name.
           returns: str name description

        '''

        if protonated:
            return makeResonanceGuiName(self.resonance)
        else:
            return '{} (D)'.format(makeResonanceGuiName(self.resonance))

    def make_shift_description(self, protonated=True):
        '''Returns protonated or deuterated chemical shift with
           a question mark if the value is estimated.
           args:    Protonated:    Bool, if True, protonated shift is
                                   returned, else the deuterated shift.
           returns: str shift description

        '''
        if protonated:
            shift = self.protonated_shift
            estimated = self.protonated_is_estimate
        else:
            shift = self.deuterated_shift
            estimated = self.deuterated_is_estimate
        if estimated:
            return '{}?'.format(round(shift, 3))
        else:
            return str(round(shift, 3))


class ResonanceComparison(object):
    """Compares two resonances in terms of chemical shift"""
    def __init__(self, resonances, shifts, deuterated=False,
                 estimated=(False, False)):
        '''Init.
           args:    resonances:    the 2 resonances that are compared.
                    shifts:        chemical shifts of the resonances.
                    deuterated:    Boolean, indicating whether shifts
                                   are deuterated or not.
                    estimated:     2-list of Booleans, indicating
                                   whether corresponding shifts are
                                   estimated or measured.

        '''

        self.resonances = resonances
        self.deuterated = deuterated
        self.shifts = shifts
        self.estimated = estimated

    @property
    def delta(self):
        '''Absolute difference between two shifts.

        '''
        return abs(self.shifts[0] - self.shifts[1])

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
        if self.resonances[0].assignNames:
            name = self.resonances[0].assignNames[0]
        elif self.resonances[1].assignNames:
            name = self.resonances[1].assignNames[0]
        if name:
            if self.deuterated:
                return '{} (D)'.format(name)
            else:
                return name

    @property
    def shifts_description(self):
        '''Describes chemical shift. If the exact chemical shift
           is estimated because of isotope correction, this is
           indicated by a question mark.

        '''

        description = []
        for shift, estimated in zip(self.shifts, self.estimated):
            if estimated:
                description.append('{}?'.format(round(shift, 3)))
            else:
                description.append(str(round(shift, 3)))

        return description
