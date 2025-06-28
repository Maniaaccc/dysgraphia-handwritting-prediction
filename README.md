# 🧠 OCR with Dyslexia & Dysgraphia Prediction

This web application analyzes a scanned image of handwritten text and compares it with an expected sentence to identify possible symptoms of **dyslexia** or **dysgraphia**. It uses **OCR (Optical Character Recognition)** with **EasyOCR**, computes error metrics, detects common letter reversals, and generates a downloadable **PDF report** summarizing the analysis.

---

## 🚀 Features

- 📷 Upload a handwriting image.
- 📝 Enter the expected sentence (up to 500 words).
- 🔍 Performs OCR on the uploaded image.
- ⚖ Compares actual vs. expected text.
- 📊 Calculates:
  - Character Error Rate (CER)
  - Word Error Rate (WER)
  - Substitutions, Insertions, Deletions
  - Letter Reversals (e.g., b ↔ d)
- 🧠 Predicts possible dyslexia risk level.
- 📄 Generates a downloadable PDF report.

---

## 💡 Tech Stack

- **Frontend**: HTML, JavaScript
- **Backend**: Flask (Python)
- **OCR**: [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- **PDF Generator**: xhtml2pdf
- **Libraries**: Pillow, Difflib, Unicodedata, WerkZeug

---

## 📁 Project Structure

ocr-dyslexia-app/
│
├── app.py # Flask backend
├── requirements.txt # Python dependencies
├── templates/
│ ├── index.html # Frontend HTML
│ └── report_template.html # PDF report template
├── static/
│ └── reports/ # Generated PDF reports
└── README.md # Project overview


---

## ⚙ Setup Instructions

### 🔹 Prerequisites

- Python 3.8 or above
- Git (if deploying with GitHub)

### 🔹 Installation

```bash
git clone https://github.com/yourusername/ocr-dyslexia-app.git
cd ocr-dyslexia-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
