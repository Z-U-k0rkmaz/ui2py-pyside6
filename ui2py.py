import sys
import os
import shutil
from pathlib import Path
import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
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
        self.setFixedSize(562, 201)
        self.setWindowIcon(QIcon(rsrc('icon.ico')))
        
        self.file_path = ''
        self.file_name = ''
        self.file_directory = ''
        
        
        self.ui.BtnConvert.clicked.connect(self.convert)
        self.ui.BtnSelectFile.clicked.connect(self.select_file)
        self.ui.BtnSelectDestinationFolder.clicked.connect(self.select_folder)
        self.ui.BtnExit.clicked.connect(self.exit)
    
      
    def convert(self):
        # Pre checks
        if not self.file_path or not os.path.isfile(self.file_path):
            QMessageBox.warning(self, "Missing file", "Please select a valid .ui file first.")
            self.ui.LblStatus.setText('Please select a valid .ui file first')
            return

        if not self.file_directory or not os.path.isdir(self.file_directory):
            QMessageBox.warning(self, "Destination folder", "Please select a valid destination folder.")
            self.ui.LblStatus.setText('Please select a valid destination folder')
            return
        
        if not os.access(self.file_directory, os.W_OK):
            self.ui.LblStatus.setText('No permission to write file')
            return

        
        uic_path = shutil.which("pyside6-uic")
        if not uic_path:
            self.ui.LblStatus.setText('pyside6-uic not found on PATH')
            QMessageBox.critical(self, "Tool missing",
                                "pyside6-uic was not found. Make sure PySide6 tools are installed and on PATH.")
            return
        
        
        output_file = self._norm(os.path.join(
            self.file_directory, f"ui_{self.file_name.replace('.ui', '.py')}"
        ))
        self.ui.LblFinalPath.setText(output_file)
        self.ui.LblStatus.setText('Starting conversion process...')

        try:
            result = subprocess.run(
                [uic_path, self.file_path, "-o", output_file],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            QTimer.singleShot(1500, lambda: self.ui.LblStatus.setText('Conversion completed'))
            
        except subprocess.CalledProcessError as e:
            details = (e.stderr or e.stdout or '').strip()
            if not details:
                details = f"Conversion failed (exit code {e.returncode})."
            
            self.ui.LblStatus.setText(details if len(details) < 200 else details[:200] + '...')
        except PermissionError:
            self.ui.LblStatus.setText('No permission to write file')
        except Exception as e:
            self.ui.LblStatus.setText(f'Unexpected error: {str(e)}')


     
    
    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'UI Files (*.ui)'
        )

        if not self.file_path:
            self.ui.LblStatus.setText('No file selected')
            return
        
        if not self.file_path.endswith('.ui'):
            self.ui.LblStatus.setText('Please select a .ui file!')
            self.file_path = ''
            return


        self.file_name = os.path.basename(self.file_path)
        self.file_directory = os.path.dirname(self.file_path)

        self.ui.LblFileName.setText(self._norm(self.file_name))
        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        
        final = os.path.join(self.file_directory, f"ui_{self.file_name.replace('.ui', '.py')}")
        self.ui.LblFinalPath.setText(self._norm(final))
        
        self.ui.LblStatus.setText('Selected file')  

  
    def select_folder(self):
        self.file_directory = QFileDialog.getExistingDirectory(self, 'Select folder')
        
        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        
        self.ui.LblStatus.setText('Selected folder')
        final = os.path.join(self.file_directory, f"ui_{self.file_name.replace('.ui', '.py')}")
        self.ui.LblFinalPath.setText(self._norm(final))
        
    
    def exit(self):
        self.close()
    
    
    def _norm(self, p: str) -> str:
        return os.path.normpath(p)

# ------------------------------- main -------------------------------

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    window = MainWindow()
    
    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ui2py.pyside6")
        
    
    window.show()
    sys.exit(app.exec())


def rsrc(p: str) -> str:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / p)







if __name__ == '__main__':
    main()
    
    