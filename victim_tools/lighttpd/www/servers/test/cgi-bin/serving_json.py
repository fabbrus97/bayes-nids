#!python
# The CGI imports
import cgi
import cgitb
cgitb.enable()

# The rest of the imports
import json
import random

data = dict(
    value=random.gauss(256., 10.),
    name=random.choice(["Sam", "Bob", "Jane", "Alice", "Foo", "Bar"]))


# The HTTP Headers
# Instead of sending text/html, here we're sending application/json
print("Content-type: application/json;charset=utf-8;")
print()
# The Content here is just the json string form of the dynamically
# generated data dictionary
print(json.dumps(data))
