import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from payments.service import PaymentService, calculate_tax


def test_charge():
    assert PaymentService().charge(100) == 110


def test_refund():
    assert PaymentService().refund(5) == -5


def test_tax():
    assert abs(calculate_tax(100) - 18) < 0.01


if __name__ == "__main__":
    test_charge()
    test_refund()
    test_tax()
