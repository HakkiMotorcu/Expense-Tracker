# 🧾 Expense Tracker (Just for Fun!)

This is an **initial version** of a lightweight expense tracker built using **Python and PyQt5**. It's designed for shared households to manage expenses, payments, and debts in a simple, visual way.

> 🚧 Not fully functional – still a work in progress. Made for fun and learning!

---

## ✨ Features (so far)

- Add shared or individual expenses
- Record payments between users
- Visualize who owes whom with a colorful debt table
- Dynamic store and product suggestions based on history
- Automatic type detection for product names (e.g. `Ekmek: Tam Buğday`)
- Price history tracking per product
- **Optional** Gemini Flash support for extracting text from receipt images 🧠📸 *(image-to-text receipt import)*

---

## 📂 Data

Everything is stored in simple `.json` files:
- `users.json`
- `expenses.json`
- `payments.json`
- `stores_products.json`

---

## 🚀 Run Locally

```bash
# 1. Clone this repo
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```
