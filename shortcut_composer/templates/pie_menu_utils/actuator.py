# SPDX-FileCopyrightText: © 2022-2023 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional, List
from core_components import Controller
from config_system import Field
from data_components import DeadzoneStrategy
from .label import Label
from .pie_widget_utils import WidgetHolder


class Actuator:
    """
    Activates the correct labels from the Pie.

    When a valid label is given in `activate()` method, it us activated
    and also remembered.

    When label is not given in `activate()` method, it means that user
    closed the pie while still being in deadzone.
    Then it is handled using the currently active strategy.

    Actuator tracks selected strategy using `strategy_field` passed on
    initialization. It can be changed in runtime.

    Strategies:
    DeadzoneStrategy.DO_NOTHING - no action is needed
    DeadzoneStrategy.PICK_TOP - first label in list is activated
    DeadzoneStrategy.PICK_PREVIOUS - remembered label is activated
    """

    def __init__(
        self,
        controller: Controller,
        strategy_field: Field,
        labels: List[Label]
    ) -> None:
        self._controller = controller
        self._last_label: Optional[Label] = None
        self._labels = labels

        def update_strategy():
            self._current_strategy = strategy_field.read()
        self._current_strategy: DeadzoneStrategy
        strategy_field.register_callback(update_strategy)
        update_strategy()

    def activate(self, active: Optional[Label]) -> None:
        """Activate the correct label"""
        if active is not None:
            # Out of deadzone, label picked
            self._controller.set_value(active.value)
            self._last_label = active
            return

        # In deadzone
        if self.selected_label is not None:
            self._controller.set_value(self.selected_label.value)

    @property
    def selected_label(self) -> Optional[Label]:
        """Return label which should be picked on deadzone."""
        if self._current_strategy == DeadzoneStrategy.DO_NOTHING:
            return None
        elif self._current_strategy == DeadzoneStrategy.PICK_TOP:
            if self._labels:
                return self._labels[0]
            return None
        elif self._current_strategy == DeadzoneStrategy.PICK_PREVIOUS:
            if self._last_label in self._labels:
                return self._last_label
            return None

    def mark_selected_widget(self, widget_holder: WidgetHolder):
        """Force color of the label that is selected for being picked."""
        widget_holder.clear_forced_widgets()

        if self.selected_label is None:
            return

        try:
            widget = widget_holder.on_label(self.selected_label)
        except ValueError:
            return
        widget.forced = True