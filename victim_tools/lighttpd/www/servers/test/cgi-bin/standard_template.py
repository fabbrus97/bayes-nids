#!python
# The CGI imports
import cgi
import cgitb
cgitb.enable()

# The rest of the imports

# The computation
the_number = 1201032 / 2912


# The HTTP Headers
print("Content-type: text/html;charset=utf-8;")
print()  # This blank print indicates the end of the Headers
# The Content
print("<h1>Hello, World!</h1>")
print("<h2>The Number: {0:0.4f}</h2>".format(the_number))
