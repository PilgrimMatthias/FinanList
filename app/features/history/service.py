from app.core import AppState
from app.database.repositories import (
    TransactionRepo,
)
from app.database.models import Transaction
from .models import TransactionDisplay
from app.core.constants import TRANSACTIONS_EXPORT_COLUMNS
from app.core.exceptions import ValidationError
import pandas as pd
from pathlib import Path
from app.core.utils import cast_str_to_datetime


class HistoryService:
    def __init__(
        self,
        transaction_repo: TransactionRepo,
        app_state: AppState,
    ):
        self.transaction_repo = transaction_repo
        self.app_state = app_state

    def get_all_transactions_ids(self, wallet_id: int):
        """Returns all transaction ids based on wallet id"""
        return [
            transaction.id
            for transaction in self.transaction_repo.get_by_wallet_id(
                wallet_id=wallet_id
            )
        ]

    def _row_to_display(self, row: tuple) -> TransactionDisplay:
        """Returns TransactionDisplay from specified row"""
        transaction = Transaction.from_row(row)

        transaction_display = TransactionDisplay(
            transaction=transaction,
            main_category_name=row[11] or "—",
            main_category_color=row[12] or "#808080",
            sub_category_name=row[13] or "—",
            sub_category_color=row[14] or "#808080",
            is_recurring=row[9] is not None,
        )

        return transaction_display

    def get_paginated_for_display(
        self,
        wallet_id: int,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
        search: str = "",
    ) -> list[TransactionDisplay]:
        """
        Returns list of TransactionDisplay object used in view

        Args:
            wallet_id (int): wallet id
            page (int): current page
            page_size (int): size of page
            sort_by (str): sorting column
            sort_order (str): sort order
            search (str, optional): serach name in db. Defaults to "".

        Returns:
            list[TransactionDisplay]: _description_
        """
        rows = self.transaction_repo.get_paginated(
            wallet_id=wallet_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        return [self._row_to_display(row) for row in rows]

    def get_count(self, wallet_id: int, search: str = "") -> int:
        """Returns number of transactions based of specified search"""
        return self.transaction_repo.get_count(wallet_id=wallet_id, search=search)

    def export_selected(self, ids: list[int], save_path=Path | str):
        """
        Method used for exporting selected ids to the xlsx/csv file.

        Args:
            ids (list[int]): list of  transaction ids
            save_path (_type_, optional): save path specified by user. Defaults to Path | str.

        Raises:
            ValidationError: _description_
        """
        if not save_path:
            raise ValidationError("Save path not specified")

        rows_to_export = self.transaction_repo.get_exported(
            wallet_id=self.app_state.active_user_id, ids=ids
        )

        df_export = pd.DataFrame(
            data=rows_to_export, columns=TRANSACTIONS_EXPORT_COLUMNS
        )
        df_export["Date"] = df_export["Date"].apply(
            lambda x: cast_str_to_datetime(x, format="%Y-%m-%d %H:%M:%S")
        )

        # Getting choosen path and extension by user
        extension = save_path.split(".")[-1].replace(")", "")
        file_path = save_path
        if extension not in file_path:
            file_path += "." + extension

        # Data save by extension type
        match extension:
            case "csv":
                df_export.to_csv(file_path, index=False, decimal=",", sep=";")
            case "xlsx":
                df_export.to_excel(file_path, index=False)

    def delete_transactions(self, ids: list[int]):
        """Method for deleting selected transaction from database"""

        self.transaction_repo.delete_many(ids=ids)

        self.app_state.emit_transaction_change()
