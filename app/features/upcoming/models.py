from app.database.models import RecurringTransaction, Transaction
from dataclasses import dataclass, field
from app.core.enums import Currency


@dataclass
class RecurringTransactionDisplay:
    """
    Represents recurring ransaction used for display in upcomings table.
    Beside basic recurring transaction model this class has also information abaout categories names and colors and also if it is overdue and days until due.
    """

    recurring: RecurringTransaction
    main_category_name: str
    main_category_color: str
    sub_category_name: str
    sub_category_color: str
    days_until_due: int  # negative if overdue
    currency: Currency 
    occurrences: list[Transaction] = field(default_factory=list)

    @property
    def is_overdue(self) -> bool:
        return self.days_until_due < 0