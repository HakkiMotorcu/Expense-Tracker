from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QColor
import json
import os

DATA_DIR = "data"
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")

class SummaryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 📌 Sayfa Başlığı
        self.title = QLabel("📊 Genel Özet")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        self.layout.addWidget(self.title)

        # 📌 Borç Tablosu
        self.debt_table = QTableWidget()
        self.debt_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.debt_table)

        # 📌 Hızlı Erişim Butonları
        self.button_layout = QHBoxLayout()
        self.add_expense_btn = QPushButton("➕ Masraf Ekle")
        self.make_payment_btn = QPushButton("💳 Ödeme Yap")
        self.view_expenses_btn = QPushButton("📄 Düzenleme Sayfası")

        for btn in [self.add_expense_btn, self.make_payment_btn, self.view_expenses_btn]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.button_layout.addWidget(btn)

        self.layout.addLayout(self.button_layout)

        # 📌 Gerçek Verileri Yükle
        self.load_data()

    def load_data(self):
        """ Kullanıcı listesini al ve borç hesaplamasını yap. """
        users, pool_in, pool_out, net_balances = self.calculate_debts()
        self.update_debt_table(users, pool_in, pool_out, net_balances)

    def calculate_debts(self):
        """ Kullanıcıların toplam borç/alacak durumunu hesaplar. """
        users = self.get_users()
        pool_in = {user: 0 for user in users}  # Kullanıcının yaptığı ödemeler (kuruş cinsinden)
        pool_out = {user: 0 for user in users}  # Kullanıcının borçlandığı miktar (kuruş cinsinden)

        # 📌 Harcamaları oku ve borçları hesapla
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
                expenses = json.load(file).get("expenses", [])

            for expense in expenses:
                payer = expense.get("paid_by", "")
                amount_kurus = int(float(expense.get("total_amount", 0)) * 100)  # 💲 Kuruş cinsine çevir

                # 📌 Ödeyen kişinin havuza girişi
                pool_in[payer] += amount_kurus

                # 📌 Auto Split (Otomatik Bölüştürme)
                if "auto_split" in expense and expense["auto_split"]:
                    for debtor, share in expense["auto_split"].items():
                        pool_out[debtor] += int(float(share) * 100)

                # 📌 Manuel Bölüştürme
                elif "manual_split" in expense and expense["manual_split"]:
                    for debtor, share in expense["manual_split"].items():
                        pool_out[debtor] += int(float(share) * 100)

                # 📌 Alt Kalem Paylaşımı (Sub Items)
                elif "sub_items" in expense and expense["sub_items"]:
                    for sub_item in expense["sub_items"]:
                        shared_users = sub_item["shared_by"]
                        sub_item_price_kurus = int(float(sub_item["price"]) * 100)
                        shares = split_equally(sub_item_price_kurus, len(shared_users))

                        for idx, debtor in enumerate(shared_users):
                            pool_out[debtor] += shares[idx]

                else:  # 📌 Eşit Paylaşım (Varsayılan)
                    shares = split_equally(amount_kurus, len(users))
                    for idx, debtor in enumerate(users):
                        pool_out[debtor] += shares[idx]

        # 📌 Ödemeleri işle
        if os.path.exists(PAYMENTS_FILE):
            with open(PAYMENTS_FILE, "r", encoding="utf-8") as file:
                payments = json.load(file).get("payments", [])

            for payment in payments:
                payer = payment["from"]
                receiver = payment["to"]
                amount_kurus = int(float(payment["amount"]) * 100)

                pool_in[payer] += amount_kurus
                pool_out[receiver] += amount_kurus

        # 📌 Net borçları hesapla
        net_balances = {user: pool_in[user] - pool_out[user] for user in users}

        return users, pool_in, pool_out, net_balances

    def update_debt_table(self, users, pool_in, pool_out, net_balances):
        """ Borç tablosunu günceller, net borç durumu 0 olanları mavi yapar. """
        self.debt_table.setRowCount(len(users))
        self.debt_table.setColumnCount(4)  # "Kullanıcı", "Ödemeler", "Borçlar", "Net Durum"

        self.debt_table.setHorizontalHeaderLabels(["Kullanıcı", "Ödeme Yaptı (₺)", "Borçlandı (₺)", "Net Durum (₺)"])

        for row_idx, user in enumerate(users):
            paid = pool_in[user] / 100  # 💲 Kuruş → ₺
            debt = pool_out[user] / 100
            net_balance = net_balances[user] / 100

            # 📌 Hücreleri doldur
            self.debt_table.setItem(row_idx, 0, QTableWidgetItem(user))
            self.debt_table.setItem(row_idx, 1, QTableWidgetItem(f"₺{paid:.2f}"))
            self.debt_table.setItem(row_idx, 2, QTableWidgetItem(f"₺{debt:.2f}"))

            # 📌 Net borç hücresini oluştur
            net_item = QTableWidgetItem(f"₺{net_balance:.2f}")
            net_item.setTextAlignment(0x0004)  # Ortala

            # 🔴 Borçluysa → Kırmızı
            if net_balance < 0:
                net_item.setForeground(QColor("red"))

            # 🟢 Alacaklıysa → Yeşil
            elif net_balance > 0:
                net_item.setForeground(QColor("green"))

            # 🔵 Nötrse → Mavi
            else:
                net_item.setForeground(QColor("blue"))

            self.debt_table.setItem(row_idx, 3, net_item)

    def get_users(self):
        """ Kullanıcı listesini JSON'dan alır ve sadece isimleri döndürür. """
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                user_data = json.load(file).get("users", [])

                if isinstance(user_data, list) and len(user_data) > 0 and isinstance(user_data[0], dict):
                    return [user["name"] for user in user_data if "name" in user]

                return user_data  # Eğer düz string listesi ise direkt döndür
        else:
            open(USERS_FILE, "w", encoding="utf-8").write('{"users": []}')
            return []

def split_equally(total_amount_kurus, num_people):
    """Toplam kuruşu eşit paylaştırır ve kalan kuruşları dağıtır."""
    base_share = total_amount_kurus // num_people
    remainder = total_amount_kurus % num_people

    shares = [base_share] * num_people
    for i in range(remainder):
        shares[i] += 1  # Kalan kuruşları sırayla dağıt

    return shares