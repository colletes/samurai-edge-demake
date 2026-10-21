import io
import os
import sys
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CoverArtUpdater(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suno MP3 Cover Art Swapper")
        self.setMinimumSize(760, 480)

        # Data store: { mp3_filepath: custom_image_filepath_or_None }
        self.songs = {}
        self.global_image_path = None

        self._init_ui()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # --- LEFT PANEL: Song Queue ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(
            QLabel("<b>1. Songs Queue</b> (Select one or multiple):")
        )

        self.song_list = QListWidget()
        self.song_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.song_list.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.song_list)

        btn_row = QHBoxLayout()
        btn_add_songs = QPushButton("Add MP3s...")
        btn_add_songs.clicked.connect(self.add_songs)
        btn_remove = QPushButton("Remove Selected")
        btn_remove.clicked.connect(self.remove_selected_songs)
        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self.clear_songs)

        btn_row.addWidget(btn_add_songs)
        btn_row.addWidget(btn_remove)
        btn_row.addWidget(btn_clear)
        left_layout.addLayout(btn_row)

        layout.addLayout(left_layout, 3)

        # --- RIGHT PANEL: Artwork Preview & Controls ---
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>2. Artwork Assignment & Preview</b>"))

        previews_box = QHBoxLayout()

        # Current Embedded Art Group
        curr_group = QGroupBox("Current Embedded Art")
        curr_vbox = QVBoxLayout(curr_group)
        self.lbl_current_art = QLabel("Select a song")
        self.lbl_current_art.setFixedSize(190, 190)
        self.lbl_current_art.setAlignment(Qt.AlignCenter)
        self.lbl_current_art.setStyleSheet(
            "border: 1px dashed #666; background: #1e1e1e; color: #888; border-radius: 6px;"
        )
        curr_vbox.addWidget(self.lbl_current_art, alignment=Qt.AlignCenter)
        previews_box.addWidget(curr_group)

        # New Art Group
        new_group = QGroupBox("New Custom Art")
        new_vbox = QVBoxLayout(new_group)
        self.lbl_new_art = QLabel("No new art assigned")
        self.lbl_new_art.setFixedSize(190, 190)
        self.lbl_new_art.setAlignment(Qt.AlignCenter)
        self.lbl_new_art.setStyleSheet(
            "border: 1px dashed #666; background: #1e1e1e; color: #888; border-radius: 6px;"
        )
        new_vbox.addWidget(self.lbl_new_art, alignment=Qt.AlignCenter)
        previews_box.addWidget(new_group)

        right_layout.addLayout(previews_box)

        # Assignment Buttons
        btn_assign_sel = QPushButton("Assign Image to Selected Song(s)...")
        btn_assign_sel.setMinimumHeight(34)
        btn_assign_sel.clicked.connect(self.assign_image_to_selected)
        right_layout.addWidget(btn_assign_sel)

        btn_assign_all = QPushButton("Assign One Image to ALL Songs in List...")
        btn_assign_all.setMinimumHeight(34)
        btn_assign_all.clicked.connect(self.assign_image_to_all)
        right_layout.addWidget(btn_assign_all)

        right_layout.addStretch()

        # Status & Save
        self.lbl_status = QLabel("Ready. Add MP3 files to begin.")
        self.lbl_status.setStyleSheet("color: #aaa;")
        right_layout.addWidget(self.lbl_status)

        self.btn_apply = QPushButton("Apply && Save New Artwork to MP3s")
        self.btn_apply.setMinimumHeight(44)
        self.btn_apply.setStyleSheet(
            "QPushButton { background-color: #2ea043; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #3fb950; }"
        )
        self.btn_apply.clicked.connect(self.apply_artwork)
        right_layout.addWidget(self.btn_apply)

        layout.addLayout(right_layout, 4)

    # --- Actions ---

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Suno MP3 Files", "", "Audio Files (*.mp3)"
        )
        for f in files:
            if f not in self.songs:
                self.songs[f] = self.global_image_path
                item = QListWidgetItem(self._format_item_text(f))
                item.setData(Qt.UserRole, f)
                self.song_list.addItem(item)

        if self.song_list.count() > 0 and not self.song_list.selectedItems():
            self.song_list.setCurrentRow(0)
        self._update_status()

    def remove_selected_songs(self):
        for item in self.song_list.selectedItems():
            path = item.data(Qt.UserRole)
            self.songs.pop(path, None)
            self.song_list.takeItem(self.song_list.row(item))
        self._on_selection_changed()
        self._update_status()

    def clear_songs(self):
        self.songs.clear()
        self.song_list.clear()
        self.global_image_path = None
        self.lbl_current_art.clear()
        self.lbl_current_art.setText("Select a song")
        self.lbl_new_art.clear()
        self.lbl_new_art.setText("No new art assigned")
        self._update_status()

    def assign_image_to_selected(self):
        selected = self.song_list.selectedItems()
        if not selected:
            QMessageBox.information(
                self,
                "Select Songs",
                "Please select at least one song from the list first.",
            )
            return

        img_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not img_path:
            return

        for item in selected:
            song_path = item.data(Qt.UserRole)
            self.songs[song_path] = img_path
            item.setText(self._format_item_text(song_path))

        self._on_selection_changed()
        self._update_status()

    def assign_image_to_all(self):
        if not self.songs:
            QMessageBox.information(
                self, "No Songs", "Please add MP3 files to the list first."
            )
            return

        img_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Image for All Songs",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not img_path:
            return

        self.global_image_path = img_path
        for i in range(self.song_list.count()):
            item = self.song_list.item(i)
            song_path = item.data(Qt.UserRole)
            self.songs[song_path] = img_path
            item.setText(self._format_item_text(song_path))

        self._on_selection_changed()
        self._update_status()

    # --- Helpers & Previews ---

    def _format_item_text(self, song_path):
        base = os.path.basename(song_path)
        assigned = self.songs.get(song_path)
        if assigned:
            return f"✅ {base}  ➔  [{os.path.basename(assigned)}]"
        return f"🎵 {base}"

    def _on_selection_changed(self):
        selected = self.song_list.selectedItems()
        if not selected:
            self.lbl_current_art.clear()
            self.lbl_current_art.setText("Select a song")
            self.lbl_new_art.clear()
            self.lbl_new_art.setText("No new art assigned")
            return

        # Preview the first selected track
        song_path = selected[0].data(Qt.UserRole)
        self._load_embedded_preview(song_path)

        new_img_path = self.songs.get(song_path)
        if new_img_path and os.path.exists(new_img_path):
            pix = QPixmap(new_img_path)
            self.lbl_new_art.setPixmap(
                pix.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.lbl_new_art.clear()
            self.lbl_new_art.setText("No new art assigned")

    def _load_embedded_preview(self, song_path):
        try:
            audio = ID3(song_path)
            apic_frames = audio.getall("APIC")
            if apic_frames:
                img_bytes = apic_frames[0].data
                pix = QPixmap()
                pix.loadFromData(img_bytes)
                self.lbl_current_art.setPixmap(
                    pix.scaled(
                        190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
                return
        except Exception:
            pass

        self.lbl_current_art.clear()
        self.lbl_current_art.setText("No embedded art")

    def _prepare_image_bytes(self, img_path):
        """Standardizes image data (converts WEBP/BMP to JPEG/PNG for full ID3 compatibility)."""
        with Image.open(img_path) as img:
            out = io.BytesIO()
            fmt = img.format if img.format in ("JPEG", "PNG") else "JPEG"
            if fmt == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(out, format=fmt, quality=95)
            mime = "image/png" if fmt == "PNG" else "image/jpeg"
            return out.getvalue(), mime

    def _update_status(self):
        total = len(self.songs)
        ready = sum(1 for v in self.songs.values() if v)
        self.lbl_status.setText(
            f"{total} track(s) loaded  |  {ready} ready with new artwork."
        )

    # --- Write ID3 Tags ---

    def apply_artwork(self):
        targets = {k: v for k, v in self.songs.items() if v}
        if not targets:
            QMessageBox.warning(
                self,
                "Nothing to Apply",
                "Assign a new cover image to at least one song first.",
            )
            return

        updated = 0
        errors = []

        for song_path, img_path in targets.items():
            try:
                img_bytes, mime = self._prepare_image_bytes(img_path)
                try:
                    audio = ID3(song_path)
                except ID3NoHeaderError:
                    audio = ID3()

                # Remove existing Suno APIC cover frame
                audio.delall("APIC")

                # Add new front cover (type=3)
                audio.add(
                    APIC(
                        encoding=3,
                        mime=mime,
                        type=3,
                        desc="Cover",
                        data=img_bytes,
                    )
                )

                # Save as ID3v2.3 for broadest OS & media player support
                audio.save(song_path, v2_version=3)

                # Touch file modification timestamp so OS refreshes Finder/Explorer icon cache
                os.utime(song_path, None)
                updated += 1
            except Exception as e:
                errors.append(f"{os.path.basename(song_path)}: {e}")

        # Refresh preview to show newly embedded cover
        self._on_selection_changed()

        if errors:
            QMessageBox.warning(
                self,
                "Completed with Errors",
                f"Updated {updated} song(s).\n\nErrors:\n" + "\n".join(errors),
            )
        else:
            QMessageBox.information(
                self,
                "Success",
                f"Successfully embedded new artwork into {updated} MP3 file(s)!",
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoverArtUpdater()
    window.show()
    sys.exit(app.exec())