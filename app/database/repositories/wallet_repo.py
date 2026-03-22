from .base_repo import BaseRepo
from ..models import Wallet


class WalletRepo(BaseRepo):

    def create(self, wallet: Wallet) -> Wallet:
        with self.db.transaction():
            cursor = self.db.execute(
                "INSERT INTO WALLETS (USER_ID, NAME, CURRENCY, INITIAL_BALANCE) VALUES (?, ?, ?, ?)",
                (wallet.user_id, wallet.name, wallet.currency, wallet.initial_balance),
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
            self.db.execute(
                """
                UPDATE 
                    WALLETS 
                SET 
                    NAME = ?,
                    CURRENCY = ?,
                    INITIAL_BALANCE = ?
                WHERE 
                    ID = ?
                """,
                (wallet.name, wallet.currency, wallet.initial_balance, wallet.id),
            )

        return self.get_by_user_id(user_id=wallet.user_id)
