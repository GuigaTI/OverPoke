THEMES = {
    "FireRed": """
        QWidget { background-color: #F8D8B8; color: black; }
        QPushButton {
            background-color: #C03028;
            border: 3px solid black;
            padding: 6px;
        }
        QPushButton:hover { background-color: #E05040; }
        QListWidget {
            background-color: #FFF0E0;
            border: 3px solid black;
        }
    """,

    "Emerald": """
        QWidget { background-color: #C8F0C8; color: black; }
        QPushButton {
            background-color: #2E8B57;
            border: 3px solid black;
            padding: 6px;
        }
        QPushButton:hover { background-color: #3CB371; }
        QListWidget {
            background-color: #E0FFE0;
            border: 3px solid black;
        }
    """,

    "Yellow": """
        QWidget { background-color: #FFF8B0; color: black; }
        QPushButton {
            background-color: #FFD700;
            border: 3px solid black;
            padding: 6px;
        }
        QPushButton:hover { background-color: #FFEA00; }
        QListWidget {
            background-color: #FFFFE0;
            border: 3px solid black;
        }
    """,

    "Minimal": """
        QWidget { background-color: #111; color: white; }
        QPushButton {
            background-color: #222;
            border: 2px solid #333;
            padding: 6px;
        }
        QPushButton:hover { background-color: #333; }
        QListWidget {
            background-color: #1a1a1a;
            border: 2px solid #333;
        }
    """
}


import sys
import os
import json
import keyboard

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QListWidget, QVBoxLayout, QColorDialog,
    QFileDialog, QInputDialog, QSystemTrayIcon,
    QMenu
)
from PyQt6.QtGui import QMovie, QColor, QIcon, QFontDatabase, QFont, QPainter, QBrush, QPolygon, QAction
from PyQt6.QtCore import Qt, QPoint

DATA_FILE = "data.json"

# =========================
# DATA
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"overlays": [], "lock_hotkey": "ctrl+shift+l"}

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"overlays": [], "lock_hotkey": "ctrl+shift+l"}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# RESIZE HANDLE PIXEL STYLE
# =========================
class PixelResizeHandle(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.resizing = False
        self.drag_position = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.PenStyle.NoPen)
        size = self.width()
        for i in range(0, size, 4):
            points = [
                QPoint(size - i - 1, size - 1),
                QPoint(size - 1, size - i - 1),
                QPoint(size - i - 5, size - 1)
            ]
            painter.drawPolygon(QPolygon(points))
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizing = True
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.resizing:
            return
        parent = self.parentWidget()
        global_pos = event.globalPosition().toPoint()
        diff = global_pos - self.drag_position
        new_w = max(100, parent.width() + diff.x())
        new_h = max(100, parent.height() + diff.y())
        parent.resize(new_w, new_h)
        parent.update_resize_handle_position()
        parent.counter.move(parent.width() - parent.counter.width() - 5, 5)
        if hasattr(parent, "movie"):
            parent.movie.setScaledSize(parent.label.size())
        self.drag_position = global_pos

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.drag_position = None
        self.parentWidget().save_geometry()


