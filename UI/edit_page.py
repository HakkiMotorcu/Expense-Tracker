import sys, json, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QComboBox, QDoubleSpinBox, QDateEdit
)
from PyQt6.QtCore import (Qt, QDate)

# JSON file paths
EXPENSES_FILE = os.path.join("data", "expenses.json")
PAYMENTS_FILE = os.path.join("data", "payments.json")
STORES_PRODUCTS_FILE = os.path.join("data", "stores_products.json")
USERS_FILE = os.path.join("data", "users.json")

class EditPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Create UI components."""
        self.main_layout = QVBoxLayout(self)

        # Return button with emoji
        
        # Tab widget for different sections
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Expenses tab with emoji in the label
        self.expenses_tab = self.create_expenses_tab()
        self.tabs.addTab(self.expenses_tab, "💸 Masraflar")

        # Payments tab with emoji in the label
        self.payments_tab = self.create_payments_tab()
        self.tabs.addTab(self.payments_tab, "💰 Ödemeler")

        # Stores tab with emoji in the label
        self.stores_tab = self.create_stores_tab()
        self.tabs.addTab(self.stores_tab, "🏪 Mağazalar")

        # Products tab with emoji in the label
        self.products_tab = self.create_products_tab()
        self.tabs.addTab(self.products_tab, "🛍️ Ürünler")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.return_button = QPushButton("⬅️ Geri Dön")
        self.return_button.clicked.connect(self.return_to_summary)
        self.main_layout.addWidget(self.return_button, alignment=Qt.AlignmentFlag.AlignLeft)


    def on_tab_changed(self, index):
        """Load data for the selected tab."""
        if index == 0:  # Expenses tab
            self.load_expenses()
        elif index == 1:  # Payments tab
            self.load_payments()
        elif index == 2:  # Stores tab
            self.load_stores()
        elif index == 3:  # Products tab
            self.load_products()
   
    def create_expenses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.filter_layout_1 = QHBoxLayout()
        self.filter_layout_2 = QHBoxLayout()
        # Add a location filter dropdown below the search box:

        self.location_filter_label = QLabel("📍 Konuma Göre Filtrele:")
        self.location_filter_dropdown = QComboBox()
        self.location_filter_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.location_filter_dropdown.addItem("Tüm Lokasyonlar")  # "All Locations"
        self.location_filter_dropdown.currentIndexChanged.connect(self.apply_location_filter)
        
        self.filter_layout_1.addWidget(self.location_filter_label)
        self.filter_layout_1.addWidget(self.location_filter_dropdown)
        layout.addLayout(self.filter_layout_1)

        # Add a Total Amount range filter below the search box:
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Toplam Tutar Aralığı:"))

        self.expense_min_spin = QDoubleSpinBox()
        self.expense_min_spin.setPrefix("₺")
        self.expense_min_spin.setDecimals(2)
        self.expense_min_spin.valueChanged.connect(self.apply_expense_range_filter)
        range_layout.addWidget(self.expense_min_spin)

        self.expense_max_spin = QDoubleSpinBox()
        self.expense_max_spin.setPrefix("₺")
        self.expense_max_spin.setDecimals(2)
        self.expense_max_spin.valueChanged.connect(self.apply_expense_range_filter)
        range_layout.addWidget(self.expense_max_spin)

        layout.addLayout(range_layout)


        # Add a "Paid By" filter dropdown below the location filter:
        self.paid_by_filter_label = QLabel("👤 Ödeyene Göre Filtrele:")
        self.paid_by_filter_dropdown = QComboBox()
        self.paid_by_filter_dropdown.addItem("Tüm Ödeyenler")  # "All Payers"
        self.paid_by_filter_dropdown.currentIndexChanged.connect(self.apply_paid_by_filter)
        self.filter_layout_1.addWidget(self.paid_by_filter_label)
        self.filter_layout_1.addWidget(self.paid_by_filter_dropdown)
        layout.addLayout(self.filter_layout_1)

        # Add a date range filter layout:
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Tarih Aralığı:"))

        self.expense_start_date = QDateEdit()
        self.expense_start_date.setCalendarPopup(True)
        self.expense_start_date.setDisplayFormat("yyyy-MM-dd")
        # Set default start date (e.g., one month ago)
        self.expense_start_date.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(self.expense_start_date)

        self.expense_end_date = QDateEdit()
        self.expense_end_date.setCalendarPopup(True)
        self.expense_end_date.setDisplayFormat("yyyy-MM-dd")
        # Set default end date to today
        self.expense_end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.expense_end_date)

        # Connect both date edits to the filtering method:
        self.expense_start_date.dateChanged.connect(self.apply_expense_date_filter)
        self.expense_end_date.dateChanged.connect(self.apply_expense_date_filter)

        layout.addLayout(date_range_layout)


        # Expenses table with emoji in headers
        self.expenses_table = QTableWidget(0, 4)
        self.expenses_table.setHorizontalHeaderLabels(["📍 Konum", "👤 Ödeyen", "💸 Toplam Tutar", "📅 Tarih"])
        layout.addWidget(self.expenses_table)
        self.expenses_table.cellDoubleClicked.connect(self.open_expense_detail)


        
        
        # Load expenses data
        self.load_expenses()
        return widget

    def create_payments_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Add a filter dropdown for the "from" column:
        self.from_filter_label = QLabel("📤 Gönderene Göre Filtrele:")
        self.from_filter_dropdown = QComboBox()
        self.from_filter_dropdown.addItem("Tüm Gönderenler")
        self.from_filter_dropdown.currentIndexChanged.connect(self.apply_payments_filters)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.from_filter_label)
        filter_layout.addWidget(self.from_filter_dropdown)


        # Add a filter dropdown for the "to" column:
        self.to_filter_label = QLabel("📥 Alana Göre Filtrele:")
        self.to_filter_dropdown = QComboBox()
        self.to_filter_dropdown.addItem("Tüm Alanlar")
        self.to_filter_dropdown.currentIndexChanged.connect(self.apply_payments_filters)
        filter_layout.addWidget(self.to_filter_label)
        filter_layout.addWidget(self.to_filter_dropdown) 

        layout.addLayout(filter_layout)

        money_range_layout = QHBoxLayout()
        money_range_layout.addWidget(QLabel("Tutar Aralığı:"))

        self.payments_min_spin = QDoubleSpinBox()
        self.payments_min_spin.setPrefix("₺")
        self.payments_min_spin.setDecimals(2)
        self.payments_min_spin.valueChanged.connect(self.apply_payments_filters)
        money_range_layout.addWidget(self.payments_min_spin)

        self.payments_max_spin = QDoubleSpinBox()
        self.payments_max_spin.setPrefix("₺")
        self.payments_max_spin.setDecimals(2)
        self.payments_max_spin.valueChanged.connect(self.apply_payments_filters)
        money_range_layout.addWidget(self.payments_max_spin)

        layout.addLayout(money_range_layout)

        date_range_layout = QHBoxLayout()
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Tarih Aralığı:"))

        self.payments_start_date = QDateEdit()
        self.payments_start_date.setCalendarPopup(True)
        self.payments_start_date.setDisplayFormat("yyyy-MM-dd")
        self.payments_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.payments_start_date.setMaximumDate(QDate.currentDate().addDays(1))
        self.payments_start_date.dateChanged.connect(self.apply_payments_filters)
        date_range_layout.addWidget(self.payments_start_date)

        self.payments_end_date = QDateEdit()
        self.payments_end_date.setCalendarPopup(True)
        self.payments_end_date.setDisplayFormat("yyyy-MM-dd")
        self.payments_end_date.setDate(QDate.currentDate())
        self.payments_end_date.setMaximumDate(QDate.currentDate().addDays(1))
        self.payments_end_date.dateChanged.connect(self.apply_payments_filters)
        date_range_layout.addWidget(self.payments_end_date)

        layout.addLayout(date_range_layout)



        # Payments table with emoji in headers
        self.payments_table = QTableWidget(0, 5)
        self.payments_table.setHorizontalHeaderLabels(["📤 Kimden", "📥 Kime", "💰 Tutar", "📅 Tarih", "⏰ Saat"])
        layout.addWidget(self.payments_table)

        # Load payments data
        self.load_payments()
        return widget

    def create_stores_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search box for stores
        self.stores_search = QLineEdit()
        self.stores_search.setPlaceholderText("🏪 Mağaza ile ara...")
        self.stores_search.textChanged.connect(lambda text: self.filter_table(self.stores_table, text))
        layout.addWidget(self.stores_search)

        # Stores table with emoji in headers
        self.stores_table = QTableWidget(0, 2)
        self.stores_table.setHorizontalHeaderLabels(["🏪 Mağaza", "🛒 Ürün Sayısı"])
        layout.addWidget(self.stores_table)

        # Load stores data
        self.load_stores()
        return widget

    def create_products_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search box for products
        self.products_search = QLineEdit()
        self.products_search.setPlaceholderText("🛍️ Ürün adı, 📦 Tür veya 💲 Fiyat ile ara...")
        self.products_search.textChanged.connect(lambda text: self.filter_table(self.products_table, text))
        layout.addWidget(self.products_search)

        # Products table with emoji in headers
        self.products_table = QTableWidget(0, 4)
        self.products_table.setHorizontalHeaderLabels(["🛍️ Ürün", "📦 Tür", "💲 Son Fiyat", "📜 Fiyat Geçmişi"])
        layout.addWidget(self.products_table)

        # Load products data
        self.load_products()
        return widget

    def load_expenses(self):
        data = self.load_json(EXPENSES_FILE)
        expenses = data.get("expenses", [])
        self.expenses_table.setRowCount(0)
        locations = set()
        for expense in expenses:
            loc = expense.get("location", "Bilinmiyor")
            locations.add(loc)
            row = self.expenses_table.rowCount()
            self.expenses_table.insertRow(row)
            self.expenses_table.setItem(row, 0, QTableWidgetItem(loc))
            self.expenses_table.setItem(row, 1, QTableWidgetItem(expense.get("paid_by", "Bilinmiyor")))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(f"₺{float(expense.get('total_amount', 0)):.2f}"))
            self.expenses_table.setItem(row, 3, QTableWidgetItem(expense.get("date", "N/A")))
        self.expenses_data = expenses

        # Update the location filter dropdown:
        self.location_filter_dropdown.blockSignals(True)
        self.location_filter_dropdown.clear()
        self.location_filter_dropdown.addItem("Tüm Lokasyonlar")
        for loc in sorted(locations):
            self.location_filter_dropdown.addItem(loc)
        self.location_filter_dropdown.blockSignals(False)

        # Update the "Paid By" filter dropdown:
        paid_by_set = set(expense.get("paid_by", "Bilinmiyor") for expense in expenses)
        self.paid_by_filter_dropdown.blockSignals(True)
        self.paid_by_filter_dropdown.clear()
        self.paid_by_filter_dropdown.addItem("Tüm Ödeyenler")
        for payer in sorted(paid_by_set):
            self.paid_by_filter_dropdown.addItem(payer)
        self.paid_by_filter_dropdown.blockSignals(False)

        # After populating self.expenses_table
        min_amount = float('inf')
        max_amount = float('-inf')
        for expense in expenses:
            try:
                amt = float(expense.get("total_amount", 0))
                if amt < min_amount:
                    min_amount = amt
                if amt > max_amount:
                    max_amount = amt
            except Exception:
                continue
        if min_amount == float('inf'):
            min_amount = 0.0
        if max_amount == float('-inf'):
            max_amount = 0.0

        self.expense_min_spin.setRange(0, max_amount)
        self.expense_min_spin.setValue(min_amount)
        self.expense_max_spin.setRange(min_amount, max_amount)
        self.expense_max_spin.setValue(max_amount)

    def load_payments(self):
        data = self.load_json(PAYMENTS_FILE)
        payments = data.get("payments", [])
        self.payments_table.setRowCount(0)
        from_set = set()
        to_set = set()
        for payment in payments:
            row = self.payments_table.rowCount()
            self.payments_table.insertRow(row)
            from_val = payment.get("from", "N/A")
            to_val = payment.get("to", "N/A")
            self.payments_table.setItem(row, 0, QTableWidgetItem(from_val))
            self.payments_table.setItem(row, 1, QTableWidgetItem(to_val))
            self.payments_table.setItem(row, 2, QTableWidgetItem(f"₺{float(payment.get('amount', 0)):.2f}"))
            self.payments_table.setItem(row, 3, QTableWidgetItem(payment.get("date", "N/A")))
            self.payments_table.setItem(row, 4, QTableWidgetItem(payment.get("time", "")))
            from_set.add(from_val)
            to_set.add(to_val)
        
        # Populate the from filter dropdown
        self.from_filter_dropdown.blockSignals(True)
        self.from_filter_dropdown.clear()
        self.from_filter_dropdown.addItem("Tüm Gönderenler")
        for val in sorted(from_set):
            self.from_filter_dropdown.addItem(val)
        self.from_filter_dropdown.blockSignals(False)
        
        # Populate the to filter dropdown
        self.to_filter_dropdown.blockSignals(True)
        self.to_filter_dropdown.clear()
        self.to_filter_dropdown.addItem("Tüm Alanlar")
        for val in sorted(to_set):
            self.to_filter_dropdown.addItem(val)
        self.to_filter_dropdown.blockSignals(False)

    def load_stores(self):
        data = self.load_json(STORES_PRODUCTS_FILE)
        stores = data.get("stores", [])
        self.stores_table.setRowCount(0)
        for store in stores:
            row = self.stores_table.rowCount()
            self.stores_table.insertRow(row)
            self.stores_table.setItem(row, 0, QTableWidgetItem(store.get("name", "İsimsiz")))
            num_products = len(store.get("products", []))
            self.stores_table.setItem(row, 1, QTableWidgetItem(str(num_products)))

    def load_products(self):
        data = self.load_json(STORES_PRODUCTS_FILE)
        stores = data.get("stores", [])
        self.products_table.setRowCount(0)
        for store in stores:
            for product in store.get("products", []):
                row = self.products_table.rowCount()
                self.products_table.insertRow(row)
                self.products_table.setItem(row, 0, QTableWidgetItem(product.get("name", "İsimsiz")))
                self.products_table.setItem(row, 1, QTableWidgetItem(product.get("type", "Bilinmiyor")))
                self.products_table.setItem(row, 2, QTableWidgetItem(f"₺{float(product.get('latest_price', 0)):.2f}"))
                history = product.get("price_history", [])
                history_str = ", ".join([f"{entry.get('date', '')}: ₺{float(entry.get('price', 0)):.2f}" for entry in history])
                self.products_table.setItem(row, 3, QTableWidgetItem(history_str))

    def load_json(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception as e:
                QMessageBox.warning(self, "❗ Hata", f"{file_path} okunurken hata oluştu:\n{e}")
                return {}
        else:
            return {}

    def apply_location_filter(self):
        selected_location = self.location_filter_dropdown.currentText()
        for row in range(self.expenses_table.rowCount()):
            item = self.expenses_table.item(row, 0)  # Location column
            if selected_location == "Tüm Lokasyonlar":
                self.expenses_table.setRowHidden(row, False)
            else:
                if item and item.text() == selected_location:
                    self.expenses_table.setRowHidden(row, False)
                else:
                    self.expenses_table.setRowHidden(row, True)

    def apply_paid_by_filter(self):
        selected_paid_by = self.paid_by_filter_dropdown.currentText()
        for row in range(self.expenses_table.rowCount()):
            item = self.expenses_table.item(row, 1)  # Column 1 is "Ödeyen"
            if selected_paid_by == "Tüm Ödeyenler":
                self.expenses_table.setRowHidden(row, False)
            else:
                if item and item.text() == selected_paid_by:
                    self.expenses_table.setRowHidden(row, False)
                else:
                    self.expenses_table.setRowHidden(row, True)

    def apply_expense_range_filter(self):
        min_val = self.expense_min_spin.value()
        max_val = self.expense_max_spin.value()
        for row in range(self.expenses_table.rowCount()):
            item = self.expenses_table.item(row, 2)  # Total Amount column
            if item:
                try:
                    amount = float(item.text().replace("₺", "").strip())
                except ValueError:
                    amount = 0.0
                if min_val <= amount <= max_val:
                    self.expenses_table.setRowHidden(row, False)
                else:
                    self.expenses_table.setRowHidden(row, True)

    def apply_expense_date_filter(self):
        start_date = self.expense_start_date.date()  # QDate
        end_date = self.expense_end_date.date()      # QDate

        if start_date > end_date:
            QMessageBox.warning(self, "Hata", "Başlangıç tarihi, bitiş tarihinden ileri olamaz!")
            # Block signals while updating the end date to avoid recursive calls:
            self.expense_end_date.blockSignals(True)
            self.expense_end_date.setDate(start_date)
            self.expense_end_date.blockSignals(False)
            # Optionally, update end_date variable here:
            end_date = start_date
            return

        for row in range(self.expenses_table.rowCount()):
            date_item = self.expenses_table.item(row, 3)
            if date_item:
                date_text = date_item.text().strip()
                row_date = QDate.fromString(date_text, "yyyy-MM-dd")
                if not row_date.isValid():
                    self.expenses_table.setRowHidden(row, True)
                else:
                    if start_date <= row_date <= end_date:
                        self.expenses_table.setRowHidden(row, False)
                    else:
                        self.expenses_table.setRowHidden(row, True)

    def apply_payments_filters(self):
        # Get the filter values (strip whitespace for reliable comparison)
        from_filter = self.from_filter_dropdown.currentText().strip()
        to_filter = self.to_filter_dropdown.currentText().strip()
        min_money = self.payments_min_spin.value()
        max_money = self.payments_max_spin.value()
        start_date = self.payments_start_date.date()
        end_date = self.payments_end_date.date()
        
        # Validate date range
        if start_date > end_date:
            QMessageBox.warning(self, "Hata", "Başlangıç tarihi, bitiş tarihinden ileri olamaz!")
            self.payments_end_date.blockSignals(True)
            self.payments_end_date.setDate(start_date)
            self.payments_end_date.blockSignals(False)
            end_date = start_date

        # Loop through each row in the payments table.
        for row in range(self.payments_table.rowCount()):
            show_row = True

            # Filter "from" (column 0)
            from_item = self.payments_table.item(row, 0)
            if from_item:
                cell_from = from_item.text().strip()
                # Debug: print comparison values
                print(f"Row {row} from: '{cell_from}' vs filter: '{from_filter}'")
                if from_filter != "Tüm Gönderenler" and cell_from != from_filter:
                    show_row = False

            # Filter "to" (column 1)
            to_item = self.payments_table.item(row, 1)
            if to_item:
                cell_to = to_item.text().strip()
                # Debug: print comparison values
                print(f"Row {row} to: '{cell_to}' vs filter: '{to_filter}'")
                if to_filter != "Tüm Alanlar" and cell_to != to_filter:
                    show_row = False

            # Filter money range (column 2, "Tutar")
            money_item = self.payments_table.item(row, 2)
            if money_item:
                try:
                    amount = float(money_item.text().replace("₺", "").strip())
                except ValueError:
                    amount = 0.0
                if not (min_money <= amount <= max_money):
                    show_row = False

            # Filter date range (column 3, "Tarih")
            date_item = self.payments_table.item(row, 3)
            if date_item:
                row_date = QDate.fromString(date_item.text().strip(), "yyyy-MM-dd")
                if not row_date.isValid() or not (start_date <= row_date <= end_date):
                    show_row = False

            self.payments_table.setRowHidden(row, not show_row)


    def filter_table(self, table, text):
        text = text.lower()
        for row in range(table.rowCount()):
            match = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            table.setRowHidden(row, not match)

    def return_to_summary(self):
        """⬅ Özet Sayfasına Dön"""
        main_window = self.parent().parent()
        if hasattr(main_window, "summary_page"):
            main_window.summary_page.load_data()
            main_window.central_widget.setCurrentWidget(main_window.summary_page)
        else:
            QMessageBox.warning(self, "Hata", "Özet sayfasına dönülemiyor!")

    def open_expense_detail(self, row, column):
        if row < len(self.expenses_data):
            expense = self.expenses_data[row]
            self.detail_page = ExpenseDetailPage(expense)
            main_window = self.parent().parent()
            main_window.central_widget.addWidget(self.detail_page)
            main_window.central_widget.setCurrentWidget(self.detail_page)

    def open_expense_detail(self, row, column):
        # Check if the row index is valid.
        if row < len(self.expenses_data):
            expense = self.expenses_data[row]
            # Create an instance of ExpenseDetailPage using the expense data.
            self.detail_page = ExpenseDetailPage(expense)
            # Assuming your main window is two levels up and contains a central_widget (a QStackedWidget)
            main_window = self.parent().parent()
            main_window.central_widget.addWidget(self.detail_page)
            main_window.central_widget.setCurrentWidget(self.detail_page)
        else:
            print("Invalid row index for expense detail.")

    def return_to_summary(self):
        main_window = self.parent().parent()
        if hasattr(main_window, "summary_page"):
            main_window.summary_page.load_data()
            main_window.central_widget.setCurrentWidget(main_window.summary_page)
        else:
            QMessageBox.warning(self, "Hata", "Özet sayfasına dönülemiyor!")
    
class ExpenseDetailPage(QWidget):
    def __init__(self, expense_data, parent=None):
        super().__init__(parent)
        self.expense_data = expense_data  # Expense details as a dictionary
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Expense Detail")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("📍 Konum:"))
        self.location_edit = QLineEdit(self.expense_data.get("location", ""))
        layout.addWidget(self.location_edit)

        layout.addWidget(QLabel("👤 Ödeyen:"))
        self.paid_by_edit = QLineEdit(self.expense_data.get("paid_by", ""))
        layout.addWidget(self.paid_by_edit)

        layout.addWidget(QLabel("💸 Toplam Tutar:"))
        self.total_edit = QLineEdit(str(self.expense_data.get("total_amount", 0)))
        layout.addWidget(self.total_edit)

        layout.addWidget(QLabel("📅 Tarih:"))
        self.date_edit = QLineEdit(self.expense_data.get("date", ""))
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("⏰ Saat:"))
        self.time_edit = QLineEdit(self.expense_data.get("time", ""))
        layout.addWidget(self.time_edit)

        sub_items = self.expense_data.get("sub_items", [])
        if sub_items:
            layout.addWidget(QLabel("📝 Alt Kalemler:"))
            self.subitems_table = QTableWidget(len(sub_items), 3)
            self.subitems_table.setHorizontalHeaderLabels(["İsim", "Tutar", "Paylaşanlar"])
            for i, item in enumerate(sub_items):
                self.subitems_table.setItem(i, 0, QTableWidgetItem(item.get("name", "")))
                self.subitems_table.setItem(i, 1, QTableWidgetItem(str(item.get("price", 0))))
                self.subitems_table.setItem(i, 2, QTableWidgetItem(", ".join(item.get("shared_by", []))))
            layout.addWidget(self.subitems_table)

        btn_layout = QHBoxLayout()
        self.return_detail_button = QPushButton("⬅️ Geri Dön")
        self.return_detail_button.clicked.connect(self.close)
        btn_layout.addWidget(self.return_detail_button)
        self.save_button = QPushButton("💾 Kaydet")
        self.save_button.clicked.connect(self.save_changes)
        btn_layout.addWidget(self.save_button)
        layout.addLayout(btn_layout)

    def save_changes(self):
        self.expense_data["location"] = self.location_edit.text()
        self.expense_data["paid_by"] = self.paid_by_edit.text()
        try:
            self.expense_data["total_amount"] = float(self.total_edit.text())
        except ValueError:
            QMessageBox.warning(self, "❗ Hata", "💢 Toplam tutar sayısal olmalı!")
            return
        self.expense_data["date"] = self.date_edit.text()
        self.expense_data["time"] = self.time_edit.text()

        if os.path.exists(EXPENSES_FILE):
            try:
                with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except Exception as e:
                QMessageBox.warning(self, "❗ Hata", f"Dosya okunurken hata:\n{e}")
                return
        else:
            data = {"expenses": []}

        expense_id = self.expense_data.get("id")
        updated = False
        for i, expense in enumerate(data.get("expenses", [])):
            if expense.get("id") == expense_id:
                data["expenses"][i] = self.expense_data
                updated = True
                break
        if not updated:
            data.setdefault("expenses", []).append(self.expense_data)
        try:
            with open(EXPENSES_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "💾 Kaydedildi", "Masraf detayları başarıyla kaydedildi.")
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "❗ Hata", f"Dosya kaydedilirken hata:\n{e}")

