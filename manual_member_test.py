from database.models import GymDB
from datetime import date, timedelta
import random

# Helper data for diversity
first_names = ["Ali", "Sara", "Youssef", "Fatima", "Omar", "Aya", "Hassan", "Lina", "Karim", "Salma"]
last_names = ["Ben Salah", "El Amrani", "Bennani", "El Idrissi", "Mouline", "Alaoui", "Chakiri", "Naciri", "El Fassi", "Berrada"]
sexes = ["M", "F"]
group_ids = [1, 2, 3]  # Cross-Fit, Wushu-Sanda Children, Wushu-Sanda Adults
insurance_type_ids = [1, 2, 3, 4]  # Full-Contact, Wushu-Sanda, Full-contact & Wushu, private
relationships = ["father", "mother", "brother", "sister", "friend", "other"]
addresses = ["123 Main St", "456 Elm St", "789 Cedar Ave", "1010 Palm Rd", "2020 Oak Blvd"]

# Generate 40 diverse members
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

db = GymDB()

for i in range(40):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    cin = f"CIN{1000+i}"
    birth = random_date(date(1980, 1, 1), date(2015, 12, 31)).isoformat()
    sex = random.choice(sexes)
    phone = f"06{random.randint(10000000, 99999999)}"
    address = random.choice(addresses)
    enroll = random_date(date(2020, 1, 1), date.today()).isoformat()
    group_id = random.choice(group_ids)
    insurance_type_id = random.choice(insurance_type_ids)
    ec_name = random.choice(first_names) + " " + random.choice(last_names)
    ec_phone = f"06{random.randint(10000000, 99999999)}"
    ec_rel = random.choice(relationships)
    status = random.choice(["active", "archived"])
    db.add_member(
        first_name=fn,
        last_name=ln,
        cin=cin,
        birth_date=birth,
        sex=sex,
        phone_number=phone,
        address=address,
        enrollment_date=enroll,
        group_id=group_id,
        insurance_type_id=insurance_type_id,
        emergency_contact_name=ec_name,
        emergency_contact_phone=ec_phone,
        emergency_contact_relationship=ec_rel,
        status=status
    )

print("Added 40 diverse members for testing.")





"""
# 5. Delete member
if member_id:
    db.delete_member(member_id)
    print(f"\nDeleted member with ID {member_id}. Current members:")
    for m in db.get_members():
        print(m) 


"""