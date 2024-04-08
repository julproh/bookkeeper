"""
Модуль отображения категорий
"""

from collections import deque
from PySide6.QtWidgets import (
    QLabel, QWidget, QGridLayout, QLineEdit, QHBoxLayout
)
from PySide6.QtGui import QStandardItem
from bookkeeper.view.widgets import (CategoryDropdown, Tree, FrameTreeViewWithControls, EditWindows)
from ..models.category import Category

width = 300
height = 150


class CategoryView(FrameTreeViewWithControls):
    """Отображение категорий."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.tree = CategoryTree(self)
        self.set_layout('Категории')
        self.add_content = AddContent()
        self.update_content = UpdateContent()
        self.delete_content = DeleteContent()
        self.edit_windows = EditWindows(
            'категории',
            self.add_content,
            self.update_content,
            self.delete_content
        )

        self.edit_windows.add.setFixedSize(width, height)
        self.edit_windows.update.setFixedSize(width, height)
        self.edit_windows.delete.setFixedSize(width, height)

    def set_up(self, categories: list[list[str]]) -> None:
        """Устанавливает данные для виджета"""
        self.tree.set_data(categories[1:])
        self.add_content.dropdown.set_data(categories)
        self.update_content.dropdown_to_edit.set_data(categories)
        self.update_content.parent_dropdown.set_data(categories)
        self.delete_content.dropdown.set_data(categories)

    def on_add_button_clicked(self) -> None:
        """Обработка нажатия кнопки добавления"""
        self.edit_windows.add.show()

    def on_update_button_clicked(self) -> None:
        """Обработка нажатия кнопки обновления"""
        self.edit_windows.update.show()

    def on_delete_button_clicked(self) -> None:
        """Обработка нажатия кнопки удаления"""
        self.edit_windows.delete.show()


class CategoryTree(Tree):
    """Иерархическая таблица категорий."""
    def set_data(self, data: list[list[str]]) -> None:
        """Устанавливает данные для древовидной структуры."""
        self.item_model.setRowCount(0)
        root = self.item_model.invisibleRootItem()
        seen: dict[str, QStandardItem] = {}
        nodes = deque(data)
        print("data "+str(data))
        print("nodes" + str(nodes))
        print(nodes)
        while nodes:
            node = nodes.popleft()
            if node[2] == '0':
                parent = root
            else:
                pid = node[2]
                if pid not in seen:
                    nodes.append(node)
                    continue

                parent = seen[pid]

            pk = node[0]
            parent.appendRow([
                 QStandardItem(node[1]),
            ])
            seen[pk] = parent.child(parent.rowCount() - 1)

        self.expandAll()


class AddContent(QWidget):
    """Контент добавления для окна редактирования."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.addWidget(QLabel('Имя'), 0, 0)
        self.name_line_edit = QLineEdit()
        layout.addWidget(self.name_line_edit, 0, 1)
        layout.addWidget(QLabel('Родитель'), 1, 0)
        self.dropdown = CategoryDropdown()
        layout.addWidget(self.dropdown, 1, 1)
        self.setLayout(layout)

    def get_name(self) -> str:
        """Возвращает имя категории."""
        return self.name_line_edit.text()

    def get_category_add(self) -> Category:
        """Возвращает категорию для добавления."""
        return Category(
            name=self.get_name(),
            parent=self.dropdown.get_selected_category_id(),
        )


class UpdateContent(QWidget):
    """Контент обновления для окна редактирования."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.addWidget(QLabel('К обновлению'), 0, 0)
        self.dropdown_to_edit = CategoryDropdown()
        layout.addWidget(self.dropdown_to_edit, 0, 1)
        # Name
        layout.addWidget(QLabel('Новое имя'), 1, 0)
        self.name_line_edit = QLineEdit()
        layout.addWidget(self.name_line_edit, 1, 1)
        # Parent
        layout.addWidget(QLabel('Новый родитель'), 2, 0)
        self.parent_dropdown = CategoryDropdown()
        layout.addWidget(self.parent_dropdown, 2, 1)

        self.setLayout(layout)

    def get_name(self) -> str:
        """Возвращает имя категории."""
        return self.name_line_edit.text()

    def get_category_update(self) -> Category:
        """Отдает категорию для добавления."""
        return Category(
            name=self.get_name(),
            parent=self.parent_dropdown.get_selected_category_id(),
            pk=self.dropdown_to_edit.get_selected_category_id(),
        )


class DeleteContent(QWidget):
    """Контент удаления для окна редактирования"""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()

        self.dropdown = CategoryDropdown()
        layout.addWidget(self.dropdown)

        self.setLayout(layout)

    def get_category_pk_to_delete(self) -> int:
        """Возвращает pk категории для удаления"""
        return self.dropdown.get_selected_category_id()
