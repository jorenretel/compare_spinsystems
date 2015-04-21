
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
    """Descrn: Opens the shift reference pop-up for two residue types.
       Inputs: ArgumentServer
       Output: None
    """
    SpinSystemComparePopup(argServer.parent)


class SpinSystemComparePopup(BasePopup):

    def __init__(self, parent, *args, **kw):

        self.guiParent = parent
        self.selectedSpinSystem1 = None
        self.protonatedShiftList = None
        self.deuteratedShiftList = None

        BasePopup.__init__(self, parent, title="Compare Spin Systems", **kw)

        self.waiting = False

    def open(self):

        self.updateAfter()
        BasePopup.open(self)

    def body(self, guiFrame):

        self.geometry('800x530')

        guiFrame.grid_columnconfigure(0, weight=1)
        guiFrame.grid_rowconfigure(0, weight=0)
        guiFrame.grid_rowconfigure(1, weight=2)
        guiFrame.grid_rowconfigure(2, weight=1)

        isotopeFrame = LabelFrame(guiFrame, text='Isotope Shift Correction')
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
        self.correctCheck = CheckButton(isotopeFrame, selected=True, grid=(0, 1))
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

        headingList = ['#', 'shift lists', 'Assignment', 'overlapping']

        tipTexts = ['Spin System Serial',
                    'shift lists', 'The residue (tentatively) assigned to this spin system',
                    'The amount of spin systems that overlap with this spin system and have no violations']

        editGetCallbacks = [self.updateTableA2]*4
        editSetCallbacks = [None]*4

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

        #editWidgets = [None]

        editGetCallbacks = [self.updateCompareTables]*4

        editSetCallbacks = [None, None, None, None]

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
        self.compareSpinSystems()
        self.updateTableA1()

    def setProtonatedShiftList(self, shiftList):
        self.protonatedShiftList = shiftList

    def setDeuteratedShiftList(self, shiftList):
        self.deuteratedShiftList = shiftList

    def updateTableA1(self):

        data = []
        objectList = []

        for key in self.matchMatrix:

            shiftLists_string = make_shiftLists_string(find_all_shiftLists_for_resonanceGroup(key))

            objectList.append(key)
            oneRow = []
            oneRow.append(key.serial)
            oneRow.append(shiftLists_string)
            oneRow.append(make_resonanceGroup_string(key))

            if key in self.amountOfMatchesPerSpinSystem:
                oneRow.append(self.amountOfMatchesPerSpinSystem[key])
            else:
                oneRow.append(0)

            data.append(oneRow)

        self.tableA1.update(objectList=objectList, textMatrix=data)
        self.tableA1.sortLine(2)

    def updateTableA2(self, obj):

        if obj != self.selectedSpinSystem1:

            self.selectedSpinSystem1 = obj

        data = []
        objectList = []
        colorMatrix = []

        for resonanceGroup, match in self.matchMatrix[obj].items():

            objectList.append(resonanceGroup)
            oneRow = []
            oneRow.append(resonanceGroup.serial)
            shiftLists_string = make_shiftLists_string(find_all_shiftLists_for_resonanceGroup(resonanceGroup))
            oneRow.append(shiftLists_string)
            oneRow.append(make_resonanceGroup_string(resonanceGroup))

            if match.deviation is None:
                oneRow.append('-')
            else:
                oneRow.append(match.deviation)

            if match.match:
                colorMatrix.append(['#298A08']*4)
            else:
                colorMatrix.append([None]*4)

            data.append(oneRow)

        #datazip = zip(data)
        #data.sort(key=lambda x: x[2])

        data, objectList, colorMatrix = zip(*sorted(zip(data, objectList, colorMatrix), key=lambda x: x[0][3]))
        self.tableA2.update(objectList=objectList,
                            textMatrix=data,
                            colorMatrix=colorMatrix)

    def updateCompareTables(self, obj):

        spinSystemComp = self.matchMatrix[self.selectedSpinSystem1][obj]
        self.updateUnionTable(spinSystemComp)
        self.updateDiffTables(spinSystemComp)

    def updateDiffTables(self, spinSystemComp):

        for diff, table in [(spinSystemComp.difference1, self.tableB1),
                            (spinSystemComp.difference2, self.tableB3)]:
            data = []
            for resonance in diff:
                if resonance.findFirstShift():
                    data.append([makeResonanceGuiName(resonance),
                                 resonance.findFirstShift().value])

            table.update(objectList=data, textMatrix=data)

    def updateUnionTable(self, spinSystemComp):

        intersectData = []
        colorMatrix = []

        for resComp in spinSystemComp.intersection:

            oneRow = [resComp.atomName]
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

    def compareSpinSystems(self):

        spinSystems = self.nmrProject.resonanceGroups

        # taking all spinsystems in the project
        for spinSystem1 in spinSystems:

            if not spinSystem1.resonances:
                continue

            for spinSystem2 in spinSystems:

                if not spinSystem2.resonances:
                    continue

                self.compare2spinSystems(spinSystem1, spinSystem2)

    def compare2spinSystems(self, spinSystem1, spinSystem2):

        correction = self.correctCheck.isSelected()

        comp = SpinSystemComparison(spinSystem1=spinSystem1,
                                    spinSystem2=spinSystem2,
                                    isotope_correction=correction,
                                    protonatedShiftList=self.protonatedShiftList,
                                    deuteratedShiftList=self.deuteratedShiftList)

        if spinSystem1 in self.matchMatrix:
            self.matchMatrix[spinSystem1][spinSystem2] = comp
        else:
            self.matchMatrix[spinSystem1] = {spinSystem2: comp}


