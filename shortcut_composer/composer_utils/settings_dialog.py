# SPDX-FileCopyrightText: © 2022 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QTabWidget,
    QDialog,
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QCursor

from api_krita import Krita
from api_krita.wrappers import Database
from .config import Config, ConfigFormWidget, ConfigComboBox, ConfigSpinBox
from .layouts import ButtonsLayout


class SettingsDialog(QDialog):
    """Dialog which allows to configure plugin elements."""

    def __init__(self) -> None:
        super().__init__()

        self.setMinimumSize(QSize(300, 200))
        self.setWindowTitle("Configure Shortcut Composer")

        self._tags: List[str] = []
        self._refresh_tags()

        general_tab = ConfigFormWidget([
            "Preset pie-menus mapping",
            ConfigComboBox(Config.TAG_RED, self, self._tags),
            ConfigComboBox(Config.TAG_GREEN, self, self._tags),
            ConfigComboBox(Config.TAG_BLUE, self, self._tags),
            "Common settings",
            ConfigSpinBox(Config.SHORT_VS_LONG_PRESS_TIME, self, 0.05, 4),
            ConfigSpinBox(Config.FPS_LIMIT, self, 5, 500),
            "Cursor trackers",
            ConfigSpinBox(Config.TRACKER_SENSITIVITY_SCALE, self, 0.05, 400),
            ConfigSpinBox(Config.TRACKER_DEADZONE, self, 1, 200),
            "Pie menus display",
            ConfigSpinBox(Config.PIE_GLOBAL_SCALE, self, 0.05, 4),
            ConfigSpinBox(Config.PIE_ICON_GLOBAL_SCALE, self, 0.05, 4),
            ConfigSpinBox(Config.PIE_DEADZONE_GLOBAL_SCALE, self, 0.05, 4),
            ConfigSpinBox(Config.PIE_ANIMATION_TIME, self, 0.01, 1),
        ])

        self._tab_dict = {"General": general_tab}
        tab_holder = QTabWidget()
        for name, tab in self._tab_dict.items():
            tab_holder.addTab(tab, name)

        full_layout = QVBoxLayout(self)
        full_layout.addWidget(tab_holder)
        full_layout.addLayout(ButtonsLayout(
            ok_callback=self.ok,
            apply_callback=self.apply,
            reset_callback=self.reset,
            cancel_callback=self.hide,
        ))
        self.setLayout(full_layout)

    def show(self) -> None:
        """Show the dialog after refreshing all its elements."""
        self.refresh()
        self.move(QCursor.pos())
        return super().show()

    def apply(self) -> None:
        """Ask all dialog zones to apply themselves."""
        for tab in self._tab_dict.values():
            tab.apply()
        Krita.trigger_action("Reload Shortcut Composer")

    def ok(self) -> None:
        """Hide the dialog after applying the changes"""
        self.apply()
        self.hide()

    def reset(self) -> None:
        """Reset all config values to defaults in krita and elements."""
        Config.reset_defaults()
        self.refresh()
        Krita.trigger_action("Reload Shortcut Composer")

    def _refresh_tags(self):
        with Database() as database:
            tags = sorted(database.get_brush_tags(), key=str.lower)
        self._tags.clear()
        self._tags.extend(tags)

    def refresh(self):
        """Ask all tabs to refresh themselves. """
        self._refresh_tags()
        for tab in self._tab_dict.values():
            tab.refresh()
