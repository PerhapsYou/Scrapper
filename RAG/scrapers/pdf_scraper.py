from PyPDF2 import PdfReader, errors  # Import PdfReadError handling
from pdf2image import convert_from_path
import pytesseract
from scrapers.cleaner import Cleaner
import os
from pathlib import Path

DIR = "knowledge"

# There are two types of PDF scrapers initialized under this class
class PDFScraper: 
    # Reads a regular PDF file
    def readPDF(self, file):
        text = ""
        try:
            reader = PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
        except errors.PdfReadError as e:
            print(f"[Error] Cannot read {file} using PdfReader — {e}")
            return None  # Triggers fallback to OCR

        if not text.strip():
            return None  # Return None if there's no readable text
        
        # Save the extracted text to a .txt file
        with open(os.path.join(DIR, Path(file).stem + ".txt"), "w", encoding="utf-8") as f:
            f.write(text)
        return text
    
    # Reads flattened PDFs / PDFs with images
    def readPDFImage(self, file):
        try:
            pages = convert_from_path(file, dpi=300)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
        except Exception as e:
            print(f"[Error] OCR failed for {file} — {e}")
            return ""

        # Clean the extracted OCR text
        cleaned_text = Cleaner.runOCRCleaner(text)

        # Save OCR text to .txt file
        with open(os.path.join(DIR, Path(file).stem + ".txt"), "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        return cleaned_text

# Scans all PDF files inside the 'knowledge' directory
def scan_all_pdfs():
    scraper = PDFScraper()
    for filename in os.listdir(DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(DIR, filename)
            print(f"[PDF Scanner] Scanning: {filename}")
            
            text = scraper.readPDF(file_path)
            if text is None or len(text.strip()) < 50:
                print(f"[Fallback OCR] {filename} appears flattened or unreadable — using OCR")
                scraper.readPDFImage(file_path)
            else:
                print(f"[Success] Extracted text from: {filename}")
                
# Optional: for standalone execution
if __name__ == "__main__":
    try:
        scan_all_pdfs()
    except Exception as e:
        print(f"[FATAL ERROR] PDF scanning failed: {e}")

