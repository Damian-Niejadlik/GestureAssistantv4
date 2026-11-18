from pathlib import Path
import ast
import re
import shutil
from datetime import datetime


def replace_one(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Nie znaleziono jednoznacznie fragmentu: {old[:90]}")
    return text.replace(old, new, 1)


def main():
    root = Path.cwd()
    ui = root / "src/gesture_assistant/ui"
    paths = [ui / name for name in ("main_window.py", "workspace.py", "theme.py")]
    original = [path.read_text(encoding="utf-8-sig") for path in paths]
    m, w, t = original
    m = replace_one(m, 'QGroupBox("Co widzi aplikacja")', 'QGroupBox("Stan rozpoznawania")')
    m = replace_one(m, '        diag_layout.addWidget(self._status_label)', '        self._control_status = QLabel("Kamera nieaktywna")\n        self._control_status.setProperty("role", "status")\n        self._control_status.setWordWrap(True)\n        self._hold_status = QLabel("Przytrzymanie: —")\n        self._hold_status.setProperty("role", "secondary")\n        for item in (self._context_label, self._effective_action_label, self._action_label):\n            item.setTextFormat(Qt.TextFormat.PlainText)\n        diag_layout.addWidget(self._control_status)\n        diag_layout.addWidget(self._status_label)')
    m = replace_one(m, '        diag_layout.addWidget(self._action_label)',
                    '        diag_layout.addWidget(self._hold_status)\n'
                    '        diag_layout.addWidget(self._action_label)')
    m = replace_one(m, '        safety_vbox.addWidget(self._sleep_check)', '        safety_vbox.addWidget(self._sleep_check)\n        confirmation_hint = QLabel(\n            "Akcje wrażliwe: wybierz, które mogą prosić o jednorazową zgodę. "\n            "Nadal musisz przypisać gest i zezwolić na akcję w profilach."\n        )\n        confirmation_hint.setWordWrap(True)\n        safety_vbox.addWidget(confirmation_hint)\n        self._destructive_checks = {}\n        for action_id, spec in sorted(ACTION_CATALOG.items()):\n            if not spec.destructive or not spec.implemented:\n                continue\n            checkbox = QCheckBox(action_name(action_id, grouped=True))\n            checkbox.setChecked(action_id in self._config["safety"]["confirmed_destructive"])\n            checkbox.setToolTip("Dopuść tylko z osobnym potwierdzeniem przy każdym wykonaniu")\n            safety_vbox.addWidget(checkbox)\n            self._destructive_checks[action_id] = checkbox')
    anchor = '        new_config["safety"]["sleep_computer"] = self._sleep_check.isChecked()'
    m = replace_one(m, anchor, anchor + "\n" + '        previous = set(new_config["safety"]["confirmed_destructive"])\n        previous.difference_update(self._destructive_checks)\n        previous.update(key for key, control in self._destructive_checks.items()\n                        if control.isChecked())\n        new_config["safety"]["confirmed_destructive"] = sorted(previous)')
    anchor = '        self._sleep_check.setChecked(self._config["safety"]["sleep_computer"])'
    index = m.rindex(anchor) + len(anchor)
    m = m[:index] + "\n" + '        for key, control in self._destructive_checks.items():\n            control.setChecked(key in self._config["safety"]["confirmed_destructive"])' + m[index:]
    start = m.index('    def _refresh_actions(')
    end = m.index('    def _confirm_action(', start)
    m = m[:start] + '    def _refresh_actions(self) -> None:\n        running = self._worker is not None and self._runtime.is_running\n        paused = self._runtime.safety.paused\n        simulation = self._runtime.executor.dry_run\n        active = running and not paused and not self._demo\n        if self._demo:\n            state, button = "Demo — tylko podgląd", "Sterowanie niedostępne w demo"\n        elif not running:\n            state, button = "Kamera nieaktywna", "Najpierw uruchom kamerę"\n        elif simulation:\n            state = "Symulacja włączona" if active else "Symulacja wyłączona"\n            button = "Wyłącz symulację" if active else "Włącz symulację"\n        else:\n            state = "Sterowanie gestami włączone" if active else "Sterowanie gestami wyłączone"\n            button = "Wyłącz sterowanie gestami" if active else "Włącz sterowanie gestami"\n\n        self._workspace.source.setText(\n            "Źródło: demo na żywo" if self._demo else\n            "Źródło: sesja kamery" if self._worker is not None else "Źródło: kamera nieaktywna"\n        )\n        self._pause_button.setEnabled(running and not self._demo)\n        self._pause_button.setText(button)\n        if self._pause_button.property("controlActive") != active:\n            self._pause_button.setProperty("controlActive", active)\n            self._pause_button.style().unpolish(self._pause_button)\n            self._pause_button.style().polish(self._pause_button)\n        self._live_toggle_button.setEnabled(not self._demo)\n        pending = self._runtime.pending_confirmation() if active else None\n        self._confirm_button.setEnabled(pending is not None)\n        self._confirm_button.setToolTip(\n            f"Oczekuje: {action_name(pending[0])}" if pending else "Brak prośby o potwierdzenie"\n        )\n        outcome = self._runtime.status() if running else None\n        self._control_status.setText(state)\n        self._action_label.setText(\n            "Ostatni wynik: —" if outcome is None else\n            f"Ostatni wynik: {action_name(outcome.action_id)}\\n"\n            f"{format_reason_pl(outcome.reason, outcome.action_id)}"\n        )\n        diag = self._runtime.diagnostics() if running and not self._demo else None\n        if diag is None:\n            self._context_label.setText("Profil: —\\nAktywne okno: —")\n            self._effective_action_label.setText("Przypisana akcja: —")\n            self._hold_status.setText("Przytrzymanie: —")\n        else:\n            profile = PROFILES.get(diag["active_profile"], "Nieustalony")\n            foreground = diag["foreground_exe"]\n            window = Path(foreground).name if foreground else "Nie ustalono"\n            self._context_label.setText(f"Profil: {profile}\\nAktywne okno: {window}")\n            action = diag["effective_action"]\n            reason = diag["reason"]\n            status = format_reason_pl(reason, action or "") if reason else "Oczekiwanie na wynik"\n            if pending:\n                status = f"Oczekuje na potwierdzenie: {action_name(pending[0])}"\n            self._effective_action_label.setText(\n                f"Przypisana akcja: {action_name(action)}\\n{status}"\n            )\n            required = diag.get("required_hold_ms", 700)\n            stable = min(max(0, diag.get("stable_ms", 0)), required)\n            duration = f"{stable / 1000:.2f} / {required / 1000:.2f} s".replace(".", ",")\n            self._hold_status.setText(f"Przytrzymanie: {duration}" if action else "Przytrzymanie: —")\n\n        if self._closing and self._worker is None and not self._runtime.is_running:\n            self.close()\n\n' + m[end:]
    if m.count('escape(') == 0:
        m = m.replace('from html import escape\n', '')
    m = m.replace('"Wznów akcje"', '"Włącz sterowanie gestami"')
    m = m.replace('"Wstrzymaj akcje"', '"Wyłącz sterowanie gestami"')
    m = m.replace('„Wznów akcje”', '„Włącz sterowanie gestami”')
    m = m.replace('„Wstrzymaj akcje”', '„Wyłącz sterowanie gestami”')
    w = w.replace('"Trening"', '"Podgląd i sterowanie"')
    selector = '    QPushButton:hover'
    index = t.index(selector)
    t = t[:index] + '    QPushButton[controlActive="true"] {{\n        background: {t.ACCENT}; color: {t.BACKGROUND}; border-color: {t.ACCENT};\n    }}\n' + t[index:]
    for file, code in zip(paths, (m, w, t)):
        ast.parse(code, filename=str(file))
    backup = root / ("backup_ui_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    backup.mkdir()
    for file in paths:
        shutil.copy2(file, backup / file.name)
    for file, code in zip(paths, (m, w, t)):
        file.write_text(code, encoding="utf-8")
    print(f"Zastosowano aktualizację. Kopia: {backup}")


if __name__ == "__main__":
    main()
