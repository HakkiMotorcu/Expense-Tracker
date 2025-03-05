from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QWidget
import sys
from UI.summary_page import SummaryPage
from UI.expense_entry_page import ExpenseEntryPage
from UI.payment_page import PaymentPage
from UI.edit_page import EditPage

class ExpenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harcama Takip Uygulaması")
        self.setGeometry(100, 100, 800, 600)

        # 📍 Sayfaları Yönetmek İçin StackedWidget Kullanıyoruz
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # 📍 Sayfaları Oluştur
        self.summary_page = SummaryPage(self)
        self.expense_entry_page = ExpenseEntryPage(self)
        self.payment_page = PaymentPage(self)
        self.edit_page = EditPage(self)

        # 📍 Sayfaları Ekleyelim
        self.central_widget.addWidget(self.summary_page)
        self.central_widget.addWidget(self.expense_entry_page)
        self.central_widget.addWidget(self.payment_page)
        self.central_widget.addWidget(self.edit_page)

        # 📍 Özet Sayfasındaki "Masraf Ekle" Butonunu Güncelle
        self.summary_page.add_expense_btn.clicked.connect(self.show_expense_entry_page)
        self.summary_page.make_payment_btn.clicked.connect(self.show_payment_page)
        self.summary_page.view_expenses_btn.clicked.connect(self.show_edit_page)
        

        

    def show_expense_entry_page(self):
        """ Masraf Ekleme Sayfasına Geçiş Yap """
        self.central_widget.setCurrentWidget(self.expense_entry_page)

    # def show_summary_page(self):
    #     """Genel Özet Sayfasına Geri Dön ve Verileri Güncelle"""
    #     self.expense_entry_page.reset_expense_page() # 🧹 Expense Entry Sayfasını Temizle
    #     self.summary_page.load_data()  # 📊 Genel özeti güncelle
    #     self.central_widget.setCurrentWidget(self.summary_page)

    def show_payment_page(self):
        """💳 Ödeme Sayfasına Geçiş"""
        self.payment_page.load_debtors()  # 📋 Borçlu Listesini Yükle
        self.central_widget.setCurrentWidget(self.payment_page)

    def show_edit_page(self):
        """Düzenleme Sayfasına Geçiş"""
        self.central_widget.setCurrentWidget(self.edit_page)

# 📍 Uygulamayı Başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec())
