import cgi
import cgitb
cgitb.enable()


print("Content-type: text/html;charset=utf-8;")
print()
print("<h1>Hello, World!</h1>")
print("<h2")
# Now the debug traceback will be interleaved with your markup
the_number = 1201032 / 0
print(">The Number: {0:0.4f}</h2>".format(the_number))
