from dataclasses import dataclass, field
from typing import Optional

from ..core.enums import OperationType, RecurrenceInterval, Currency


@dataclass
class User:
    """Represents application user"""

    name: str
    id: Optional[int] = None
    created_at: Optional[str] = None

    # Column order must match from_row() index mapping
    COLUMNS = "id, name, created_at"

    @classmethod
    def from_row(cls, row: tuple) -> "User":
        return cls(
            id=row[0],
            name=row[1],
            created_at=row[2],
        )


@dataclass
class UserProfile:
    """Represents informations about user.

    Mostly information about income and spendings.
    """

    user_id: int
    id: Optional[int] = None
    gross_salary_monthly: float = field(default=0)
    net_salary_monthly: float = field(default=0)
    estimated_expenses_monthly: float = field(default=0)

    # Column order must match from_row() index mapping
    COLUMNS = "id, user_id, gross_salary_monthly, net_salary_monthly, estimated_expenses_monthly"

    @classmethod
    def from_row(cls, row: tuple) -> "UserProfile":
        return cls(
            id=row[0],
            user_id=row[1],
            gross_salary_monthly=row[2],
            net_salary_monthly=row[3],
            estimated_expenses_monthly=row[4],
        )


@dataclass
class Wallet:
    """Represents a single wallet for specific purpose."""

    user_id: int
    name: str = ""
    currency: Currency = field(default=Currency.PLN)
    initial_balance: float = field(default=0)
    id: Optional[int] = None
    created_at: Optional[str] = None

    # Column order must match from_row() index mapping
    COLUMNS = "id, user_id, name, currency, initial_balance, created_at"

    @classmethod
    def from_row(cls, row: tuple) -> "Wallet":
        return cls(
            id=row[0],
            user_id=row[1],
            name=row[2],
            currency=Currency(row[3]) if row[3] else None,
            initial_balance=row[4],
            created_at=row[5],
        )


@dataclass
class Category:
    """Represents financial category for transaction

    Main categories: parent_id is None, operation_type is None.
    Subcategories: parent_id points to main, operation_type is required.
    """

    wallet_id: int
    parent_id: Optional[int] = None
    name: str = ""
    operation_type: Optional[OperationType] = None
    color: str = field(default="#0085FC")
    is_protected: bool = field(default=0)
    id: Optional[int] = None

    # Column order must match from_row() index mapping
    COLUMNS = "id, wallet_id, parent_id, name, operation_type, color, is_protected"

    @classmethod
    def from_row(cls, row: tuple) -> "Category":
        return cls(
            id=row[0],
            wallet_id=row[1],
            parent_id=row[2],
            name=row[3],
            operation_type=OperationType(row[4]) if row[4] else None,
            color=row[5],
            is_protected=row[6],
        )


@dataclass
class Transaction:
    """Represents a single financial operation within wallet."""

    wallet_id: int
    category_id: int
    recurring_id: Optional[int] = None
    title: str = ""
    description: str = ""
    date: Optional[str] = None
    operation_type: Optional[OperationType] = None
    merchant: Optional[str] = None
    amount: float = field(default=0)
    id: Optional[int] = None
    created_at: Optional[str] = None

    # Column order must match from_row() index mapping
    COLUMNS = "id, wallet_id, category_id, title, description, date, operation_type, amount, merchant, recurring_id, created_at"

    @classmethod
    def from_row(cls, row: tuple) -> "Transaction":
        return cls(
            id=row[0],
            wallet_id=row[1],
            category_id=row[2],
            title=row[3],
            description=row[4],
            date=row[5],
            operation_type=OperationType(row[6]) if row[6] else None,
            amount=row[7],
            merchant=row[8],
            recurring_id=row[9],
            created_at=row[10],
        )


@dataclass
class RecurringTransaction:
    """Represents a recurring financial operation within wallet."""

    wallet_id: int
    category_id: int
    title: str = ""
    description: str = ""
    operation_type: Optional[OperationType] = None
    merchant: Optional[str] = None
    amount: float = field(default=0)
    recurrence_interval: RecurrenceInterval = field(default=RecurrenceInterval.MONTHLY)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    next_due_date: Optional[str] = None
    is_active: bool = field(default=True)
    id: Optional[int] = None
    created_at: Optional[str] = None

    # Column order must match from_row() index mapping
    COLUMNS = "id, wallet_id, category_id, title, description, operation_type, amount, merchant, recurrence_interval, start_date, end_date, next_due_date, is_active, created_at"

    @classmethod
    def from_row(cls, row: tuple) -> "RecurringTransaction":
        return cls(
            id=row[0],
            wallet_id=row[1],
            category_id=row[2],
            title=row[3],
            description=row[4],
            operation_type=OperationType(row[5]) if row[5] else None,
            amount=row[6],
            merchant=row[7],
            recurrence_interval=RecurrenceInterval(row[8]) if row[8] else None,
            start_date=row[9],
            end_date=row[10],
            next_due_date=row[11],
            is_active=row[12],
            created_at=row[13],
        )
