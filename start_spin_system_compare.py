'''Start-up script
'''
from compare_spin_systems_gui import SpinSystemComparePopup

def start_spinsystem_compare(argServer):
    SpinSystemComparePopup(argServer.parent)