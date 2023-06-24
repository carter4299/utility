import pandas as pd
import random
import string
import sqlite3
import os

conn = sqlite3.connect(os.path.join(r'C:\Users\~you~\Desktop\~your folder~', 'all_users.db'))
c = conn.cursor()

try:
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT, balance INTEGER)")

    user_ids = []
    balances = []
    for _ in range(1000000):
        temp_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(6, 18)))
        temp_bal = random.randint(0, 10000)

        user_ids.append(temp_id)
        balances.append(temp_bal)

        c.execute("INSERT INTO users VALUES (:user_id, :balance)", {'user_id': temp_id, 'balance': temp_bal})

    conn.commit()

except sqlite3.Error as e:
    print(f"An error occurred: {e.args[0]}")

finally:
    df = pd.DataFrame({
        'user_id': user_ids,
        'balance': balances,
    })
    df.to_csv('all_users.csv', index=False)

    conn.close()
