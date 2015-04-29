'''Start-up script, should be loaded as a ccpn analysis Macro.
'''
from compare_spin_systems_gui import SpinSystemComparePopup


def start_spinsystem_compare(argServer):#
    '''Open the popup.'''
    SpinSystemComparePopup(argServer.parent)
