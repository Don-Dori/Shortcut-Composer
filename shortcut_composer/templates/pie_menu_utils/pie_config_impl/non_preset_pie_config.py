# SPDX-FileCopyrightText: © 2022-2023 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Callable, Generic, TypeVar
from PyQt5.QtGui import QColor

from data_components import DeadzoneStrategy
from api_krita import Krita
from ..pie_config import PieConfig

T = TypeVar("T")


class NonPresetPieConfig(PieConfig[T], Generic[T]):
    """FieldGroup representing config of PieMenu of non-preset values."""

    def __init__(
        self,
        name: str,
        values: List[T],
        pie_radius_scale: float,
        icon_radius_scale: float,
        save_local: bool,
        background_color: QColor,
        active_color: QColor,
        pie_opacity: int,
        deadzone_strategy: DeadzoneStrategy
    ) -> None:
        super().__init__(name)

        self.PIE_RADIUS_SCALE = self.field("Pie scale", pie_radius_scale)
        self.ICON_RADIUS_SCALE = self.field("Icon scale", icon_radius_scale)

        self.SAVE_LOCAL = self.field("Save local", save_local)
        self.DEADZONE_STRATEGY = self.field("deadzone", deadzone_strategy)
        self.ORDER = self._create_editable_dual_field("Values", values)

        use_default = active_color is None and background_color is None
        if background_color is None:
            background_color = Krita.get_main_color_from_theme()
        if active_color is None:
            active_color = Krita.get_active_color_from_theme()
        self.USE_DEFAULT_THEME = self.field("Use default theme", use_default)
        self.BACKGROUND_COLOR = self.field("Bg color", background_color)
        self.ACTIVE_COLOR = self.field("Active color", active_color)
        self.PIE_OPACITY = self.field("Pie opacity", pie_opacity)
        self.allow_value_edit = True

    def values(self) -> List[T]:
        """Return values defined be the user to display as icons."""
        return self.ORDER.read()

    def set_values(self, values: List[T]) -> None:
        """Change current values to new ones."""
        self.ORDER.write(values)

    def refresh_order(self) -> None:
        """Refresh the values in case the active document changed."""
        self.ORDER.write(self.values())

    def set_current_as_default(self):
        """Set current pie values as a new default list of values."""
        self.ORDER.default = self.ORDER.read()

    def reset_the_default(self) -> None:
        """Set empty pie as a new default list of values."""
        self.ORDER.default = []

    def reset_to_default(self) -> None:
        self.ORDER.reset_default()
        self.refresh_order()

    def is_order_default(self) -> bool:
        """Return whether order is the same as default one."""
        return self.ORDER.read() == self.ORDER.default

    def register_to_order_related(self, callback: Callable[[], None]) -> None:
        """Register callback to all fields related to value order."""
        self.ORDER.register_callback(callback)
