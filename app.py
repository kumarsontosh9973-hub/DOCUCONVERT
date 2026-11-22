
from pathlib import Path
from uuid import uuid4
import subprocess

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from pdf2docx import Converter

app = Flask(__name__)
app.secret_key = "my_document_converter_secret"

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "converted"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# PDF TO WORD CONVERSION
@app.route("/pdf-to-word", methods=["POST"])
def pdf_to_word():

    file = request.files.get("document")

    if not file or file.filename == "":
        flash("Please select a PDF file.")
        return redirect(url_for("home"))

    if not file.filename.lower().endswith(".pdf"):
        flash("Please upload a PDF file only.")
        return redirect(url_for("home"))

    filename = secure_filename(file.filename)
    unique_id = uuid4().hex

    pdf_path = UPLOAD_FOLDER / f"{unique_id}_{filename}"
    word_path = OUTPUT_FOLDER / f"{unique_id}.docx"

    file.save(pdf_path)

    converter = None

    try:
        converter = Converter(str(pdf_path))
        converter.convert(str(word_path))

        return send_file(
            word_path,
            as_attachment=True,
            download_name=Path(filename).stem + ".docx"
        )

    except Exception:
        flash("PDF conversion failed. Please try another PDF.")
        return redirect(url_for("home"))

    finally:
        if converter:
            converter.close()

        if pdf_path.exists():
            pdf_path.unlink()


# WORD TO PDF CONVERSION
@app.route("/word-to-pdf", methods=["POST"])
def word_to_pdf():

    file = request.files.get("document")

    if not file or file.filename == "":
        flash("Please select a Word file.")
        return redirect(url_for("home"))

    if not file.filename.lower().endswith(".docx"):
        flash("Please upload a DOCX file only.")
        return redirect(url_for("home"))

    filename = secure_filename(file.filename)
    unique_id = uuid4().hex

    word_path = UPLOAD_FOLDER / f"{unique_id}_{filename}"
    pdf_path = OUTPUT_FOLDER / f"{unique_id}.pdf"

    file.save(word_path)

    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(OUTPUT_FOLDER),
                str(word_path)
            ],
            check=True,
            capture_output=True,
            text=True
        )

        generated_pdf = OUTPUT_FOLDER / f"{word_path.stem}.pdf"

        if not generated_pdf.exists():
            raise FileNotFoundError("PDF file was not created.")

        generated_pdf.rename(pdf_path)

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=Path(filename).stem + ".pdf"
        )

    except Exception:
        flash("Word conversion failed. Please try again.")
        return redirect(url_for("home"))

    finally:
        if word_path.exists():
            word_path.unlink()


# Run application
if __name__ == "__main__":
    app.run(debug=True)
