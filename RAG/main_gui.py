# main_gui.py

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt
import os
import shutil
import sys

# Import your scraper modules
from scrapers import web_scraper, pdf_scraper, txt_formatter

# Accepted file types for drag-and-drop
ACCEPTED_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
UPLOAD_DIR = "knowledge/"

class DropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("RAG Scraper & Formatter GUI")
        self.setGeometry(300, 300, 600, 450)

        layout = QVBoxLayout()

        self.instructions = QLabel("📂 Drag and drop .txt, .pdf, or image files below:")
        layout.addWidget(self.instructions)

        self.logBox = QTextEdit()
        self.logBox.setReadOnly(True)
        layout.addWidget(self.logBox)

        self.runButton = QPushButton("🚀 Run Full Pipeline")
        self.runButton.clicked.connect(self.runPipeline)
        layout.addWidget(self.runButton)

        self.setLayout(layout)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def log(self, message):
        self.logBox.append(message)
        QApplication.processEvents()  # Force update during long tasks

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ACCEPTED_EXTENSIONS:
                dest = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
                shutil.copy(file_path, dest)
                self.log(f"✅ File added: {os.path.basename(file_path)}")
            else:
                self.log(f"⚠️ Unsupported file type: {os.path.basename(file_path)}")

    def runPipeline(self):
        self.log("🚀 Starting pipeline...")

        try:
            self.log("🕸️ Running web scraper...")
            web_scraper.run_scraper()

            self.log("📄 Running PDF scraper...")
            pdf_scraper.scan_all_pdfs()

            self.log("🧼 Cleaning and formatting...")
            txt_formatter.process_all_files()

            self.log("✅ Done. Cleaned files are in cleaned_knowledge/")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")


def main():
    print("App started")
    app = QApplication(sys.argv)
    window = DropWidget()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
