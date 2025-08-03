import sys
import os
import shutil
from pathlib import Path
import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox,QSizePolicy
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtCore import QTimer, Qt

from ui_form import Ui_MainWindow  

import subprocess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self._setup_output_row_layout()
        self._init_output_row_widgets()
        self._clear_output_row()

        
        # --- Spacing inside the path line ---
        self.ui.horizontalLayout_2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ui.horizontalLayout_2.setSpacing(0)
        self.ui.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

        # --- Outlook ---
        self._init_output_row_widgets()

        # EdBase adjusts width to text as you type
        self.ui.EdBase.textChanged.connect(lambda _ : self._fit_to_text(self.ui.EdBase))

        self.setAcceptDrops(True)  # drag-and-drop support

        self.setWindowTitle("PySide6 UI to PY Converter")
        self.setFixedSize(562, 201)
        self.setWindowIcon(QIcon(ICON_PATH))

        self.file_path = ''
        self.file_name = ''
        self.file_directory = ''

        # Not visible/grey at startup
        self._clear_output_row()
        
        
        self.ui.EdBase.setPlaceholderText("file_name")
        self.ui.EdBase.setToolTip("Output file name — click to edit")
        self.ui.EdBase.setCursor(Qt.IBeamCursor)
        for ro in (self.ui.EdPrefix, self.ui.EdSuffix):
            ro.setCursor(Qt.ArrowCursor)
            
        self.setTabOrder(self.ui.BtnConvert, self.ui.EdBase)

        # Signals
        self.ui.BtnConvert.clicked.connect(self.convert)
        self.ui.BtnSelectFile.clicked.connect(self.select_file)
        self.ui.BtnSelectDestinationFolder.clicked.connect(self.select_folder)
        self.ui.BtnExit.clicked.connect(self.exit)

#region ---------------- helpers ----------------
    def _setup_output_row_layout(self):
        """Reset the layout spacing of the row containing the three QLineEdits."""
        lay = self.ui.horizontalLayout_2
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

    def _init_output_row_widgets(self):
        """Configure Prefix/Base/Suffix QLineEdits as labels."""
        for le in (self.ui.EdPrefix, self.ui.EdBase, self.ui.EdSuffix):
            le.setFrame(False)
            le.setContentsMargins(0, 0, 0, 0)
            le.setTextMargins(0, 0, 0, 0)
            le.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            le.setMinimumWidth(0)

        # Prefix/Suffix: not clickable/editable (display only)
        for ro in (self.ui.EdPrefix, self.ui.EdSuffix):
            ro.setReadOnly(True)
            ro.setFocusPolicy(Qt.NoFocus)
            ro.setContextMenuPolicy(Qt.NoContextMenu)
            ro.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # EdBase: user modifiable
        self.ui.EdBase.setReadOnly(False)

        # Recalculate width as base changes
        self.ui.EdBase.textChanged.connect(lambda _=None: self._fit_to_text(self.ui.EdBase))

    def _fit_to_text(self, le):
        """Adjust the width of the given QLineEdit to the text (no clipping)."""
        fm = QFontMetrics(le.font())
        tm, cm = le.textMargins(), le.contentsMargins()
        extra = int(tm.left() + tm.right() + cm.left() + cm.right())
        txt = le.text() or " "                      # at least 1 character
        w = fm.horizontalAdvance(txt) + extra + 8   # +6..8 px buffer
        le.setFixedWidth(max(0, min(w, 2000)))

    def _clear_output_row(self):
        """Empty the line and make it invisible at application startup."""
        for le in (self.ui.EdPrefix, self.ui.EdBase, self.ui.EdSuffix):
            le.clear()
            le.setFixedWidth(0)
        # Keep Base passive until index arrives
        self.ui.EdBase.setEnabled(False)

    def _refresh_output_row(self, set_default_name=False):
        """Update from a single point when file/folder is selected."""
        # Prefix
        prefix = (self._norm(self.file_directory) + os.sep) if self.file_directory else ""
        self.ui.EdPrefix.setText(prefix)
        self._fit_to_text(self.ui.EdPrefix)

        # Base
        if set_default_name and self.file_name:
            self.ui.EdBase.setText(f"ui_{Path(self.file_name).stem}")
        self.ui.EdBase.setEnabled(bool(self.file_directory))
        self._fit_to_text(self.ui.EdBase)

        # Suffix
        self.ui.EdSuffix.setText(".py" if self.file_directory else "")
        self._fit_to_text(self.ui.EdSuffix)
#endregion

    
#region Catch the drag event and triggering the file selection function
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            
            if urls and urls[0].toLocalFile().endswith('.ui'):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.endswith('.ui'):
                self.file_path = file_path
                self.file_name = os.path.basename(self.file_path)
                self.file_directory = os.path.dirname(self.file_path)
                
                self.ui.LblFileName.setText(self._norm(self.file_name))
                self.ui.LblDestinationName.setText(self._norm(self.file_directory))
                 
                self._refresh_output_row(set_default_name=True)
                self.ui.LblStatus.setText('File dropped and ready for conversion')
    
#endregion
     
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
        
        
        # output file name
        base_text = self.ui.EdBase.text().strip()
        if not base_text:
            base_text = f"ui_{os.path.splitext(self.file_name)[0]}"
        
        if base_text.lower().endswith(".py"):
            base_text = base_text[:-3]
        
        output_file = self._norm(os.path.join(
            self.file_directory, base_text + ".py"
        ))

        self.ui.LblStatus.setText('Starting conversion process...')

        try:
            # Prevent instant console opening and closing in Windows
            startupinfo = None
            creationflags = 0
            if sys.platform.startswith("win"):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |=subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
            
            
            result = subprocess.run(
                [uic_path, self.file_path, "-o", output_file],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo, # windows
                creationflags=creationflags # windows
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
        
        self._refresh_output_row(set_default_name=True)
        self.ui.LblStatus.setText('Selected file')  

  
    def select_folder(self):
        self.file_directory = QFileDialog.getExistingDirectory(self, 'Select folder')
        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        
        self._refresh_output_row(set_default_name=False)
        self.ui.LblStatus.setText('Selected folder')
        
    
    def exit(self):
        self.close()
    
    
    def _norm(self, p: str) -> str:
        return os.path.normpath(p)

# ------------------------------- main -------------------------------

def main():    
    app = QApplication(sys.argv)
    
    load_qss(app=app)
    
    app.setQuitOnLastWindowClosed(True)
    
    window = MainWindow()
    
    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ui2py.pyside6")
        
    
    window.show()
    sys.exit(app.exec())


def rsrc(p: str) -> str:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent) 
    return str(Path(base) / "assets" / p)


def load_qss(app, filename="style.qss"):
    with open(rsrc(f"styles/{filename}"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

# icon selection according to operating system
if sys.platform.startswith("win"):
    ICON_PATH = rsrc("icons/icon.ico")
else:
    ICON_PATH = rsrc("icons/icon.png") # other


if __name__ == '__main__':
    main()
    
    