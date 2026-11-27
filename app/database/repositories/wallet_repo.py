from .base_repo import BaseRepo
from ..models import Wallet


class WalletRepo(BaseRepo):
    """Handles CRUD for wallets."""

    def create(self, wallet: Wallet) -> Wallet:
        with self.db.transaction():
            return self.create_no_commit(wallet=wallet)

    def create_no_commit(self, wallet: Wallet) -> Wallet:
        cursor = self.db.execute(
            """
            INSERT INTO WALLETS (
                USER_ID,
                NAME,
                CURRENCY,
                INITIAL_BALANCE,
                NET_SALARY_MONTHLY,
                EVERYDAY_SPENDING_MONTHLY,
                FORECAST_FLOOR
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                wallet.user_id,
                wallet.name,
                wallet.currency,
                wallet.initial_balance,
                wallet.net_salary_monthly,
                wallet.everyday_spending_monthly,
                wallet.forecast_floor,
            ),
        )
        wallet.id = cursor.lastrowid
        return wallet

    def get_by_id(self, id: int) -> Wallet | None:
        row = self.db.execute(
            f"SELECT {Wallet.COLUMNS} FROM WALLETS WHERE ID = ?",
            (id,),
        ).fetchone()
        return Wallet.from_row(row) if row else None

    def get_by_user_id(self, user_id: int) -> list[Wallet]:
        rows = self.db.execute(
            f"""
            SELECT
                {Wallet.COLUMNS}
            FROM
                WALLETS
            WHERE
                USER_ID = ?
            """,
            (user_id,),
        ).fetchall()
        return [Wallet.from_row(row) for row in rows]

    def get_all(self) -> list[Wallet]:
        rows = self.db.execute(f"SELECT {Wallet.COLUMNS} FROM WALLETS").fetchall()

        return [Wallet.from_row(row) for row in rows]

    def update(self, wallet: Wallet) -> Wallet:
        with self.db.transaction():
            self.update_no_commit(wallet=wallet)

        return self.get_by_id(id=wallet.id)

    def update_no_commit(self, wallet: Wallet) -> None:
        self.db.execute(
            """
            UPDATE
                WALLETS
            SET
                NAME = ?,
                CURRENCY = ?,
                INITIAL_BALANCE = ?,
                NET_SALARY_MONTHLY = ?,
                EVERYDAY_SPENDING_MONTHLY = ?,
                FORECAST_FLOOR = ?
            WHERE
                ID = ?
            """,
            (
                wallet.name,
                wallet.currency,
                wallet.initial_balance,
                wallet.net_salary_monthly,
                wallet.everyday_spending_monthly,
                wallet.forecast_floor,
                wallet.id,
            ),
        )

    def get_balance(self, wallet_id: int) -> float:
        """Current balance - initial balance plus every transaction to date."""
        return self.get_balance_at(wallet_id=wallet_id)

    def get_balance_at(self, wallet_id: int, as_of: str = None) -> float:
        """Balance counting only transactions strictly BEFORE as_of."""
        query = """
            SELECT
                w.INITIAL_BALANCE + COALESCE(SUM(CASE
                    WHEN t.OPERATION_TYPE <> 'Income' THEN -t.AMOUNT
                    ELSE t.AMOUNT
                END), 0) AS BALANCE
            FROM
                WALLETS w
            LEFT JOIN TRANSACTIONS t ON
                t.WALLET_ID = w.ID
                AND (? IS NULL OR t.DATE < ?)
            WHERE
                w.ID = ?
            GROUP BY
                w.ID
        """
        params = (as_of, as_of, wallet_id)
        balance = self.db.execute(query=query, params=params).fetchone()

        return balance[0] if balance and balance[0] is not None else 0.0

    def delete_by_id(self, wallet_id: int):
        with self.db.transaction():
            self.db.execute("DELETE FROM WALLETS WHERE ID = ?", (wallet_id,))