# =========================
# OVERLAY
# =========================
class Overlay(QWidget):
    def __init__(self, data, manager=None):
        super().__init__(None)

        self.manager = manager
        self.data = data
        self.drag_position = None
        self.hotkey_ref = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(
            data.get("x", 100),
            data.get("y", 100),
            data.get("width", 200),
            data.get("height", 200)
        )

        # GIF
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.load_gif()

        # COUNTER
        self.counter = QLabel(str(self.data.get("value", 0)), self)
        self.counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.counter.setFixedWidth(100)
        self.counter.setFixedHeight(30)

        pixel_font = QFont("pixel", 18)
        pixel_font.setBold(True)
        self.counter.setFont(pixel_font)

        self.counter.setStyleSheet(f"""
            color: rgb({self.data['color'][0]}, {self.data['color'][1]}, {self.data['color'][2]});
            background-color: rgba(0,0,0,120);
            border: 2px solid black;
            border-radius: 3px;
        """)

        self.counter.move(self.width() - self.counter.width() - 5, 5)
        self.counter.show()

        # HANDLE DE REDIMENSIONAMENTO PIXEL
        self.resize_handle = PixelResizeHandle(self)
        self.update_resize_handle_position()
        self.resize_handle.show()


    def update_resize_handle_position(self):
        self.resize_handle.move(self.width() - self.resize_handle.width(),
                                self.height() - self.resize_handle.height())

    # GIF
    def load_gif(self):
        gif_path = self.data.get("gif")
        if gif_path:
            self.movie = QMovie(gif_path)
            self.label.setMovie(self.movie)
            self.movie.start()

    # HOTKEY
    def register_hotkey(self):
        try:
            self.hotkey_ref = keyboard.add_hotkey(
                self.data["hotkey"],
                self.increment
            )
        except:
            self.hotkey_ref = None

    def unregister_hotkey(self):
        try:
            if self.hotkey_ref:
                keyboard.remove_hotkey(self.hotkey_ref)
        except:
            pass

    def increment(self):
        self.data["value"] += 1
        self.counter.setText(str(self.data["value"]))
        self.counter.move(self.width() - self.counter.width() - 5, 5)
        save_data(self.manager.data)

    def reset_counter(self):
        self.data["value"] = 0
        self.counter.setText("0")
        self.counter.move(self.width() - self.counter.width() - 5, 5)
        save_data(self.manager.data)

    # ESTILO COUNTER
    def update_counter_style(self):
        r, g, b = self.data["color"]
        self.counter.setStyleSheet(f"""
            color: rgb({r},{g},{b});
            font-size: 20px;
            font-weight: bold;
            background: transparent;
        """)

    # SALVA POSIÇÃO E TAMANHO
    def save_geometry(self):
        self.data["x"] = self.x()
        self.data["y"] = self.y()
        self.data["width"] = self.width()
        self.data["height"] = self.height()
        save_data(self.manager.data)

    # DRAG
    def mousePressEvent(self, event):
        if self.data.get("locked"):
            return
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            local_pos = event.position().toPoint()
            if self.resize_handle.geometry().contains(local_pos):
                return  # handle cuida do resize
            else:
                self.drag_position = global_pos - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.data.get("locked"):
            return
        if self.drag_position:
            global_pos = event.globalPosition().toPoint()
            self.move(global_pos - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        self.save_geometry()

    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, "movie"):
            self.movie.setScaledSize(self.label.size())
        self.counter.move(self.width() - self.counter.width() - 5, 5)
        self.update_resize_handle_position()
        super().resizeEvent(event)


# =========================
# MANAGER
# =========================

