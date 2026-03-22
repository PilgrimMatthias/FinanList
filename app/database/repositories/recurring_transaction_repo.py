from .base_repo import BaseRepo
from ..models import RecurringTransaction


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

    def get_due(self, wallet_id: int, today: str) -> list[RecurringTransaction]:
        """Returns active recurring transactions where next_due_date has passed."""
        rows = self.db.execute(
            f"""
            SELECT {RecurringTransaction.COLUMNS}
                FROM RECURRING_TRANSACTIONS
                WHERE WALLET_ID = ?
                AND NEXT_DUE_DATE <= ?
                AND IS_ACTIVE = 1
            """,
            (wallet_id, today),
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
