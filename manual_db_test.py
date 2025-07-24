from database.models import GymDB

# Initialize the database manager (uses gym_payments.db by default)
db = GymDB()

p = db.get_unpaid_members_for_month(7) 
for member in p:
    print(member['id'])

print("--------------------------------")
print(len(p))
