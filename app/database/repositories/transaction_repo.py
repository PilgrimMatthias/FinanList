from .base_repo import BaseRepo
from ..models import Transaction


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
