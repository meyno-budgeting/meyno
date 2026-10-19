import typing
import uuid
from datetime import date

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from sqlalchemy.orm import Session

from meyno.controller.transaction import get_all_transactions
from meyno.database.models import Transaction


class TransactionTableModel(QAbstractTableModel):
    def __init__(self, session: Session, parent=None) -> None:
        super().__init__(parent)

        self._session = session
        self._headers = ["Date", "Payee", "Category", "Amount"]
        self._transactions: list[tuple[uuid.UUID, date, str, str, int]] = []

    @typing.override
    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self._transactions)

    @typing.override
    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0

        return len(self._headers)

    @typing.override
    def data(
        self,
        index: QModelIndex,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            transaction = self._transactions[index.row()]
            value = transaction[index.column() + 1]

            if index.column() == 3:
                return f"${value / 100:,.2f}"

            return str(value)

        return None

    @typing.override
    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ) -> str | int | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

        return section + 1

    def refresh(self) -> None:
        transactions = get_all_transactions(self._session)

        self.beginResetModel()
        self._transactions = [
            self._transaction_to_row(transaction) for transaction in transactions
        ]
        self.endResetModel()

    @staticmethod
    def _transaction_to_row(
        transaction: Transaction,
    ) -> tuple[uuid.UUID, date, str, str, int]:
        payee = transaction.payee.name if transaction.payee is not None else ""

        if transaction.transfer_other_side is not None:
            category = "Transfer"
        elif len(transaction.splits) == 1:
            split = transaction.splits[0]
            category = split.category.name if split.category is not None else ""
        else:
            category = ""

        return (
            transaction.transaction_id,
            transaction.date,
            payee,
            category,
            transaction.amount,
        )
