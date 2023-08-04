from flask import Flask, request, send_from_directory, Response
from PyPDF2 import PdfReader, PdfWriter
import os
import uuid
import shutil

UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Check if the request has the 'file' part
    if 'file' not in request.files:
        return Response('No file part', status=400)
    
    files = request.files.getlist('file')
    file_order = request.form.get('fileOrder')  # Retrieve the file order from the form data
    file_order = [int(index) for index in file_order.split(',')] if file_order else range(len(files))

    # Check file size and content type
    for file in files:
        if not file or file.filename == '':
            return Response('No selected file', status=400)
        if not file.filename.endswith('.pdf') or file.content_type != 'application/pdf':
            return Response('Invalid file type', status=400)

    pdf_writer = PdfWriter()

    for index in file_order:  # Iterate through the files in the specified order
        file = files[index]
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])  # Using reader.pages[page_number]

   # Create a unique file name for the merged PDF
    unique_filename = str(uuid.uuid4()) + '_merged.pdf'
    merged_pdf_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    with open(merged_pdf_path, 'wb') as merged_file:
        pdf_writer.write(merged_file)

    # Serve the file and clean up
    response = send_from_directory(UPLOAD_FOLDER, unique_filename)
    response.call_on_close(lambda: os.unlink(merged_pdf_path))  # Delete the file after serving

    return response


if __name__ == '__main__':
    app.run()
