from flask import send_file, render_template_string
from xhtml2pdf import pisa
import io
import datetime
from flask import Flask, request, jsonify, render_template
from PIL import Image
import easyocr
import difflib
import os
import unicodedata
from werkzeug.utils import secure_filename

app = Flask(__name__)
reader = easyocr.Reader(['en'])

REVERSAL_PAIRS = [('b', 'd'), ('d', 'b'), ('p', 'q'), ('q', 'p')]

def normalize(text):
    return unicodedata.normalize('NFKC', text.lower())

def count_reversals(expected, actual):
    return sum(1 for a, b in zip(expected, actual) if (a, b) in REVERSAL_PAIRS)

def predict_dyslexia(subs, inserts, deletes, reversals, cer, wer):
    score = 0

    if cer > 0.25: score += 2
    elif cer > 0.1: score += 1

    if wer > 0.3: score += 2
    elif wer > 0.1: score += 1

    if subs > 7: score += 2
    elif subs > 3: score += 1

    if inserts > 5: score += 2
    elif inserts > 2: score += 1

    if deletes > 5: score += 2
    elif deletes > 2: score += 1

    if reversals >= 5: score += 2
    elif reversals >= 3: score += 1

    if score >= 7:
        return "High likelihood of dyslexia (🔥) – Recommend detailed screening."
    elif score >= 4:
        return "Moderate likelihood (⚠️) – Monitor and observe further."
    else:
        return "Low likelihood (✅) – No significant indicators found."

def calculate_stats(expected, actual):
    expected = normalize(expected)
    actual = normalize(actual)
    matcher = difflib.SequenceMatcher(None, expected, actual)

    comparison_html = ""
    subs, inserts, deletes = 0, 0, 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        chunk = expected[i1:i2]
        if tag == 'equal':
            comparison_html += f"<span class='correct'>{chunk}</span>"
        else:
            comparison_html += f"<span class='incorrect' title='Got: {actual[j1:j2]}'>{chunk}</span>"
            if tag == 'replace': subs += 1
            elif tag == 'insert': inserts += 1
            elif tag == 'delete': deletes += 1

    char_error_rate = round(1 - matcher.ratio(), 3)
    word_error_rate = round(1 - difflib.SequenceMatcher(None, expected.split(), actual.split()).ratio(), 3)
    reversals = count_reversals(expected, actual)
    dyslexia_risk = predict_dyslexia(subs, inserts, deletes, reversals, char_error_rate, word_error_rate)

    return {
        "comparison_html": comparison_html,
        "char_error_rate": char_error_rate,
        "word_error_rate": word_error_rate,
        "substitutions": subs,
        "insertions": inserts,
        "deletions": deletes,
        "reversed_letters": reversals,
        "dyslexia_risk": dyslexia_risk
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ocr-compare', methods=['POST'])
def ocr_compare():
    image = request.files.get('image')
    expected = request.form.get('expected', '').strip()

    if not image or not expected:
        return jsonify({'error': 'Missing image or expected sentence'}), 400
    if len(expected.split()) > 500:
        return jsonify({'error': 'Expected sentence exceeds 500 words'}), 400

    try:
        filename = secure_filename(image.filename)
        temp_path = os.path.join("temp_" + filename)
        image.save(temp_path)

        results = reader.readtext(temp_path, detail=0)
        os.remove(temp_path)

        actual = " ".join(results).strip()
        if not actual:
            return jsonify({'error': 'OCR failed to recognize any text'}), 400

        stats = calculate_stats(expected, actual)

        return jsonify({
            "expected": expected,
            "ocr_output": actual,
            **stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Render HTML content from Jinja2 template
    html = render_template('report_template.html', **data, timestamp=timestamp)
    
    # Ensure reports directory exists
    os.makedirs('static/reports', exist_ok=True)
    report_filename = f"static/reports/report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Convert HTML to PDF using xhtml2pdf
    with open(report_filename, "w+b") as pdf_file:
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=pdf_file)
    
    if pisa_status.err:
        return jsonify({"error": "PDF generation failed"}), 500
    
    return jsonify({ "download_url": f"/{report_filename}" })


if __name__ == '__main__':
    app.run(debug=True)

