import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from payments.service import PaymentService, calculate_tax
from payments.workflow import evaluate_payment, run_payment_flow


def test_charge():
    assert PaymentService().charge(100) == 110


def test_refund():
    assert PaymentService().refund(5) == -5


def test_tax():
    assert abs(calculate_tax(100) - 18) < 0.01


def test_evaluate_standard_payment():
    quote = evaluate_payment("standard", 100)
    assert quote.payment_type == "standard"
    assert quote.rate == Decimal("0.1")
    assert quote.fee == 10
    assert quote.total == 110


def test_evaluate_plants_payment():
    quote = evaluate_payment("plants", 100)
    assert quote.payment_type == "plants"
    assert quote.rate == Decimal("0.2")
    assert quote.fee == 20
    assert quote.total == 120


def test_evaluate_payment_rejects_invalid_values():
    for payment_type, amount in (("unknown", 100), ("standard", 0), ("plants", -1)):
        try:
            evaluate_payment(payment_type, amount)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid payment input was accepted.")


def test_run_payment_flow_retries_invalid_input_and_reports_total():
    answers = iter(("unknown", "plants", "invalid", "0", "100"))
    output = []

    quote = run_payment_flow(lambda _prompt: next(answers), output.append)

    assert quote.total == 120
    assert "Rate: 20%" in output
    assert "Fee: 20" in output
    assert "Total payment: 120" in output


if __name__ == "__main__":
    test_charge()
    test_refund()
    test_tax()
    test_evaluate_standard_payment()
    test_evaluate_plants_payment()
    test_evaluate_payment_rejects_invalid_values()
    test_run_payment_flow_retries_invalid_input_and_reports_total()
