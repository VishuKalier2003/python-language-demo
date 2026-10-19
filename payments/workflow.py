from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from payments.fee_by_five_service import FeeByFivePaymentService
from payments.service import PaymentService


@dataclass(frozen=True)
class PaymentQuote:
    payment_type: str
    amount: int
    rate: Decimal
    fee: int
    total: int


def evaluate_payment(payment_type: str, amount: int) -> PaymentQuote:
    normalized_type = payment_type.strip().lower()
    if normalized_type == "standard":
        service = PaymentService()
        divisor = 10
    elif normalized_type == "plants":
        service = FeeByFivePaymentService()
        divisor = 5
    else:
        raise ValueError("Payment type must be 'standard' or 'plants'.")

    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise ValueError("Payment amount must be a positive whole number.")

    return PaymentQuote(
        payment_type=normalized_type,
        amount=amount,
        rate=Decimal(1) / divisor,
        fee=service.fee(amount),
        total=service.charge(amount),
    )


def run_payment_flow(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> PaymentQuote:
    while True:
        payment_type = input_fn("Payment type (standard or plants): ").strip().lower()
        if payment_type in {"standard", "plants"}:
            break
        output_fn("Invalid payment type. Enter 'standard' or 'plants'.")

    while True:
        amount_text = input_fn("Payment amount (positive whole number): ").strip()
        try:
            amount = int(amount_text)
        except ValueError:
            output_fn("Invalid amount. Enter a positive whole number.")
            continue
        if amount <= 0:
            output_fn("Invalid amount. Enter a positive whole number.")
            continue
        break

    quote = evaluate_payment(payment_type, amount)
    output_fn(f"Payment type: {quote.payment_type}")
    output_fn(f"Amount: {quote.amount}")
    output_fn(f"Rate: {quote.rate:.0%}")
    output_fn(f"Fee: {quote.fee}")
    output_fn(f"Total payment: {quote.total}")
    return quote


if __name__ == "__main__":
    run_payment_flow()
