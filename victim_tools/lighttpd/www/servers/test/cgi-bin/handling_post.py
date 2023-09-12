import cgi
import cgitb
cgitb.enable()

import os

request_method = os.environ["REQUEST_METHOD"]

content_buffer = []

if request_method.upper() == "POST":
    # This page is receiving a POST request, so they must
    # be submitting data, process it accordingly.
    content_buffer.append("Content-type: text/html;charset=utf-8;")
    content_buffer.append("")
    content_buffer.append("<h1>You posted, huzzah!</h1>")

    form_data = cgi.FieldStorage()
    content_buffer.append("Your text was:<pre>{0}</pre>".format(form_data.getvalue("text-input")))
    content_buffer.append("<div><a href='/cgi-bin/handling_post.py'>Back To Form</a></div>")
else:
    # This page is not receiving a POST request, so display
    # the form
    content_buffer.append("Content-type: text/html;charset=utf-8;")
    content_buffer.append("")
    content_buffer.append("""
<h1>Handling Post Requests</h1>
<form action="/cgi-bin/handling_post.py" method="POST">
    <input type='text' placeholder="Put some text here, to show the server"
     name='text-input' style='width:400px;'/>
    <input type='submit'/>
</form>
    """)

print('\n'.join(content_buffer))
