from .base_repo import BaseRepo
from ..models import UserProfile


class UserProfileRepo(BaseRepo):
    """Handles CRUD for users."""

    def create(self, profile: UserProfile) -> UserProfile:
        with self.db.transaction():
            return self.create_no_commit(profile=profile)
        
    def create_no_commit(self, profile: UserProfile) -> UserProfile:
        cursor = self.db.execute(
            """
            INSERT
                INTO
                USER_PROFILE (
                USER_ID,
                CURRENCY)
            VALUES (?,?)
            """,
            (
                profile.user_id,
                profile.currency,
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


    def update_no_commit(self, user_profile:UserProfile) -> UserProfile:
        self.db.execute(
            """
            UPDATE
                USER_PROFILE
            SET
                CURRENCY = ?
            WHERE
                ID = ?
            """,
            (
                user_profile.currency,
                user_profile.id,
            ),
        )
