import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

from ui_form import Ui_MainWindow  

import subprocess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("PySide6 UI to PY Converter")
        self.setFixedSize(550, 201)
        self.setWindowIcon(QIcon('icon.ico'))
        
        self.file_path = ''
        self.file_name = ''
        self.file_directory = ''
        
        
        self.ui.BtnConvert.clicked.connect(self.convert)
        self.ui.BtnSelectFile.clicked.connect(self.select_file)
        self.ui.BtnSelectDestinationFolder.clicked.connect(self.select_folder)
        self.ui.BtnExit.clicked.connect(self.exit)
    
      
    def convert(self):
        if not self.file_path or not os.path.isfile(self.file_path):
            self.ui.LblStatus.setText('Please select a valid .ui file first')
            return

        if not self.file_directory or not os.path.isdir(self.file_directory):
            self.ui.LblStatus.setText('Please select a valid destination folder')
            return

        
        uic_command = "pyside6-uic"
        
        output_file = os.path.join(
            self.file_directory, f"ui_{self.file_name.replace('.ui', '.py')}"
        )

        command = f'{uic_command} "{self.file_path}" -o "{output_file}"'
        self.ui.LblStatus.setText('Starting conversion process...')

        try:
            subprocess.run(command, shell=True, check=True)
            QTimer.singleShot(1500, lambda: self.ui.LblStatus.setText('Conversion completed'))
        except subprocess.CalledProcessError as e:
            self.ui.LblStatus.setText('Conversion failed!')
            print("Conversion error:", e)

     
    
    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'UI Files (*.ui)'
        )

        if not self.file_path:
            self.ui.LblStatus.setText('No file selected')
            return

        self.file_name = os.path.basename(self.file_path)
        self.file_directory = os.path.dirname(self.file_path) + os.sep

        self.ui.LblFileName.setText(self.file_name)
        self.ui.LblDestinationName.setText(self.file_directory)
        
        self.ui.LblFinalPath.setText(
            os.path.join(self.file_directory, f"ui_{self.file_name.replace('.ui', '.py')}")
        )
        
        self.ui.LblStatus.setText('Selected file')  

  
    def select_folder(self):
        self.file_directory = QFileDialog.getExistingDirectory(self, 'Select folder') + '/'
        
        self.ui.LblDestinationName.setText(self.file_directory)
        
        self.ui.LblStatus.setText('Selected folder')
        self.ui.LblFinalPath.setText(f"{self.file_directory}ui_{self.file_name.replace('.ui', '.py')}")
        
    
    def exit(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
    