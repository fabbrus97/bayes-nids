#!python
# The CGI imports
import cgi
import cgitb
cgitb.enable()

import os
from http import cookies
import pprint


# The cookie string is stored in the environment
raw_user_cookies = os.getenv("HTTP_COOKIE")
# Creates a dictionary-like object which knows
# how to parse the cookie string, and maps key
# to a wrapped object called a Morsel, which
# includes the key, value, expiration, security,
# and isolation
user_cookies = cookies.SimpleCookie()
user_cookies.load(raw_user_cookies)

visited_times_morsel = user_cookies.get("visited_this_page")
if visited_times_morsel is None:
    visited_times = 0
else:
    visited_times = int(visited_times_morsel.value)

new_cookies = cookies.SimpleCookie()
# Create the new Morsel object with value (visited_times + 1)
new_cookies["visited_this_page"] = visited_times + 1
new_cookies["visited_this_page"]["path"] = "/"

# If the visit counter exceeds 20, we'll delete the cookie
if visited_times > 5:
    new_cookies["visited_this_page"]["expires"] = "Thu, 01, Jan 1990 00:00:00 GMT"


# The HTTP Headers
print("Content-type: text/html;charset=utf-8;")
print(new_cookies)
print()  # This blank print indicates the end of the Headers
# The Content
print("""<html><head></head>
<body>
    <h1>Cookies</h1>
    <div>
    A cookie is a key-value pair that is included in each HTTP
    request made by the browser that may persist across several
    sessions. They may or may not be visible to JavaScript under
    <code>document.cookie</code></div>
    """)
print("<p>Cookies received on the server")
print("<pre>{}</pre></p>".format(pprint.pformat({morsel.key: morsel.value for morsel in user_cookies.values()})))
print("<p>Visible to the client-side code:<br><pre>")
print("<script>document.write(document.cookie)</script>")
print("""</pre></p>
</body></html>""")
