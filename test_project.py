import pytest
from cs50p.Week10.project import *
from classes import *


bill = Bill()
payee = Payee("James")
bill.payees["James"] = payee

def test_paxcount_incorrect():
    with pytest.raises(ValueError):
        bill.paxcount = "Error"


def test_paxcount_correct():
    bill.paxcount = 2
    assert bill.paxcount == 2


def test_addItem_incorrect():
    with pytest.raises(ValueError):
        bill.addItem({"error": "error"})


def test_billAddItem_correct():
    test_item = {"serial": 0, "name": "Fish & Chips", "payee": "James", "price": 3}
    bill.addItem(test_item)
    assert bill.items[0] == test_item


def test_payeeAddItem_correct():
    test_item = {"serial": 0, "name": "Fish & Chips", "price": 3}
    payee.addItem(test_item)
    assert payee.items[0] == test_item


def test_removeItem():
    bill.removeItem(0)
    assert len(bill.items) == 0


def test_sum_incorrect():
    with pytest.raises(ValueError):
        payee.sum = "Error"


def test_sum_coreect():
    payee.sum = 2
    assert payee.sum == 2


def test_assignPayees():
    test_item = {"serial": 0, "name": "Fish & Chips", "payee": "James", "price": 3}
    bill.addItem(test_item)
    assign_payees()
    assert bill.payees[test_item["payee"]].sum == 3


def test_clearPayees():
    clear_payees()
    assert len(bill.payees["James"].items) == 0



# remodled functions for testing as this will be ran in a non-webpage environment
def assign_payees():
    clear_payees()
    for item in bill.items:
            bill.payees[item["payee"]].addItem({"serial": item["serial"], "name": item["name"], "price": item["price"]})
    for payee in bill.payees:
        if bill.svccharge:
            bill.payees[payee].sum *= 1.1
        if bill.gst:
            bill.payees[payee].sum *= 1.09
        bill.payees[payee].sum -= (bill.discount / len(bill.payees))

# remodled functions for testing as this will be ran in a non-webpage environment
def clear_payees():
    for payee in bill.payees:
        bill.payees[payee].items = []
        bill.payees[payee].sum = 0


