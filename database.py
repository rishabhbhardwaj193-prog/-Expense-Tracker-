import sqlite3

DATABASE = "expense.db"

def init_db():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        type TEXT,

        category TEXT,

        amount REAL,

        description TEXT,

        date TEXT

    )
    """)

    conn.commit()

    conn.close()


def add_transaction(t, c, a, d, dt):
    
    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions(type, category, amount, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (t, c, a, d, dt))



    conn.commit()
    

    conn.close()

def get_transactions(search="", category="", date=""):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if search:
        query += " AND LOWER(TRIM(category)) LIKE ?"
        params.append("%" + search.lower().strip() + "%")

    if category:
        query += " AND TRIM(category) = ?"
        params.append(category)
    
    if date:
        query += " AND date = ?"
        params.append(date)

    query += " ORDER BY id DESC"

    

    cur.execute(query, params)

    rows = cur.fetchall()

    

    conn.close()

    return rows

def delete_transaction(id):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("DELETE FROM transactions WHERE id = ?", (id,))

    conn.commit()

    conn.close()

def get_transaction(id):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM transactions WHERE id = ?",
        (id,)
    )

    row = cur.fetchone()

    conn.close()

    return row

def update_transaction(id, t, c, a, d, dt):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
        UPDATE transactions
        SET type = ?,
            category = ?,
            amount = ?,
            description = ?,
            date = ?
        WHERE id = ?
    """, (t, c, a, d, dt, id))

    conn.commit()

    conn.close()

def export_transactions():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("SELECT * FROM transactions ORDER BY id DESC")

    rows = cur.fetchall()

    conn.close()

    return rows

def get_monthly_expenses():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
        SELECT substr(date,1,7), SUM(amount)
        FROM transactions
        WHERE LOWER(type)='expense'
        GROUP BY substr(date,1,7)
        ORDER BY substr(date,1,7)
    """)

    data = cur.fetchall()

    conn.close()

    return data

def get_category_summary():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
        SELECT TRIM(category), SUM(amount)
                FROM transactions
                GROUP BY TRIM(category)
                ORDER BY SUM(amount) DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows

