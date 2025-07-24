import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter
from database.models import GymDB
from datetime import date

# Arabic section names
# Add 'overview' section

titles = {
    'overview': 'نظرة عامة',
    'members': 'الأعضاء',
    'payments': 'المدفوعات',
    'monthly_payments': 'المدفوعات الشهرية',
    'insurance_payments': 'مدفوعات التأمين',
    'other_payments': 'مدفوعات أخرى',
    'transactions_history': 'سجل المعاملات',
    'settings': 'الإعدادات',
}

# Placeholder icons (use built-in Qt icons or replace with your own SVGs/PNGs)
icons = {
    'overview': QIcon.fromTheme('view-dashboard'),
    'members': QIcon.fromTheme('user-group'),
    'payments': QIcon.fromTheme('wallet'),
    'monthly_payments': QIcon.fromTheme('view-calendar'),
    'insurance_payments': QIcon.fromTheme('security-high'),
    'other_payments': QIcon.fromTheme('money'),
    'transactions_history': QIcon.fromTheme('view-list'),
    'settings': QIcon.fromTheme('settings'),
}

MATERIAL_PRIMARY = '#1976D2'  # Material Blue 700
MATERIAL_PRIMARY_LIGHT = '#E3F2FD'
MATERIAL_BG = '#FAFAFA'
MATERIAL_MENU_BG = '#F5F5F5'
MATERIAL_SUBMENU_BG = '#F0F4F8'
MATERIAL_ACTIVE = '#1565C0'  # Material Blue 800
MATERIAL_TEXT = '#222'
MATERIAL_FONT = 'Segoe UI, Arial, sans-serif'

ARABIC_HEADERS = [
    'الاسم الأول',  # First Name
    'اسم العائلة',  # Last Name
    'الجنس',        # Sex
    'المجموعة',     # Group
    'نوع التأمين',  # Insurance Type
]

class MenuButton(QPushButton):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(40)
        self.setFont(QFont(MATERIAL_FONT, 12))
        self.setStyleSheet(f'''
            QPushButton {{
                background: transparent;
                color: {MATERIAL_TEXT};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: right;
            }}
            QPushButton:hover {{
                background: {MATERIAL_PRIMARY_LIGHT};
            }}
        ''')
    def set_active(self, active):
        if active:
            self.setStyleSheet(f'''
                QPushButton {{
                    background: {MATERIAL_PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    text-align: right;
                    font-weight: bold;
                }}
            ''')
        else:
            self.setStyleSheet(f'''
                QPushButton {{
                    background: transparent;
                    color: {MATERIAL_TEXT};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    text-align: right;
                }}
                QPushButton:hover {{
                    background: {MATERIAL_PRIMARY_LIGHT};
                }}
            ''')

class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة عضو جديد')
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout()
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText('الاسم الأول')
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText('اسم العائلة')
        self.sex = QComboBox()
        self.sex.addItems(['ذكر', 'أنثى'])
        self.group = QComboBox()
        self.insurance_type = QComboBox()
        # Populate group and insurance type from DB
        db = GymDB()
        self.group.addItems([g['name'] for g in db.get_groups()])
        self.insurance_type.addItems([i['name'] for i in db.get_insurance_types()])
        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        layout.addWidget(self.sex)
        layout.addWidget(self.group)
        layout.addWidget(self.insurance_type)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
    def get_data(self):
        return {
            'first_name': self.first_name.text(),
            'last_name': self.last_name.text(),
            'sex': self.sex.currentText(),
            'group': self.group.currentText(),
            'insurance_type': self.insurance_type.currentText(),
        }

