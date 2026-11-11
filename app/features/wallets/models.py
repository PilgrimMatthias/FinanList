from dataclasses import dataclass

@dataclass
class WalletSummary:
    left_each_month: float
    savings_rate:float

@dataclass
class PlanSuggestion:
    income: float
    expenses: float
    months_counted: int