class Manager(QWidget):
    def __init__(self):
        super().__init__()
        self.data = load_data()
        self.register_lock_hotkey()
        self.overlays = []

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()

        font_path = os.path.join(base_path, "pixel.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                pixel_font = QFont(families[0])
                pixel_font.setPointSize(10)
                self.setFont(pixel_font)

        self.setWindowTitle("OverPoke")
        self.resize(350, 420)

        self.current_theme = self.data.get("theme", "Minimal")
        self.setStyleSheet(THEMES[self.current_theme])

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_selected)
        layout.addWidget(self.list_widget)

        btn_start = QPushButton("Iniciar Overlay Selecionado")
        btn_start.clicked.connect(self.start_selected)
        layout.addWidget(btn_start)

        btn_create = QPushButton("Novo Overlay")
        btn_create.clicked.connect(self.create_overlay)
        layout.addWidget(btn_create)

        btn_reset = QPushButton("Resetar Selecionado")
        btn_reset.clicked.connect(self.reset_selected)
        layout.addWidget(btn_reset)

        btn_lock = QPushButton("Lock / Unlock")
        btn_lock.clicked.connect(self.toggle_lock)
        layout.addWidget(btn_lock)

        btn_lock_hotkey = QPushButton("Editar Hotkey Lock")
        btn_lock_hotkey.clicked.connect(self.edit_lock_hotkey)
        layout.addWidget(btn_lock_hotkey)

        btn_theme = QPushButton("Alterar Tema HUD")
        btn_theme.clicked.connect(self.change_theme)
        layout.addWidget(btn_theme)

        btn_close = QPushButton("Fechar Overlay Selecionado")
        btn_close.clicked.connect(self.close_selected)
        layout.addWidget(btn_close)

        self.setLayout(layout)
        self.init_tray()
        self.load_overlays()
        self.show()

    # ------------------------
    # Funções do Manager
    # ------------------------
    def register_lock_hotkey(self):
        try:
            self.lock_hotkey_ref = keyboard.add_hotkey(
                self.data.get("lock_hotkey", "ctrl+shift+l"),
                self.toggle_lock
            )
        except:
            self.lock_hotkey_ref = None

    def unregister_lock_hotkey(self):
        try:
            if self.lock_hotkey_ref:
                keyboard.remove_hotkey(self.lock_hotkey_ref)
        except:
            pass

    def edit_lock_hotkey(self):
        self.unregister_lock_hotkey()
        hotkey, ok = QInputDialog.getText(
            self,
            "Editar Hotkey do Lock",
            "Nova hotkey:",
            text=self.data.get("lock_hotkey", "ctrl+shift+l")
        )
        if ok and hotkey:
            self.data["lock_hotkey"] = hotkey
            save_data(self.data)
        self.register_lock_hotkey()

    def change_theme(self):
        theme, ok = QInputDialog.getItem(
            self,
            "Selecionar Tema",
            "Escolha o tema:",
            list(THEMES.keys()),
            0,
            False
        )
        if ok:
            self.current_theme = theme
            self.data["theme"] = theme
            save_data(self.data)
            self.setStyleSheet(THEMES[theme])

    def start_selected(self):
        index = self.list_widget.currentRow()
        if index < 0:
            return
        overlay = self.overlays[index]
        overlay.show()

    def close_selected(self):
        index = self.list_widget.currentRow()
        if index < 0:
            return
        overlay = self.overlays[index]
        overlay.hide()

    def init_tray(self):
        # Pega o caminho correto do ícone, mesmo dentro do exe
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()

        icon_path = os.path.join(base_path, "icon.ico")

        self.tray = QSystemTrayIcon(QIcon(icon_path), self)

        menu = QMenu()
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()


    def load_overlays(self):
        for data in self.data["overlays"]:
            overlay = Overlay(data, self)
            self.overlays.append(overlay)
            self.list_widget.addItem(data["name"])

    def create_overlay(self):
        name, ok = QInputDialog.getText(self, "Nome", "Nome do Overlay:")
        if not ok or not name:
            return
        hotkey, ok = QInputDialog.getText(self, "Hotkey", "Hotkey para incrementar:")
        if not ok or not hotkey:
            return
        gif_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar GIF", "", "GIF Files (*.gif)"
        )
        if not gif_path:
            return
        color = QColorDialog.getColor()
        if not color.isValid():
            return
        overlay_data = {
            "name": name,
            "gif": gif_path,
            "x": 200,
            "y": 200,
            "width": 250,
            "height": 150,
            "value": 0,
            "hotkey": hotkey,
            "color": [color.red(), color.green(), color.blue()],
            "locked": False
        }
        self.data["overlays"].append(overlay_data)
        save_data(self.data)
        overlay = Overlay(overlay_data, self)
        self.overlays.append(overlay)
        self.list_widget.addItem(name)

    def edit_selected(self):
        index = self.list_widget.currentRow()
        if index < 0:
            return
        overlay = self.overlays[index]
        name, ok = QInputDialog.getText(self, "Editar Nome", "Novo nome:", text=overlay.data["name"])
        if ok and name:
            overlay.data["name"] = name
        overlay.unregister_hotkey()
        hotkey, ok = QInputDialog.getText(self, "Editar Hotkey", "Nova hotkey:", text=overlay.data["hotkey"])
        if ok and hotkey:
            overlay.data["hotkey"] = hotkey
        overlay.register_hotkey()
        color = QColorDialog.getColor()
        if color.isValid():
            overlay.data["color"] = [color.red(), color.green(), color.blue()]
            overlay.update_counter_style()
        save_data(self.data)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for overlay in self.overlays:
            self.list_widget.addItem(overlay.data["name"])

    def reset_selected(self):
        index = self.list_widget.currentRow()
        if index >= 0:
            self.overlays[index].reset_counter()

    def toggle_lock(self):
        for overlay in self.overlays:
            overlay.data["locked"] = not overlay.data.get("locked", False)
        save_data(self.data)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = Manager()
    sys.exit(app.exec())
