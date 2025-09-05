import sys
import os
import shutil
from pathlib import Path
import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSizePolicy, QMenu
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QCoreApplication

from ui_form import Ui_MainWindow

import subprocess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.window_width_anim = QPropertyAnimation(self, b"size")
        self.window_width_anim.setDuration(300)
        self.window_width_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.ui.ListSelectedFiles.setVisible(False)

        self._setup_output_row_layout()
        self._init_output_row_widgets()  # --- Outlook ---
        self._clear_output_row() # Not visible/grey at startup

        # --- Spacing inside the path line ---
        self.ui.horizontalLayout_2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ui.horizontalLayout_2.setSpacing(0)
        self.ui.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.ui.EdBase.textChanged.connect(lambda _: self._fit_to_text(self.ui.EdBase))

        self.setAcceptDrops(True)
        self.setWindowTitle("PySide6 UI to PY Converter")
        self.setMinimumSize(562, 201)
        self.setMaximumSize(770, 201)
        self.setWindowIcon(QIcon(ICON_PATH))

        self.file_paths: list[str] = []
        self.file_name = ''
        self.file_directory = ''

        self.ui.EdBase.setPlaceholderText("file_name")
        self.ui.EdBase.setToolTip("Output file name — click to edit")
        self.ui.EdBase.setCursor(Qt.IBeamCursor)
        for ro in (self.ui.EdPrefix, self.ui.EdSuffix):
            ro.setCursor(Qt.ArrowCursor)

        self.setTabOrder(self.ui.BtnConvert, self.ui.EdBase)

        # Button signals
        self.ui.BtnConvert.clicked.connect(self.convert)
        self.ui.BtnSelectFile.clicked.connect(self.select_file)
        self.ui.BtnSelectDestinationFolder.clicked.connect(self.select_folder)
        self.ui.BtnExit.clicked.connect(self.exit)
        
        
        # Liste etkileşimi için sağ tık menüsü ve klavye kısayolu
        self.ui.ListSelectedFiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ListSelectedFiles.customContextMenuRequested.connect(self.show_list_context_menu)

#region ---------------- helpers ----------------
    def _animate_list(self, show=False, hide=False):
        self.window_width_anim.stop()
        try:
            self.window_width_anim.finished.disconnect()  
        except TypeError:
            pass  

        if show:
            self.ui.ListSelectedFiles.setVisible(True)
            self.ui.ListSelectedFiles.setFixedHeight(151)
            self.window_width_anim.setStartValue(QSize(562, 201))
            self.window_width_anim.setEndValue(QSize(770, 201))
            self.window_width_anim.start()

        elif hide:
            self.window_width_anim.setStartValue(QSize(self.width(), 201))
            self.window_width_anim.setEndValue(QSize(562, 201))
            self.window_width_anim.start()
            self.window_width_anim.finished.connect(lambda: self.ui.ListSelectedFiles.setVisible(False))

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
        for ro in (self.ui.EdPrefix, self.ui.EdSuffix): # Prefix/Suffix: not clickable/editable (display only)
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
            if any(url.toLocalFile().endswith('.ui') for url in event.mimeData().urls()):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        urls = event.mimeData().urls()
        ui_files = [url.toLocalFile() for url in urls if url.toLocalFile().endswith('.ui')]

        if not ui_files:
            self.ui.LblStatus.setText('No valid .ui files dropped')
            event.ignore()
            return

        self.file_paths = ui_files
        self.file_directory = os.path.dirname(ui_files[0])

        if len(ui_files) == 1:
            self.file_name = os.path.basename(ui_files[0])
            self.file_path = ui_files[0]
            self.ui.LblFileName.setText(self._norm(self.file_name))
            self._refresh_output_row(set_default_name=True)
            self._animate_list(hide=True)
        else:
            self.ui.LblFileName.setText(f"{len(ui_files)} files dropped")
            self.ui.ListSelectedFiles.clear()
            for f in ui_files:
                self.ui.ListSelectedFiles.addItem(os.path.basename(f))
            self._clear_output_row()
            self._animate_list(show=True)

        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        self.ui.LblStatus.setText('Files dropped and ready for conversion')
        event.acceptProposedAction()

