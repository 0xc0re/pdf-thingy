from flask import Flask, request, send_from_directory, Response
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
import tempfile
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
    file_order = request.form.get('fileOrder')
    file_order = [int(index) for index in file_order.split(',')] if file_order else range(len(files))

    pdf_writer = PdfWriter()

    try:
        for index in file_order:
            file = files[index]
            if file.filename.endswith('.pdf') and file.content_length <= MAX_FILE_SIZE:
                pdf_reader = PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
            else:
                return Response('Invalid file or file size exceeded', status=400)

        # Create a temporary file for the merged PDF
        merged_file = tempfile.NamedTemporaryFile(delete=False)
        pdf_writer.write(merged_file)
        merged_file.close()

        return send_file(merged_file.name, as_attachment=True, attachment_filename='merged.pdf', mimetype='application/pdf')

    except Exception as e:
        return Response(str(e), status=500)

    finally:
        # Cleanup: Remove temporary merged file
        if merged_file:
            os.unlink(merged_file.name)


if __name__ == '__main__':
    app.run()
