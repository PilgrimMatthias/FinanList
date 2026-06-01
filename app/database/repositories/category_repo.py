from .base_repo import BaseRepo
from ..models import Category


class CategoryRepo(BaseRepo):
    """Handles CRUD for hierarchical categories.

    Main categories have parent_id = NULL.
    Deleting a main category cascades to all subcategories.
    """

    def create(self, category: Category) -> Category:
        with self.db.transaction():
            cursor = self.db.execute(
                """
                INSERT
                    INTO
                    CATEGORIES (WALLET_ID,
                    PARENT_ID,
                    NAME,
                    OPERATION_TYPE,
                    COLOR,
                    IS_PROTECTED)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    category.wallet_id,
                    category.parent_id,
                    category.name,
                    category.operation_type,
                    category.color,
                    category.is_protected,
                ),
            )
            category.id = cursor.lastrowid
            return category

    def get_by_id(self, id: int) -> Category | None:
        row = self.db.execute(
            f"""
            SELECT
                {Category.COLUMNS}
            FROM
                CATEGORIES
            WHERE
                ID = ?
            """,
            (id,),
        ).fetchone()
        return Category.from_row(row) if row else None

    def get_by_wallet_id(self, wallet_id) -> list[Category]:
        rows = self.db.execute(
            f"""
            SELECT
                {Category.COLUMNS}
            FROM
                CATEGORIES
            WHERE
                WALLET_ID = ?
            """,
            (wallet_id,),
        ).fetchall()
        return [Category.from_row(row) for row in rows]

    def count_by_wallet_id(self, wallet_id: int) -> int:
        """Count categories by wallet id"""
        cursor = self.db.execute(
            f"""
            SELECT
                COUNT(*)
            FROM
                CATEGORIES
            WHERE
                WALLET_ID = ?
            """,
            (wallet_id,),
        ).fetchone()

        return cursor[0] if cursor else 0

    def get_main_categories(self, wallet_id: int) -> list[Category]:
        rows = self.db.execute(
            f"""
            SELECT
                {Category.COLUMNS}
            FROM
                CATEGORIES
            WHERE
                WALLET_ID = ?
                AND PARENT_ID IS NULL
            """,
            (wallet_id,),
        ).fetchall()
        return [Category.from_row(row) for row in rows]

    def get_subcategories(self, parent_id: int) -> list[Category]:
        rows = self.db.execute(
            f"""
            SELECT
                {Category.COLUMNS}
            FROM
                CATEGORIES
            WHERE
                PARENT_ID = ?
            """,
            (parent_id,),
        ).fetchall()
        return [Category.from_row(row) for row in rows]

    def get_by_name_and_wallet(self, name: str, wallet_id: int) -> Category | None:
        row = self.db.execute(
            f"""
            SELECT
                {Category.COLUMNS}
            FROM
                CATEGORIES
            WHERE
                NAME = ?
                AND WALLET_ID = ?
            """,
            (name, wallet_id),
        ).fetchone()

        return Category.from_row(row) if row else None

    def update(self, category: Category) -> Category:
        with self.db.transaction():
            self.db.execute(
                """
                UPDATE
                    CATEGORIES
                SET
                    PARENT_ID = ?,
                    NAME = ?,
                    OPERATION_TYPE = ?,
                    COLOR = ?,
                    IS_PROTECTED = ?
                WHERE
                    ID = ?
                """,
                (
                    category.parent_id,
                    category.name,
                    category.operation_type,
                    category.color,
                    category.is_protected,
                    category.id,
                ),
            )

        return self.get_by_id(id=category.id)

    def delete_by_id(self, id: int) -> None:
        with self.db.transaction():
            self.db.execute("DELETE FROM CATEGORIES WHERE ID = ?", (id,))
