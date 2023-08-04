from flask import Flask, request, send_from_directory, Response
from PyPDF2 import PdfReader, PdfWriter
import os

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
    files = request.files.getlist('file')
    file_order = request.form.get('fileOrder')  # Retrieve the file order from the form data
    file_order = [int(index) for index in file_order.split(',')] if file_order else range(len(files))

    pdf_writer = PdfWriter()

    for index in file_order:  # Iterate through the files in the specified order
        file = files[index]
        if file.filename.endswith('.pdf'):
            pdf_reader = PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])  # Using reader.pages[page_number]

    merged_pdf_path = os.path.join(UPLOAD_FOLDER, 'merged.pdf')
    with open(merged_pdf_path, 'wb') as merged_file:
        pdf_writer.write(merged_file)

    return send_from_directory(UPLOAD_FOLDER, 'merged.pdf')


if __name__ == '__main__':
    app.run()
