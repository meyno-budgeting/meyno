import sys
import typing

from PySide6.QtWidgets import QApplication, QMainWindow

from meyno.database.connection import SessionLocal
from meyno.gui.main_window_ui import Ui_main_window
from meyno.gui.transaction_table_model import TransactionTableModel


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.session = SessionLocal()

        self.transaction_model = TransactionTableModel(self.session, self)
        self.transactionTableView.setModel(self.transaction_model)
        self.transaction_model.refresh()

    @typing.override
    def closeEvent(self, event) -> None:
        self.session.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