#endregion

    def convert(self):
        # Pre checks
        if not self.file_paths or not all(os.path.isfile(f) for f in self.file_paths):
            QMessageBox.warning(self, "Missing file", "Please select valid .ui files first.")
            self.ui.LblStatus.setText('Please select valid .ui files')
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
            QMessageBox.critical(self, "Tool missing", "pyside6-uic was not found. Make sure PySide6 tools are installed and on PATH.")
            return

        # Prevent instant console opening and closing in Windows
        startupinfo = None
        creationflags = 0
        if sys.platform.startswith("win"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        multiple = len(self.file_paths) > 1
        errors = []

        for file in self.file_paths:
            fname = os.path.basename(file)
            stem = Path(fname).stem
            out_base = self.ui.EdBase.text().strip() if not multiple else f"ui_{stem}"
            if out_base.lower().endswith('.py'):
                out_base = out_base[:-3]

            output_file = self._norm(os.path.join(self.file_directory, out_base + ".py"))

            try:
                subprocess.run(
                    [uic_path, file, "-o", output_file],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=startupinfo,
                    creationflags=creationflags
                )
            except subprocess.CalledProcessError as e:
                msg = (e.stderr or e.stdout or '').strip()
                errors.append(f"{fname}: {msg}")
            except Exception as e:
                errors.append(f"{fname}: {str(e)}")

        if errors:
            self.ui.LblStatus.setText(f"{len(errors)} error(s) occurred. Check console.")
            for err in errors:
                print(err)
        else:
            self.ui.LblStatus.setText('Conversion completed')

    def select_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select .ui files', '', 'UI Files (*.ui)')
        
        if not files:
            self.ui.LblStatus.setText('No file selected')
            return

        self.file_paths = [f for f in files if f.endswith('.ui')]
        if not self.file_paths:
            self.ui.LblStatus.setText('No valid .ui files selected')
            return

        self.ui.ListSelectedFiles.clear()
        if len(self.file_paths) == 1:
            self.file_path = self.file_paths[0]
            self.file_name = os.path.basename(self.file_path)
            self.ui.LblFileName.setText(self._norm(self.file_name))
            self._refresh_output_row(set_default_name=True)
            self._animate_list(hide=True)
        else:
            self.ui.LblFileName.setText(f"{len(self.file_paths)} files selected")
            for f in self.file_paths:
                self.ui.ListSelectedFiles.addItem(os.path.basename(f))
            self._clear_output_row()
            self._animate_list(show=True)

        self.file_directory = os.path.dirname(self.file_paths[0])
        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        self.ui.LblStatus.setText('Files ready for conversion')

    def select_folder(self):
        self.file_directory = QFileDialog.getExistingDirectory(self, 'Select folder')
        if not self.file_directory:
            self.ui.LblStatus.setText('No folder selected')
            return

        self.ui.LblDestinationName.setText(self._norm(self.file_directory))
        self._refresh_output_row(set_default_name=False)
        self.ui.LblStatus.setText('Selected folder')


    # ------------------ delete file from list ------------------
    def remove_selected_files(self):
        selected_items = self.ui.ListSelectedFiles.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = self.ui.ListSelectedFiles.row(item)
            file_name = item.text()
            file_path = [f for f in self.file_paths if os.path.basename(f) == file_name]
            if file_path:
                self.file_paths.remove(file_path[0])
            
            self.ui.ListSelectedFiles.takeItem(row)
            
        new_count = len(self.file_paths)
        if new_count == 1:
            self.ui.LblFileName.setText(self._norm(os.path.basename(self.file_paths[0])))
            self.file_name = os.path.basename(self.file_paths[0])
            self._refresh_output_row(set_default_name=True)
            self._animate_list(hide=True)
            self.ui.LblStatus.setText('One file left, ready to convert')
        elif new_count == 0:
            self.ui.LblFileName.setText(QCoreApplication.translate("MainWindow", u"File not selected yet", None))
            self.ui.LblStatus.setText(QCoreApplication.translate("MainWindow", u"Please select valid .ui files", None))
            self._clear_output_row()
            self._animate_list(hide=True)
        else:
            self.ui.LblFileName.setText(f"{new_count} files dropped")
            self.ui.LblStatus.setText(f"{len(selected_items)} file was deleted from the list.")

    def show_list_context_menu(self, pos):
        menu = QMenu()
        remove_action = menu.addAction("Remove Selected File")
        
        selected_item = self.ui.ListSelectedFiles.itemAt(pos)
        if selected_item:
            action = menu.exec(self.ui.ListSelectedFiles.viewport().mapToGlobal(pos))
            if action == remove_action:
                self.remove_selected_files()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            if self.ui.ListSelectedFiles.isVisible() and self.ui.ListSelectedFiles.hasFocus():
                self.remove_selected_files()
        else:
            super().keyPressEvent(event)



    # ------------------ exit ------------------
    def exit(self):
        self.close()

    def _norm(self, p: str) -> str:
        return os.path.normpath(p)

# ------------------------------- main -------------------------------
def main():
    app = QApplication(sys.argv)
    load_qss(app, "system")
    app.styleHints().colorSchemeChanged.connect(lambda _: load_qss(app, "system")) # for system change
    app.setQuitOnLastWindowClosed(True)
    app.setWindowIcon(QIcon(ICON_PATH))

    window = MainWindow()
    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ui2py.pyside6")

    window.show()
    sys.exit(app.exec())

def rsrc(p: str) -> str:
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / "assets" / p)

def load_qss(app: QApplication, mode: str = "system"):
    if mode == "system":
        scheme = app.styleHints().colorScheme()
        is_dark = (scheme == Qt.ColorScheme.Dark)
    else:
        is_dark = (mode.lower() == "dark")

    qss_path = Path(rsrc(f"styles/{'dark_style.qss' if is_dark else 'light_style.qss'}"))
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


# OS-specific icon
if sys.platform.startswith("win"):
    ICON_PATH = rsrc("icons/icon.ico")
else:
    ICON_PATH = rsrc("icons/icon.png")

if __name__ == '__main__':
    main()