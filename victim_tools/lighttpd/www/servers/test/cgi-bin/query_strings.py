#!python
import cgi
import cgitb
cgitb.enable()

import os
import pprint
from urllib.parse import parse_qs

# The query string is put into the environment variables
# by the CGI server, and made accessible using the `os` module
query_string = os.environ["QUERY_STRING"]
request_method = os.environ["REQUEST_METHOD"]

# Convert the query string into a dictionary where elements are lists of scalars
query_string_dict = parse_qs(query_string)

# The HTTP Headers
print("Content-type: text/html;charset=utf-8;")
print()  # This blank print indicates the end of the Headers
# The Content
# Start with a preamble describing the page
print("This script is meant to demonstrate how a Query String will be parsed into Python objects.")
print("A Query String is everything after the first '?' in a URL, and is made up of 'name=value' pairs.")
print("It will be stored in an environment variable and made accessible to the CGI script")
# This link points back to this page, with some extra query string parameters appended
# to demonstrate the behavior
print("<div style='margin-top:5px;'><a href='/cgi-bin/query_strings.py?foo=bar&baz=ping&baz=pong'>Example</a></div>")
print("<div style='margin-top:5px;'>")
print("Request Method: {0}<br><br>".format(request_method))
print("The query string is \"{0}\" <pre>{1}</pre>".format(query_string, pprint.pformat(query_string_dict)))
print("</div>")
