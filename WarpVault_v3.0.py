#!/usr/bin/python
import os
import sys
import re
import subprocess
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QProgressBar, QTabBar)
from PySide6.QtCore import Qt, QThread, Signal

# --- CONFIGURATION (EDIT THESE PATHS) ---

# 1. Path to your non-Steam game folders (e.g., Faugus, Heroic, GOG standalone)
FAUGUS_PATH = "/home/USERNAME/YOUR_GAME_FOLDER/"

# 2. Paths to your Steam Library 'steamapps' folders.
# You can add multiple paths here if you use multiple drives.
STEAM_LIBS = [
    "/home/USERNAME/.local/share/Steam/steamapps/",
    "/path/to/your/External_Drive/SteamLibrary/steamapps/"
]

# 3. The destination where your compressed backups will be stored.
# This is your "Vault." It can be a local HDD, a network mount, or a secondary SSD.
VAULT_BASE = "/path/to/your/BACKUP_STORAGE_DRIVE/WarpVault_Storage/"

# ----------------------------------------

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti"]:
        if b < factor: return f"{b:.1f} {unit}{suffix}"
        b /= factor
    return f"{b:.1f} Pi{suffix}"

class WarpWorker(QThread):
    progress_text = Signal(str)
    progress_val = Signal(int)
    finished = Signal(str)
    item_complete = Signal()

    def __init__(self, items, mode="compress"):
        super().__init__()
        self.items = items
        self.mode = mode

    def run(self):
        total = len(self.items)
        for index, (item_name, folder_id, source_root, vault_path) in enumerate(self.items):
            is_steam_op = "Steam" in vault_path

            if is_steam_op:
                clean_base = re.sub(r'\s*\(\d+\).*$', '', item_name).strip()
                clean_base = re.sub(r'[^\w\-_\.]', '_', clean_base)
                archive_name = f"{clean_base}_({folder_id}).tar.gz"
            else:
                clean_name = re.sub(r'[^\w\-_\.]', '_', item_name.split(" [")[0])
                archive_name = f"{clean_name}.tar.gz"

            archive_path = os.path.join(vault_path, archive_name)
            self.progress_val.emit(int((index / total) * 100))

            if self.mode == "compress":
                self.progress_text.emit(f"🚀 Warping: {item_name}...")
                # The "tar" command handles the heavy lifting.
                # "--exclude" lines prevent backing up unnecessary temporary files.
                cmd = ["tar", "-I", "pigz", "-cf", archive_path,
                       "--exclude=*/shadercache/*", "--exclude=*/Temp/*", folder_id]
                res = subprocess.run(cmd, cwd=source_root)
            else:
                self.progress_text.emit(f"📂 Reconstituting: {item_name}...")
                actual_archive = archive_path
                if not os.path.exists(actual_archive) and is_steam_op:
                    if os.path.exists(vault_path):
                        for f in os.listdir(vault_path):
                            if folder_id in f and f.endswith(".tar.gz"):
                                actual_archive = os.path.join(vault_path, f)
                                break

                if not os.path.exists(actual_archive): continue
                os.makedirs(source_root, exist_ok=True)
                cmd = ["tar", "-I", "pigz", "-xf", actual_archive, "-C", source_root]
                res = subprocess.run(cmd)

            if res.returncode == 0:
                self.item_complete.emit()

        self.progress_val.emit(100)
        self.finished.emit("Vault Operation Complete.")

