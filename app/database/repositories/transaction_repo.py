from .base_repo import BaseRepo
from ..models import Transaction

SORT_COLUMNS = {
    "date": "t.date",
    "amount": "t.amount",
    "merchant": "t.merchant",
    "title": "t.title",
    "type": "t.operation_type",
    "category": "sub_cat.name",
}


class TransactionRepo(BaseRepo):
    """Handles CRUD for financial operations."""

    def create(self, transaction: Transaction) -> Transaction:
        with self.db.transaction():
            cursor = self.db.execute(
                """
                INSERT
                    INTO
                    TRANSACTIONS (WALLET_ID,
                    CATEGORY_ID,
                    TITLE,
                    DESCRIPTION,
                    DATE,
                    OPERATION_TYPE,
                    AMOUNT,
                    MERCHANT,
                    RECURRING_ID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    transaction.wallet_id,
                    transaction.category_id,
                    transaction.title,
                    transaction.description,
                    transaction.date,
                    transaction.operation_type,
                    transaction.amount,
                    transaction.merchant,
                    transaction.recurring_id,
                ),
            )
            transaction.id = cursor.lastrowid
            return transaction

    def get_by_id(self, id: int) -> Transaction | None:
        row = self.db.execute(
            f"""
                SELECT 
                    {Transaction.COLUMNS} 
                FROM 
                    TRANSACTIONS 
                WHERE 
                    ID = ?""",
            (id,),
        ).fetchone()

        return Transaction.from_row(row) if row else None

    def get_by_wallet_id(self, wallet_id: int) -> list[Transaction]:
        rows = self.db.execute(
            f"""
                SELECT 
                    {Transaction.COLUMNS} 
                FROM 
                    TRANSACTIONS 
                WHERE 
                    WALLET_ID = ?
            """,
            (wallet_id,),
        ).fetchall()

        return [Transaction.from_row(row) for row in rows]

    def get_by_filters(
        self,
        wallet_id: int,
        category_id: int | None = None,
        operation_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[Transaction]:
        query = f"SELECT {Transaction.COLUMNS} FROM TRANSACTIONS WHERE WALLET_ID = ?"
        params = [wallet_id]

        if category_id:
            query += " AND CATEGORY_ID = ?"
            params.append(category_id)
        if operation_type:
            query += " AND OPERATION_TYPE = ?"
            params.append(operation_type)
        if date_from:
            query += " AND DATE >= ?"
            params.append(date_from)
        if date_to:
            query += " AND DATE <= ?"
            params.append(date_to)

        rows = self.db.execute(query, tuple(params)).fetchall()
        return [Transaction.from_row(row) for row in rows]

    def update(self, transaction: Transaction) -> Transaction:
        with self.db.transaction():
            self.db.execute(
                """
                UPDATE 
                    TRANSACTIONS 
                SET 
                    CATEGORY_ID = ?,
                    TITLE = ?,
                    DESCRIPTION = ?,
                    DATE = ?,
                    OPERATION_TYPE = ?,
                    AMOUNT = ?,
                    MERCHANT = ?,
                    RECURRING_ID = ?
                WHERE 
                    ID = ?
                """,
                (
                    transaction.category_id,
                    transaction.title,
                    transaction.description,
                    transaction.date,
                    transaction.operation_type,
                    transaction.amount,
                    transaction.merchant,
                    transaction.recurring_id,
                    transaction.id,
                ),
            )

        return self.get_by_id(id=transaction.id)

    def delete_by_id(self, id: int) -> None:
        with self.db.transaction():
            self.db.execute("DELETE FROM TRANSACTIONS WHERE ID = ?", (id,))

    def reassign_category(self, from_category_id: int, to_category_id: int):
        with self.db.transaction():
            self.db.execute(
                "UPDATE TRANSACTIONS SET CATEGORY_ID = ? WHERE CATEGORY_ID = ?",
                (to_category_id, from_category_id),
            )

    def exists_by_category(self, category_id: int) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM TRANSACTIONS WHERE CATEGORY_ID = ? LIMIT 1",
            (category_id,),
        ).fetchone()
        return row is not None

    def count_by_category(self, category_id: int) -> int:
        count = self.db.execute(
            "SELECT COUNT(*) FROM TRANSACTIONS WHERE CATEGORY_ID = ?",
            (category_id,),
        ).fetchone()
        return count[0] if count else 0

    def get_paginated(
        self,
        wallet_id: int,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "date",
        sort_order: str = "DESC",
        search: str = "",
    ) -> list[tuple]:
        # TODO: implement search option
        offset = (page - 1) * page_size
        sort_column = SORT_COLUMNS[sort_by]

        if sort_by == "amount":
            # Sort by signed amount so expenses and income order intuitively
            sort_column = """
            CASE 
                WHEN T.OPERATION_TYPE = 'Income' then T.AMOUNT
                ELSE -T.AMOUNT
            END 
            """

        sort_direction = "DESC" if sort_order.upper() == "DESC" else "ASC"

        query = f"""
            SELECT
                T.ID,
                T.WALLET_ID,
                T.CATEGORY_ID,
                T.TITLE,
                T.DESCRIPTION,
                T.DATE,
                T.OPERATION_TYPE,
                T.AMOUNT,
                T.MERCHANT,
                T.RECURRING_ID,
                T.CREATED_AT,
                MAIN_CAT.NAME AS MAIN_NAME,
                MAIN_CAT.COLOR AS MAIN_COLOR,
                SUB_CAT.NAME AS SUB_MAIN,
                SUB_CAT.COLOR AS SUB_COLOR
            FROM
                TRANSACTIONS T
            LEFT JOIN CATEGORIES SUB_CAT 
            ON
                T.CATEGORY_ID == SUB_CAT.ID
            LEFT JOIN CATEGORIES MAIN_CAT
            ON
                SUB_CAT.PARENT_ID == MAIN_CAT.ID
            WHERE T.WALLET_ID = ?
                and (t.title like ?
                or t.DESCRIPTION  like ?
                or t.DATE like ?
                or t.AMOUNT like ?
                or t.MERCHANT like ?)
            ORDER BY {sort_column} {sort_direction}
            LIMIT ? OFFSET ?
        """
        search_pattern = f"%{search}%"
        params = (
            wallet_id,
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
            page_size,
            offset,
        )
        rows = self.db.execute(query=query, params=params).fetchall()

        return rows

    def get_exported(self, wallet_id: int, ids: list[int]):
        placeholders = ",".join(["?" for _ in ids])

        query = f"""
            SELECT
                T.TITLE,
                WALLETS.NAME as WALLET_NAME,
                MAIN_CAT.NAME AS MAIN_CATEGORY_NAME,
                SUB_CAT.NAME AS SUB_CATEGORY_NAME,
                T.DESCRIPTION,
                T.DATE,
                T.OPERATION_TYPE,
                T.MERCHANT,
                T.AMOUNT,
                WALLETS.CURRENCY
            FROM
                TRANSACTIONS T
            LEFT JOIN WALLETS 
            ON
                T.WALLET_ID  == WALLETS.ID
            LEFT JOIN CATEGORIES SUB_CAT 
            ON
                T.CATEGORY_ID == SUB_CAT.ID
            LEFT JOIN CATEGORIES MAIN_CAT
            ON
                SUB_CAT.PARENT_ID == MAIN_CAT.ID
            WHERE
                T.WALLET_ID = ?
                AND T.ID IN ({placeholders})
        """
        params = (wallet_id, *ids)
        rows = self.db.execute(query=query, params=params).fetchall()

        return rows

    def get_count(self, wallet_id: int, search: str = "") -> int:
        query = """
            SELECT
                COUNT(*)
            FROM
                TRANSACTIONS T
            WHERE T.WALLET_ID = ?
                and (t.title like ?
                or t.DESCRIPTION  like ?
                or t.DATE like ?
                or t.AMOUNT like ?
                or t.MERCHANT like ?)
        """
        search_pattern = f"%{search}%"
        params = (
            wallet_id,
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
        )
        count = self.db.execute(query=query, params=params).fetchone()

        return count[0] if count else 0

    def delete_many(self, ids: list[int]) -> None:
        placeholders = ",".join(["?" for _ in ids])
        with self.db.transaction():
            self.db.execute(
                f"DELETE FROM TRANSACTIONS WHERE ID IN ({placeholders})",
                tuple(ids),
            )
