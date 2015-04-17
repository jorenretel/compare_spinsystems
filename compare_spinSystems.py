
from memops.gui.LabelFrame import LabelFrame
from ccpnmr.analysis.popups.BasePopup import BasePopup
from ccpnmr.analysis.core.MoleculeBasic import getResidueCode
from memops.gui.ScrolledMatrix import ScrolledMatrix
from ccpnmr.analysis.core.AssignmentBasic import (getShiftLists,
                                                  makeResonanceGuiName)


def open_spinsystem_compare(argServer):
    """Descrn: Opens the shift reference pop-up for two residue types.
       Inputs: ArgumentServer
       Output: None
    """
    SpinSystemCompatePopup(argServer.parent)


class SpinSystemCompatePopup(BasePopup):

    def __init__(self, parent, *args, **kw):


        self.guiParent = parent
        self.selectedSpinSystem1 = None

        BasePopup.__init__(self, parent, title="Compare Spin Systems", **kw)

        self.waiting = False

    def open(self):

        self.updateAfter()
        BasePopup.open(self)

    def body(self, guiFrame):

        self.geometry('800x530')

        guiFrame.grid_columnconfigure(0, weight=1)
        guiFrame.grid_rowconfigure(0, weight=1)
        guiFrame.grid_rowconfigure(1, weight=2)
        guiFrame.grid_rowconfigure(2, weight=1)

        isotopeFrame = LabelFrame(guiFrame, text='Isotope Shift Correction')
        isotopeFrame.grid(row=0, column=0, sticky='nsew')

        frameA = LabelFrame(guiFrame, text='Spin Systems')
        frameA.grid(row=1, column=0, sticky='nsew')

        frameA.grid_rowconfigure(0, weight=1)
        frameA.grid_columnconfigure(0,  weight=1)
        frameA.grid_columnconfigure(1,  weight=1)

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
        frameB.grid_columnconfigure(0,  weight=1)
        frameB.grid_columnconfigure(1,  weight=2)
        frameB.grid_columnconfigure(2,  weight=1)

        frameB1 = LabelFrame(frameB, text='Unique to Spin System 1')
        frameB1.grid(row=0, column=0, sticky='nsew')
        frameB1.expandGrid(0, 0)

        frameB2 = LabelFrame(frameB, text='Intersection')
        frameB2.grid(row=0, column=1, sticky='nsew')
        frameB2.expandGrid(0, 0)

        frameB3 = LabelFrame(frameB, text='Unique to Spin System 2')
        frameB3.grid(row=0, column=2, sticky='nsew')
        frameB3.expandGrid(0, 0)

        # Table A1

        headingList = ['#', 'shift lists', 'Assignment', 'overlapping']

        tipTexts = ['Spin System Serial', 'shift lists','The residue (tentatively) assigned to this spin system',
                    'The amount of spin systems that overlap with this spin system and have no violations']

        editWidgets = [None, None, None, None]

        editGetCallbacks = [self.updateTableA2, self.updateTableA2, self.updateTableA2, self.updateTableA2]

        editSetCallbacks = [None, None, None, None]

        self.tableA1 = ScrolledMatrix(frameA1, headingList=headingList,
                                      #editWidgets=editWidgets,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableA1.grid(row=0, column=0, sticky='nsew')

        # Table A2

        headingList = ['#', 'shift lists', 'Assignment', 'RMSD']
        tipTexts = ['Spin System Serial', 'The residue (tentatively) assigned to this spin system',
                    'Root mean squared deviation of this spin system to the spin system selected in the table on the left.']

        editWidgets = [None, None, None]

        editGetCallbacks = [self.updateCompareTables,
                            self.updateCompareTables,
                            self.updateCompareTables,
                            self.updateCompareTables]

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
        editWidgets = [None, None]
        editGetCallbacks = [None, None]
        editSetCallbacks = [None, None]
        self.tableB1 = ScrolledMatrix(frameB1, headingList=headingList,
                                      #callback=self.noAction,
                                      editWidgets=editWidgets,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableB1.grid(row=0, column=0, sticky='nsew')

        # Table B 2

        headingList = ['atom', 'c.s. 1',  'c.s. 2',  'delta c.s.']
        tipTexts = ['name of the atom',  'chemical shift of atom with this name in spin system 1',
                    'chemical shift of atom with this name in spin system 2',
                    'difference between the chemical shift of spin systems 1 and 2']
        editWidgets = [None, None, None, None]
        editGetCallbacks = [None, None, None, None]
        editSetCallbacks = [None, None, None, None]
        self.tableB2 = ScrolledMatrix(frameB2, headingList=headingList,
                                      editWidgets=editWidgets,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableB2.grid(row=0, column=0, sticky='nsew')

        # Table B 3

        headingList = ['atom', 'c.s.']
        tipTexts = ['atom', 'chemical shift.']
        editWidgets = [None, None]
        editGetCallbacks = [None, None]
        editSetCallbacks = [None, None]
        self.tableB3 = ScrolledMatrix(frameB3, headingList=headingList,
                                      #callback=self.noAction,
                                      editWidgets=editWidgets,
                                      multiSelect=False,
                                      editGetCallbacks=editGetCallbacks,
                                      editSetCallbacks=editSetCallbacks,
                                      tipTexts=tipTexts)
        self.tableB3.grid(row=0, column=0, sticky='nsew')

        self.matchMatrix = {}
        self.amountOfMatchesPerSpinSystem = {}

        self.updateTableA1()
        self.compareSpinSystems()
        self.updateTableA1()

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
                colorMatrix.append(['#298A08', '#298A08',
                                    '#298A08', '#298A08'])
            else:
                colorMatrix.append([None,  None,  None, None])

            data.append(oneRow)

        #datazip = zip(data)
        #data.sort(key=lambda x: x[2])

        data, objectList, colorMatrix = zip(*sorted(zip(data, objectList, colorMatrix), key=lambda x: x[0][3]))
        self.tableA2.update(objectList=objectList,
                            textMatrix=data,
                            colorMatrix=colorMatrix)

    def updateDiffTables(self, spinSystemMatch):

        shiftLists = getShiftLists(self.nmrProject)

        for diff, table in [(spinSystemMatch.difference1, self.tableB1),
                            (spinSystemMatch.difference2, self.tableB3)]:
            data = []
            for resonance in diff:
                data.append([makeResonanceGuiName(resonance),
                             resonance.findFirstShift().value])
                #print resonance.findFirstShift(parentList=shiftLists[1])
                print '---'
                print resonance.findAllShifts(parentList=shiftLists[0])
                print resonance.getShifts()

            table.update(objectList=data, textMatrix=data)

    def updateCompareTables(self,  obj):

        matching = self.matchMatrix[self.selectedSpinSystem1][obj]

        intersectData = []
        colorMatrix = []
        self.updateDiffTables(matching)

        for resonance1, resonance2, delta in zip(matching.intersectionResonances1,
                                                 matching.intersectionResonances2,
                                                 matching.intersectionDelta):

            oneRow = []

            # oneRow.append(resonance1.serial)
            # oneRow.append(resonance2.serial)

            colorMatrix.append(['#298A08', '#298A08', '#298A08', '#298A08'])

            if resonance1.assignNames:

                oneRow.append(resonance1.assignNames[0])

            else:

                oneRow.append('?')

            oneRow.append(resonance1.findFirstShift().value)
            oneRow.append(resonance2.findFirstShift().value)

            oneRow.append(delta)

            intersectData.append(oneRow)

        for resonance1, resonance2, delta in zip(matching.violation1,
                                                 matching.violation2,
                                                 matching.violationDelta):

            oneRow = []
            colorMatrix.append([None, None, None,  None])
            oneRow.append(makeResonanceString(resonance1))
            oneRow.append(resonance1.findFirstShift().value)
            oneRow.append(resonance2.findFirstShift().value)
            oneRow.append(delta)

            intersectData.append(oneRow)

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

                self.compare2spinSystems(spinSystem1,  spinSystem2)

    def compare2spinSystems(self,  spinSystem1,  spinSystem2):

        newMatch = SpinSystemMatch()

        newMatch.spinSystem1 = spinSystem1
        newMatch.spinSystem2 = spinSystem2

        for resonance1 in spinSystem1.resonances:

            for resonance2 in spinSystem2.resonances:

                if not (resonance1.assignNames and resonance2.assignNames):
                    continue
                if not (resonance1.assignNames[0] == resonance2.assignNames[0]):
                    continue
                if not (resonance1.findFirstShift() and resonance2.findFirstShift()):
                    continue

                delta = abs(resonance1.findFirstShift().value - resonance2.findFirstShift().value)

                if newMatch.deviation is None:
                    newMatch.deviation = 0
                newMatch.deviation += delta**2

                if delta < 0.5:

                    newMatch.intersectionResonances1.append(resonance1)
                    newMatch.intersectionResonances2.append(resonance2)
                    newMatch.intersectionDelta.append(delta)

                else:

                    newMatch.violation1.append(resonance1)
                    newMatch.violation2.append(resonance2)
                    newMatch.violationDelta.append(delta)

        for resonance1 in spinSystem1.resonances:

            if resonance1 not in newMatch.intersectionResonances1 + newMatch.violation1:

                newMatch.difference1.append(resonance1)

        for resonance2 in spinSystem2.resonances:

            if resonance2 not in newMatch.intersectionResonances2 + newMatch.violation2:

                newMatch.difference2.append(resonance2)

        if newMatch.deviation is not None and (newMatch.violation1 or newMatch.intersectionResonances1):
            newMatch.deviation = (float(
                newMatch.deviation) / (len(newMatch.intersectionResonances1) + len(newMatch.violation1)))**(0.5)

        if newMatch.intersectionResonances1 and not newMatch.violation1:

            newMatch.match = True

            if spinSystem1 in self.amountOfMatchesPerSpinSystem:

                self.amountOfMatchesPerSpinSystem[spinSystem1] += 1

            else:

                self.amountOfMatchesPerSpinSystem[spinSystem1] = 0

        if spinSystem1 in self.matchMatrix:

            self.matchMatrix[spinSystem1][spinSystem2] = newMatch

        else:

            self.matchMatrix[spinSystem1] = {spinSystem2: newMatch}


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


def makeResonanceString(resonance):
    if resonance.assignNames:
        return resonance.assignNames[0]
    else:
        return '[{}]'.format(resonance.serial)




class SpinSystemMatch(object):

    def __init__(self):

        self.spinSystem1 = None
        self.spinSystem2 = None

        self.match = False

        self.deviation = None

        self.intersectionResonances1 = []
        self.intersectionResonances2 = []
        self.intersectionDelta = []

        self.violation1 = []
        self.violation2 = []
        self.violationDelta = []

        self.difference1 = []
        self.difference2 = []

