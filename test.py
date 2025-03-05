import json
import os


DATA_DIR = "data"
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")

# JSON'u oku ve yükle
def load_expenses():
    try:
        with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("expenses", [])  # "expenses" listesini al, yoksa boş liste döndür
    except FileNotFoundError:
        print("Dosya bulunamadı, boş bir liste döndürülüyor.")
        return []
    except json.JSONDecodeError:
        print("JSON formatı hatalı, lütfen kontrol edin.")
        return []
def load_users():
        """ Kullanıcı listesini JSON'dan alır ve sadece isimleri döndürür. """
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                user_data = json.load(file).get("users", [])

                # Eğer kullanıcılar dict olarak saklanıyorsa sadece isimleri al
                if isinstance(user_data, list) and len(user_data) > 0 and isinstance(user_data[0], dict):
                    return [user["name"] for user in user_data if "name" in user]

                return user_data  # Eğer düz string listesi ise direkt döndür
        else:
            open(USERS_FILE, "w", encoding="utf-8").write('{"users": []}')  # Dosya yoksa oluştur
            return []
def load_payements():
    if os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, "r", encoding="utf-8") as file:
            payments = json.load(file).get("payments", [])
            return payments
    else:
        open(PAYMENTS_FILE, "w", encoding="utf-8").write('{"payments": []}')  # Dosya yoksa oluştur
        return []
# Kullanım
expenses = load_expenses()
users = load_users()
payments = load_payements()
print(users)
print(payments)

pool_out ={user : 0 for user in users}
pool_in ={user : 0 for user in users}

for expense in expenses:
    print('____________________________________________________')
    print(expense.get("paid_by"))  
    print(expense.get("total_amount"))
    pool_in[expense.get("paid_by")] += expense.get("total_amount")
    if 'auto_split' in expense and expense['auto_split'] != {}:
        for name in expense['auto_split']:
            print(name,': ',expense['auto_split'][name])
            pool_out[name] += expense['auto_split'][name]

    elif 'manual_split' in expense and expense['manual_split'] != {}:
        for name in expense['manual_split']:
            print(name,': ',expense['manual_split'][name])
            pool_out[name] += expense['manual_split'][name]
    
    elif 'sub_items' in expense and expense['sub_items'] != []:
        for sub_item in expense['sub_items']:
            print(sub_item["name"],': ',sub_item["price"],sub_item['shared_by'])  # Ürün adını ve fiyatını alır
            for name in sub_item['shared_by']:
                pool_out[name] += sub_item["price"]/len(sub_item['shared_by'])
    else:
        for name in users:
            pool_out[name] += expense['total_amount']/len(users)

print(pool_out)  
print(pool_in)

for payment in payments:
    pool_in[payment['from']] += payment['amount']
    pool_out[payment['to']] += payment['amount']

print(pool_out)
print(pool_in)

for i in users:
    print(i,':',pool_in[i]-pool_out[i])
    