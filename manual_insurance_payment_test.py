from database.models import GymDB
from datetime import date

db = GymDB()

# 1. Add a new insurance payment for a valid member

payment_id = 2



if payment_id:
    db.delete_insurance_payment(payment_id)
    print(f"\nDeleted insurance payment with ID {payment_id}. Current payments:")
    for p in db.get_insurance_payments():
        print(p) 

       