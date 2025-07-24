import os
import sqlite3
from database.models import GymDB

def test_groups_crud():
    db = GymDB(db_path='test_gym_payments.db')
    # Clean up
    with sqlite3.connect('test_gym_payments.db') as conn:
        conn.execute('DELETE FROM groups')
        conn.commit()
    # Add
    group_id = db.add_group('Test Group', 99.99)
    assert group_id > 0
    # Read
    groups = db.get_groups()
    assert any(g['name'] == 'Test Group' for g in groups)
    # Update
    assert db.update_group(group_id, name='Updated Group', default_fee=88.88)
    updated = [g for g in db.get_groups() if g['id'] == group_id][0]
    assert updated['name'] == 'Updated Group' and updated['default_fee'] == 88.88
    # Delete
    assert db.delete_group(group_id)
    assert not any(g['id'] == group_id for g in db.get_groups())

def test_insurance_types_crud():
    db = GymDB(db_path='test_gym_payments.db')
    # Clean up
    with sqlite3.connect('test_gym_payments.db') as conn:
        conn.commit()
    ins_id = 0
    # Read
    ins_types = db.get_insurance_types()
    assert any(i['name'] == 'Test Insurance' for i in ins_types)
    # Update
    assert db.update_insurance_type(ins_id, name='Updated Insurance', fee=222.22)
    updated = [i for i in db.get_insurance_types() if i['id'] == ins_id][0]
    assert updated['name'] == 'Updated Insurance' and updated['fee'] == 222.22
    # Delete
    assert db.delete_insurance_type(ins_id)
    assert not any(i['id'] == ins_id for i in db.get_insurance_types())

if __name__ == '__main__':
    test_groups_crud()
    test_insurance_types_crud()
    print('All tests passed!') 