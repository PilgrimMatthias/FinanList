import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Analysis:
    """
    Analysis module create data to plot for the user based on their choosen analysis type.

    """

    def __init__(
        self,
        analysis_type,
        date_from,
        date_to,
        transactions,
        upcomings=None,
        category=None,
        account_balance=None,
        average_revenue=None,
        average_spendings=None,
    ):

        # User inputs
        self.analysis_type = analysis_type
        self.date_from = date_from
        self.date_to = date_to
        self.transactions = transactions
        self.upcomings = upcomings
        self.category = category
        self.account_balance = account_balance
        self.average_revenue = average_revenue
        self.average_spendings = average_spendings

        # Data
        self.result_table = None

        match self.analysis_type:
            case "Categorical":
                self.result_table = self.calculate_categorical()
            case "Aggregate":
                self.result_table = self.calculate_aggregate()
            case "Prognosis":
                self.result_table = self.calculate_prognosis()

        print(self.result_table)

    def calculate_categorical(self):
        """
        Make calculation for categorical analysis type.
        Categorical analysis is analysis based on choosen user category.

        Returns:
            pandas.DataFrame: Table with results
        """
        transactions = self.transactions.copy()
        transactions = transactions[
            (transactions["2_date"] >= self.date_from)
            & (transactions["2_date"] <= self.date_to)
        ]

        transactions["Year-month"] = transactions["2_date"].apply(
            lambda x: x.strftime("%Y-%m")
        )
        transactions = transactions[
            (transactions["4_type"] == "Expense")
            & (transactions["5_category"].str.contains(self.category))
        ].drop("4_type", axis=1)

        transactions = (
            transactions.groupby(["Year-month", "5_category"])["6_amount"]
            .sum()
            .reset_index(drop=False)
        )

        transactions["5_category"] = transactions["5_category"].apply(
            lambda x: x.split(" - ")[-1]
        )

        result_table = pd.pivot_table(
            transactions,
            values="6_amount",
            index="Year-month",
            columns="5_category",
            aggfunc="sum",
            fill_value=0,
        ).reset_index(drop=False)
        result_table["Summary"] = result_table.iloc[:, 1:].sum(axis=1)

        return result_table.round(2)

    def calculate_aggregate(self):
        """
        Make calculation for aggregate analysis type.
        Aggregate analysis if summary monthly cashflow analysis.

        Returns:
            pandas.DataFrame: Table with results
        """
        transactions = self.transactions.copy()
        transactions = transactions[
            (transactions["2_date"] >= self.date_from)
            & (transactions["2_date"] <= self.date_to)
        ]

        transactions["Year-month"] = transactions["2_date"].apply(
            lambda x: x.strftime("%Y-%m")
        )

        transactions = (
            transactions.groupby(["Year-month", "4_type"])["6_amount"]
            .sum()
            .reset_index(drop=False)
        )

        expense = transactions[transactions["4_type"] == "Expense"].drop(
            "4_type", axis=1
        )
        expense.columns = ["Year-month", "Expense"]
        income = transactions[transactions["4_type"] == "Income"].drop("4_type", axis=1)
        income.columns = ["Year-month", "Income"]

        result_table = transactions["Year-month"].drop_duplicates()
        result_table = pd.merge(
            left=result_table, right=income, how="left", on="Year-month"
        )
        result_table = pd.merge(
            left=result_table, right=expense, how="left", on="Year-month"
        ).fillna(0)

        result_table["Difference"] = result_table["Income"] - result_table["Expense"]

        result_table["Savings %"] = (
            1 - result_table["Expense"] / result_table["Income"]
        ) * 100
        result_table["Savings %"] = np.where(
            result_table["Savings %"] < 0, 0, result_table["Savings %"]
        )

        return result_table.round(2)

    def calculate_prognosis(self):
        """
        Make calculation for prognosis analysis type.
        Prognosis is analysis to see futurte account balance based on constant data such as salary, mean expeneses and planned operations.

        Returns:
            pandas.DataFrame: Table with results
        """
        last_month_spendings = self.average_spendings
        last_month_revenue = self.average_revenue
        transactions = self.transactions
        last_transaction_date = datetime.today()

        if not transactions.empty:

            last_transaction_date = transactions["2_date"].iloc[-1]

            # Calculate current account balance
            transactions = transactions.copy()
            transactions = transactions[
                (transactions["2_date"] >= last_transaction_date + relativedelta(day=1))
                & (transactions["2_date"] <= last_transaction_date)
                & (transactions["4_type"] == "Expense")
            ]

            transactions["Year-month"] = transactions["2_date"].apply(
                lambda x: x.strftime("%Y-%m")
            )

            # Calculate average spendings - last month summary spendings
            last_month_spendings = (
                transactions.groupby(["Year-month"])["6_amount"].sum().values[0]
            )
            last_month_spendings = self.average_spendings - last_month_spendings
            last_month_spendings = (
                0 if last_month_spendings <= 0 else last_month_spendings
            )

            # Set value for first revenue value in result table (first month)
            last_month_revenue = self.transactions.copy()
            last_month_revenue = last_month_revenue[
                (
                    last_month_revenue["2_date"]
                    >= last_transaction_date + relativedelta(day=1)
                )
                & (
                    last_month_revenue["2_date"]
                    <= last_transaction_date + relativedelta(day=31)
                )
                & (last_month_revenue["4_type"] == "Income")
            ]
            last_month_revenue = (
                0 if not last_month_revenue.empty else self.average_revenue
            )

        month_list = []
        current = last_transaction_date
        while current <= self.date_to:
            month_list.append(current.strftime("%Y-%m"))
            current += relativedelta(months=1)

        result_table = pd.DataFrame(
            {
                "Year-month": month_list,
                "Account balance": [self.account_balance] * len(month_list),
                "Average revenue": [self.average_revenue] * len(month_list),
                "Average spendings": [self.average_spendings] * len(month_list),
            }
        )

        planned_expenses = None
        if not self.upcomings is None:
            planned_expenses = self.upcomings.copy()
            planned_expenses = planned_expenses[
                (
                    planned_expenses["2_date"]
                    >= last_transaction_date + relativedelta(day=1)
                )
                & (planned_expenses["2_date"] <= self.date_to)
            ]

            planned_expenses["Year-month"] = planned_expenses["2_date"].apply(
                lambda x: x.strftime("%Y-%m")
            )

            planned_expenses = (
                planned_expenses.groupby(["Year-month"])["6_amount"]
                .sum()
                .reset_index(drop=False)
            )
            planned_expenses.columns = ["Year-month", "Planned expenses"]
        else:
            planned_expenses = pd.DataFrame(
                {
                    "Year-month": month_list,
                    "Planned expenses": [np.nan] * len(month_list),
                }
            )

        result_table = pd.merge(
            left=result_table, right=planned_expenses, how="left", on="Year-month"
        ).fillna(0)

        for index in result_table.index:
            temp_revenue = 0
            temp_spendings = 0
            temp_balance = 0
            # First month values
            if index == 0:
                temp_revenue = last_month_revenue
                temp_spendings = last_month_spendings
                temp_balance = result_table.iloc[index, 1]

                result_table.at[index, "Average spendings"] = temp_spendings

            # Rest month values
            else:
                temp_revenue = self.average_revenue
                temp_spendings = self.average_spendings
                temp_balance = result_table.iloc[index - 1, 1]

            # Get planned expenses
            temp_planned_expenses = result_table.iloc[index, -1]

            # Calculate balance
            temp_balance = temp_balance + (
                temp_revenue - temp_spendings - temp_planned_expenses
            )

            # Add value to result
            result_table.at[index, "Account balance"] = temp_balance

        result_table = result_table[
            result_table["Year-month"].apply(lambda x: self.get_date(x))
            >= self.date_from
        ].reset_index(drop=True)
        return result_table

    def get_date(self, year_month):
        """
        Get date based on provided string in format YYYY-MM.

        Args:
            year_month (string): Year and month

        Returns:
            Datetime: first day of month
        """
        date = datetime.strptime(f"{year_month}-01", "%Y-%m-%d") + relativedelta(day=31)

        return date

    def get_data_to_table(self):
        """
        Get data to be displayed on table

        Returns:
            pandas.DataFrame: data to table
        """
        data_to_table = self.result_table.copy()
        for col in data_to_table.columns:
            data_to_table[col] = data_to_table[col].apply(
                lambda x: str(x).replace(".", ",")
            )
        return data_to_table

    def get_data_to_plot(self):
        """
        Get data to be displayed on plot

        Returns:
            pandas.DataFrame: data to plot
        """
        data_to_plot = self.result_table.copy()

        data_to_plot.index = data_to_plot["Year-month"]
        data_to_plot = data_to_plot.drop("Year-month", axis=1)

        match self.analysis_type:
            case "Categorical":
                data_to_plot = data_to_plot.iloc[:, :-1]
                data_to_plot = pd.DataFrame(data_to_plot.sum(axis=1), columns=["Sum"])
            case "Aggregate":
                data_to_plot = pd.DataFrame(data_to_plot.iloc[:, :2])
            case "Prognosis":
                data_to_plot = pd.DataFrame(data_to_plot["Account balance"]).iloc[:14]

        return data_to_plot

    def get_display_plot_data(self):
        """
        Same as get_data_to_plot, but with just last 3 months.
        Used only for main section plot

        Returns:
            pandas.DataFrame: data to plot with only last 3 months
        """
        data_to_plot = self.result_table.copy()

        data_to_plot.index = data_to_plot["Year-month"]
        data_to_plot = data_to_plot.drop("Year-month", axis=1)

        data_to_plot = data_to_plot.iloc[:4]

        return pd.DataFrame(data_to_plot.sum(axis=1), columns=["Sum"])