def find_all_shiftLists_for_resonanceGroup(resonanceGroup):

    shiftLists = set()

    for resonance in resonanceGroup.resonances:
        shiftLists.update([shift.parentList for shift in resonance.getShifts()])

    return sorted(list(shiftLists), reverse=True)


def make_shiftLists_string(shiftLists):

    return ','.join([str(shiftList.serial) for shiftList in shiftLists])


def make_resonanceGroup_string(resonanceGroup):

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


def make_resonance_string(resonance):
    if resonance.assignNames:
        return resonance.assignNames[0]
    else:
        return '[{}]'.format(resonance.serial)


class SpinSystemComparison(object):

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

        resonances1 = self.spinSystem1.getResonances()
        resonances2 = self.spinSystem2.getResonances()
        combinations = []
        compared1 = set()
        compared2 = set()

        for res1 in resonances1:
            if not (res1.assignNames and res1.findFirstShift()):
                continue
            for res2 in resonances2:
                if not (res2.assignNames and res2.findFirstShift()):
                    continue
                if res1.assignNames[0] == res2.assignNames[0]:
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

        for resonance_comparison in self.intersection:
            if not resonance_comparison.match:
                return False
        return True


class ShiftedResonce(object):

    def __init__(self, resonance, protonatedShiftList, deuteratedShiftList):

        self.resonance = resonance
        self.protonatedShiftList = protonatedShiftList
        self.deuteratedShiftList = deuteratedShiftList
        self.protonated_shift = None
        self.deuterated_shift = None
        self.protonated_is_estimate = False
        self.deuterated_is_estimate = False
        self.determine_shifts()

    def determine_shifts(self):

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
            print 'alarm'
            print self.resonance.serial
            print self.resonance.findFirstShift()
            print 'aaaa'
            print self.protonated_shift
            print 'bbb'
            print self.deuterated_shift


class ResonanceComparison(object):
    """docstring for resonanceMatch"""
    def __init__(self, resonances, shifts, deuterated=False,
                 estimated=(False, False)):

        super(ResonanceComparison, self).__init__()
        self.resonances = resonances
        self.deuterated = deuterated
        self.shifts = shifts
        self.estimated = estimated

    @property
    def delta(self):
        return abs(self.shifts[0] - self.shifts[1])

    @property
    def match(self):
        if self.delta < 0.5:
            return True
        return False

    @property
    def atomName(self):
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

        description = []
        for shift, estimated in zip(self.shifts, self.estimated):
            if estimated:
                description.append('{}?'.format(round(shift, 3)))
            else:
                description.append(str(round(shift, 3)))

        return description