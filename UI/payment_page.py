from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QHBoxLayout, QTextEdit, QFileDialog, QMessageBox, QDateEdit, QTimeEdit
)
from PyQt6.QtCore import Qt, QDate , QTime
from datetime import datetime
import json
import os
import shutil

# 📁 Dosya Yolları
USERS_FILE = "data/users.json"
EXPENSES_FILE = "data/expenses.json"
PAYMENTS_FILE = "data/payments.json"
PAYMENT_RECIEPTS_DIR = "/Users/hakkimotorcu/Desktop/Harcama Listesi/payment_reciepts"

class PaymentPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.receipt_path = None  # 📁 Fatura Dosyası Yolu
        self.init_ui()

    def init_ui(self):
        """💳 Ödeme Yapma Sayfasının Arayüzü"""

        # 📋 Ana Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 📌 Başlık
        self.title = QLabel("💳 Ödeme Yapma Sayfası")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        self.layout.addWidget(self.title)

        # 👤 Borçlu Seçimi
        self.debtor_layout = QHBoxLayout()
        self.debtor_label = QLabel("👤 Borçlu:")
        self.debtor_dropdown = QComboBox()
        self.debtor_dropdown.currentIndexChanged.connect(self.load_creditors)
        self.debtor_layout.addWidget(self.debtor_label)
        self.debtor_layout.addWidget(self.debtor_dropdown)
        self.layout.addLayout(self.debtor_layout)

        # 💵 Alacaklı Seçimi
        self.creditor_layout = QHBoxLayout()
        self.creditor_label = QLabel("💵 Alacaklı:")
        self.creditor_dropdown = QComboBox()
        self.creditor_dropdown.currentIndexChanged.connect(self.auto_fill_debt)
        self.creditor_layout.addWidget(self.creditor_label)
        self.creditor_layout.addWidget(self.creditor_dropdown)
        self.layout.addLayout(self.creditor_layout)

        # 💰 Ödeme Miktarı
        self.amount_layout = QHBoxLayout()
        self.amount_label = QLabel("💰 Ödeme Miktarı:")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("₺0.00")
        self.amount_layout.addWidget(self.amount_label)
        self.amount_layout.addWidget(self.amount_input)
        self.layout.addLayout(self.amount_layout)

        # 📅 Tarih ve Saat Seçimi (Değiştirilebilir)
        self.date_time_layout = QHBoxLayout()

        # 📅 Tarih Edit
        self.date_label = QLabel("📅 Ödeme Tarihi:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")  
        self.date_edit.setDate(QDate.currentDate())

        # ⏰ Saat Edit
        self.time_label = QLabel("⏰ Saat:")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")  # ✅ Saat Formatı (24 Saat)
        self.time_edit.setTime(datetime.now().time())

        # Layout'a Ekle
        self.date_time_layout.addWidget(self.date_label)
        self.date_time_layout.addWidget(self.date_edit)
        self.date_time_layout.addWidget(self.time_label)
        self.date_time_layout.addWidget(self.time_edit)

        self.layout.addLayout(self.date_time_layout)

        # 📝 Not Alanı
        self.note_label = QLabel("📝 Ödeme Notu (Opsiyonel):")
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Ek bilgi veya not ekleyin...")
        self.layout.addWidget(self.note_label)
        self.layout.addWidget(self.note_input)

        # 📸 Fatura Ekleme
        self.photo_layout = QHBoxLayout()
        self.photo_label = QLabel("📸 Fatura Ekle:")
        self.photo_button = QPushButton("📁 Fotoğraf Seç")
        self.photo_button.clicked.connect(self.add_receipt)
        self.selected_photo_label = QLabel("Seçilen Dosya: Yok")
        self.selected_photo_label.setStyleSheet("font-weight: bold; color: green;")

        self.photo_layout.addWidget(self.photo_label)
        self.photo_layout.addWidget(self.photo_button)
        self.layout.addLayout(self.photo_layout)
        self.layout.addWidget(self.selected_photo_label)
        
        # ✅ Ödeme Yap Butonu
        self.pay_button = QPushButton("💳 Ödeme Yap")
        self.pay_button.clicked.connect(self.process_payment)

        # ⬅ Geri Dön Butonu
        self.back_button = QPushButton("⬅ Geri Dön")
        self.back_button.clicked.connect(self.return_to_summary)
        
        # Layout'a Ekle
        self.buttom_layout = QHBoxLayout()
        self.buttom_layout.addWidget(self.back_button)
        self.buttom_layout.addWidget(self.pay_button)
        self.layout.addLayout(self.buttom_layout)

    # =================================
    # 🟡 Fonksiyon Taslakları
    # =================================

    def load_debtors(self):
        """📋 Load Users Who Have Debts"""
        main_window = self.parent().parent()
        _, _, pool_out, _ = main_window.summary_page.calculate_debts()

        self.debtor_dropdown.clear()
        self.debtor_dropdown.addItem("👤 Kullanıcı Seçiniz")
        for user, debt in pool_out.items():
            if debt > 0:
                self.debtor_dropdown.addItem(user)

    def load_creditors_old(self):
        """💵 Load Creditors Based on Selected Debtor"""
        debtor = self.debtor_dropdown.currentText()
        if debtor == "👤 Kullanıcı Seçiniz":
            return

        settlements = self.calculate_settlements()
        self.creditor_dropdown.clear()
        self.creditor_dropdown.addItem("💵 Alacaklı Seçiniz")

        for settlement in settlements:
            if settlement["from"] == debtor:
                creditor = settlement["to"]
                self.creditor_dropdown.addItem(creditor)

        # Eğer sadece bir alacaklı varsa, direkt doldur
        if self.creditor_dropdown.count() == 2:
            self.creditor_dropdown.setCurrentIndex(1)
    
    def load_creditors(self):
        """💵 Load Creditors Based on Selected Debtor"""
        debtor = self.debtor_dropdown.currentText()
        if debtor == "👤 Kullanıcı Seçiniz":
            return

        # 📂 Tüm Kullanıcıları Yükle
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users_data = json.load(file)
                all_users = [user["name"] for user in users_data.get("users", [])]
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Kullanıcılar yüklenemedi!")
            return

        # 💵 Alacaklı Dropdown'unu Doldur
        self.creditor_dropdown.clear()
        self.creditor_dropdown.addItem("💵 Alacaklı Seçiniz")

        # Borçlu dışında tüm kullanıcıları alacaklı olarak ekle
        for user in all_users:
            if user != debtor:
                self.creditor_dropdown.addItem(user)

    def auto_fill_debt(self):
        """🔄 Mevcut Borcu Otomatik Doldurur (calculate_settlements kullanarak)"""
        debtor = self.debtor_dropdown.currentText()
        creditor = self.creditor_dropdown.currentText()

        if debtor == "👤 Kullanıcı Seçiniz" or creditor == "💵 Alacaklı Seçiniz":
            self.amount_input.setText("₺0.00")
            return

        # 📂 Mevcut Borçları calculate_settlements ile al
        settlements = self.calculate_settlements()

        # 🔍 Doğru borç miktarını bul
        total_debt = 0.0
        for settlement in settlements:
            if settlement["from"] == debtor and settlement["to"] == creditor:
                total_debt = settlement["amount"]
                break

        self.amount_input.setText(f"₺{total_debt:.2f}")

    def add_receipt(self):
        """📸 Fatura Fotoğrafı Ekler"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Fatura Seç", "", "Görseller (*.png *.jpg *.jpeg *.bmp *.pdf)")

        if file_path:
            self.receipt_path = file_path
            self.selected_photo_label.setText(f"Seçilen Dosya: {os.path.basename(file_path)}")
        else:
            self.selected_photo_label.setText("Seçilen Dosya: Yok")
            self.receipt_path = None

    def process_payment(self):
        """💾 Ödeme Kaydeder ve Borç Tablosunu Günceller"""
        debtor = self.debtor_dropdown.currentText()
        total_amount_text = self.amount_input.text().replace("₺", "").strip()
        note = self.note_input.toPlainText()
        payment_date = self.date_edit.date().toString("dd/MM/yyyy")
        payment_time = self.time_edit.time().toString("HH:mm")
        receipt = self.receipt_path

        # 🛑 Giriş Doğrulama
        if debtor == "👤 Kullanıcı Seçiniz":
            QMessageBox.warning(self, "Hata", "Borçlu Seçiniz!")
            return

        try:
            total_amount = float(total_amount_text)
            if total_amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir ödeme miktarı girin!")
            return

        creditor = self.creditor_dropdown.currentText()
        if creditor == "💵 Alacaklı Seçiniz":
            QMessageBox.warning(self, "Hata", "Alacaklı Seçiniz!")
            return

        # 💾 JSON'a Kaydet
        try:
            if not os.path.exists(PAYMENTS_FILE):
                with open(PAYMENTS_FILE, "w", encoding="utf-8") as file:
                    json.dump({"payments": []}, file, indent=4, ensure_ascii=False)
            if receipt:
                new_reciept_path = 'Yok' if receipt is None else f'Fatura_{debtor}_{creditor}_{payment_date}_{payment_time}{os.path.splitext(receipt)[1]}'
                os.rename(receipt, os.path.join(PAYMENT_RECIEPTS_DIR, new_reciept_path))
            else:
                new_reciept_path = 'Yok'
            with open(PAYMENTS_FILE, "r+", encoding="utf-8") as file:
                data = json.load(file)
                new_payment = {
                        "date": payment_date,
                        "time": payment_time,
                        "from": debtor,
                        "to": creditor,
                        "amount": total_amount,
                        "note": note,
                        "receipt": new_reciept_path
                }
                data["payments"].append(new_payment)

                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
                shutil.copy2(receipt, dest_path)
            QMessageBox.information(self, "Başarılı", "Ödemeler başarıyla kaydedildi!")
            self.reset_payment_page()

        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Ödeme kaydedilemedi!")

    def reset_payment_page(self):
        """🔄 Ödeme Sayfasını Sıfırlar"""
        self.debtor_dropdown.setCurrentIndex(0)
        self.creditor_dropdown.clear()
        self.creditor_dropdown.addItem("💵 Alacaklı Seçiniz")
        self.amount_input.setText("₺0.00")
        self.note_input.clear()
        self.selected_photo_label.setText("Seçilen Dosya: Yok")
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.receipt_path = None

    def return_to_summary(self):
        """⬅ Özet Sayfasına Dön"""
        main_window = self.parent().parent()
        if hasattr(main_window, "summary_page"):
            main_window.summary_page.load_data()
            main_window.central_widget.setCurrentWidget(main_window.summary_page)
            self.reset_payment_page()
        else:
            QMessageBox.warning(self, "Hata", "Özet sayfasına dönülemiyor!")

    def calculate_settlements(self):
        """💸 Kim Kime Ne Kadar Ödemeli?"""
        main_window = self.parent().parent()

        users, pool_in, pool_out, net_balances = main_window.summary_page.calculate_debts()
        print(f"Net Balances: {net_balances}")
        # 🟢 Alacaklılar ve 🔴 Borçluları listeleriz
        creditors = []
        debtors = []

        for user, balance in net_balances.items():
            balance_kurus = round(balance)  # 💲 Kuruş cinsine çevir
            if balance_kurus > 0:
                creditors.append((user, balance_kurus))
            elif balance_kurus < 0:
                debtors.append((user, -balance_kurus))  # Pozitif hale getiriyoruz

        # 🧮 Azalan sıraya göre sıralama
        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)

        # ✅ Debug: Check initial lists
        print(f"Creditors: {creditors}")
        print(f"Debtors: {debtors}")

        settlements = []

        for debtor, debt_amount in debtors:
            print(f"\nProcessing Debtor: {debtor}, Amount Owed: {debt_amount / 100:.2f}₺")
            while debt_amount > 0 and creditors:
                creditor, credit_amount = creditors[0]

                payment = min(debt_amount, credit_amount)

                settlements.append({
                    "from": debtor,
                    "to": creditor,
                    "amount": round(payment / 100, 2)  # ₺ cinsine çevir
                })

                print(f"Payment from {debtor} to {creditor}: {payment / 100:.2f}₺")

                debt_amount -= payment
                credit_amount -= payment

                if credit_amount == 0:
                    creditors.pop(0)
                else:
                    creditors[0] = (creditor, credit_amount)

        # ✅ Debug: Final settlements
        print(f"\nSettlements: {settlements}")

        return settlements

    def split_amount(self, total_amount, creditors):
        """
        🔄 Borçlu kişinin borcunu alacaklılar arasında böler.
        
        :param total_amount: (float) Toplam borç miktarı
        :param creditors: (list) Alacaklı isim listesi
        :return: (dict) Her alacaklıya düşen miktar
        """
        num_creditors = len(creditors)
        if num_creditors == 0:
            return {}

        # 💲 Kuruş bazında hesaplama
        total_kurus = round(total_amount * 100)
        base_share = total_kurus // num_creditors
        remainder = total_kurus % num_creditors

        # 🟢 Her alacaklıya eşit miktar + kalan kuruşlar sırayla eklenir
        split_result = {}
        for idx, creditor in enumerate(creditors):
            share = base_share + (1 if idx < remainder else 0)
            split_result[creditor] = round(share / 100, 2)  # ₺ cinsinden döndür

        return split_result

