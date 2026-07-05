from flask import Flask, render_template, request, redirect, Response
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
from database import (
    init_db,
    add_transaction,
    get_transactions,
    delete_transaction,
    get_transaction,
    update_transaction,
    export_transactions,
    get_monthly_expenses,
    get_category_summary    
)

def generate_pie_chart(income, expense):

    if income == 0 and expense == 0:
        income = 1
        expense = 1

    labels = ["Income", "Expense"]
    values = [income, expense]
    colors = ["green", "red"]

    plt.figure(figsize=(5,5))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors
    )

    plt.title("Income vs Expense")

    os.makedirs("static/images", exist_ok=True)

    plt.savefig("static/images/pie_chart.png")

    plt.close()

def generate_bar_chart():

    data = get_monthly_expenses()

    months = []
    amounts = []

    for month, amount in data:
        months.append(month)
        amounts.append(amount)

    plt.figure(figsize=(7,4))

    plt.bar(months, amounts, color="royalblue")

    plt.title("Monthly Expenses")
    plt.xlabel("Month")
    plt.ylabel("Expense")

    plt.tight_layout()

    os.makedirs("static/images", exist_ok=True)

    plt.savefig("static/images/bar_chart.png")

    plt.close()

app = Flask(__name__)
init_db()

@app.route("/")
def home():

    search = request.args.get("search", "")
    category = request.args.get("category", "")
    date = request.args.get("date", "")
    
    transactions = get_transactions(search, category, date)
    category_summary = get_category_summary()

    income = 0
    expense = 0

    for row in transactions:

        if row[1] == "Income":

            income += row[3]

        else:

            expense += row[3]

    balance = income - expense

    generate_pie_chart(income, expense)

    generate_bar_chart()

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expense=expense,
        balance=balance,
        category_summary=category_summary
    )


@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        t = request.form["type"]
        c = request.form["category"].strip().lower()
        amount = request.form["amount"]
        if not amount:
            return "Amount is required"
        a = float(amount)

        d = request.form["description"].strip()
        dt = request.form["date"]
        add_transaction(t, c, a, d, dt)

    

    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):

    delete_transaction(id)

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if request.method == "POST":

        t = request.form["type"]
        c = request.form["category"].strip().lower()
        a = float(request.form["amount"])
        d = request.form["description"].strip()
        dt = request.form["date"]

        update_transaction(id, t, c, a, d, dt)

        return redirect("/")

    transaction = get_transaction(id)

    return render_template(
        "edit.html",
        transaction=transaction
    )

@app.route("/export")
def export():

    rows = export_transactions()

    csv_data = "ID,Type,Category,Amount,Description,Date\n"

    for row in rows:
        csv_data += f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transactions.csv"
        }
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )