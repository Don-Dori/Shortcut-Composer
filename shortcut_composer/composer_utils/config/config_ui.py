# SPDX-FileCopyrightText: © 2022 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import abstractmethod
from typing import Any, List, Union, Final, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QSplitter,
    QComboBox,
    QSpinBox,
    QWidget,
    QLabel)

from ..config import FieldBase


class ConfigBasedWidget:
    def __init__(
        self,
        config_field: FieldBase,
        parent: Optional[QWidget] = None,
        pretty_name: Optional[str] = None,
    ) -> None:
        self._parent = parent
        self.config_field: Final[FieldBase] = config_field
        self.pretty_name = self._init_pretty_name(pretty_name)
        self.widget: QWidget

    @abstractmethod
    def read(self): ...

    @abstractmethod
    def set(self, value): ...

    def reset(self):
        self.set(self.config_field.read())

    def save(self):
        self.config_field.write(self.read())

    def _init_pretty_name(self, pretty_name: Optional[str]) -> str:
        if pretty_name is not None:
            return pretty_name
        return self.config_field.name


class ConfigSpinBox(ConfigBasedWidget):
    def __init__(
        self,
        config_field: Union[FieldBase[int], FieldBase[float]],
        parent: Optional[QWidget] = None,
        pretty_name: Optional[str] = None,
        step: float = 1,
        max_value: float = 100,
    ) -> None:
        super().__init__(config_field, parent, pretty_name)
        self._step = step
        self._max_value = max_value
        self._spin_box = self._init_spin_box()
        self.widget: Final[Union[QSpinBox, QDoubleSpinBox]] = self._spin_box
        self.reset()

    def read(self):
        return self._spin_box.value()

    def set(self, value):
        self._spin_box.setValue(value)

    def _init_spin_box(self):
        spin_box = (QSpinBox() if self.config_field.type is int
                    else QDoubleSpinBox())
        spin_box.setMinimumWidth(90)
        spin_box.setObjectName(self.config_field.name)
        spin_box.setMinimum(0)
        spin_box.setSingleStep(self._step)  # type: ignore
        spin_box.setMaximum(self._max_value)  # type: ignore
        return spin_box


class ConfigComboBox(ConfigBasedWidget):
    def __init__(
        self,
        config_field: FieldBase[str],
        parent: Optional[QWidget] = None,
        pretty_name: Optional[str] = None,
        allowed_values: List[Any] = [],
    ) -> None:
        super().__init__(config_field, parent, pretty_name)
        self._allowed_values = allowed_values
        self._combo_box = self._init_combo_box()
        self.widget: Final[QComboBox] = self._combo_box
        self.reset()

    def _init_combo_box(self) -> QComboBox:
        combo_box = QComboBox()
        combo_box.setObjectName(self.config_field.name)
        return combo_box

    def reset(self):
        self._combo_box.clear()
        self._combo_box.addItems(self._allowed_values)
        self.set(self.config_field.read())

    def read(self):
        return self._combo_box.currentText()

    def set(self, value):
        return self._combo_box.setCurrentText(value)


class ConfigFormWidget(QWidget):
    """Dialog zone consisting of spin boxes."""

    def __init__(self, elements: List[Union[ConfigBasedWidget, str]]) -> None:
        super().__init__()
        self._layout = QFormLayout()
        self._layout.RowWrapPolicy(QFormLayout.DontWrapRows)
        self._layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self._layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._layout.setLabelAlignment(Qt.AlignRight)
        self.setLayout(self._layout)

        self._widgets: List[ConfigBasedWidget] = []
        for element in elements:
            if isinstance(element, str):
                self._add_label(element)
            elif isinstance(element, ConfigBasedWidget):
                self._add_row(element)
            else:
                raise TypeError("Unsupported arguments.")

    def _add_row(self, element: ConfigBasedWidget) -> None:
        self._widgets.append(element)
        self._layout.addRow(f"{element.pretty_name}:", element.widget)

    def _add_label(self, text: str):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        self._layout.addRow(QSplitter(Qt.Horizontal))
        self._layout.addRow(label)

    def refresh(self) -> None:
        """Read values from krita config and apply them to stored boxes."""
        for element in self._widgets:
            element.reset()

    def apply(self) -> None:
        """Write values from stored spin boxes to krita config file."""
        for element in self._widgets:
            element.save()
