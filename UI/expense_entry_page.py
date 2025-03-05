from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QHeaderView, QInputDialog, QRadioButton, QButtonGroup, QStackedWidget
)
import json
from datetime import date
from PyQt6.QtWidgets import QComboBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor,QBrush

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Set precision for monetary calculations
getcontext().prec = 10  # Adjust as needed


# JSON Dosyaları
STORES_PRODUCTS_FILE = "data/stores_products.json"
USERS_FILE = "data/users.json"
EXPENSES_FILE = "data/expenses.json"

class ExpenseEntryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.disable_widgets(self.layout)
        self.load_users() 
        self.previous_store_index = 0
        self.previous_payer_index = 0
        
    def init_ui(self):
        """UI öğelerini oluşturur"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QLabel("➕ Masraf Ekleme Sayfası")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        self.layout.addWidget(self.title)

        # Kullanıcı seçimi (Kim ödedi?)
        self.payer_layout = QHBoxLayout()
        self.payer_label = QLabel("👤 Kim Ödedi?")
        self.payer_dropdown = QComboBox()       
        self.payer_layout.addWidget(self.payer_label)
        self.payer_layout.addWidget(self.payer_dropdown)
        self.layout.addLayout(self.payer_layout)

        # Mağaza seçimi
        self.store_layout = QHBoxLayout()
        self.store_label = QLabel("🏪 Mağaza")
        self.store_dropdown = QComboBox()
        # self.store_dropdown.currentIndexChanged.connect(self.load_products)

        self.add_store_button = QPushButton("➕ Yeni Mağaza")
        self.add_store_button.clicked.connect(self.add_new_store)#tanimlanmamis fonksiyon
        
        self.store_layout.addWidget(self.store_label)
        self.store_layout.addWidget(self.store_dropdown)
        self.store_layout.addWidget(self.add_store_button)

        self.store_dropdown.setEnabled(False)        
        self.add_store_button.setEnabled(False)
        self.layout.addLayout(self.store_layout)

        # Giriş tipi
        self.entry_type_layout = QHBoxLayout()
        self.entry_type_label = QLabel("📋 Giriş Tipi:")

        self.manual_radio = QRadioButton("Manuel Bölme")
        self.subitems_radio = QRadioButton("Ürün Listesi")

        # Varsayılan olarak "Sub Items Split" seçili
        self.subitems_radio.setChecked(True)

        # Butonları bir gruba bağla (Aynı anda sadece biri seçili olabilir)
        self.entry_type_group = QButtonGroup()
        self.entry_type_group.addButton(self.subitems_radio)
        self.entry_type_group.addButton(self.manual_radio)

        self.entry_type_layout.addWidget(self.entry_type_label)
        self.entry_type_layout.addWidget(self.subitems_radio)
        self.entry_type_layout.addWidget(self.manual_radio)
        self.layout.addLayout(self.entry_type_layout)
        
        self.entry_type_group.buttonClicked.connect(self.on_entry_type_changed)

        # 🔄 Stacked Widget to Switch Between Views
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # ✅ Initialize Product View (Ürün Listesi)
        self.product_view = QWidget()
        self.product_view_layout = QVBoxLayout(self.product_view)

        self.product_dropdown = QComboBox()
        self.add_new_product_button = QPushButton("➕ Yeni Ürün")
        self.add_new_product_button.clicked.connect(self.add_new_product)

        self.product_name_layout = QHBoxLayout()
        self.product_name_layout.addWidget(QLabel("🛍️ Ürün Seçimi"))
        self.product_name_layout.addWidget(self.product_dropdown)
        self.product_name_layout.addWidget(self.add_new_product_button)

        self.product_view_layout.addLayout(self.product_name_layout)

        self.price_input = QLineEdit()
        self.count_input = QLineEdit()
        self.count_input.setPlaceholderText("1")
        self.count_input.setText("1")
        self.add_product_button = QPushButton("➕ Ürün Ekle")
        self.price_layout = QHBoxLayout()
        self.price_layout.addWidget(QLabel("💰 Fiyat"))
        self.price_layout.addWidget(self.price_input)
        self.price_layout.addWidget(QLabel("🔢 Adet"))
        self.price_layout.addWidget(self.count_input)
        self.price_layout.addWidget(self.add_product_button)
        self.product_view_layout.addLayout(self.price_layout)

    
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Ürün", "Birim Fiyati","Adet","Toplam Fiyat","Paylaşan"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.product_view_layout.addWidget(QLabel("📋 Ürün Listesi"))
        self.product_view_layout.addWidget(self.product_table)

        self.product_dropdown.currentIndexChanged.connect(self.on_product_selected)
        self.add_product_button.clicked.connect(self.add_product_to_table)

        self.product_total_price_layout = QHBoxLayout()
        self.product_total_label = QLabel("💸 Toplam Tutar:")
        self.product_total_input = QLineEdit()
        self.product_total_input.setText("0.00")
        self.product_total_input.setReadOnly(True)

        self.product_total_price_layout.addWidget(self.product_total_label)
        self.product_total_price_layout.addWidget(self.product_total_input)
        self.product_view_layout.addLayout(self.product_total_price_layout)

       
        # Ürün silme butonu ekleyelim
        self.product_table.itemSelectionChanged.connect(self.on_product_selected_highlight)

        self.delete_product_button = QPushButton("🗑️ Ürünü Sil")
        self.delete_product_button.clicked.connect(self.delete_selected_product)
        self.product_view_layout.addWidget(self.delete_product_button)

        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)


        # ✅ Initialize Manual Split View (Manuel Bölme)
        self.manual_view = QWidget()
        self.manual_view_layout = QVBoxLayout(self.manual_view)

        self.manual_total_layout = QHBoxLayout()
        self.manual_total_label = QLabel("💸 Toplam Tutar:")
        self.manual_total_input = QLineEdit()
        self.manual_total_input.setPlaceholderText("₺0.00")

        self.auto_split_button = QPushButton("🔄 Eşit Böl")
        self.auto_split_button.clicked.connect(self.auto_split_amount)

        self.manual_split_table = QTableWidget()
        self.manual_split_table.setColumnCount(2)
        self.manual_split_table.setHorizontalHeaderLabels(["Kullanıcı", "Tutar"])
        self.manual_split_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.manual_total_layout.addWidget(self.manual_total_label)
        self.manual_total_layout.addWidget(self.manual_total_input)
        self.manual_total_layout.addWidget(self.auto_split_button)
        self.manual_view_layout.addLayout(self.manual_total_layout)
        self.manual_view_layout.addWidget(QLabel("👥 Kişi Başına Pay"))
        self.manual_view_layout.addWidget(self.manual_split_table)

        self.manual_split_table.cellChanged.connect(self.update_manual_total_amount)
        self.manual_total_input.textChanged.connect(self.check_manual_total)
        
        # Tablo hücre değişikliklerini dinle
        self.product_table.cellChanged.connect(self.prevent_negative_values)
        self.manual_split_table.cellChanged.connect(self.prevent_negative_values)

        # Add Both Views to StackedWidget
        self.stacked_widget.addWidget(self.product_view)  # Index 0
        self.stacked_widget.addWidget(self.manual_view)   # Index 1

        
        # 💾 Save Button
        self.buttom_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 Kaydet")
        self.save_button.clicked.connect(self.save_expense)

        # 📍 Masraf Ekleme Sayfasına "Geri Dön" Butonu Ekleyelim
        self.back_button = QPushButton("⬅ Geri Dön")
        self.back_button.clicked.connect(self.return_to_summary)  # Geri Dön butonuna tıklandığında return_to_summary fonksiyonunu çalıştır
                
        
        self.buttom_layout.addWidget(self.back_button)  
        self.buttom_layout.addWidget(self.save_button)
        self.layout.addLayout(self.buttom_layout)  # Butonları layout'a ekle

        # Set Default View
        self.on_entry_type_changed(self.subitems_radio)

    def disable_widgets(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            if item.layout():  # Check if the item has a nested layout
                self.disable_widgets(item.layout())
            elif item.widget():
                widget = item.widget()
                if not isinstance(widget, QLabel):  # Skip QLabel if needed
                    widget.setEnabled(False)
        self.back_button.setEnabled(True)

    def enable_widgets(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            if item.layout():  # Check for nested layouts
                self.enable_widgets(item.layout())
            elif item.widget():
                widget = item.widget()
                if not isinstance(widget, QLabel):
                    print(f"Enabling widget: {widget} ({type(widget)})")
                    widget.setEnabled(True)

    def load_users(self):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                
                self.payer_dropdown.clear()
                self.payer_dropdown.addItem("👤 Kullanıcı Seçiniz")  # Varsayılan boş değer
                self.payer_dropdown.addItems([user["name"] for user in data["users"]])

                # Kullanıcı seçilmeden işlemleri engelle
                self.payer_dropdown.setCurrentIndex(0)
                self.payer_dropdown.setEnabled(True)
                # Kullanıcı seçildiğinde mağazaları yükle
                self.payer_dropdown.currentIndexChanged.connect(self.on_payer_selected)

        except FileNotFoundError:
            self.payer_dropdown.clear()
            self.payer_dropdown.addItem("👤 Kullanıcı Bulunamadı")

    def track_previous_index(self, index):
        """Track the previous index of the store dropdown."""
        self.previous_payer_index = index

    def on_payer_selected(self):
        """Kullanıcı seçildiğinde mağazaları yükler"""
        if self.payer_dropdown.currentIndex() == 0:
            self.clear_widgets(self.layout)  # Kullanıcı seçilmediyse tüm widgetları temizle
            self.store_dropdown.setEnabled(False)  # Kullanıcı seçilmediyse mağaza seçimi kapalı
            self.add_store_button.setEnabled(False)  # Kullanıcı seçilmediyse mağaza ekleme kap
        else:
            if self.previous_payer_index != 0 and self.store_dropdown.currentIndex() != 0:
                # Show confirmation dialog
                reply = QMessageBox.question(
                    self,
                    "Önceki Değerleri Sil",
                    "Önceden girilen değerleri silmek istiyor musunuz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                current_index = self.payer_dropdown.currentIndex()
                current_store_index = self.store_dropdown.currentIndex()
                print(f"Current Index: {current_index}")
                print(f"Current Store Index: {current_store_index}")
                if reply == QMessageBox.StandardButton.Yes:
                    self.clear_widgets(self.layout)  # Call your clear function
                    self.payer_dropdown.setCurrentIndex(current_index)
                    self.store_dropdown.setCurrentIndex(current_store_index)
                    print("Değerler silindi.")
                    self.store_dropdown.setEnabled(True)
                    self.load_stores_products()  # Kullanıcı seçildiğinde mağazaları yükle
                else:
                    print("Değerler korunuyor.")
            else:
                self.store_dropdown.setEnabled(True)
                self.load_stores_products()  # Kullanıcı seçildiğinde mağazaları yükle    
        self.track_previous_index(self.payer_dropdown.currentIndex())

    def on_store_selected(self):
        """Enables the entry type radio buttons when a store is selected."""
        # Check if a valid store is selected
        if self.store_dropdown.currentIndex() != 0:  # Assuming index 0 is placeholder like "Select Store"
            self.subitems_radio.setEnabled(True)
            self.manual_radio.setEnabled(True)
            self.stacked_widget.setEnabled(True)
            self.on_entry_type_changed(self.subitems_radio)  # Default to subitems view
            if self.previous_store_index!=self.store_dropdown.currentIndex():
                self.subitems_radio.setChecked(True)
                self.on_entry_type_changed(self.subitems_radio)  # Default to subitems view
                self.clear_widgets(self.product_view_layout)
                self.clear_widgets(self.manual_view_layout)
            
        else:
            # Disable if no valid store is selected
            self.subitems_radio.setEnabled(False)
            self.manual_radio.setEnabled(False)
            self.product_dropdown.setEnabled(False)
            self.product_dropdown.clear()
            self.stacked_widget.setEnabled(False)
        
        self.previous_store_index=self.store_dropdown.currentIndex()

    def on_entry_type_changed(self, button):
        """Switch between views based on entry type."""
        if button == self.subitems_radio:
            self.stacked_widget.setCurrentIndex(0)
            # self.product_view.setEnabled(True)
            # self.manual_view.setEnabled(False)
            self.enable_widgets(self.product_view_layout)
            self.disable_widgets(self.manual_view_layout)
            self.clear_widgets(self.manual_view_layout)
            self.load_products()
            print("Ürün Listesi görünümü aktif.")
        elif button == self.manual_radio:
            self.stacked_widget.setCurrentIndex(1)
            self.enable_widgets(self.manual_view_layout)
            self.disable_widgets(self.product_view_layout)
            self.clear_widgets(self.product_view_layout)
            self.load_users_into_manual_split()  # ✅ Load users when manual split is selected
            print("Manuel Bölme görünümü aktif.")

    def on_product_selected(self):
        """Ürün seçildiğinde fiyatı getirir ve güncellenmesini kontrol eder"""
        if self.product_dropdown.currentIndex() != 0:
            self.fill_price_field()            
        else:
            self.price_input.clear()

    def on_product_selected_highlight(self):
        """Seçilen ürünü mavi renkle vurgular ve varsayılan renge geri döner"""
        selected_rows = self.product_table.selectionModel().selectedRows()

        # Önce tüm satırların arka planını sıfırla (varsayılan renge döner)
        for row in range(self.product_table.rowCount()):
            for col in range(self.product_table.columnCount()):
                item = self.product_table.item(row, col)
                if item is None:
                    item = QTableWidgetItem("")  # Eksik hücre varsa oluştur
                    self.product_table.setItem(row, col, item)
                item.setBackground(QBrush())  # 🎨 Varsayılan arka plan rengine döndür

        # Seçili satır yoksa hiçbir şey yapma
        if not selected_rows:
            return

        # Seçilen satırı mavi ile vurgula
        for index in selected_rows:
            row = index.row()

            # Açık mavi tonu
            highlight_color = QColor(173, 216, 230)  # Light Blue

            for col in range(self.product_table.columnCount()):
                item = self.product_table.item(row, col)
                if item is None:
                    item = QTableWidgetItem("")
                    self.product_table.setItem(row, col, item)
                item.setBackground(highlight_color)

    def clear_widgets(self, layout):
        """Clear all widgets inside the given layout, including stacked widget pages."""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            
            # Handle nested layouts and stacked widgets
            if isinstance(item.widget(), QStackedWidget):
                stacked_widget = item.widget()
                for page_index in range(stacked_widget.count()):
                    print(f"Clearing stacked widget page: {page_index}")
                    page = stacked_widget.widget(page_index)
                    self.clear_widgets(page.layout())  # Recursively clear each page
            elif isinstance(item.layout(), (QHBoxLayout, QVBoxLayout)):
                self.clear_widgets(item.layout())
            elif item.widget():
                widget = item.widget()
                print(f"Clearing item: {widget} ({type(widget)})")

                # Skip QLabel if you want to preserve it
                if isinstance(widget, QLabel):
                    continue

                # Clear QLineEdit
                elif isinstance(widget, QLineEdit):
                    widget.clear()

                # Reset QComboBox to first index
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)

                # Clear QTableWidget rows
                elif isinstance(widget, QTableWidget):
                    print(f"Row Count Before: {widget.rowCount()}")
                    widget.setRowCount(0)
                    widget.viewport().update()  # Force GUI refresh
                    print(f"Row Count After: {widget.rowCount()} (Table cleared)")

                # Clear QPushButton text if needed (optional)
                elif isinstance(widget, QPushButton):
                    widget.setText(widget.text())

        # Reset total input field (if applicable)
        self.product_total_input.setText("0.00")

    def load_stores_products(self,index=0):
        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.store_dropdown.clear()
                self.store_dropdown.addItem("🏪 Mağaza Seçiniz")  # Varsayılan boş değer
                self.store_dropdown.addItems([store["name"] for store in data["stores"]])
                # Mağaza seçilmeden işlemleri engelle
                self.store_dropdown.setCurrentIndex(index)
                self.store_dropdown.setEnabled(True)
                self.add_store_button.setEnabled(True)
                # Mağaza seçildiğinde ürünleri yükle
                self.store_dropdown.currentIndexChanged.connect(self.on_store_selected)

        except FileNotFoundError:
            self.store_dropdown.clear()
            self.store_dropdown.addItem("🏪 Mağaza Bulunamadı")

    def load_products(self):
        """Seçili mağazaya göre ürünleri yükler"""
        selected_store = self.store_dropdown.currentText()
        self.product_dropdown.clear()

        if not selected_store:
            return  # Eğer mağaza seçilmezse işlem yapma

        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.product_dropdown.addItem("🛍️ Ürün Seçiniz")  # Varsayılan boş değer
            store = next((s for s in data["stores"] if s["name"] == selected_store), None)
            if store and "products" in store:
                self.product_dropdown.addItems([p["name"] for p in store["products"]])


        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Ürünler yüklenemedi!")

    def add_new_user(self):
        """Yeni kullanıcı ekler"""
        new_user, ok = QInputDialog.getText(self, "Yeni Kullanıcı", "Kullanıcı Adı:")
        if ok and new_user.strip():
            with open(USERS_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)
                data["users"].append({"id": len(data["users"]) + 1, "name": new_user.strip()})
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
            self.load_users()

    def add_new_store(self):
        """Yeni bir mağaza ekler ve var olan mağazaları kontrol eder."""
        
        # Get store name from user input
        store_name, ok = QInputDialog.getText(self, "Yeni Mağaza", "Mağaza Adı:")

        # If user cancels or inputs an empty string
        if not ok or not store_name.strip():
            QMessageBox.warning(self, "Hata", "Mağaza adı boş olamaz!")
            return

        store_name = store_name.strip()

        try:
            # Open the JSON file
            with open(STORES_PRODUCTS_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)

                # Check if store already exists
                existing_store = next((s for s in data["stores"] if s["name"].lower() == store_name.lower()), None)

                if existing_store:
                    QMessageBox.warning(self, "Hata", "Bu mağaza zaten mevcut!")
                    return

                # Add new store
                new_store = {
                    "name": store_name,
                    "products": []
                }

                data["stores"].append(new_store)

                # Write back to JSON
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()

            # Update store dropdown in the UI
            self.store_dropdown.addItem(store_name)

            QMessageBox.information(self, "Başarılı", f"{store_name} mağazası başarıyla eklendi!")

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Mağaza eklenemedi! JSON dosyası okunamadı.")

    def fill_price_field(self):
        """Seçilen ürünün fiyatını getirir (fiyat değişimini hemen kaydetmez)"""
        selected_store = self.store_dropdown.currentText()
        selected_product = self.product_dropdown.currentText()
        if self.count_input.text() == "":
            self.count_input.setText("1")
        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            store = next((s for s in data["stores"] if s["name"] == selected_store), None)
            if store:
                product = next((p for p in store["products"] if p["name"] == selected_product), None)
                if product:
                    current_price = str(product["latest_price"])
                    self.price_input.setText(current_price)
                else:
                    self.price_input.clear()
            else:
                self.price_input.clear()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Ürün bilgileri yüklenemedi!")

    def update_product_price(self, store_name, product_name, new_price):
        """Eğer fiyat değiştiyse, stores_products.json içinde günceller (tarih + saat ayrı kaydedilir)"""
        try:
            with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            store = next((s for s in data["stores"] if s["name"] == store_name), None)
            if store:
                product = next((p for p in store["products"] if p["name"] == product_name), None)
                if product:
                    # ✅ Only update if price has changed
                    if product["latest_price"] != new_price:
                        # Prepare readable date and time
                        now = datetime.now()
                        current_date = now.strftime("%Y-%m-%d")
                        current_time = now.strftime("%H:%M:%S")

                        # Add old price to price_history if not already present
                        if "price_history" not in product:
                            product["price_history"] = []

                        product["price_history"].append({
                            "date": current_date,
                            "time": current_time,
                            "price": product["latest_price"]
                        })

                        # Update the latest price
                        product["latest_price"] = new_price

                        # Save updated JSON
                        with open(STORES_PRODUCTS_FILE, "w", encoding="utf-8") as file:
                            json.dump(data, file, indent=4, ensure_ascii=False)

                        print(f"Fiyat güncellendi: {product_name} - Yeni Fiyat: {new_price}")
                    else:
                        print("Fiyat aynı, güncelleme yapılmadı.")

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Fiyat güncellenemedi!")

    def add_product_to_table(self):
        """Seçilen ürünü tabloya ekler ve fiyat değişimini kaydeder"""
        product_name = self.product_dropdown.currentText()
        product_price = self.price_input.text()
        product_count = self.count_input.text()
        selected_store = self.store_dropdown.currentText()

        if not product_name or not product_price:
            QMessageBox.warning(self, "Hata", "Lütfen ürün seçin ve fiyat girin!")
            return

        try:
            product_price = float(product_price)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir fiyat girin!")
            return

        try:
            product_count = int(product_count)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir adet girin!")
            return

        # Add new row to table
        row_position = self.product_table.rowCount()
        self.product_table.insertRow(row_position)
        self.product_table.setItem(row_position, 0, QTableWidgetItem(product_name))
        self.product_table.setItem(row_position, 1, QTableWidgetItem(f"{product_price:.2f}"))
        self.product_table.setItem(row_position, 2, QTableWidgetItem(f"{product_count}"))
        self.product_table.setItem(row_position, 3, QTableWidgetItem(f"{product_count * product_price:.2f}"))

        # Update total price field
        self.product_total_input.setText(f"{float(self.product_total_input.text()) + product_price * product_count:.2f}")

        # Add sharing combobox
        shared_with_combo = QComboBox()
        shared_with_combo.addItem("Ortak")  # Shared option
        users = [self.payer_dropdown.itemText(i) for i in range(1, self.payer_dropdown.count())]
        shared_with_combo.addItems(users)
        self.product_table.setCellWidget(row_position, 4, shared_with_combo)

        # ✅ Update product price only after adding to table
        self.update_product_price(selected_store, product_name, product_price)

        # Enable save button if table has rows
        self.save_button.setEnabled(self.product_table.rowCount() != 0)

    def save_expense(self):
        """Harcamayı JSON'a kaydeder ve expenses.json dosyasını günceller."""
        paid_by = self.payer_dropdown.currentText()
        location = self.store_dropdown.currentText()
        current_date = datetime.today().strftime("%Y-%m-%d")  # 📅 Tarihi al
        current_time = datetime.now().strftime("%H:%M")  # ⏰ Saati al
        total_amount = 0  # 💰 Toplam harcama miktarı

        sub_items = []
        for row in range(self.subitems_table.rowCount()):
            name = self.subitems_table.item(row, 0).text()
            price = float(self.subitems_table.item(row, 1).text().replace("₺", ""))
            total_amount += price  # Toplam miktarı hesapla

            # Paylaşım bilgilerini al (QComboBox)
            shared_with_combo = self.subitems_table.cellWidget(row, 2)
            shared_with = shared_with_combo.currentText()

            # Eğer "Ortak" seçilmişse, tüm kullanıcıları paylaşım listesine ekle
            if shared_with == "Ortak":
                shared_with = [self.payer_dropdown.itemText(i) for i in range(self.payer_dropdown.count())]
            else:
                shared_with = [shared_with]

            sub_items.append({"name": name, "price": price, "shared_by": shared_with})

        # 📂 JSON dosyasını güncelle
        try:
            if os.path.exists(EXPENSES_FILE):
                with open(EXPENSES_FILE, "r+", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = {"expenses": []}  # Eğer dosya yoksa boş bir JSON oluştur

            # Yeni harcamayı ekle
            new_expense = {
                "id": len(data["expenses"]) + 1,
                "date": current_date,  # 📅 Tarihi ekle
                "time": current_time,  # ⏰ Saati ekle
                "location": location,
                "paid_by": paid_by,
                "total_amount": total_amount,  # 💰 Toplam harcamayı ekle
                "sub_items": sub_items
            }

            data["expenses"].append(new_expense)

            # Güncellenmiş verileri dosyaya yaz
            with open(EXPENSES_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", "Harcama başarıyla kaydedildi!")

        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            QMessageBox.warning(self, "Hata", f"Harcamalar kaydedilemedi!\n{e}")

    def add_new_product(self):
        """Yeni ürün ekler ve fiyatını belirler."""
        selected_store = self.store_dropdown.currentText()

        if not selected_store:
            QMessageBox.warning(self, "Hata", "Önce bir mağaza seçmelisiniz!")
            return

        # Open the custom dialog
        dialog = ProductInputDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_product_name, price_text = dialog.get_inputs()

        # Validate Product Name
        if not new_product_name.strip():
            QMessageBox.warning(self, "Hata", "Ürün adı boş olamaz!")
            return

        # Parse type:name if provided
        if ':' in new_product_name:
            product_type, product_name = map(str.strip, new_product_name.split(':', 1))
        else:
            product_type = "Bilinmeyen"
            product_name = new_product_name.strip()

        # Validate Price
        try:
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir fiyat girin!")
            return

        try:
            with open(STORES_PRODUCTS_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)

                # Find the selected store
                store = next((s for s in data["stores"] if s["name"] == selected_store), None)
                if not store:
                    QMessageBox.warning(self, "Hata", "Seçilen mağaza bulunamadı!")
                    return

                # Check if the product already exists
                existing_product = next((p for p in store["products"] if p["name"] == product_name), None)
                if existing_product:
                    QMessageBox.warning(self, "Hata", "Bu ürün zaten mevcut!")
                    return

                # Add new product
                new_product_id = data["last_product_id"] + 1
                data["last_product_id"] = new_product_id

                new_product = {
                    "id": new_product_id,
                    "type": product_type,
                    "name": product_name,
                    "price_history": [{"date": date.today().isoformat(), "price": price}],
                    "latest_price": price
                }
                store["products"].append(new_product)

                # Update JSON file
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()

            # Update the UI dropdown
            self.product_dropdown.addItem(product_name)
            QMessageBox.information(self, "Başarılı", f"{product_name} mağaza: {selected_store} içinde eklendi!")

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Dosya okunamadı veya JSON formatı hatalı!")

        """Seçilen ürünü tabloya ekler ve fiyat değişimini kontrol eder"""
        product_name = self.product_dropdown.currentText()
        product_price = self.price_input.text()
        product_count = self.count_input.text()
        selected_store = self.store_dropdown.currentText()

        if not product_name or not product_price:
            QMessageBox.warning(self, "Hata", "Lütfen ürün seçin ve fiyat girin!")
            return

        try:
            product_price = float(product_price)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir fiyat girin!")
            return
        try:
            product_count = int(product_count)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir adet girin!")
            return

        # Yeni satır ekle
        row_position = self.product_table.rowCount()
        
        self.product_table.insertRow(row_position)
        self.product_table.setItem(row_position, 0, QTableWidgetItem(product_name))
        self.product_table.setItem(row_position, 1, QTableWidgetItem(f"{product_price}"))
        self.product_table.setItem(row_position, 2, QTableWidgetItem(f"{product_count}"))
        self.product_table.setItem(row_position, 3, QTableWidgetItem(f"{product_count*product_price}"))

        self.product_total_input.setText(str(float(self.product_total_input.text()) + product_price*product_count))

        # Paylaşım için ComboBox ekleyelim
        shared_with_combo = QComboBox()
        shared_with_combo.addItem("Ortak")  # Ortak seçeneği
        users = [self.payer_dropdown.itemText(i) for i in range(1,self.payer_dropdown.count())]
        shared_with_combo.addItems(users)  # Kullanıcıları ekle
        self.product_table.setCellWidget(row_position, 4, shared_with_combo)

        # **Fiyat değişmişse güncelle**
        self.update_product_price(selected_store, product_name, product_price)
        if self.product_table.rowCount() != 0:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)
        # QMessageBox.information(self, "Başarılı", f"{product_name} tabloya eklendi!")
    
    def save_expense(self):
        """Harcamayı JSON'a kaydeder"""
        paid_by = self.payer_dropdown.currentText()
        location = self.store_dropdown.currentText()
        sub_items = []
        manual_split = {}
        if self.stacked_widget.currentIndex() == 0:
            if self.product_table.rowCount() == 0:
                QMessageBox.warning(self, "Hata", "Lütfen en az bir ürün ekleyin!")
                return
            for row in range(self.product_table.rowCount()):
                name = self.product_table.item(row, 0).text()
                price = float(self.product_table.item(row, 1).text().replace("₺", ""))
                count = int(self.product_table.item(row, 2).text())
                total_item_price = price * count
                shared_with_combo = self.product_table.cellWidget(row, 4)  # ComboBox'ı al
                shared_with = shared_with_combo.currentText()  # Seçili kişi veya "Ortak"

                if shared_with == "Ortak":
                    shared_with = [self.payer_dropdown.itemText(i) for i in range(1,self.payer_dropdown.count())]
                    print(shared_with)
                else:
                    shared_with = [shared_with]

                sub_items.append({"name": name, "item_price": price, "count":count, 'price':total_item_price, "shared_by": shared_with})

            with open(EXPENSES_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)
                data["expenses"].append({
                    "id": len(data["expenses"]) + 1,
                    "location": location,
                    "date": date.today().isoformat(),
                    'time': datetime.now().strftime("%H:%M"),
                    'total_amount': sum([item['price'] for item in sub_items]),
                    "paid_by": paid_by,
                    "sub_items": sub_items
                })
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)

        elif self.stacked_widget.currentIndex() == 1:
            if self.manual_split_table.rowCount() == 0:
                QMessageBox.warning(self, "Hata", "Lütfen en az bir kişi ekleyin!")
                return

            total_amount_text = self.manual_total_input.text().replace("₺", "").strip()
            try:
                total_amount = float(total_amount_text)
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçerli bir toplam tutar girin!")
                return

            sum_of_splits = 0.0
            manual_split = {}

            for row in range(self.manual_split_table.rowCount()):
                name = self.manual_split_table.item(row, 0).text()
                amount_text = self.manual_split_table.item(row, 1).text().strip()

                try:
                    amount = float(amount_text)
                except ValueError:
                    QMessageBox.warning(self, "Hata", f"{name} için geçerli bir tutar girin!")
                    return

                sum_of_splits += amount
                manual_split[name] = amount

            if abs(sum_of_splits - total_amount) > 0.011:  # Allowing slight floating-point differences
                QMessageBox.warning(self, "Hata", "Girilen tutarlar toplamı, toplam tutar ile eşleşmiyor!")
                return

            # ✅ Save Manual Split Data
            with open(EXPENSES_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)
                data["expenses"].append({
                    "id": len(data["expenses"]) + 1,
                    "location": location,
                    "date": date.today().isoformat(),
                    'time': datetime.now().strftime("%H:%M"),
                    'total_amount': total_amount,
                    "paid_by": paid_by,
                    "manual_split": manual_split
                })
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)


        QMessageBox.information(self, "Başarılı", "Harcama başarıyla kaydedildi!")
        self.reset_expense_page()
        
    def return_to_summary(self):
        """Geri butonuna basıldığında Genel Özet Sayfasına yönlendirir ve verileri günceller."""
        main_window = self.parent().parent()
        if hasattr(main_window, "summary_page"):
            print("Genel Özet Sayfasına dönülüyor...")
            main_window.summary_page.load_data()  # Genel Özet verilerini güncelle
            main_window.central_widget.setCurrentWidget(main_window.summary_page)  # Genel Özet Sayfasına geç
            self.reset_expense_page()  # Masraf Ekleme Sayfasını sıfırla
        
    def reset_expense_page(self):
        self.payer_dropdown.setCurrentIndex(0)

    def auto_split_amount(self):
        """Auto-split the total amount equally among users (handles rounding issues)."""
        total_amount_text = self.manual_total_input.text().replace("₺", "").strip()

        try:
            total_amount = float(total_amount_text)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir toplam tutar girin!")
            return

        row_count = self.manual_split_table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "Hata", "Tabloda kullanıcı yok!")
            return

        # 💲 Convert to kuruş for precise splitting
        total_kurus = round(total_amount * 100)
        base_share = total_kurus // row_count
        remainder = total_kurus % row_count

        # 🟢 Distribute base share and handle any remainder
        for row in range(row_count):
            share_kurus = base_share + (1 if row < remainder else 0)
            per_user_amount = share_kurus / 100  # Convert back to ₺
            self.manual_split_table.setItem(row, 1, QTableWidgetItem(f"{per_user_amount:.2f}"))

        # QMessageBox.information(self, "Başarılı", "Toplam tutar eşit şekilde paylaştırıldı!")

    def load_users_into_manual_split(self):
        """Add all users to the manual split table."""
        users = [self.payer_dropdown.itemText(i) for i in range(1, self.payer_dropdown.count())]  # Assuming payer_dropdown has users

        self.manual_split_table.setRowCount(len(users))
        for idx, user in enumerate(users):
            user_item = QTableWidgetItem(user)
            user_item.setFlags(user_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make user names non-editable

            amount_item = QTableWidgetItem("0.00")
            self.manual_split_table.setItem(idx, 0, user_item)
            self.manual_split_table.setItem(idx, 1, amount_item)

    def update_manual_total_amount(self, row, column):
        """Update total amount and enable save button when valid."""
        # Only react if the amount column (1) is edited
        if column != 1:
            return

        total_sum = 0.0
        valid_entries = False

        # Calculate the sum of all amounts in the table
        for i in range(self.manual_split_table.rowCount()):
            try:
                amount = float(self.manual_split_table.item(i, 1).text())
                if amount > 0:
                    valid_entries = True
            except (ValueError, AttributeError):
                amount = 0.0  # Treat invalid or empty cells as 0
            total_sum += amount

        # Get current total from the input field
        total_amount_text = self.manual_total_input.text().replace("₺", "").strip()
        try:
            current_total = float(total_amount_text)
        except ValueError:
            current_total = 0.0

        # 🟢 Update total if 0, empty, or less than table sum
        if abs(total_sum - current_total) < 0.01 or current_total == 0.0 or current_total < total_sum:
            self.manual_total_input.setText(f"₺{total_sum:.2f}")


        # ✅ Enable Save button if there are valid entries and total > 0
        if valid_entries and total_sum > 0:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def check_manual_total(self):
        """Enable save button if manual total input is valid."""
        total_amount_text = self.manual_total_input.text().replace("₺", "").strip()
        try:
            total_amount = float(total_amount_text)
            if total_amount > 0:
                self.save_button.setEnabled(True)
            else:
                self.save_button.setEnabled(False)
        except ValueError:
            self.save_button.setEnabled(False)

    def prevent_negative_values(self, row, column):
        """Tablolarda negatif değer girişini engeller"""
        table = self.sender()  # Hangi tablo olduğunu belirle
        item = table.item(row, column)

        if item:
            try:
                value = float(item.text())
                if value < 0:
                    QMessageBox.warning(self, "Hata", "Negatif değer girilemez!")
                    item.setText("0.00")  # Eksi değeri sıfırla
            except ValueError:
                pass  # Geçersiz veri girildiğinde hata vermemesi için

    def delete_selected_product(self):
        """Tablodan seçilen ürünü siler ve toplam fiyatı günceller"""
        selected_row = self.product_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silmek için bir ürün seçin!")
            return

        product_name = self.product_table.item(selected_row, 0).text()

        reply = QMessageBox.question(
            self,
            "Ürünü Sil",
            f"'{product_name}' ürününü silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Toplam fiyatı güncelle
            total_price = float(self.product_total_input.text())
            product_total = float(self.product_table.item(selected_row, 3).text())
            new_total = total_price - product_total
            self.product_total_input.setText(f"{new_total:.2f}")

            # Satırı sil
            self.product_table.removeRow(selected_row)

            # Kaydet butonunu kontrol et
            self.save_button.setEnabled(self.product_table.rowCount() != 0)



from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox, QDialogButtonBox
from datetime import date
import json

class ProductInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeni Ürün Ekle")

        self.layout = QVBoxLayout()

        # Product Name Input
        self.name_label = QLabel("Ürün Adı (Type:Name formatını kullanabilirsiniz):")
        self.name_input = QLineEdit()

        # Price Input
        self.price_label = QLabel("Fiyat:")
        self.price_input = QLineEdit()

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Add Widgets to Layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.price_label)
        self.layout.addWidget(self.price_input)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_inputs(self):
        return self.name_input.text(), self.price_input.text()


