'''
CCPN Analysis macro that helps with comparing (isotope shifted) spin systems.


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

from memops.gui.LabelFrame import LabelFrame
from memops.gui.PulldownList import PulldownList
from memops.gui.CheckButton import CheckButton
from memops.gui.Label import Label
from memops.gui.ScrolledMatrix import ScrolledMatrix
from ccpnmr.analysis.popups.BasePopup import BasePopup
from ccpnmr.analysis.core.MoleculeBasic import getResidueCode
from ccpnmr.analysis.core.AssignmentBasic import getShiftLists
from compare_spin_systems import (SpinSystemComparison,
                                  find_all_shiftLists_for_resonanceGroup)


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
        headingList = ['#', 'shift lists', 'Assignment', 'offset']
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

        for shiftedShifts, table in [(spinSystemComp.unique_to_1, self.tableB1),
                                     (spinSystemComp.unique_to_2, self.tableB3)]:
            data = []
            for shiftedShift in shiftedShifts:

                data.append([shiftedShift.create_name(),
                             shiftedShift.create_shift_description()])

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
