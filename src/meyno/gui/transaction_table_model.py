import typing

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class TransactionTableModel(QAbstractTableModel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._headers = ["Date", "Payee", "Category", "Amount"]

        self._transactions = [
            ["2026-10-01", "Employer", "Income", 250000],
            ["2026-10-02", "Grocery Store", "Groceries", -8542],
            ["2026-10-03", "Electric Company", "Utilities", -12500],
        ]

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
    ):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._transactions[index.row()][index.column()]

            if index.column() == 3:
                return f"${value / 100:,.2f}"

            return value

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
