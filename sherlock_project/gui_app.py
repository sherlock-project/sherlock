import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sherlock_project.notify import QueryNotifyGUI
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView, QProgressBar)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class SherlockGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.apply_styles()

    def initUI(self):

        # Main window settings
        self.setWindowTitle("Sherlock OSINT Dashboard")
        self.resize(800, 600)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Top section: Heading
        title_label = QLabel("🕵️‍♂️Sherlock Username Search")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("TitleLabel")
        main_layout.addWidget(title_label)

        # Usage Guide / Information Box and Color Legend
        self.info_label = QLabel(
            "ℹ️ Enter the username you want to search for and click the 'Search' button.\n"
            "Results are added to the table alphabetically as they are found. Color Codes: 🟢 Found (Green) | 🔴 Not Found (Red) | 🟡 Error (Yellow)"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setObjectName("infoLabel")
        main_layout.addWidget(self.info_label)

        # Search bar and button for horizontal layout
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter the username to search (e.g., elif123)")
        
        self.search_button = QPushButton("Search")
        self.search_button.setCursor(Qt.PointingHandCursor)
        # We are attaching the function that will run when the button is clicked (Signal-Slot logic).
        self.search_button.clicked.connect(self.start_search)

        search_layout.addWidget(self.username_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        # Bottom section: Results table
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["Platform", "Status", "URL"])
        
        # Resize table columns proportionally to the window
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setShowGrid(False)
        self.result_table.verticalHeader().setVisible(False)


        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        main_layout.addWidget(self.result_table)

        # Progress Bar Settings
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide() 
        main_layout.addWidget(self.progress_bar)

        # Assign main layout to central widget
        central_widget.setLayout(main_layout)


    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                color: #1F2937;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #infoLabel {
                color: #4338CA; 
                font-size: 13px;
                background-color: #E0E7FF; 
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #C7D2FE;
                margin-bottom: 5px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #000000;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F9FAFB;
                gridline-color: #E5E7EB;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #E5E7EB;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #374151;
            }
            QProgressBar {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                text-align: center;
                background-color: #E5E7EB;
                color: #1F2937;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 12px;
                border-radius: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1; 
                min-height: 30px;
                border-radius: 6px; 
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)



    def start_search(self):
        username = self.username_input.text().strip()
        if not username:
            return

        self.result_table.setRowCount(0)
        self.search_button.setEnabled(False)
        self.search_button.setText("Searching...")

        self.worker = SherlockWorker(username)
        self.worker.result_signal.connect(self.add_result_to_table)
        self.worker.finished_signal.connect(self.search_finished)
        self.progress_bar.show() 
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()

    def add_result_to_table(self, site, status, url, color_code):
        status_text = "✅ Found" if status == "Found" else "❌ Not Found"
        
        insert_row = self.result_table.rowCount() 
        
        for i in range(self.result_table.rowCount()):
            current_site = self.result_table.item(i, 0).text()
            current_status = self.result_table.item(i, 1).text()
            
            if status_text == "✅ Found":
                # Rule 1: The newly entered "Found" data should be placed above the first "Not Found" row in the table.
                if current_status == "❌ Not Found":
                    insert_row = i
                    break
                # Rule 2: Claimed sites should be sorted alphabetically (A-Z) within the found section
                elif current_site.lower() > site.lower():
                    insert_row = i
                    break
            else:
                # Rule 3: Newly entered "Not Found" entries should skip over existing "Found" rows

                if current_status == "✅ Found":
                    continue
                # Rule 4: "Not Found" sites should be sorted alphabetically (A-Z) within their own section
                if current_site.lower() > site.lower():
                    insert_row = i
                    break
        
        self.result_table.insertRow(insert_row)

        # 1. We create cell objects.
        site_item = QTableWidgetItem(site)
        status_item = QTableWidgetItem(status_text)
        url_item = QTableWidgetItem(url)
        
        # 2. We apply color coding to the text based on the status (green for "Found", red for "Not Found").
        site_item.setForeground(QColor(color_code))
        status_item.setForeground(QColor(color_code))
        url_item.setForeground(QColor(color_code))
        
        # 3. We insert the items into the table at the determined row index.
        self.result_table.setItem(insert_row, 0, site_item)
        self.result_table.setItem(insert_row, 1, status_item)
        self.result_table.setItem(insert_row, 2, url_item)
        
        self.result_table.scrollToBottom()

    def search_finished(self):
        self.search_button.setEnabled(True)
        self.search_button.setText("Search")
        self.progress_bar.setValue(self.progress_bar.maximum())
        print("[*] Search completed.")
    
    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

class SherlockWorker(QThread):
    result_signal = pyqtSignal(str, str, str, str)
    finished_signal = pyqtSignal()
    progress_signal = pyqtSignal(int, int) 

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.checked_count = 0

    def run(self):
        gui_notifier = QueryNotifyGUI(self.result_signal)
        
        try:
            with open("sherlock_project/resources/data.json", "r", encoding="utf-8") as f:
                site_data = json.load(f)
            if "$schema" in site_data:
                del site_data["$schema"]
        except Exception as e:
            self.finished_signal.emit()
            return
            
        total_sites = len(site_data)

        # The Callback function that Sherlock.py will call at the end of each site visit.
        def progress_callback():
            self.checked_count += 1
            self.progress_signal.emit(self.checked_count, total_sites)
        
        # We are sending the callback as a parameter.
        sherlock(self.username, site_data, gui_notifier, timeout=60, progress_callback=progress_callback)
        self.finished_signal.emit()


def run_gui():
    app = QApplication(sys.argv) 
    window = SherlockGUI()
    window.show()
    sys.exit(app.exec_())

#  If this file is executed directly, the GUI should open.
if __name__ == "__main__":
    run_gui()