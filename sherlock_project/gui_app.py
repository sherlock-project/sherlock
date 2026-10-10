import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sherlock_project.notify import QueryNotifyGUI
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                            QHeaderView, QAbstractItemView, QProgressBar, QTextEdit, QListWidget,
                            QListWidgetItem, QDialog, QScrollArea, QCheckBox, QDialogButtonBox)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class SherlockGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.apply_styles()
        self.count_total = 0
        self.count_found = 0
        self.count_not_found = 0

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

        # Statistics Cards Layout
        self.stats_layout = QHBoxLayout()

        self.card_total = QLabel("🔍 Scanned\n0")
        self.card_found = QLabel("✅ Found\n0")
        self.card_not_found = QLabel("❌ Not Found\n0")

        # We are applying a consistent style to all three cards and adding them to the horizontal layout.
        for card in [self.card_total, self.card_found, self.card_not_found]:
            card.setAlignment(Qt.AlignCenter)
            card.setObjectName("statCard")
            self.stats_layout.addWidget(card)

        main_layout.addLayout(self.stats_layout)

        # Search bar and button for horizontal layout
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter the username to search (e.g., elif123)")

        self.search_button = QPushButton("Search")
        self.search_button.setCursor(Qt.PointingHandCursor)
        # We are attaching the function that will run when the button is clicked (Signal-Slot logic).
        self.search_button.clicked.connect(self.start_search)

        # We are creating a new button for the site filter and connecting it to the corresponding function that will open the filter dialog.
        self.filter_button = QPushButton("⚙️ Filter Sites")
        self.filter_button.setCursor(Qt.PointingHandCursor)
        self.filter_button.clicked.connect(self.open_site_filter)
        self.filter_button.setStyleSheet("background-color: #64748B; color: white;") 

        search_layout.addWidget(self.username_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.filter_button)
        main_layout.addLayout(search_layout)

        # Bottom section: Results table
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["Platform", "Status", "URL"])

        # We are creating a visually appealing empty state label that will be shown when there are no results to display. 
        # This provides a better user experience and guides the user on what to do next.
        self.empty_state_label = QLabel(
            "🔎\n\nReady to investigate.\nEnter a target username above to start the OSINT scan."
        )
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("""
            color: #94A3B8; 
            font-size: 16px;
            font-weight: bold;
            background-color: #FFFFFF;
            border: 2px dashed #E2E8F0; 
            border-radius: 8px;
            padding: 80px; 
        """)
        main_layout.addWidget(self.empty_state_label)

        # Initially, the results table is hidden and only the empty state label is visible.
        #  Once results start coming in, we will hide the empty state and show the table.
        self.result_table.setVisible(False)

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
            QLabel#TitleLabel {
                font-size: 26px; 
                font-weight: bold;
                color: #1E293B;
                margin-bottom: 5px;
            }
            #infoLabel {
                background-color: #EFF6FF;
                color: #1D4ED8;
                border: 1px solid #BFDBFE;
                border-radius: 6px;
                padding: 6px 15px; 
                font-size: 12px; 
                margin-bottom: 10px;
            }
            QLabel#statCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                border: 1px solid #C7D2FE;
                margin-bottom: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                color: #334155;
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
    
    def open_site_filter(self):
        # We are loading the site information only when the filter dialog is opened for the first time.
        # This way, we avoid unnecessary loading during the initial startup of the application and only load the data when it's actually needed.
        if not hasattr(self, 'sites_info'):
            self.sites_info = SitesInformation(data_file_path="sherlock_project/resources/data.json")
            self.all_sites = self.sites_info.get_sites_for_ui()
            self.selected_sites = [site['name'] for site in self.all_sites] 
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Target Platforms")
        dialog.resize(400, 500)
        dialog.setStyleSheet(self.styleSheet()) 
        
        layout = QVBoxLayout(dialog)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.checkboxes = {}
        for site in self.all_sites:
            # We are adding a clear NSFW tag next to the site name for platforms that are marked as NSFW in the data. 
            # This allows users to easily identify and exclude adult content platforms from their search if they choose to do so.
            nsfw_tag = " 🔞 (NSFW)" if site['is_nsfw'] else ""
            cb = QCheckBox(f"{site['name']}{nsfw_tag}")
            
            if site['name'] in self.selected_sites:
                cb.setChecked(True)
                
            self.checkboxes[site['name']] = cb
            scroll_layout.addWidget(cb)
            
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            self.selected_sites = [name for name, cb in self.checkboxes.items() if cb.isChecked()]



    def start_search(self):
        username = self.username_input.text().strip()
        # When the search starts, we hide the empty state label and show the results table.
        #  This allows us to display incoming results in real-time as they are found.
        self.empty_state_label.setVisible(False)
        self.result_table.setVisible(True)

        if not username:
            return

        self.result_table.setRowCount(0)
        self.search_button.setEnabled(False)
        self.search_button.setText("Searching...")

        self.worker = SherlockWorker(username, getattr(self, 'selected_sites', None))
        self.worker.result_signal.connect(self.add_result_to_table)
        self.worker.finished_signal.connect(self.search_finished)
        self.progress_bar.show() 
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()

        # We reset the statistics cards and counters at the start of a new search.
        self.count_total = 0
        self.count_found = 0
        self.count_not_found = 0
        self.card_total.setText("🔍 Scanned\n0")
        self.card_found.setText("✅ Found\n0")
        self.card_not_found.setText("❌ Not Found\n0")

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
        # We are creating a hidden text item that will remain in the background to avoid disrupting the sorting algorithm.
        status_hidden_item = QTableWidgetItem(status_text)
        status_hidden_item.setForeground(QColor(0, 0, 0, 0))
        url_item = QTableWidgetItem(url)

        # 2. We apply color coding to the text based on the status (green for "Found", red for "Not Found").
        site_item.setForeground(QColor(color_code))
        status_item.setForeground(QColor(color_code))
        url_item.setForeground(QColor(color_code))

        # We are creating QLabel for the new badge design.
        badge_label = QLabel(status_text)
        badge_label.setAlignment(Qt.AlignCenter)

        if status == "Found":
            # Light pastel green background, bold dark green text.
            badge_label.setStyleSheet("""
                background-color: #D1FAE5; 
                color: #065F46; 
                border-radius: 10px; 
                padding: 4px 10px; 
                font-weight: bold;
            """)
        else:
            # Light pastel red background, bold dark red text.
            badge_label.setStyleSheet("""
                background-color: #FEE2E2; 
                color: #991B1B; 
                border-radius: 10px; 
                padding: 4px 10px; 
                font-weight: bold;
            """)

        # We are preparing a carrier QWidget so that the badge fits perfectly inside the cell and doesn't look unsightly.
        badge_container = QWidget()
        badge_container.setStyleSheet("background-color: transparent;")
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(10, 2, 10, 2)
        badge_layout.addWidget(badge_label)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 3. We insert the items into the table at the determined row index.
        self.result_table.setItem(insert_row, 0, site_item)
        self.result_table.setItem(insert_row, 1, status_item)
        self.result_table.setItem(insert_row, 1, status_hidden_item)
        # We place our visual badge on the corresponding cell.
        self.result_table.setCellWidget(insert_row, 1, badge_container)
        self.result_table.setItem(insert_row, 2, url_item)
        

        self.result_table.scrollToBottom()

        # We update the statistics cards based on the new result.
        self.count_total += 1
        if status == "Found":
            self.count_found += 1
        else:
            self.count_not_found += 1

        self.card_total.setText(f"🔍 Scanned\n{self.count_total}")
        self.card_found.setText(f"✅ Found\n{self.count_found}")
        self.card_not_found.setText(f"❌ Not Found\n{self.count_not_found}")

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

    def __init__(self, username, selected_sites=None):
        super().__init__()
        self.username = username
        self.selected_sites = selected_sites if selected_sites is not None else []
        self.checked_count = 0

    def run(self):
        gui_notifier = QueryNotifyGUI(self.result_signal)
        
        try:
            # We are loading the site information from the JSON file and applying the user's site filter preferences before starting the search.
            sites_info = SitesInformation(data_file_path="sherlock_project/resources/data.json")
            
            if self.selected_sites:
                sites_info.filter_sites_by_names(self.selected_sites)
                
            site_data = {}
            for site in sites_info:
                site_data[site.name] = site.information
                
        except Exception as e:
            print("Error loading sites:", e)
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