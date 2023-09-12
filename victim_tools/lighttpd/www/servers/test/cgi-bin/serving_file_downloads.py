#!python
# The CGI imports
import cgi
import cgitb
cgitb.enable()

import random


def make_data():
    data = dict(
        value=random.gauss(256., 10.),
        name=random.choice(["Sam", "Bob", "Jane", "Alice", "Foo", "Bar"]))
    return data


print("Content-type: text/csv;charset=utf-8;")
print("Content-disposition: attachment;filename=\"data.csv\"")
print()
print("name,value")
for i in range(30):
    row = make_data()
    print(row['name'], ",", row['value'])
