from database.models import GymDB
from datetime import date

db = GymDB()


payment_id = 1


if payment_id:
    db.delete_other_payment(payment_id)
    print(f"\nDeleted other payment with ID {payment_id}. Current payments:")
    for p in db.get_other_payments():
        print(p) 

