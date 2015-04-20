from isotope_shift import correct_for_isotope_shift
import pytest


def test_correct_for_isotope_shift_raises_exception():
    with pytest.raises(ValueError):
        correct_for_isotope_shift('Leu', 'CD1', 30.0)


def test_correct_for_isotope_shift_correct_value_protonated():
    assert correct_for_isotope_shift('Ala', 'CA', 0.0) == -0.473


def test_correct_for_isotope_shift_correct_value_deuterated():
    assert correct_for_isotope_shift('Ala', 'CA', 0.0, deuterated=True) == 0.473
