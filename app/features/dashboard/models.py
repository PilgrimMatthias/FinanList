from dataclasses import dataclass, field

@dataclass
class MonthSummary:
    """
    ## Represents Monthly cashflow
    
    - income - income
    - outgoing - expenses + investments + savings
    - net - income - outgoing
    - by_type - summary by type
    """
    income:float = 0.0
    outgoing:float = 0.0
    net:float = 0.0
    by_type:dict = field(default_factory=dict)


@dataclass
class CategoryTotal:
    """
    ## Represents total amount by category

    - category_id: id of category
    - name: category name
    - color: category color
    - amount: total amount spent
    - total_percentage - total percentage for category/ sum of all spendings
    """
    category_id: int | None
    name: str
    color: str
    amount:float
    total_percentage:float