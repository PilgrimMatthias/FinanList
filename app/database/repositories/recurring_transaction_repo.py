from .base_repo import BaseRepo
from ..models import RecurringTransaction

SORT_COLUMNS = {
    "next_due_date": "t.next_due_date",
    "amount": "t.amount",
    "interval": "t.recurrence_interval",
    "title": "t.title",
    "type": "t.operation_type",
    "is_active": "t.is_active",
    "category": "sub_cat.name",
}


class RecurringTransactionRepo(BaseRepo):
    """Handles CRUD for recurring transactions."""

    def create(
        self, recurring_transaction: RecurringTransaction
    ) -> RecurringTransaction:
        with self.db.transaction():
            cursor = self.db.execute(
                """
                INSERT
                    INTO
                    RECURRING_TRANSACTIONS (WALLET_ID,
                    CATEGORY_ID,
                    TITLE,
                    DESCRIPTION,
                    OPERATION_TYPE,
                    AMOUNT,
                    MERCHANT,
                    RECURRENCE_INTERVAL,
                    START_DATE,
                    END_DATE,
                    NEXT_DUE_DATE,
                    IS_ACTIVE
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    recurring_transaction.wallet_id,
                    recurring_transaction.category_id,
                    recurring_transaction.title,
                    recurring_transaction.description,
                    recurring_transaction.operation_type,
                    recurring_transaction.amount,
                    recurring_transaction.merchant,
                    recurring_transaction.recurrence_interval,
                    recurring_transaction.start_date,
                    recurring_transaction.end_date,
                    recurring_transaction.next_due_date,
                    recurring_transaction.is_active,
                ),
            )
            recurring_transaction.id = cursor.lastrowid
            return recurring_transaction

    def get_by_id(self, id: int) -> RecurringTransaction | None:
        row = self.db.execute(
            f"""
                SELECT 
                    {RecurringTransaction.COLUMNS} 
                FROM 
                    RECURRING_TRANSACTIONS 
                WHERE 
                    ID = ?""",
            (id,),
        ).fetchone()

        return RecurringTransaction.from_row(row) if row else None

    def get_by_wallet_id(self, wallet_id: int) -> list[RecurringTransaction]:
        rows = self.db.execute(
            f"""
                SELECT 
                    {RecurringTransaction.COLUMNS} 
                FROM 
                    RECURRING_TRANSACTIONS 
                WHERE 
                    WALLET_ID = ?
            """,
            (wallet_id,),
        ).fetchall()

        return [RecurringTransaction.from_row(row) for row in rows]

    def get_by_filters(
        self,
        wallet_id: int,
        category_id: int | None = None,
        operation_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        next_due_date: str | None = None,
        is_active: bool | None = None,
    ) -> list[RecurringTransaction]:
        query = f"SELECT {RecurringTransaction.COLUMNS} FROM RECURRING_TRANSACTIONS WHERE WALLET_ID = ?"
        params = [wallet_id]

        if category_id:
            query += " AND CATEGORY_ID = ?"
            params.append(category_id)
        if operation_type:
            query += " AND OPERATION_TYPE = ?"
            params.append(operation_type)
        if start_date:
            query += " AND START_DATE >= ?"
            params.append(start_date)
        if end_date:
            query += " AND END_DATE <= ?"
            params.append(end_date)
        if next_due_date:
            query += " AND NEXT_DUE_DATE >= ?"
            params.append(next_due_date)
        if is_active is not None:
            query += " AND IS_ACTIVE = ?"
            params.append(is_active)

        rows = self.db.execute(query, tuple(params)).fetchall()
        return [RecurringTransaction.from_row(row) for row in rows]

    def count_by_wallet_id(self, wallet_id: int) -> int:
        """Count recurring transactions by wallet id"""
        cursor = self.db.execute(
            f"""
            SELECT
                COUNT(*)
            FROM
                RECURRING_TRANSACTIONS
            WHERE
                WALLET_ID = ?
            """,
            (wallet_id,),
        ).fetchone()

        return cursor[0] if cursor else 0

    def update(
        self, recurring_transaction: RecurringTransaction
    ) -> RecurringTransaction:
        with self.db.transaction():
            self.db.execute(
                """
                UPDATE 
                    RECURRING_TRANSACTIONS 
                SET 
                    CATEGORY_ID = ?,
                    TITLE = ?,
                    DESCRIPTION = ?,
                    OPERATION_TYPE = ?,
                    AMOUNT = ?,
                    MERCHANT = ?,
                    RECURRENCE_INTERVAL = ?,
                    START_DATE = ?,
                    END_DATE = ?,
                    NEXT_DUE_DATE = ?,
                    IS_ACTIVE = ?
                WHERE 
                    ID = ?
                """,
                (
                    recurring_transaction.category_id,
                    recurring_transaction.title,
                    recurring_transaction.description,
                    recurring_transaction.operation_type,
                    recurring_transaction.amount,
                    recurring_transaction.merchant,
                    recurring_transaction.recurrence_interval,
                    recurring_transaction.start_date,
                    recurring_transaction.end_date,
                    recurring_transaction.next_due_date,
                    recurring_transaction.is_active,
                    recurring_transaction.id,
                ),
            )

        return self.get_by_id(id=recurring_transaction.id)

    def delete_by_id(self, id: int) -> None:
        with self.db.transaction():
            self.db.execute("DELETE FROM RECURRING_TRANSACTIONS WHERE ID = ?", (id,))

    def reassign_category(self, from_category_id: int, to_category_id: int):
        with self.db.transaction():
            self.db.execute(
                "UPDATE RECURRING_TRANSACTIONS SET CATEGORY_ID = ? WHERE CATEGORY_ID = ?",
                (to_category_id, from_category_id),
            )

    def exists_by_category(self, category_id: int) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM RECURRING_TRANSACTIONS WHERE CATEGORY_ID = ? LIMIT 1",
            (category_id,),
        ).fetchone()
        return row is not None

    def count_by_category(self, category_id: int) -> int:
        count = self.db.execute(
            "SELECT COUNT(*) FROM RECURRING_TRANSACTIONS WHERE CATEGORY_ID = ?",
            (category_id,),
        ).fetchone()
        return count[0] if count else 0
    
    def delete_many(self, ids: list[int]) -> None:
        placeholders = ",".join(["?" for _ in ids])
        with self.db.transaction():
            self.db.execute(
                f"DELETE FROM RECURRING_TRANSACTIONS WHERE ID IN ({placeholders})",
                tuple(ids),
            )

    def get_paginated(
        self,
        wallet_id: int,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "next_due_date",
        sort_order: str = "DESC",
        search: str = "",
    ) -> list[tuple]:
        """Returns recurring transactions for pagination"""
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
                T.OPERATION_TYPE,
                T.AMOUNT,
                T.MERCHANT,
                T.RECURRENCE_INTERVAL,
                T.START_DATE,
                T.END_DATE,
                T.NEXT_DUE_DATE,
                T.IS_ACTIVE,
                T.CREATED_AT,
                MAIN_CAT.NAME AS MAIN_NAME,
                MAIN_CAT.COLOR AS MAIN_COLOR,
                SUB_CAT.NAME AS SUB_MAIN,
                SUB_CAT.COLOR AS SUB_COLOR,
                WALLETS.CURRENCY AS CURRENCY
            FROM
                RECURRING_TRANSACTIONS T
            LEFT JOIN CATEGORIES SUB_CAT 
            ON
                T.CATEGORY_ID == SUB_CAT.ID
            LEFT JOIN CATEGORIES MAIN_CAT
            ON
                SUB_CAT.PARENT_ID == MAIN_CAT.ID
            LEFT JOIN WALLETS
            ON
                T.WALLET_ID == WALLETS.ID
            WHERE T.WALLET_ID = ?
                and (t.title like ?
                or t.AMOUNT like ?
                or t.RECURRENCE_INTERVAL like ?
                or t.NEXT_DUE_DATE like ?
                or t.IS_ACTIVE like ?)
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

    def get_count(self, wallet_id: int, search: str = "") -> int:
        """Get count of transactions for pagination"""
        query = """
            SELECT
                COUNT(*)
            FROM
                RECURRING_TRANSACTIONS T
            WHERE T.WALLET_ID = ?
            and (t.title like ?
                or t.AMOUNT like ?
                or t.RECURRENCE_INTERVAL like ?
                or t.NEXT_DUE_DATE like ?
                or t.IS_ACTIVE like ?)
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

    def get_due(self, wallet_id: int, today: str) -> list[tuple]:
        """Returns active recurring transactions where next_due_date has passed."""
        rows = self.db.execute(
            f"""
            SELECT
                T.ID,
                T.WALLET_ID,
                T.CATEGORY_ID,
                T.TITLE,
                T.DESCRIPTION,
                T.OPERATION_TYPE,
                T.AMOUNT,
                T.MERCHANT,
                T.RECURRENCE_INTERVAL,
                T.START_DATE,
                T.END_DATE,
                T.NEXT_DUE_DATE,
                T.IS_ACTIVE,
                T.CREATED_AT,
                MAIN_CAT.NAME AS MAIN_NAME,
                MAIN_CAT.COLOR AS MAIN_COLOR,
                SUB_CAT.NAME AS SUB_MAIN,
                SUB_CAT.COLOR AS SUB_COLOR,
                WALLETS.CURRENCY AS CURRENCY
            FROM 
                RECURRING_TRANSACTIONS T
            LEFT JOIN CATEGORIES SUB_CAT 
            ON
                T.CATEGORY_ID == SUB_CAT.ID
            LEFT JOIN CATEGORIES MAIN_CAT
            ON
                SUB_CAT.PARENT_ID == MAIN_CAT.ID
            LEFT JOIN WALLETS
            ON
                T.WALLET_ID == WALLETS.ID
            WHERE T.WALLET_ID = ?
                AND T.NEXT_DUE_DATE <= ?
                AND T.IS_ACTIVE = 1
                AND (T.END_DATE IS NULL OR T.NEXT_DUE_DATE <= T.END_DATE)
            """,
            (wallet_id, today),
        ).fetchall()
        return rows

    def get_due_count(self, wallet_id, today) -> int:
        cursor = self.db.execute(
            f"""
            SELECT
                COUNT(*)
            FROM
                RECURRING_TRANSACTIONS
            WHERE
                WALLET_ID = ?
                AND NEXT_DUE_DATE <= ?
                AND IS_ACTIVE = 1
                AND (END_DATE IS NULL OR NEXT_DUE_DATE <= END_DATE)
            """,
            (wallet_id, today),
        ).fetchone()

        return cursor[0] if cursor else 0

    def toggle_active(
        self, recurring_id: int
    ) -> RecurringTransaction:
        "Flips is_active flag"
        with self.db.transaction():
            self.db.execute(
                "UPDATE RECURRING_TRANSACTIONS SET IS_ACTIVE = NOT IS_ACTIVE WHERE ID = ?",
                (recurring_id,),
            )
        return self.get_by_id(id=recurring_id)
