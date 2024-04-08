"""
Файл для запуска приложения.
"""

import sys
from PySide6.QtWidgets import QApplication
from bookkeeper.view.main import MainWindow
from bookkeeper.presenter.presenter import Presenter
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SqliteRepository


if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = MainWindow()
    view.show()

    category_repository = SqliteRepository[Category]("bookkeeper", Category)
    expense_repository = SqliteRepository[Expense]("bookkeeper", Expense)
    budget_repository = SqliteRepository[Budget]("bookkeeper", Budget)

    window = Presenter(
        view,
        category_repository,
        expense_repository,
        budget_repository,
    )
    window.show()

    sys.exit(app.exec())