class MemberProfileWidget(QWidget):
    def __init__(self, first_name, last_name, back_callback, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel(f'هذا هو ملف {first_name} {last_name}')
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont(MATERIAL_FONT, 18, QFont.Bold))
        layout.addWidget(label)
        back_btn = QPushButton('العودة إلى قائمة الأعضاء')
        back_btn.setStyleSheet(f'background: {MATERIAL_PRIMARY}; color: white; font-weight: bold; border-radius: 8px; padding: 8px 24px; font-size: 13pt;')
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(back_callback)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gym Manager')
        self.resize(1100, 700)
        self.setStyleSheet(f'background: {MATERIAL_BG}; font-family: {MATERIAL_FONT};')
        self.active_section = 'overview'
        # Define EYE_ICON after QApplication is constructed
        self.EYE_ICON = QIcon.fromTheme('view-preview')
        if self.EYE_ICON.isNull():
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(Qt.black)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawEllipse(4, 8, 16, 8)
            painter.drawEllipse(10, 11, 4, 4)
            painter.end()
            self.EYE_ICON = QIcon(pixmap)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Right menu
        menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_widget.setLayout(menu_layout)
        menu_widget.setFixedWidth(300)
        menu_widget.setStyleSheet(f'background: {MATERIAL_MENU_BG}; border-top-left-radius: 16px; border-bottom-left-radius: 16px;')

        # Section buttons
        self.menu_buttons = {}
        self.submenu_buttons = {}

        # Overview (first section)
        btn_overview = MenuButton(titles['overview'], icons['overview'])
        btn_overview.clicked.connect(lambda: self.switch_section('overview'))
        menu_layout.addWidget(btn_overview)
        self.menu_buttons['overview'] = btn_overview

        # Members
        btn_members = MenuButton(titles['members'], icons['members'])
        btn_members.clicked.connect(lambda: self.switch_section('members'))
        menu_layout.addWidget(btn_members)
        self.menu_buttons['members'] = btn_members

        # Payments (with subsections)
        btn_payments = MenuButton(titles['payments'], icons['payments'])
        btn_payments.clicked.connect(lambda: self.switch_section('payments'))
        menu_layout.addWidget(btn_payments)
        self.menu_buttons['payments'] = btn_payments

        # Subsections (visually nested)
        sub_menu_container = QWidget()
        sub_menu_container.setStyleSheet(f'background: {MATERIAL_SUBMENU_BG}; border-radius: 8px;')
        sub_menu_layout = QVBoxLayout()
        sub_menu_layout.setContentsMargins(32, 0, 0, 0)
        sub_menu_layout.setSpacing(0)
        sub_menu_container.setLayout(sub_menu_layout)
        # Add a vertical line to the left of the submenu
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setLineWidth(2)
        line.setStyleSheet(f'color: {MATERIAL_PRIMARY_LIGHT}; background: {MATERIAL_PRIMARY_LIGHT};')
        sub_menu_layout.addWidget(line, alignment=Qt.AlignLeft)
        for key in ['monthly_payments', 'insurance_payments', 'other_payments']:
            btn = MenuButton(titles[key], icons[key])
            btn.setStyleSheet(f'''
                QPushButton {{
                    background: transparent;
                    color: {MATERIAL_TEXT};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 32px 8px 16px;
                    text-align: right;
                    font-size: 11.5pt;
                }}
                QPushButton:hover {{
                    background: {MATERIAL_PRIMARY_LIGHT};
                }}
            ''')
            btn.clicked.connect(lambda checked, k=key: self.switch_section(k))
            sub_menu_layout.addWidget(btn)
            self.submenu_buttons[key] = btn
        menu_layout.addWidget(sub_menu_container)

        # Transactions history
        btn_history = MenuButton(titles['transactions_history'], icons['transactions_history'])
        btn_history.clicked.connect(lambda: self.switch_section('transactions_history'))
        menu_layout.addWidget(btn_history)
        self.menu_buttons['transactions_history'] = btn_history

        # Settings
        btn_settings = MenuButton(titles['settings'], icons['settings'])
        btn_settings.clicked.connect(lambda: self.switch_section('settings'))
        menu_layout.addWidget(btn_settings)
        self.menu_buttons['settings'] = btn_settings

        menu_layout.addStretch()

        # Main content area
        self.stack = QStackedWidget()
        self.section_widgets = {}
        # Add all section widgets to the stack first
        for key in ['overview', 'members', 'monthly_payments', 'insurance_payments', 'other_payments', 'payments', 'transactions_history', 'settings']:
            w = QWidget()
            layout = QVBoxLayout()
            if key == 'members':
                # --- Filter and Search Bar ---
                filter_layout = QHBoxLayout()
                # Search bar
                search_bar = QLineEdit()
                search_bar.setPlaceholderText('بحث بالاسم...')
                search_bar.setFixedWidth(200)
                search_bar.setStyleSheet('font-size: 12pt; padding: 6px 12px; border-radius: 8px; border: 1px solid #bbb;')
                filter_layout.addWidget(search_bar)
                # Sex filter
                sex_filter = QComboBox()
                sex_filter.addItem('الجنس')
                sex_filter.addItems(['ذكر', 'أنثى'])
                sex_filter.setFixedWidth(100)
                filter_layout.addWidget(sex_filter)
                # Group filter
                group_filter = QComboBox()
                group_filter.addItem('المجموعة')
                db = GymDB()
                group_filter.addItems([g['name'] for g in db.get_groups()])
                group_filter.setFixedWidth(130)
                filter_layout.addWidget(group_filter)
                # Insurance type filter
                insurance_filter = QComboBox()
                insurance_filter.addItem('نوع التأمين')
                insurance_filter.addItems([i['name'] for i in db.get_insurance_types()])
                insurance_filter.setFixedWidth(130)
                filter_layout.addWidget(insurance_filter)
                filter_layout.addStretch()
                layout.addLayout(filter_layout)
                # Add New Member button
                add_btn = QPushButton('إضافة عضو جديد')
                add_btn.setStyleSheet(f'background: {MATERIAL_PRIMARY}; color: white; font-weight: bold; border-radius: 8px; padding: 8px 24px; font-size: 13pt;')
                add_btn.setCursor(Qt.PointingHandCursor)
                layout.addWidget(add_btn, alignment=Qt.AlignRight)
                # Members table
                table = QTableWidget()
                table.setColumnCount(6)
                table.setHorizontalHeaderLabels(['', *ARABIC_HEADERS])
                table.setRowCount(0)  # Will fill with data later
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.setLayoutDirection(Qt.RightToLeft)
                table.setStyleSheet('font-size: 13pt;')
                table.horizontalHeader().setStyleSheet(f'''
                    QHeaderView::section {{
                        background-color: {MATERIAL_PRIMARY};
                        color: white;
                        font-weight: bold;
                        font-size: 14pt;
                        border: none;
                        padding: 8px 0px;
                    }}
                ''')
                layout.addWidget(table)
                w.setLayout(layout)
                self.section_widgets[key] = w
                self.stack.addWidget(w)
                # Store widgets for later use
                self.members_table = table
                self.add_member_btn = add_btn
                self.members_search_bar = search_bar
                self.members_sex_filter = sex_filter
                self.members_group_filter = group_filter
                self.members_insurance_filter = insurance_filter
                self.members_profile_widget = None
            else:
                label = QLabel(f'This is the {key.replace("_", " ")} section')
                label.setAlignment(Qt.AlignCenter)
                label.setFont(QFont(MATERIAL_FONT, 18, QFont.Bold))
                layout.addWidget(label)
                w.setLayout(layout)
                self.section_widgets[key] = w
                self.stack.addWidget(w)

        # Add widgets to the main layout after all widgets are created
        main_layout.addWidget(self.stack)
        main_layout.addWidget(menu_widget)

        # Connect add member button
        self.add_member_btn.clicked.connect(self.open_add_member_dialog)
        # Connect search and filter signals
        self.members_search_bar.textChanged.connect(self.refresh_members_table)
        self.members_sex_filter.currentIndexChanged.connect(self.refresh_members_table)
        self.members_group_filter.currentIndexChanged.connect(self.refresh_members_table)
        self.members_insurance_filter.currentIndexChanged.connect(self.refresh_members_table)
        self.refresh_members_table()

        # Default section
        self.switch_section('overview')

    def switch_section(self, section):
        # Set all buttons to inactive
        for btn in self.menu_buttons.values():
            btn.set_active(False)
        for btn in self.submenu_buttons.values():
            btn.set_active(False)
        # Set the active button
        if section in self.menu_buttons:
            self.menu_buttons[section].set_active(True)
        elif section in self.submenu_buttons:
            self.submenu_buttons[section].set_active(True)
        # Find the widget index for the section
        widget = self.section_widgets.get(section)
        if widget:
            self.stack.setCurrentWidget(widget)
        self.active_section = section

    def open_add_member_dialog(self):
        dialog = AddMemberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            db = GymDB()
            # Find group_id and insurance_type_id
            group_id = next((g['id'] for g in db.get_groups() if g['name'] == data['group']), None)
            insurance_type_id = next((i['id'] for i in db.get_insurance_types() if i['name'] == data['insurance_type']), None)
            if group_id and insurance_type_id:
                # Use default values for missing fields
                db.add_member(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    cin='-',
                    birth_date='2000-01-01',
                    sex='M' if data['sex'] == 'ذكر' else 'F',
                    phone_number='-',
                    address='-',
                    enrollment_date=date.today().isoformat(),
                    group_id=group_id,
                    insurance_type_id=insurance_type_id,
                    emergency_contact_name='-',
                    emergency_contact_phone='-',
                    emergency_contact_relationship='other',
                    status='active'
                )
                QMessageBox.information(self, 'تمت الإضافة', 'تمت إضافة العضو بنجاح!')
                self.refresh_members_table()
            else:
                QMessageBox.warning(self, 'خطأ', 'تعذر العثور على المجموعة أو نوع التأمين.')

    def show_member_profile(self, first_name, last_name):
        if self.members_profile_widget:
            self.stack.removeWidget(self.members_profile_widget)
        self.members_profile_widget = MemberProfileWidget(first_name, last_name, self.back_to_members)
        self.stack.addWidget(self.members_profile_widget)
        self.stack.setCurrentWidget(self.members_profile_widget)

    def back_to_members(self):
        self.stack.setCurrentWidget(self.section_widgets['members'])

    def refresh_members_table(self):
        db = GymDB()
        members = db.get_members()
        # Sort by enrollment_date descending
        members.sort(key=lambda m: m['enrollment_date'], reverse=True)
        # Apply search and filters
        search_text = self.members_search_bar.text().strip()
        sex = self.members_sex_filter.currentText()
        group = self.members_group_filter.currentText()
        insurance = self.members_insurance_filter.currentText()
        filtered = []
        for m in members:
            group_name = next((g['name'] for g in db.get_groups() if g['id'] == m['group_id']), '')
            insurance_name = next((i['name'] for i in db.get_insurance_types() if i['id'] == m['insurance_type_id']), '')
            row_data = [m['first_name'], m['last_name'], 'ذكر' if m['sex'] == 'M' else 'أنثى', group_name, insurance_name]
            # Search by name
            if search_text and not (search_text in m['first_name'] or search_text in m['last_name']):
                continue
            # Filter by sex
            if sex != 'الجنس' and row_data[2] != sex:
                continue
            # Filter by group
            if group != 'المجموعة' and row_data[3] != group:
                continue
            # Filter by insurance type
            if insurance != 'نوع التأمين' and row_data[4] != insurance:
                continue
            filtered.append((m['first_name'], m['last_name'], *row_data))
        self.members_table.setRowCount(len(filtered))
        for row_idx, row_data in enumerate(filtered):
            first_name, last_name, *table_row = row_data
            # Eye icon button
            btn = QPushButton()
            btn.setIcon(self.EYE_ICON)
            btn.setToolTip('عرض الملف الشخصي')
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet('border: none;')
            btn.clicked.connect(lambda checked, fn=first_name, ln=last_name: self.show_member_profile(fn, ln))
            self.members_table.setCellWidget(row_idx, 0, btn)
            for col_idx, value in enumerate(table_row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.members_table.setItem(row_idx, col_idx + 1, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 