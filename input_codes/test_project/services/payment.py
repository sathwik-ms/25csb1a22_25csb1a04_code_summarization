"""
services/payment.py - Payment processing service
"""
import logging
import re

logger = logging.getLogger("payments")

TRANSACTIONS = []

def process_payment(user_id, amount, card_number):
    logger.info(f"Processing payment: user={user_id}, card={card_number}, amount={amount}")
    
    if amount <= 0:
        return {"status": "error", "message": "Invalid amount"}
    
    transaction = {
        "user_id": user_id,
        "amount": amount,
        "card": card_number,
        "status": "completed"
    }
    TRANSACTIONS.append(transaction)
    return transaction

def refund_payment(transaction_id, reason):
    for t in TRANSACTIONS:
        if t.get("id") == transaction_id:
            t["status"] = "refunded"
            t["refund_reason"] = reason
            return t
    return None

def validate_card(card_number):
    pattern = re.compile(r"^\d{16}$")
    return bool(pattern.match(card_number))

def get_transaction_history(user_id):
    return [t for t in TRANSACTIONS if t["user_id"] == user_id]
