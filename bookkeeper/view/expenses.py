"""
Модуль отображения расходов.
"""

from datetime import date
from typing import Tuple
from PySide6.QtWidgets import (
    QLabel, QWidget, QHeaderView,
    QGridLayout, QLineEdit, QDateEdit, QDoubleSpinBox
)
from PySide6.QtCore import QDate
from ..view.widgets import (FrameTableViewWithControls, DeleteTableContent, CategoryDropdown,
                                     Table, EditWindows, AddUpdateTableContent)
from ..models.expense import Expense

HEADERS = ["Дата", "Сумма", "Категория", "Комментарий"]

width = 400
height = 200


class ExpenseView(FrameTableViewWithControls):
    """Отображение расходов."""
    expenses: list[list[str]]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        header_resize_modes = [
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.Stretch
        ]

        self.table = Table(HEADERS, header_resize_modes, self)
        self.set_layout('Расходы')

        self.add_content = AddUpdateContent()
        self.update_content = AddUpdateContent()
        self.delete_content = DeleteTableContent()

        self.edit_windows = EditWindows(
            'расхода',
            self.add_content,
            self.update_content,
            self.delete_content
        )

        self.edit_windows.add.setFixedSize(width, height)
        self.edit_windows.update.setFixedSize(width, height)
        self.edit_windows.delete.setFixedSize(width, height)

    def set_up(self, expenses: list[list[str]], categories: list[list[str]]) -> None:
        """Устанавливает данные для виджета"""
        self.expenses = expenses
        if expenses is not None:
            self.table.set_data(expenses)
        if categories is not None:
            self.update_content.category_dropdown.set_data(categories)
            self.add_content.category_dropdown.set_data(categories)

    def on_add_button_clicked(self) -> None:
        """Обработка нажатия кнопки добавления"""
        self.edit_windows.add.show()

    def on_update_button_clicked(self) -> None:
        """Обработка нажатия кнопки обновления"""
        row_id = self.table.currentRow()
        if row_id < 0:
            return

        self.update_content.set_row(row_id, self.expenses[self.table.currentRow()])
        self.edit_windows.update.show()

    def on_delete_button_clicked(self) -> None:
        """Обработка нажатия кнопки удаления"""
        row_id = self.table.currentRow()
        if row_id < 0:
            return

        self.delete_content.set_row_id(self.table.currentRow())
        self.edit_windows.delete.show()


class AddUpdateContent(AddUpdateTableContent):
    """Контент добавления/обновления для окна редактирования расходов"""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)

        layout.addWidget(QLabel('Дата'), 0, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.date_edit, 0, 1)

        layout.addWidget(QLabel('Сумма'), 1, 0)
        self.amount_edit = QDoubleSpinBox()
        self.amount_edit.setMinimum(0)
        self.amount_edit.setMaximum(100000)
        layout.addWidget(self.amount_edit, 1, 1)

        layout.addWidget(QLabel('Категория'), 2, 0)
        self.category_dropdown = CategoryDropdown()
        layout.addWidget(self.category_dropdown, 2, 1)

        layout.addWidget(QLabel('Комментарий'), 3, 0)
        self.comment_edit = QLineEdit()
        self.comment_edit.setMaxLength(20)
        layout.addWidget(self.comment_edit, 3, 1)

        self.setLayout(layout)

    def get_amount(self) -> int:
        """Возвращает сумму расхода"""
        return int(self.amount_edit.value())

    def get_selected_category_id(self) -> int:
        """Возвращает pk категрии"""
        idx = self.category_dropdown.currentIndex()
        if idx == -1:
            idx = 0
        return int(self.category_dropdown.itemData(idx))

    def get_comment(self) -> str:
        """Возвращает комментарий"""
        return self.comment_edit.text()

    def get_date(self) -> date:
        """Возвращает дату"""
        (year, month, day) = self.date_edit.date().getDate()

        return date(year, month, day)

    def get_expense_add(self) -> Expense:
        """Возвращает расход для добавления"""
        return Expense(
            amount=self.get_amount(),
            category=self.get_selected_category_id(),
            comment=self.get_comment(),
            expense_date=self.get_date(),
        )

    def get_expense_update(self) -> Tuple[int, Expense]:
        """Возвращает номер строки и расход для обновления"""
        return self.row_id, self.get_expense_add()

    def set_row(self, row_id: int, row: list[str]) -> None:
        """Устанавливает данные для контента добавления/обновления"""
        self.row_id = row_id
        self.date_edit.setDate(QDate.fromString(row[0], 'yyyy-MM-dd'))
        self.amount_edit.setValue(float(row[1]))
        self.category_dropdown.set_current_item(row[2])
        self.comment_edit.setText(row[3])
