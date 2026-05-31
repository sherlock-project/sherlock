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
            /* Main Background */
            QMainWindow {
                background-color: #1e1e2e;
            }
            /* General Font and Color */
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #cdd6f4;
            }
            /* Title Customization */
            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #89b4fa;
                margin-bottom: 15px;
            }
            /* Text Input Field */
            QLineEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
                background-color: #1e1e2e;
            }
            /* Search Button */
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            /* Table General Settings */
            QTableWidget {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 8px;
                font-size: 14px;
                outline: none;
            }
            /* Table Rows */
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #313244;
            }
            QTableWidget::item:selected {
                background-color: #313244;
                color: #89b4fa;
            }
            /* Table Header */
            QHeaderView::section {
                background-color: #313244;
                color: #a6adc8;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                text-align: left;
            }
            /* Scrollbar Aesthetics */
            QScrollBar:vertical {
                border: none;
                background: #1e1e2e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #45475a;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #585b70;
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

    def add_result_to_table(self, site, status, url):
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
        self.result_table.setItem(insert_row, 0, QTableWidgetItem(site))
        self.result_table.setItem(insert_row, 1, QTableWidgetItem(status_text))
        self.result_table.setItem(insert_row, 2, QTableWidgetItem(url))
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
    result_signal = pyqtSignal(str, str, str)
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