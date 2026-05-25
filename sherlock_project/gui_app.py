import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt

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
        self.search_button.clicked.connect(self.start_search_mock)

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




    def start_search_mock(self):
        """
        This function is for testing purposes only.
        Later, we will connect it to the original sherlock.py.
        """
        username = self.username_input.text()
        
        if not username:
            return

        
        # Clean the table and add 2 rows of fake data for testing.
        self.result_table.setRowCount(0)
        
        mock_results = [
            {"site": "GitHub", "status": "Found", "url": f"https://github.com/{username}"},
            {"site": "Instagram", "status": "Not Found", "url": "-"}
        ]

        for row_idx, result in enumerate(mock_results):
            self.result_table.insertRow(row_idx)
            
            # Durum kısmına daha estetik görünmesi için emoji ekledik
            status_text = "✅ Found" if result["status"] == "Found" else "❌ Not Found"
            
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(result["site"]))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(status_text))
            self.result_table.setItem(row_idx, 2, QTableWidgetItem(result["url"]))

def run_gui():
    app = QApplication(sys.argv) 
    window = SherlockGUI()
    window.show()
    sys.exit(app.exec_())

#  If this file is executed directly, the GUI should open.
if __name__ == "__main__":
    run_gui()