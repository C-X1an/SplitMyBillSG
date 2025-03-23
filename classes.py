class Bill:
    def __init__(self):
        self._paxcount = 0
        self.items = []
        self.gst = False
        self.svccharge = False
        self.discount = 0
        self.payees = {}


    @property
    def paxcount(self):
        return self._paxcount

    @paxcount.setter
    def paxcount(self, paxcount):
        if isinstance(paxcount, int):
            self._paxcount = paxcount
        else:
            raise ValueError("Pax Count is not an integer")


    def addItem(self, item):
        if isinstance(item, dict) == False:
            raise ValueError("Item was not parsed as a dictionary")
        if len(item) != 4:
            raise ValueError("Item should have 4 key-value pairs")
        if item["payee"] and item["payee"] not in self.payees:
            raise ValueError("Invalid Payee")
        self.items.append(item)


    def removeItem(self, serial):
            self.items.pop(serial)
            for index in range(serial, len(self.items)):
                self.items[index]["serial"] -= 1

class Payee:
    def __init__(self, name):
        self.name = name
        self.items = []
        self.sum = 0


    def addItem(self, item: dict):
        if isinstance(item, dict) == False:
            raise ValueError("Item parsed was not a dictionary")
        if len(item) != 3:
            raise ValueError("Item should have 3 key-value pairs")
        self.items.append(item)
        self.sum += float(item["price"])


    @property
    def sum(self):
        return self._sum

    @sum.setter
    def sum(self, sum):
        if isinstance(sum, int):
            self._sum = sum
        elif isinstance(sum, float):
            self._sum = sum
        else:
            raise ValueError("Sum must be an integer or float")
        self._sum = round(self._sum, 2)
