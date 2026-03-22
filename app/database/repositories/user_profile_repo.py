from .base_repo import BaseRepo
from ..models import UserProfile


class UserProfileRepo(BaseRepo):
    """Handles CRUD for users."""

    def create(self, profile: UserProfile) -> UserProfile:
        with self.db.transaction():
            cursor = self.db.execute(
                """
                INSERT
                    INTO
                    USER_PROFILE (USER_ID,
                    GROSS_SALARY_MONTHLY,
                    NET_SALARY_MONTHLY,
                    ESTIMATED_EXPENSES_MONTHLY)
                VALUES (?,?,?,?)
                """,
                (
                    profile.user_id,
                    profile.gross_salary_monthly,
                    profile.net_salary_monthly,
                    profile.estimated_expenses_monthly,
                ),
            )
            profile.id = cursor.lastrowid
            return profile

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        row = self.db.execute(
            f"""
            SELECT
                {UserProfile.COLUMNS}
            FROM
                USER_PROFILE
            WHERE
                USER_ID = ?;
            """,
            (user_id,),
        ).fetchone()

        return UserProfile.from_row(row) if row else None

    def get_all(self) -> list[UserProfile]:
        rows = self.db.execute(
            f"SELECT {UserProfile.COLUMNS} FROM USER_PROFILE"
        ).fetchall()

        return [UserProfile.from_row(row) for row in rows]

    def update(self, profile: UserProfile) -> UserProfile:
        with self.db.transaction():
            self.db.execute(
                """
                UPDATE 
                    USER_PROFILE 
                SET 
                    GROSS_SALARY_MONTHLY = ?,
                    NET_SALARY_MONTHLY = ?,
                    ESTIMATED_EXPENSES_MONTHLY = ?
                WHERE 
                    USER_ID = ?;
                """,
                (
                    profile.gross_salary_monthly,
                    profile.net_salary_monthly,
                    profile.estimated_expenses_monthly,
                    profile.user_id,
                ),
            )

        return self.get_by_user_id(user_id=profile.user_id)
