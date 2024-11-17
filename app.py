from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QWidget, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd
import json
import sys

# Global DataFrame to hold the processed data
global_data = pd.DataFrame()

# Function to process JSON file
def process_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        rows = []
        current_employee = {}
        for entry in data:
            if entry.get("sts") == "IN":
                current_employee = entry
            elif entry.get("sts") == "OUT":
                current_employee = {}
            else:
                row = {
                    "Station No": str(entry.get("stn", "")),
                    "User ID": str(entry.get("uid", "")),
                    "User Name": str(current_employee.get("name", "")),
                    "Shift No": str(current_employee.get("sftno", "")),
                    "Date": str(entry.get("dt", "")),
                    "Time": str(entry.get("t", "")),
                    "Programme No": str(entry.get("pgmno", "")),
                    "Cycle": str(entry.get("cycle", "")),
                    "Angle": str(entry.get("angle", "")),
                    "Weld Current": str(entry.get("wldcrt", "")),
                    "Spot Count": str(entry.get("sptct", "")),
                    "Force": str(entry.get("force", "")),
                    "Weld Count": str(entry.get("wldct", "")),
                    "Job": str(entry.get("job", ""))
                }
                rows.append(row)
        return pd.DataFrame(rows)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to process file: {e}")
        return None

# Main Application Window
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskTrak - JSON Viewer")
        self.setGeometry(100, 100, 1200, 700)

        # Main Layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Fonts and Colors
        self.title_font = QFont("Arial", 16, QFont.Bold)
        self.label_font = QFont("Arial", 12)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #003366;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00509E;
            }
            QLabel {
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
                gridline-color: #ddd;
                font-size: 12px;
            }
        """)

        # Upload Button
        self.upload_button = QPushButton("Upload JSON File")
        self.upload_button.setFont(self.label_font)
        self.upload_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.upload_button)

        # Filter Layout
        self.filter_layout = QHBoxLayout()
        self.filters = {}
        for column in ["Station No", "User ID", "User Name", "Shift No", "Date", "Time", "Programme No"]:
            label = QLabel(f"{column}:")
            label.setFont(self.label_font)
            self.filter_layout.addWidget(label)
            combo_box = QComboBox()
            combo_box.addItem("All")
            combo_box.setFont(self.label_font)
            self.filters[column] = combo_box
            self.filter_layout.addWidget(combo_box)

        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.setFont(self.label_font)
        self.apply_button.clicked.connect(self.apply_filters)
        self.filter_layout.addWidget(self.apply_button)

        self.layout.addLayout(self.filter_layout)

        # Table to display data
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

    def browse_file(self):
        global global_data
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if not file_path:
            return

        df = process_file(file_path)
        if df is not None:
            global_data = df
            self.populate_filters(df)
            self.display_table(df)

    def populate_filters(self, dataframe):
        for column, combo_box in self.filters.items():
            combo_box.clear()
            combo_box.addItem("All")
            unique_values = sorted(dataframe[column].dropna().unique())
            combo_box.addItems([str(value) for value in unique_values])

    def apply_filters(self):
        global global_data
        filtered_data = global_data.copy()
        for column, combo_box in self.filters.items():
            selected_value = combo_box.currentText()
            if selected_value != "All":
                filtered_data = filtered_data[filtered_data[column] == selected_value]

        if filtered_data.empty:
            QMessageBox.information(self, "No Data", "No rows match the selected filters.")
        else:
            self.display_table(filtered_data)

    def display_table(self, dataframe):
        self.table.clear()
        self.table.setRowCount(dataframe.shape[0])
        self.table.setColumnCount(dataframe.shape[1])
        self.table.setHorizontalHeaderLabels(dataframe.columns)

        for i, row in dataframe.iterrows():
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)

# Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
