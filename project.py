import datetime
from flask import Flask, render_template, redirect, flash, url_for, send_file, request, session
from mindee import Client, PredictResponse, product
from classes import Bill, Payee
from flask_session import Session

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return redirect("/pax_receipt")


@app.route("/pax_receipt", methods=["GET", "POST"])
def pax_receipt():
    if request.method == "POST":
        bill = session["bill"]
        bill.paxcount = int(request.form.get("paxcount"))
        if receipt:= request.files.get("file"):
            # does not work (theory is that session variables not allowed to store FileStorage Objects)
            # bill.receipt = request.files["file"]
            mindee_client = Client(api_key="bc00c18445c0b62850eac398051d842a")
            input_doc = mindee_client.source_from_bytes(receipt.read(), receipt.filename)
            result: PredictResponse = mindee_client.parse(product.ReceiptV5, input_doc)
            for line_items_elem in result.document.inference.prediction.line_items:
                item_name, quantity, unit_price, total_amount = line_items_elem.description, line_items_elem.quantity, line_items_elem.unit_price, line_items_elem.total_amount
                if not unit_price and total_amount and quantity:
                        unit_price = total_amount / quantity
                try:
                    for _ in range(int(quantity)):
                        bill.addItem({ "serial": len(bill.items), "name": item_name, "payee": None, "price": unit_price })
                except TypeError:
                    pass
            for taxes_elem in result.document.inference.prediction.taxes:
                if taxes_elem.rate == 9 or taxes_elem.code == "GST":
                    bill.gst = True
                elif taxes_elem.rate == 10:
                    bill.svccharge = True
        return redirect(url_for("naming"))
    else:
        session["bill"] = Bill()
        return render_template("pax_receipt.html", bill=session["bill"])


@app.route("/naming", methods=["GET", "POST"])
def naming():
    bill = session["bill"]
    if request.method == "POST":
        for counter in range(bill.paxcount):
            name = request.form.get("name" + str(counter + 1))
            bill.payees[name] = Payee(name)
        return redirect("/items_list")
    else:
        return render_template("naming.html", paxcount=int(bill.paxcount))


@app.route("/items_list", methods=["GET", "POST"])
def items_list():
    bill = session["bill"]
    if request.method == "POST":
        gst, svccharge, discount = request.form.get("gst"), request.form.get("svccharge"), float(request.form.get("discount"))
        bill.gst = True if gst else False
        bill.svccharge = True if svccharge else False
        bill.discount = discount
        try:
            assign_payees()
        except KeyError:
            flash("Items cannot be submitted, ensure all items have a valid payee", "error")
            return redirect("/items_list")
        return redirect("/summary")
    else:
        return render_template("items_list.html", items=bill.items, bill=bill, payees=bill.payees)


def assign_payees():
    bill = session["bill"]
    clear_payees()
    for item in bill.items:
            bill.payees[item["payee"]].addItem({"serial": item["serial"], "name": item["name"], "price": item["price"]})
    for payee in bill.payees:
        if bill.svccharge:
            bill.payees[payee].sum *= 1.1
        if bill.gst:
            bill.payees[payee].sum *= 1.09
        bill.payees[payee].sum -= (bill.discount / len(bill.payees))


def clear_payees():
    bill = session["bill"]
    for payee in bill.payees:
        bill.payees[payee].items = []
        bill.payees[payee].sum = 0


@app.route("/add_item", methods=["POST"])
def add_item():
    bill = session["bill"]
    item_name, unit_price, payee = request.form.get("item-name"), request.form.get("item-price"), request.form.get("item-payee")
    bill.addItem({ "serial": len(bill.items), "name": item_name, "payee": payee, "price": unit_price })
    return redirect("/items_list")


@app.route("/edit_item", methods=["POST"])
def edit_item():
    bill = session["bill"]
    serial, item_name, unit_price, payee = int(request.form.get("item-serial")), request.form.get("item-name"), float(request.form.get("item-price")), request.form.get("item-payee")
    bill.items[serial]["name"], bill.items[serial]["price"], bill.items[serial]["payee"] = item_name, unit_price, payee
    return redirect("/items_list")


@app.route("/remove_item", methods=["POST"])
def remove_item():
    bill = session["bill"]
    serial = int(request.form.get("item-serial"))
    bill.removeItem(serial)
    return redirect("/items_list")


@app.route("/summary", methods=["GET", "POST"])
def summary():
    if request.method == "POST":
        session.clear()
        return redirect("/pax_receipt")
    else:
        bill = session["bill"]
        return render_template("summary.html", bill=bill, payees=bill.payees)

def main():
    app.run()


if __name__ == "__main__":
    main()
