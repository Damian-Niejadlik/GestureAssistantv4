import csv
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QFrame,
    QHBoxLayout, QLabel, QListWidget, QMenu, QMessageBox, QPushButton, QScrollArea,
    QSpinBox, QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget, QCheckBox,
)

from src.gesture_assistant.ui import tokens
from src.gesture_assistant.ui.calibration import CalibrationPage
from src.gesture_assistant.ui.display_names import action_name

from copy import deepcopy

from src.gesture_assistant.integrations import ACTION_CATALOG


def label(text, role="secondary"):
    widget = QLabel(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setWordWrap(True)
    widget.setProperty("role", role)
    return widget


def card():
    frame = QFrame()
    frame.setProperty("role", "card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(tokens.SPACE)
    return frame, layout


def scroll(widget):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(widget)
    return area


def app_icon():
    image = QPixmap(32, 32)
    image.fill(QColor(tokens.BACKGROUND))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(tokens.ACCENT), 2))
    painter.drawRoundedRect(4, 4, 24, 24, 6, 6)
    painter.drawLine(9, 19, 14, 12)
    painter.drawLine(14, 12, 19, 21)
    painter.drawLine(19, 21, 23, 14)
    painter.end()
    return QIcon(image)


class Workspace(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        preview, bindings, parameters = (window._tabs.widget(i) for i in range(3))
        while window._tabs.count():
            window._tabs.removeTab(0)
        self.setObjectName("Workspace")
        layout = QHBoxLayout(self)
        sidebar, nav = card()
        sidebar.setFixedWidth(216)
        layout.setSpacing(16)
        nav.addWidget(label("GestureAssistant", "title"))
        self.pages = QStackedWidget()
        self.nav = []
        for index, text in enumerate(("Start", "Podgląd i sterowanie", "Historia", "Ustawienia", "Kalibracja gestów")):
            button = QPushButton(text)
            button.setCheckable(True)
            button.setProperty("nav", True)
            button.clicked.connect(lambda checked=False, i=index: self.navigate(i))
            nav.addWidget(button)
            self.nav.append(button)
        nav.addStretch()
        self.source = label("Źródło: kamera nieaktywna")
        nav.addWidget(self.source)
        nav.addWidget(label("0.1.0 · Etap 4"))
        help_button = QPushButton("Pomoc")
        help_button.clicked.connect(self.help)
        nav.addWidget(help_button)
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)
        start, content = card()
        content.addWidget(label("Steruj gestami", "title"))
        content.addWidget(label("Profile: Auto, Teams, Przeglądarka, Prezentacja, Multimedia i System."))
        content.addWidget(label("Ustaw kamerę na wysokości dłoni. Pokaż jedną, całą dłoń "
                                "w równym świetle; zostaw miejsce na ruch."))
        prepare = QPushButton("Przygotuj sesję")
        prepare.setProperty("primary", True)
        prepare.clicked.connect(self.prepare)
        content.addWidget(prepare)
        demo = QPushButton("Demo na żywo · bez wykonywania akcji")
        demo.clicked.connect(self.open_demo)
        content.addWidget(demo)
        content.addWidget(label("Ostatnie wykonane akcje"))
        self.recent = label("Brak wykonanych akcji w tej sesji.")
        content.addWidget(self.recent)
        content.addStretch()
        self.pages.addWidget(scroll(start))
        self.pages.addWidget(scroll(preview))
        history, panel = card()
        panel.addWidget(label("Historia sesji", "title"))
        self.filter = QComboBox()
        self.filter.addItems(("Wszystkie wyniki", "Wykonane", "Symulacje", "Odmowy i błędy"))
        self.filter.currentIndexChanged.connect(self.refresh_history)
        panel.addWidget(self.filter)
        self.rows = QListWidget()
        self.rows.currentRowChanged.connect(self.details)
        panel.addWidget(self.rows, 1)
        self.detail = label("Brak zapisanych wyników w tej sesji.")
        panel.addWidget(self.detail)
        controls = QHBoxLayout()
        self.export_button = QPushButton("Eksportuj widoczne do CSV")
        self.export_button.clicked.connect(self.export)
        controls.addWidget(self.export_button)
        self.clear_button = QPushButton("Usuń historię sesji")
        self.clear_button.clicked.connect(self.clear)
        controls.addWidget(self.clear_button)
        panel.addLayout(controls)
        self.pages.addWidget(history)
        settings = QStackedWidget()
        settings.addWidget(bindings)
        settings.addWidget(parameters)
        settings.addWidget(self._build_confirmation_settings())
        container, options = card()
        options.addWidget(label("Ustawienia", "title"))
        selector = QComboBox()
        selector.addItems(
            ("Profile akcji", "Gesty, ruchy i bezpieczeństwo", "Potwierdzanie akcji")
        )
        selector.currentIndexChanged.connect(self._load_confirmation_settings)
        selector.currentIndexChanged.connect(settings.setCurrentIndex)
        options.addWidget(selector)
        options.addWidget(settings, 1)
        self.pages.addWidget(container)
        self.calibration = CalibrationPage(window)
        self.pages.addWidget(scroll(self.calibration))
        self.visible_records = []
        self.navigate(0)
        self.refresh_history()
        self.tray = None
        icon = app_icon()
        window.setWindowIcon(icon)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(icon, window)
            self.tray.setToolTip("GestureAssistant")
            menu = QMenu(window)
            menu.addAction("Pokaż okno", self.show_window)
            menu.addAction("Zakończ sesję", window._stop_analysis)
            menu.addAction("Zamknij aplikację", window.close)
            self.tray.setContextMenu(menu)
            self.tray.activated.connect(self.activate_tray)
            self.tray.show()

    def show_window(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def activate_tray(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()

    def help(self):
        QMessageBox.information(self, "Pomoc", "Trening korzysta z prawdziwej kamery. "
                                "Demo nie wykonuje akcji. Do sterowania inną aplikacją "
                                "przełącz fokus na jej okno po wznowieniu akcji.")

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav):
            button.setChecked(i == index)
        if index in (0, 2):
            self.refresh_history()

    def prepare(self):
        if self.window._worker is not None:
            self.navigate(1)
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Przygotowanie sesji")
        form = QFormLayout(dialog)
        profile = QComboBox(dialog)
        source = self.window._mode_combo
        for index in range(source.count()):
            profile.addItem(source.itemText(index))
        profile.setCurrentIndex(source.currentIndex())
        camera = QSpinBox(dialog)
        camera.setRange(self.window._camera_index.minimum(), self.window._camera_index.maximum())
        camera.setValue(self.window._camera_index.value())
        form.addRow("Profil", profile)
        form.addRow("Numer kamery", camera)
        form.addRow(label("Otwórz podgląd i sprawdź, czy widać całą dłoń. Ocena jakości "
                          "jest przybliżona. Akcje pozostaną wstrzymane do ręcznego wznowienia."))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Otwórz podgląd")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Wróć")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            source.setCurrentIndex(profile.currentIndex())
            self.window._camera_index.setValue(camera.value())
            self.navigate(1)
            self.window._start_analysis()


    def _build_confirmation_settings(self):
        page, layout = card()
        layout.addWidget(label("Potwierdzanie akcji", "title"))
        layout.addWidget(
            label(
                "Wybierz, które akcje mogą prosić o jednorazową zgodę. "
                "Każdą akcję nadal trzeba przypisać do gestu i dopuścić "
                "w profilach. Zaznaczenie poniżej nie wykonuje żadnej akcji."
            )
        )

        self._confirmation_checks = {}
        for action_id, spec in sorted(
            ACTION_CATALOG.items(),
            key=lambda item: action_name(item[0], grouped=True),
        ):
            if not spec.destructive or not spec.implemented:
                continue

            checkbox = QCheckBox(action_name(action_id, grouped=True))
            checkbox.setToolTip(
                "Aplikacja poprosi o osobną zgodę przy każdym wykonaniu."
            )
            layout.addWidget(checkbox)
            self._confirmation_checks[action_id] = checkbox

        self._confirmation_notice = label("")
        layout.addWidget(self._confirmation_notice)

        save = QPushButton("Zapisz zasady potwierdzania")
        save.setProperty("primary", True)
        save.clicked.connect(self._save_confirmation_settings)
        layout.addWidget(save)
        layout.addStretch()

        self._load_confirmation_settings(2)
        return scroll(page)

    def _load_confirmation_settings(self, index):
        if index != 2:
            return
        saved = set(self.window._config["safety"]["confirmed_destructive"])
        for action_id, checkbox in self._confirmation_checks.items():
            checkbox.setChecked(action_id in saved)
        self._confirmation_notice.clear()

    def _save_confirmation_settings(self):
        if self.window._demo:
            self._confirmation_notice.setText(
                "Zakończ demo lub kalibrację przed zapisaniem tych ustawień."
            )
            return

        config = deepcopy(self.window._config)
        confirmed = set(config["safety"]["confirmed_destructive"])
        confirmed.difference_update(self._confirmation_checks)
        confirmed.update(
            action_id
            for action_id, checkbox in self._confirmation_checks.items()
            if checkbox.isChecked()
        )
        config["safety"]["confirmed_destructive"] = sorted(confirmed)

        if self.window._apply_configuration(config):
            self._confirmation_notice.setText(
                "Zapisano zasady potwierdzania. Aby użyć gestu, ponownie "
                "włącz sterowanie w widoku kamery."
            )
        else:
            self._confirmation_notice.setText(
                "Nie udało się zapisać zasad. Sprawdź komunikat błędu."
            )

    def open_demo(self):
        if self.window._worker is not None or self.window._runtime.is_running:
            QMessageBox.information(self, "Demo", "Najpierw zakończ bieżącą sesję.")
            return
        self.window._demo = True
        self.navigate(1)
        self.window._start_analysis()
        if self.window._worker is None:
            self.window._demo = False

    def refresh_history(self):
        records = self.window._runtime.history()
        mode = self.filter.currentIndex()
        self.visible_records = [record for record in reversed(records) if (
            mode == 0 or self.category(record[1])[0] == mode
        )]
        self.rows.clear()
        for stamp, outcome in self.visible_records:
            date = datetime.fromtimestamp(stamp).strftime("%H:%M:%S")
            self.rows.addItem(f"{date}  ·  {self.category(outcome)[1]}  ·  {action_name(outcome.action_id, grouped=True)}")
        executed = [action_name(outcome.action_id) for _, outcome in reversed(records) if outcome.executed]
        self.recent.setText("\n".join(executed[:4]) or "Brak wykonanych akcji w tej sesji.")
        self.export_button.setEnabled(bool(self.visible_records))
        self.clear_button.setEnabled(bool(records))
        self.details(-1)

    @staticmethod
    def category(outcome):
        if outcome.executed:
            return 1, "Wykonano"
        if outcome.reason == "dry_run_no_side_effect":
            return 2, "Symulacja"
        return 3, "Odmowa lub błąd"

    def details(self, row):
        if 0 <= row < len(self.visible_records):
            _, outcome = self.visible_records[row]
            self.detail.setText(f"{action_name(outcome.action_id, grouped=True)}\n{self.category(outcome)[1]}"
                                f"\n\nSzczegóły techniczne: {outcome.reason}")
        else:
            self.detail.setText("Wybierz wpis, aby zobaczyć szczegóły." if self.visible_records
                                else "Brak wyników dla bieżącego filtru.")

    def export(self):
        name, _ = QFileDialog.getSaveFileName(self, "Eksport historii", "historia.csv", "CSV (*.csv)")
        if not name:
            return
        try:
            with Path(name).open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow(("Czas lokalny", "Akcja", "Stan"))
                for stamp, outcome in self.visible_records:
                    writer.writerow((datetime.fromtimestamp(stamp).isoformat(timespec="seconds"),
                                     outcome.action_id, self.category(outcome)[1]))
        except OSError as exc:
            QMessageBox.warning(self, "Eksport nieudany", str(exc))

    def clear(self):
        if QMessageBox.question(self, "Usunąć wpisy?", "Usunąć całą historię bieżącej sesji?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.window._runtime.clear_history()
            self.refresh_history()
