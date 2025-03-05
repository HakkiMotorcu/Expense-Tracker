from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QTabWidget, QLineEdit, QHBoxLayout, QMessageBox, QComboBox
)
import json
import os

DATA_DIR = "data"
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")
STORES_PRODUCTS_FILE = os.path.join(DATA_DIR, "stores_products.json")

class EditPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with tabs for Expenses, Payments, Stores, and Products."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("✏️ Düzenleme Sayfası")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.expenses_tab = QWidget()
        self.payments_tab = QWidget()
        self.stores_tab = QWidget()
        self.products_tab = QWidget()

        self.tab_widget.addTab(self.expenses_tab, "💰 Harcamalar")
        self.tab_widget.addTab(self.payments_tab, "💳 Ödemeler")
        self.tab_widget.addTab(self.stores_tab, "🏪 Mağazalar")
        self.tab_widget.addTab(self.products_tab, "🛍️ Ürünler")

        self.setup_expenses_tab()
        self.setup_payments_tab()
        self.setup_stores_tab()
        self.setup_products_tab()

    def setup_expenses_tab(self):
        """Set up the Expenses tab UI."""
        layout = QVBoxLayout()
        self.expenses_tab.setLayout(layout)
        
        self.expense_search = QLineEdit()
        self.expense_search.setPlaceholderText("🔍 Harcamalarda ara...")
        self.expense_search.textChanged.connect(self.filter_expenses)
        layout.addWidget(self.expense_search)

        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Ödeyen", "Tutar", "İşlem"])
        layout.addWidget(self.expense_table)

        self.load_expenses()

    def setup_payments_tab(self):
        """Set up the Payments tab UI."""
        layout = QVBoxLayout()
        self.payments_tab.setLayout(layout)
        
        self.payment_search = QLineEdit()
        self.payment_search.setPlaceholderText("🔍 Ödemelerde ara...")
        self.payment_search.textChanged.connect(self.filter_payments)
        layout.addWidget(self.payment_search)

        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(5)
        self.payment_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Borçlu", "Miktar", "İşlem"])
        layout.addWidget(self.payment_table)
        
        self.load_payments()

    def setup_stores_tab(self):
        """Set up the Stores tab UI."""
        layout = QVBoxLayout()
        self.stores_tab.setLayout(layout)
        
        self.store_search = QLineEdit()
        self.store_search.setPlaceholderText("🔍 Mağazalarda ara...")
        self.store_search.textChanged.connect(self.filter_stores)
        layout.addWidget(self.store_search)

        self.store_table = QTableWidget()
        self.store_table.setColumnCount(2)
        self.store_table.setHorizontalHeaderLabels(["Mağaza Adı", "İşlem"])
        layout.addWidget(self.store_table)
        
        self.load_stores()

    def setup_products_tab(self):
        """Set up the Products tab UI."""
        layout = QVBoxLayout()
        self.products_tab.setLayout(layout)
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("🔍 Ürünlerde ara...")
        self.product_search.textChanged.connect(self.filter_products)
        layout.addWidget(self.product_search)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)
        self.product_table.setHorizontalHeaderLabels(["Ürün Adı", "Mağaza", "İşlem"])
        layout.addWidget(self.product_table)
        
        self.load_products()


    def load_expenses(self):
        """Load expenses from JSON and populate the table."""
        try:
            with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.expense_table.setRowCount(len(data.get("expenses", [])))

            for row, expense in enumerate(data["expenses"]):
                self.expense_table.setItem(row, 0, QTableWidgetItem(expense["date"]))
                self.expense_table.setItem(row, 1, QTableWidgetItem(expense["time"]))
                self.expense_table.setItem(row, 2, QTableWidgetItem(expense["paid_by"]))
                self.expense_table.setItem(row, 3, QTableWidgetItem(f"₺{expense['total_amount']:.2f}"))

                # ✅ FIXED: Correctly capture row index
                delete_button = QPushButton("🗑️ Sil")
                delete_button.clicked.connect(lambda _, i=row: self.delete_expense(i))
                self.expense_table.setCellWidget(row, 4, delete_button)

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Harcamalar yüklenemedi!")

    def load_payments(self):
        


    def delete_expense(self, row):
        """Delete selected expense."""
        try:
            with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            del data["expenses"][row]
            
            with open(EXPENSES_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Başarılı", "Harcama silindi!")
            self.load_expenses()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Silme işlemi başarısız oldu!")

    def filter_expenses(self):
        """Filter expenses based on search input."""
        search_text = self.expense_search.text().lower()
        for row in range(self.expense_table.rowCount()):
            item = self.expense_table.item(row, 2)  # 'Ödeyen' column
            self.expense_table.setRowHidden(row, search_text not in item.text().lower() if item else True)

    def filter_payments(self):
        """Filter payments based on search input."""
        search_text = self.payment_search.text().lower()
        for row in range(self.payment_table.rowCount()):
            item = self.payment_table.item(row, 2)  # 'Borçlu' column
            self.payment_table.setRowHidden(row, search_text not in item.text().lower() if item else True)

    def filter_stores(self):
        """Filter stores based on search input."""
        search_text = self.store_search.text().lower()
        for row in range(self.store_table.rowCount()):
            item = self.store_table.item(row, 0)  # 'Mağaza Adı' column
            self.store_table.setRowHidden(row, search_text not in item.text().lower() if item else True)

    def filter_products(self):
        """Filter products based on search input."""
        search_text = self.product_search.text().lower()
        for row in range(self.product_table.rowCount()):
            item = self.product_table.item(row, 0)  # 'Ürün Adı' column
            self.product_table.setRowHidden(row, search_text not in item.text().lower() if item else True)

    def delete_payment(self, row):
        """Delete selected payment."""
        try:
            with open(PAYMENTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            del data["payments"][row]

            with open(PAYMENTS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", "Ödeme silindi!")
            self.load_payments()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Ödeme silinemedi!")

    def delete_store(self, row):
        """Delete selected store."""
        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            del data["stores"][row]

            with open(STORES_PRODUCTS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", "Mağaza silindi!")
            self.load_stores()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Mağaza silinemedi!")

    def delete_product(self, row):
        """Delete selected product."""
        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            for store in data["stores"]:
                if row < len(store["products"]):
                    del store["products"][row]
                    break

            with open(STORES_PRODUCTS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", "Ürün silindi!")
            self.load_products()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Ürün silinemedi!")