class WarpVault(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WarpVault v3.0 | Ultimate Edition")
        self.resize(750, 950)
        self.steam_map = self.get_steam_mapping()
        self.init_ui()

    def get_steam_mapping(self):
        # This function uses protontricks to match AppIDs to real game names
        mapping = {}
        try:
            result = subprocess.run(['protontricks', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                matches = re.findall(r"(?:Found\s'|Non-Steam\sshortcut:\s)(.*?)(?:'\s|\s)\((\d+)\)", result.stdout)
                for name, appid in matches:
                    mapping[appid] = name
        except: pass
        return mapping

    def init_ui(self):
        # Custom CSS for the "Neon/Cyber" aesthetic
        self.setStyleSheet("""
            QMainWindow { background-color: #0f0f13; }
            QWidget { background-color: #0f0f13; color: #cfcfcf; font-family: 'Segoe UI', sans-serif; }

            QTabWidget::pane { border: 2px solid #00f2ff; background: #15151b; top: -1px; }

            QTabBar {
                qproperty-expanding: false;
                qproperty-drawBase: 0;
                outline: none;
            }

            QTabBar::tab {
                background: #1a1a24;
                padding: 15px;
                border: 1px solid #2d2d3d;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                width: 330px;
                margin-right: 4px;
                outline: none;
            }

            QTabBar::tab:selected {
                background: #00f2ff;
                color: #000;
                border: 1px solid #00f2ff;
                margin-bottom: -1px;
            }

            QTabBar::tab:hover:!selected { background: #252535; border: 1px solid #444; }

            QTableWidget { background: #18181f; border: 1px solid #333; gridline-color: transparent; font-size: 16px; outline: none; }
            QTableWidget::item { padding-left: 10px; padding-right: 25px; }

            QPushButton { background-color: #252535; border: 1px solid #444; padding: 18px; border-radius: 6px; font-size: 14px; font-weight: bold; outline: none; }
            #compressBtn { background-color: #00f2ff; color: #000; }
            #recoverBtn { background-color: #ff00ff; color: #fff; }

            QProgressBar { border: 1px solid #333; border-radius: 4px; text-align: center; height: 20px; background: #111; font-size: 13px; }
            QProgressBar::chunk { background-color: #00f2ff; }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(False)

        self.table_f = self.create_table_widget()
        self.table_s = self.create_table_widget()

        self.tabs.addTab(self.create_tab(self.table_f, "NON-STEAM"), "NON-STEAM")
        self.tabs.addTab(self.create_tab(self.table_s, "STEAM"), "STEAM")
        layout.addWidget(self.tabs)

        self.pbar = QProgressBar()
        self.pbar.hide()
        layout.addWidget(self.pbar)

        footer = QHBoxLayout()
        self.log = QLabel("Engine Ready...")
        self.log.setStyleSheet("color: #00f2ff; font-family: monospace; font-size: 15px; font-weight: bold;")
        self.storage_info = QLabel("")
        self.storage_info.setStyleSheet("color: #aaa; font-size: 14px; font-weight: bold;")
        footer.addWidget(self.log)
        footer.addStretch()
        footer.addWidget(self.storage_info)
        layout.addLayout(footer)

        self.refresh_lists()

    def create_table_widget(self):
        table = QTableWidget(0, 2)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        return table

    def create_tab(self, table_widget, mode_name):
        tab = QWidget(); lay = QVBoxLayout(tab)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.addWidget(table_widget)

        ctrl = QHBoxLayout()
        all_btn = QPushButton("SELECT ALL"); clr_btn = QPushButton("CLEAR ALL")
        all_btn.clicked.connect(lambda: self.bulk(table_widget, Qt.Checked))
        clr_btn.clicked.connect(lambda: self.bulk(table_widget, Qt.Unchecked))
        ctrl.addWidget(all_btn); ctrl.addWidget(clr_btn); lay.addLayout(ctrl)

        act_row = QHBoxLayout()
        c_btn = QPushButton(f"⚡ COMPRESS {mode_name}"); c_btn.setObjectName("compressBtn")
        c_btn.clicked.connect(lambda: self.start_warp(table_widget, "compress"))
        r_btn = QPushButton(f"🛡️ RECOVER {mode_name}"); r_btn.setObjectName("recoverBtn")
        r_btn.clicked.connect(lambda: self.start_warp(table_widget, "recover"))
        act_row.addWidget(c_btn); act_row.addWidget(r_btn); lay.addLayout(act_row)
        return tab

    def bulk(self, widget, state):
        for i in range(widget.rowCount()):
            item = widget.item(i, 0)
            if item: item.setCheckState(state)

    def refresh_lists(self):
        try:
            usage = shutil.disk_usage(VAULT_BASE)
            self.storage_info.setText(f"{usage.free // (1024**3)} GB FREE")
        except: self.storage_info.setText("DRIVE OFFLINE")

        self._populate_table(self.table_f, [FAUGUS_PATH], os.path.join(VAULT_BASE, "Faugus"), False)
        self._populate_table(self.table_s, [os.path.join(p, "compatdata") for p in STEAM_LIBS], os.path.join(VAULT_BASE, "Steam"), True)

    def _populate_table(self, table, live_roots, vault_root, is_steam):
        checked_ids = set()
        for i in range(table.rowCount()):
            if table.item(i, 0).checkState() == Qt.Checked:
                checked_ids.add(table.item(i, 0).data(Qt.UserRole)[1])

        table.setRowCount(0)
        live_found = {}
        vault_files = {}

        if os.path.exists(vault_root):
            for f in os.listdir(vault_root):
                f_path = os.path.join(vault_root, f)
                if os.path.isfile(f_path):
                    vault_files[f] = get_size_format(os.path.getsize(f_path))

        for root in live_roots:
            if os.path.exists(root):
                for f in os.listdir(root):
                    if os.path.isdir(os.path.join(root, f)):
                        if is_steam and not f.isdigit(): continue
                        live_found[f] = root

        all_ids = set(live_found.keys())
        for vf in vault_files.keys():
            v_id_match = re.search(r'\((\d+)\)', vf)
            if v_id_match: all_ids.add(v_id_match.group(1))
            elif not is_steam and vf.endswith(".tar.gz"): all_ids.add(vf.replace(".tar.gz", ""))

        for fid in sorted(all_ids):
            if not is_steam and fid.isdigit() and fid not in live_found: continue
            raw_name = self.steam_map.get(fid, fid)
            display_name = f"{raw_name} ({fid})" if is_steam else fid

            vault_size = ""
            vault_found = False
            for f, size in vault_files.items():
                if (is_steam and (f"({fid})" in f or f"_{fid}_" in f)) or (not is_steam and f == f"{fid}.tar.gz"):
                    vault_size = size; vault_found = True; break

            status = " [SYNCED]" if fid in live_found and vault_found else " [LIVE]" if fid in live_found else " [VAULT ONLY]"
            color = Qt.green if "SYNCED" in status else Qt.cyan if "LIVE" in status else Qt.magenta

            row = table.rowCount()
            table.insertRow(row)

            name_item = QTableWidgetItem(f"{display_name}{status}")
            name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
            name_item.setCheckState(Qt.Checked if fid in checked_ids else Qt.Unchecked)
            name_item.setForeground(color)
            name_item.setData(Qt.UserRole, (display_name, fid, live_found.get(fid, live_roots[-1] if live_roots else ""), vault_root))
            table.setItem(row, 0, name_item)

            size_item = QTableWidgetItem(vault_size)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            size_item.setForeground(color)
            table.setItem(row, 1, size_item)

    def start_warp(self, table, action):
        selected = []
        for i in range(table.rowCount()):
            if table.item(i, 0).checkState() == Qt.Checked:
                selected.append(table.item(i, 0).data(Qt.UserRole))

        if not selected: return
        self.pbar.show()
        self.worker = WarpWorker(selected, action)
        self.worker.progress_text.connect(self.log.setText)
        self.worker.progress_val.connect(self.pbar.setValue)
        self.worker.finished.connect(lambda m: [self.log.setText(m), self.pbar.hide()])
        self.worker.item_complete.connect(self.refresh_lists)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = WarpVault(); window.show(); sys.exit(app.exec())
