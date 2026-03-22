from .base_repo import BaseRepo
from ..models import User


class UserRepo(BaseRepo):
    def create(self, user: User) -> User:
        with self.db.transaction():
            cursor = self.db.execute(
                "INSERT INTO users (name) VALUES (?)", (user.name,)
            )
            user.id = cursor.lastrowid
            return user

    def get_user_by_id(self, id: int) -> User | None:
        row = self.db.execute(
            f"""
            SELECT
                {User.COLUMNS}
            FROM
                USERS
            WHERE
                ID = ?
            """,
            (id,),
        ).fetchone()
        return User.from_row(row) if row else None

    def get_all(self) -> list[User]:
        rows = self.db.execute(f"SELECT {User.COLUMNS} FROM USERS").fetchall()

        return [User.from_row(row) for row in rows]

    def delete_by_id(self, id: int) -> None:
        with self.db.transaction():
            self.db.execute("DELETE FROM USERS WHERE ID = ?", (id,))
