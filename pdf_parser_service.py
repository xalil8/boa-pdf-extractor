
#!/usr/bin/env python3
# install dependencies:
# pip install Flask pdfplumber

import io
import re
import pdfplumber
from flask import Flask, request, render_template_string

app = Flask(__name__)

# regex patterns
# PAGE_RE = re.compile(r"Page\s+(\d+)\s+of\s+\d+")
# AMT_RE  = re.compile(r"([\-]?[0-9]{1,3}(?:,[0-9]{3})*\.\d{2})$")
PAGE_RE     = re.compile(r"Page\s+(\d+)\s+of\s+\d+")
AMT_RE      = re.compile(r"([\-]?[0-9]{1,3}(?:,[0-9]{3})*\.\d{2})$")
# match either “BANK OF AMERICA” or “BOFA MERCH SVCS” followed by “DES:DEPOSIT”
DEPOSIT_RE  = re.compile(r"(?:BANK OF AMERICA|BOFA MERCH SVCS)\s+DES:DEPOSIT", re.IGNORECASE)

def process_pdf_stream(file_stream):
    """
    Read a PDF file-like stream, extract all DES:DEPOSIT lines
    (both BANK OF AMERICA and BOFA MERCH SVCS), and compute sums.
    Returns (pos_sum, neg_sum).
    """
    file_bytes = file_stream.read()
    pdf_file   = io.BytesIO(file_bytes)
    overall_pos = overall_neg = 0.0

    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    lines = text.splitlines()
    current_page = None

    for i, line in enumerate(lines[:-1]):
        # track page numbers if you need them
        m_page = PAGE_RE.search(line)
        if m_page:
            current_page = int(m_page.group(1))

        # now catch both patterns
        if DEPOSIT_RE.search(line):
            m_amt    = AMT_RE.search(line)
            next_line = lines[i+1]
            # ensure the ID:… CCD line follows
            if m_amt and next_line.startswith("ID:") and "CCD" in next_line:
                amt = float(m_amt.group(1).replace(',', ''))
                if amt >= 0:
                    overall_pos += amt
                else:
                    overall_neg += amt

    return overall_pos, overall_neg

# def process_pdf_stream(file_stream):
#     """
#     Read a PDF file-like stream, extract BoA DES:DEPOSIT lines,
#     and compute overall positive/negative sums.
#     Returns (pos_sum, neg_sum).
#     """
#     # load PDF bytes into pdfplumber
#     file_bytes = file_stream.read()
#     pdf_file = io.BytesIO(file_bytes)

#     overall_pos = overall_neg = 0.0
#     with pdfplumber.open(pdf_file) as pdf:
#         text = "".join((page.extract_text() or "") + "\n" for page in pdf.pages)

#     lines = text.splitlines()
#     current_page = None
#     for i, line in enumerate(lines[:-1]):
#         # update page number
#         m_page = PAGE_RE.search(line)
#         if m_page:
#             current_page = int(m_page.group(1))

#         # detect BoA deposit header
#         if "BANK OF AMERICA" in line and "DES:DEPOSIT" in line:
#             m_amt = AMT_RE.search(line)
#             next_line = lines[i+1]
#             if m_amt and next_line.startswith("ID:") and "CCD" in next_line:
#                 amt = float(m_amt.group(1).replace(',', ''))
#                 if amt >= 0:
#                     overall_pos += amt
#                 else:
#                     overall_neg += amt

#     return overall_pos, overall_neg


TEMPLATE = '''
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>BoA Deposit Summaries</title></head>
<body>
  <h1>BoA Deposit Summaries</h1>
  <form method="POST" enctype="multipart/form-data">
    <p><input type="file" name="pdfs" multiple accept="application/pdf" /></p>
    <p><button type="submit">Upload & Process</button></p>
  </form>
  {% if results %}
    <h2>Results:</h2>
    <ul>
    {% for fname, summary in results %}
      <li><strong>{{ fname }}</strong>: {{ summary }}</li>
    {% endfor %}
    </ul>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        for file in request.files.getlist('pdfs'):
            fname = file.filename
            if fname.lower().endswith('.pdf'):
                pos, neg = process_pdf_stream(file.stream)
                summary = f"Overall: total DEPOSIT (+) = {pos:.4f}, total WITHDRAW (-) = {neg:.4f}"
                results.append((fname, summary))
    return render_template_string(TEMPLATE, results=results)

if __name__ == '__main__':
    # serve on http://localhost:5000
    app.run(host='0.0.0.0', port=5001)
