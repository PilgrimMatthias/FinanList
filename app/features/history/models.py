from app.database.models import Transaction
from dataclasses import dataclass


@dataclass
class TransactionDisplay:
    """
    Represents transaction used for display in history table.
    Beside basic transaction model this class has also information abaout categories names and colors and also if it is recurring.
    """

    transaction: Transaction
    main_category_name: str
    main_category_color: str
    sub_category_name: str
    sub_category_color: str
    is_recurring: bool

    @classmethod
    def from_row(cls, row: tuple) -> "TransactionDisplay":
        return cls(
            transaction=row[0],
            main_category_name=row[1],
            main_category_color=row[2],
            sub_category_name=row[3],
            sub_category_color=row[4],
            is_recurring=row[5],
        )
