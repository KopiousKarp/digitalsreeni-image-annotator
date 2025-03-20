import os
import json
import shutil
import random
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
                             QLabel, QSpinBox, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt

class SAMTrackerTool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sam2 Tracker")
        self.setGeometry(100, 100, 500, 300)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("SAM2 Video Segmentation Tool")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # Description
        description = QLabel("This tool uses SAM2 to perform video object segmentation.")
        layout.addWidget(description)
        
        # Spacer
        layout.addSpacing(20)
        
        # Video selection button
        self.select_video_button = QPushButton("Select Video File")
        self.select_video_button.clicked.connect(self.select_video)
        layout.addWidget(self.select_video_button)
        
        # File path display
        self.file_path_label = QLabel("No video selected")
        layout.addWidget(self.file_path_label)
        
        # Spacer
        layout.addSpacing(20)
        
        # Process button
        self.process_button = QPushButton("Process Video with SAM2")
        self.process_button.clicked.connect(self.process_video)
        self.process_button.setEnabled(False)  # Disabled until video is selected
        layout.addWidget(self.process_button)
        
        self.setLayout(layout)

    def select_video(self):
        """Open file dialog to select a video file"""
        self.video_file, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video File", 
            "", 
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if self.video_file:
            self.file_path_label.setText(os.path.basename(self.video_file))
            self.process_button.setEnabled(True)
        
    def process_video(self):
        """Process the selected video with SAM2"""
        if not self.video_file:
            QMessageBox.warning(self, "Error", "Please select a video file first.")
            return
            
        # This is where we would add SAM2 processing code
        QMessageBox.information(
            self, 
            "Processing Started", 
            f"Starting SAM2 processing on video: {os.path.basename(self.video_file)}"
        )
        # Call SAM2 processing logic here
        
    def show_centered(self, parent):
        parent_geo = parent.geometry()
        self.move(parent_geo.center() - self.rect().center())
        self.show()