# BoA PDF Extractor

A Flask web application for extracting and summarizing deposit transactions from Bank of America PDF statements.

## Features

- Upload multiple PDF bank statements
- Extract deposit transactions (both positive and negative)
- Calculate total deposits and withdrawals
- Web interface for easy file processing

## Dependencies

```bash
pip install Flask pdfplumber

Usage

Run the application:

bashpython app.py

Open browser to http://localhost:5001
Upload PDF bank statements
View extracted deposit summaries

How it Works

Uses regex patterns to identify deposit transactions
Matches "BANK OF AMERICA" or "BOFA MERCH SVCS" with "DES:DEPOSIT"
Validates transactions with following "ID:" and "CCD" lines
Separates positive (deposits) and negative (withdrawals) amounts

File Structure
boa-pdf-extractor/
├── app.py          # Main Flask application
└── README.md       # This file
Notes

Designed specifically for Bank of America statement format
Supports multi-page PDF processing
Handles comma-separated monetary values
Educational/personal use only