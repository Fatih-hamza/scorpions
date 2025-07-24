import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, date
import calendar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GymDB:
    def __init__(self, db_path: str = "gym_payments.db"):
        self.db_path = db_path
        # Do NOT call self.init_db() automatically. Only call it explicitly when needed.

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    def init_db(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            # Drop tables if they exist
            cursor.execute('DROP TABLE IF EXISTS insurance_payments')
            cursor.execute('DROP TABLE IF EXISTS monthly_payments')
            cursor.execute('DROP TABLE IF EXISTS members')
            cursor.execute('DROP TABLE IF EXISTS groups')
            cursor.execute('DROP TABLE IF EXISTS insurance_types')
            # Recreate groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    default_fee DECIMAL(10,2) NOT NULL
                )
            ''')
            # Recreate insurance_types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insurance_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    fee DECIMAL(10,2) NOT NULL
                )
            ''')
            # Insert initial data for groups
            cursor.executemany('''
                INSERT OR IGNORE INTO groups (name, default_fee) VALUES (?, ?)
            ''', [
                ("Cross-Fit", 120),
                ("Wushu-Sanda Children", 100),
                ("Wushu-Sanda Adults", 120)
            ])
            # Insert initial data for insurance_types
            cursor.executemany('''
                INSERT OR IGNORE INTO insurance_types (name, fee) VALUES (?, ?)
            ''', [
                ("Full-Contact", 150),
                ("Wushu-Sanda", 150),
                ("Full-contact & Wushu", 300),
                ("private", 200)
            ])
            # Create members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    cin VARCHAR(20) NOT NULL,
                    birth_date DATE NOT NULL,
                    sex TEXT CHECK(sex IN ('M', 'F')) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    address VARCHAR(255),
                    enrollment_date DATE NOT NULL,
                    group_id INTEGER NOT NULL,
                    insurance_type_id INTEGER NOT NULL,
                    emergency_contact_name VARCHAR(100),
                    emergency_contact_phone VARCHAR(20),
                    emergency_contact_relationship TEXT CHECK(emergency_contact_relationship IN ('father', 'mother', 'brother', 'sister', 'friend', 'other')),
                    status TEXT CHECK(status IN ('active', 'archived')) DEFAULT 'active',
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    FOREIGN KEY (insurance_type_id) REFERENCES insurance_types(id)
                )
            ''')
            # Create monthly_payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_date DATE NOT NULL,
                    month TEXT NOT NULL,
                    comment TEXT,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')
            # Create insurance_payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insurance_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_date DATE NOT NULL,
                    comment TEXT,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')
            conn.commit()

    # CRUD for Groups
    def add_group(self, name: str, default_fee: float) -> Optional[int]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO groups (name, default_fee) VALUES (?, ?)', (name, default_fee))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Error: Could not add group '{name}'. Reason: {e}. This group may already exist.")
            return None

    def get_groups(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM groups')
            return [dict(row) for row in cursor.fetchall()]

    def update_group(self, group_id: int, name: Optional[str] = None, default_fee: Optional[float] = None) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            if name is not None:
                fields.append('name = ?')
                values.append(name)
            if default_fee is not None:
                fields.append('default_fee = ?')
                values.append(default_fee)
            if not fields:
                return False
            values.append(group_id)
            cursor.execute(f'UPDATE groups SET {", ".join(fields)} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_group(self, group_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
            conn.commit()
            return cursor.rowcount > 0

    # CRUD for Insurance Types
    def add_insurance_type(self, name: str, fee: float) -> Optional[int]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO insurance_types (name, fee) VALUES (?, ?)', (name, fee))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Error: Could not add insurance type '{name}'. Reason: {e}. This insurance type may already exist.")
            return None

    def get_insurance_types(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM insurance_types')
            return [dict(row) for row in cursor.fetchall()]

    def update_insurance_type(self, insurance_id: int, name: Optional[str] = None, fee: Optional[float] = None) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            if name is not None:
                fields.append('name = ?')
                values.append(name)
            if fee is not None:
                fields.append('fee = ?')
                values.append(fee)
            if not fields:
                return False
            values.append(insurance_id)
            cursor.execute(f'UPDATE insurance_types SET {", ".join(fields)} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_insurance_type(self, insurance_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM insurance_types WHERE id = ?', (insurance_id,))
            conn.commit()
            return cursor.rowcount > 0

    # CRUD for Members
    def add_member(self, first_name: str, last_name: str, cin: str, birth_date: str, sex: str,
                   phone_number: str, address: str, enrollment_date: str, group_id: int, insurance_type_id: int,
                   emergency_contact_name: str, emergency_contact_phone: str, emergency_contact_relationship: str,
                   status: str = 'active') -> Optional[int]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO members (
                        first_name, last_name, cin, birth_date, sex, phone_number, address, enrollment_date,
                        group_id, insurance_type_id, emergency_contact_name, emergency_contact_phone,
                        emergency_contact_relationship, status, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    first_name, last_name, cin, birth_date, sex, phone_number, address, enrollment_date,
                    group_id, insurance_type_id, emergency_contact_name, emergency_contact_phone,
                    emergency_contact_relationship, status, datetime.now()
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The group_id or insurance_type_id does not exist. Please provide valid IDs.")
            else:
                print(f"Error: Could not add member '{first_name} {last_name}'. Reason: {e}.")
            return None
        except Exception as e:
            print(f"Unexpected error when adding member: {e}")
            return None

    def get_members(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM members')
            return [dict(row) for row in cursor.fetchall()]

    def get_member_by_id(self, member_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM members WHERE id = ?', (member_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_member(self, member_id: int, **kwargs) -> bool:
        valid_fields = [
            'first_name', 'last_name', 'cin', 'birth_date', 'sex', 'phone_number', 'address',
            'enrollment_date', 'group_id', 'insurance_type_id', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship', 'status'
        ]
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_fields:
            print("No valid fields provided for update.")
            return False
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                set_clause = ', '.join([f'{field} = ?' for field in update_fields.keys()])
                values = list(update_fields.values()) + [member_id]
                cursor.execute(f'UPDATE members SET {set_clause} WHERE id = ?', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The group_id or insurance_type_id does not exist. Please provide valid IDs.")
            else:
                print(f"Error updating member: {e}")
            return False
        except Exception as e:
            print(f"Error updating member: {e}")
            return False

    def delete_member(self, member_id: int) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM members WHERE id = ?', (member_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting member: {e}")
            return False

    # CRUD for Monthly Payments
    def add_monthly_payment(self, member_id: int, amount: Optional[float] = None, payment_date: Optional[str] = None,
                            month: Optional[str] = None, comment: Optional[str] = None) -> Optional[int]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                # Get default amount if not provided
                if amount is None:
                    cursor.execute('''
                        SELECT g.default_fee FROM members m JOIN groups g ON m.group_id = g.id WHERE m.id = ?
                    ''', (member_id,))
                    row = cursor.fetchone()
                    if row:
                        amount = row[0]
                    else:
                        print("Error: Member not found or group not found for default fee.")
                        return None
                # Default payment_date is today
                if payment_date is None:
                    payment_date = date.today().isoformat()
                # Default month is current month name
                if month is None:
                    month = calendar.month_name[date.today().month]
                cursor.execute('''
                    INSERT INTO monthly_payments (member_id, amount, payment_date, month, comment, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (member_id, amount, payment_date, month, comment, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error: Could not add monthly payment. Reason: {e}.")
            return None
        except Exception as e:
            print(f"Unexpected error when adding monthly payment: {e}")
            return None

    def get_monthly_payments(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mp.*, m.first_name, m.last_name, g.name AS group_name
                FROM monthly_payments mp
                JOIN members m ON mp.member_id = m.id
                JOIN groups g ON m.group_id = g.id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_monthly_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM monthly_payments WHERE id = ?', (payment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_monthly_payment(self, payment_id: int, **kwargs) -> bool:
        valid_fields = ['member_id', 'amount', 'payment_date', 'month', 'comment']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        # If month is provided as a date, convert to month name
        if 'month' in update_fields:
            try:
                m = update_fields['month']
                if len(m) == 10 and '-' in m:
                    y, mo, d = m.split('-')
                    update_fields['month'] = calendar.month_name[int(mo)]
            except Exception:
                pass
        if not update_fields:
            print("No valid fields provided for update.")
            return False
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                set_clause = ', '.join([f'{field} = ?' for field in update_fields.keys()])
                set_clause += ', recorded_at = ?'
                values = list(update_fields.values()) + [datetime.now(), payment_id]
                cursor.execute(f'UPDATE monthly_payments SET {set_clause} WHERE id = ?', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error updating monthly payment: {e}")
            return False
        except Exception as e:
            print(f"Error updating monthly payment: {e}")
            return False

    def delete_monthly_payment(self, payment_id: int) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM monthly_payments WHERE id = ?', (payment_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting monthly payment: {e}")
            return False

    def add_insurance_payment(self, member_id: int, amount: float = None, payment_date: str = None, comment: str = None) -> int:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                # Get default amount if not provided
                if amount is None:
                    cursor.execute('''
                        SELECT it.fee FROM members m JOIN insurance_types it ON m.insurance_type_id = it.id WHERE m.id = ?
                    ''', (member_id,))
                    row = cursor.fetchone()
                    if row:
                        amount = row[0]
                    else:
                        print("Error: Member not found or insurance type not found for default fee.")
                        return None
                # Default payment_date is today
                if payment_date is None:
                    payment_date = date.today().isoformat()
                cursor.execute('''
                    INSERT INTO insurance_payments (member_id, amount, payment_date, comment, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (member_id, amount, payment_date, comment, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error: Could not add insurance payment. Reason: {e}.")
            return None
        except Exception as e:
            print(f"Unexpected error when adding insurance payment: {e}")
            return None

    def get_insurance_payments(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ip.*, m.first_name, m.last_name, it.name AS insurance_type_name
                FROM insurance_payments ip
                JOIN members m ON ip.member_id = m.id
                JOIN insurance_types it ON m.insurance_type_id = it.id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_insurance_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM insurance_payments WHERE id = ?', (payment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_insurance_payment(self, payment_id: int, **kwargs) -> bool:
        valid_fields = ['member_id', 'amount', 'payment_date', 'comment']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_fields:
            print("No valid fields provided for update.")
            return False
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                set_clause = ', '.join([f'{field} = ?' for field in update_fields.keys()])
                set_clause += ', recorded_at = ?'
                values = list(update_fields.values()) + [datetime.now(), payment_id]
                cursor.execute(f'UPDATE insurance_payments SET {set_clause} WHERE id = ?', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error updating insurance payment: {e}")
            return False
        except Exception as e:
            print(f"Error updating insurance payment: {e}")
            return False

    def delete_insurance_payment(self, payment_id: int) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM insurance_payments WHERE id = ?', (payment_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting insurance payment: {e}")
            return False

    def add_other_payment(self, member_id: int, amount: float, payment_date: str, transaction_type: str, comment: str = None) -> int:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO other_payments (member_id, amount, payment_date, transaction_type, comment, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (member_id, amount, payment_date, transaction_type, comment, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error: Could not add other payment. Reason: {e}.")
            return None
        except Exception as e:
            print(f"Unexpected error when adding other payment: {e}")
            return None

    def get_other_payments(self) -> List[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT op.*, m.first_name, m.last_name
                FROM other_payments op
                JOIN members m ON op.member_id = m.id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_other_payment_by_id(self, payment_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM other_payments WHERE id = ?', (payment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_other_payment(self, payment_id: int, **kwargs) -> bool:
        valid_fields = ['member_id', 'amount', 'payment_date', 'transaction_type', 'comment']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_fields:
            print("No valid fields provided for update.")
            return False
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                set_clause = ', '.join([f'{field} = ?' for field in update_fields.keys()])
                set_clause += ', recorded_at = ?'
                values = list(update_fields.values()) + [datetime.now(), payment_id]
                cursor.execute(f'UPDATE other_payments SET {set_clause} WHERE id = ?', values)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY constraint failed' in str(e):
                print("Error: The member_id does not exist. Please provide a valid member ID.")
            else:
                print(f"Error updating other payment: {e}")
            return False
        except Exception as e:
            print(f"Error updating other payment: {e}")
            return False

    def delete_other_payment(self, payment_id: int) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM other_payments WHERE id = ?', (payment_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting other payment: {e}")
            return False

    def add_other_payments_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS other_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_date DATE NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    comment TEXT,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')
            conn.commit()

    def get_member_statistics(self) -> dict:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'active'")
            active = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'archived'")
            archived = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM members")
            total = cursor.fetchone()[0]
            return {
                'active': active,
                'archived': archived,
                'total': total,
                'active_ratio': f"{active}/{total}" if total > 0 else "0/0"
            }

    def get_monthly_payment_coverage(self) -> dict:
        import calendar
        from datetime import date
        with self._connect() as conn:
            cursor = conn.cursor()
            # Get current month name
            current_month = calendar.month_name[date.today().month]
            # Count unique members who paid for the current month
            cursor.execute("""
                SELECT COUNT(DISTINCT member_id) FROM monthly_payments WHERE month = ?
            """, (current_month,))
            paid_members = cursor.fetchone()[0]
            # Count active members
            cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'active'")
            active_members = cursor.fetchone()[0]
            percent = (paid_members / active_members * 100) if active_members > 0 else 0
            return {
                'paid_members': paid_members,
                'active_members': active_members,
                'percentage': percent
            }

    def get_unpaid_insurance_count(self) -> dict:
        with self._connect() as conn:
            cursor = conn.cursor()
            # Count active members
            cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'active'")
            active_members = cursor.fetchone()[0]
            # Count unique members who have made an insurance payment
            cursor.execute("SELECT COUNT(DISTINCT member_id) FROM insurance_payments")
            paid_members = cursor.fetchone()[0]
            unpaid = active_members - paid_members
            return {
                'active_members': active_members,
                'paid_members': paid_members,
                'unpaid_members': unpaid,
                'percentage': f"{unpaid}/{active_members}" if active_members > 0 else "0/0"
            }

    def get_new_members_this_month(self) -> int:
        from datetime import date
        with self._connect() as conn:
            cursor = conn.cursor()
            today = date.today()
            year = today.year
            month = today.month
            # SQLite strftime('%Y', ...) and strftime('%m', ...) for year and month
            cursor.execute('''
                SELECT COUNT(*) FROM members
                WHERE status = 'active'
                  AND strftime('%Y', enrollment_date) = ?
                  AND strftime('%m', enrollment_date) = ?
            ''', (str(year), f"{month:02d}"))
            count = cursor.fetchone()[0]
            return count

    def get_unpaid_members_for_month(self, month_number: int) -> list:
        import calendar
        if not (1 <= month_number <= 12):
            print("Invalid month number. Must be between 1 and 12.")
            return []
        month_name = calendar.month_name[month_number]
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Get IDs of active members who did not pay for the given month
            cursor.execute('''
                SELECT * FROM members
                WHERE status = 'active'
                  AND id NOT IN (
                      SELECT member_id FROM monthly_payments WHERE month = ?
                  )
            ''', (month_name,))
            return [dict(row) for row in cursor.fetchall()]

    def get_unpaid_insurance_members(self) -> list:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM members
                WHERE status = 'active'
                  AND id NOT IN (
                      SELECT member_id FROM insurance_payments
                  )
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_all_payments_for_member(self, member_id: int) -> list:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            payments = []
            # Monthly payments
            cursor.execute('''
                SELECT member_id, payment_date, 'monthly' AS payment_type, amount, comment
                FROM monthly_payments
                WHERE member_id = ?
            ''', (member_id,))
            payments.extend([dict(row) for row in cursor.fetchall()])
            # Insurance payments
            cursor.execute('''
                SELECT member_id, payment_date, 'insurance' AS payment_type, amount, comment
                FROM insurance_payments
                WHERE member_id = ?
            ''', (member_id,))
            payments.extend([dict(row) for row in cursor.fetchall()])
            # Other payments
            cursor.execute('''
                SELECT member_id, payment_date, 
                    CASE 
                        WHEN transaction_type IS NOT NULL THEN transaction_type
                        ELSE 'other'
                    END AS payment_type, 
                    amount, comment
                FROM other_payments
                WHERE member_id = ?
            ''', (member_id,))
            payments.extend([dict(row) for row in cursor.fetchall()])
            # Sort by payment_date (optional)
            payments.sort(key=lambda x: x['payment_date'])
            return payments

def send_whatsapp_reminders(phone_numbers: list, message: str = "Hi member, this is a reminder to pay your gym fees."):
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com/")
    try:
        # Wait for either the popup or the search bar
        WebDriverWait(driver, 120).until(
            lambda d: (
                d.find_elements(By.XPATH, '//button[.//span[text()="Continue" or text()="Continuer" or text()="OK" or text()="Ok" or text()="Got it" or text()="D\'accord"]]') or
                d.find_elements(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
        )
        # Check for popup
        popups = driver.find_elements(By.XPATH, '//button[.//span[text()="Continue" or text()="Continuer" or text()="OK" or text()="Ok" or text()="Got it" or text()="D\'accord"]]')
        if popups:
            popups[0].click()
            print("Closed popup.")
            # Wait for the search bar after closing popup
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
        else:
            print("No popup detected. Proceeding to send messages...")
        print("Logged in to WhatsApp Web. Starting to send messages...")
    except Exception as e:
        print("Login to WhatsApp Web failed or timed out.")
        driver.quit()
        return

    for number in phone_numbers:
        url = f"https://web.whatsapp.com/send?phone={number}"
        driver.get(url)
        try:
            # Wait for the chat header (contact name) to ensure chat is loaded
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//header//span[@title]'))
            )
            # Now wait for the message box at the bottom
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//footer//div[@contenteditable="true" and @data-tab]'))
            )
            time.sleep(1)
            message_box = driver.find_element(By.XPATH, '//footer//div[@contenteditable="true" and @data-tab]')
            message_box.click()
            message_box.send_keys(Keys.CONTROL, 'a')
            message_box.send_keys(Keys.DELETE)
            time.sleep(0.2)
            message_box.send_keys(message)
            time.sleep(0.2)
            message_box.send_keys(Keys.ENTER)
            print(f"Message sent to {number}")
            time.sleep(2)
        except Exception as e:
            print(f"Failed to send to {number}: {e}")

    driver.quit()

  