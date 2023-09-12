import cgi
import cgitb
cgitb.enable()

import os

content_buffer = []

request_method = os.environ["REQUEST_METHOD"]

content_buffer = []

if request_method.upper() == "POST":
    # This page is receiving a POST request, so they must
    # be submitting data, process it accordingly.
    content_buffer.append("Content-type: text/html;charset=utf-8;")
    content_buffer.append("")
    form_data = cgi.FieldStorage()
    # If the user was allowed to upload multiple files, this will either be
    # a single file object, or a list
    file_storage = form_data['input-file']
    if not isinstance(file_storage, list):
        file_storage = [file_storage]
    content_buffer.append("<h1>You Uploaded {} File{}!</h1><a href='/cgi-bin/handling_file_uploads.py'>Back</a>".format(
        len(file_storage), "s" if len(file_storage) > 1 else ""))
    for file_obj in file_storage:
        # All files so uploaded are opened in binary mode, which
        # means that all reads produce bytes objects, and that newlines
        # are not normalized.
        file_content = file_obj.file.read().decode(
            "utf-8").replace("\r\n", "\n")
        content_buffer.append("""
        <h3>{name}</h3>
        <div style='max-height:400px;overflow-y:auto;width:900px;'>
            <pre>{file_storage}</pre>
        </div>
        """.format(
            name=file_obj.filename,
            file_storage=file_content))
else:
    # This page is not receiving a POST request, so display
    # the form
    content_buffer.append("Content-type: text/html;charset=utf-8;")
    content_buffer.append("")
    # To permit file uploads, the <form> tag must have the attribute `enctype="multipart/form-data"`
    # to permit the form to include files
    content_buffer.append("""
    <h1>Handling File Uploads</h1>
    <form action="/cgi-bin/handling_file_uploads.py" method="POST" enctype="multipart/form-data">
        <input type='file' placeholder="Put some text here, to show the server"
         name='input-file' multiple style='width:400px;'/>
        <input type='submit'/>
    </form>
    """)

print('\n'.join(content_buffer))
