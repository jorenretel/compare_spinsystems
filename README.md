# Compare Spinsystems
A small [CCPNMR Analysis](http://www.ccpn.ac.uk/software/analysis) plug-in that helps comparing spin systems to one another. For CA and CB chemical shifts the plug-in can correct for isotope shifts.

The user interface shows you two tables on top where you can select any two spin systems to compare. At the moment you select a spin system in the first table, the closest matching spin systems in terms of chemical shifts will appear in the second table. After selecting a spin system in the second table, the tables at the bottom show resonances types that are either unique to one of the spin systems or are present in both, in which case they are compared in the table in the middle.

![The graphical user interface of the plug-in](/img/compare_spin_systems_gui.png?raw=true)

To use this plug-in. Just clone this repository or download it as a zip-archive. Unpack it wherever you want. Open CCPN analysis and open this macro by clicking:

Menu -> Organize Macros -> Add Macro -> navigate to the location you unpacked the archive and select compare_spinSystems.py -> select the open_spinsystem_compare function in the bottom half of the menu -> Load Macro.

If everything is correct, the macro now appears in the list of macros and you can run it.

I use this tool to match up sets of spin systems from different experiments. To be more precise, I have a set of solid-state NMR 1H detected experiments that contain chemical shift information of H, N, Ca, and Cb resonances. Furthermore there is a set of 13C detected experiments that mostly contain carbon side chain resonance information. Both types of experiments are connected to different shift lists since the proton detected experiments are all recorded on samples where all non-exchangeable sides are deuterated, whereas the carbon detected experiments where all performed on fully protonated samples. I made a set of spin systems for each set of experiments because often it is not immediately clear to which spin system already present in the project signals in newer spectra belong. Sometimes it is easier to merge spin systems after one of them has already been assigned to a residue. Anyway, by merging spin systems I am effectively adding side chain chemical shift information to a assigned spin system that only contains backbone + CB resonances.

Of course other people might have different reasons for having double sets of spin systems in a project or wanting to compare spin systems. Hope this helps.



Copyright (C) 2015 Joren Retel

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see http://www.gnu.org/licenses/.

