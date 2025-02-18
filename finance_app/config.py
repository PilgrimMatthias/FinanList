# Config file with all needed data for the app

# Application settings
APP_NAME = "FinanList"
VERSION = "1.0.0"
AUTHOR = "Maciej Stasiłowicz"

# Window settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

import os

# Paths to data directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
RAW_DIR = os.path.join(DATA_DIR, "raw")


# User settings file names
USER_CATEGORIES = "categories.json"
USER_TRANSACTIONS = "transactions.json"
USER_UPCOMING_OPER = "upcomings.json"

# Paths to images
LOGO_PATH = os.path.join(IMAGES_DIR, "app_logo.png")
ADD_ICON = os.path.join(IMAGES_DIR, "plus_circle.png")
DOWN_ICON = os.path.join(IMAGES_DIR, "down_icon.png")
SEARCH_ICON_BLACK = os.path.join(IMAGES_DIR, "search_black.png")
SEARCH_ICON_WHITE = os.path.join(IMAGES_DIR, "search_white.png")
ASCENDING_ICON = os.path.join(IMAGES_DIR, "ascending-sort.png")
DESCENDING_ICON = os.path.join(IMAGES_DIR, "descending-sort.png")
FILTER_ICON = os.path.join(IMAGES_DIR, "filter.png")

# Export extensions
EXPORT_EXT = ["csv", "xlsx"]

# Export file name
EXPORT_FILE_NAME = "Transactions_Export_"

# Sections in app
SECTION_LIST = {"Home": 0, "Analysis": 2, "History": 3, "Upcoming": 4, "Categories": 1}

# Plot colors
COLORS = {"Expense": "#66b8ff", "Income": "#33e65f", "Sum": "#66b8ff"}


CURRENCIES = {
    "AFN": "Afghani",
    "DZD": "Algerian Dinar",
    "ARS": "Argentine Peso",
    "AMD": "Armenian Dram",
    "AWG": "Aruban Guilder",
    "AUD": "Australian Dollar",
    "AZN": "Azerbaijanian Manat",
    "BSD": "Bahamian Dollar",
    "BHD": "Bahraini Dinar",
    "THB": "Baht",
    "PAB": "Balboa",
    "BBD": "Barbados Dollar",
    "BYR": "Belarussian Ruble",
    "BZD": "Belize Dollar",
    "BMD": "Bermudian Dollar",
    "VEF": "Bolivar Fuerte",
    "BOB": "Boliviano",
    "BRL": "Brazilian Real",
    "BND": "Brunei Dollar",
    "BGN": "Bulgarian Lev",
    "BIF": "Burundi Franc",
    "CAD": "Canadian Dollar",
    "CVE": "Cape Verde Escudo",
    "KYD": "Cayman Islands Dollar",
    "GHS": "Cedi",
    "CLP": "Chilean Peso",
    "COP": "Colombian Peso",
    "KMF": "Comoro Franc",
    "CDF": "Congolese Franc",
    "BAM": "Convertible Mark",
    "NIO": "Cordoba Oro",
    "CRC": "Costa Rican Colon",
    "HRK": "Croatian Kuna",
    "CUP": "Cuban Peso",
    "CZK": "Czech Koruna",
    "GMD": "Dalasi",
    "DKK": "Danish Krone",
    "MKD": "Denar",
    "DJF": "Djibouti Franc",
    "STD": "Dobra",
    "DOP": "Dominican Peso",
    "VND": "Dong",
    "XCD": "East Caribbean Dollar",
    "EGP": "Egyptian Pound",
    "SVC": "El Salvador Colon",
    "ETB": "Ethiopian Birr",
    "EUR": "Euro",
    "FKP": "Falkland Islands Pound",
    "FJD": "Fiji Dollar",
    "HUF": "Forint",
    "GIP": "Gibraltar Pound",
    "XAU": "Gold",
    "HTG": "Gourde",
    "PYG": "Guarani",
    "GNF": "Guinea Franc",
    "GYD": "Guyana Dollar",
    "HKD": "Hong Kong Dollar",
    "UAH": "Hryvnia",
    "ISK": "Iceland Krona",
    "INR": "Indian Rupee",
    "IRR": "Iranian Rial",
    "IQD": "Iraqi Dinar",
    "JMD": "Jamaican Dollar",
    "JOD": "Jordanian Dinar",
    "KES": "Kenyan Shilling",
    "PGK": "Kina",
    "LAK": "Kip",
    "KWD": "Kuwaiti Dinar",
    "MWK": "Kwacha",
    "AOA": "Kwanza",
    "MMK": "Kyat",
    "GEL": "Lari",
    "LVL": "Latvian Lats",
    "LBP": "Lebanese Pound",
    "ALL": "Lek",
    "HNL": "Lempira",
    "SLL": "Leone",
    "RON": "Leu",
    "LRD": "Liberian Dollar",
    "LYD": "Libyan Dinar",
    "SZL": "Lilangeni",
    "LTL": "Lithuanian Litas",
    "LSL": "Loti",
    "MGA": "Malagasy Ariary",
    "MYR": "Malaysian Ringgit",
    "MUR": "Mauritius Rupee",
    "MZN": "Metical",
    "MXN": "Mexican Peso",
    "MDL": "Moldovan Leu",
    "MAD": "Moroccan Dirham",
    "BOV": "Mvdol",
    "NGN": "Naira",
    "ERN": "Nakfa",
    "NAD": "Namibia Dollar",
    "NPR": "Nepalese Rupee",
    "ANG": "Netherlands Antillean Guilder",
    "ILS": "New Israeli Sheqel",
    "TMT": "New Manat",
    "TWD": "New Taiwan Dollar",
    "NZD": "New Zealand Dollar",
    "BTN": "Ngultrum",
    "KPW": "North Korean Won",
    "NOK": "Norwegian Krone",
    "PEN": "Nuevo Sol",
    "MRO": "Ouguiya",
    "PKR": "Pakistan Rupee",
    "XPD": "Palladium",
    "MOP": "Pataca",
    "TOP": "Pa’anga",
    "CUC": "Peso Convertible",
    "UYU": "Peso Uruguayo",
    "PHP": "Philippine Peso",
    "XPT": "Platinum",
    "GBP": "Pound Sterling",
    "BWP": "Pula",
    "QAR": "Qatari Rial",
    "GTQ": "Quetzal",
    "ZAR": "Rand",
    "OMR": "Rial Omani",
    "KHR": "Riel",
    "MVR": "Rufiyaa",
    "IDR": "Rupiah",
    "RUB": "Russian Ruble",
    "RWF": "Rwanda Franc",
    "SHP": "Saint Helena Pound",
    "SAR": "Saudi Riyal",
    "RSD": "Serbian Dinar",
    "SCR": "Seychelles Rupee",
    "XAG": "Silver",
    "SGD": "Singapore Dollar",
    "SBD": "Solomon Islands Dollar",
    "KGS": "Som",
    "SOS": "Somali Shilling",
    "TJS": "Somoni",
    "ZAR": "South African Rand",
    "LKR": "Sri Lanka Rupee",
    "XSU": "Sucre",
    "SDG": "Sudanese Pound",
    "SRD": "Surinam Dollar",
    "SEK": "Swedish Krona",
    "CHF": "Swiss Franc",
    "SYP": "Syrian Pound",
    "BDT": "Taka",
    "WST": "Tala",
    "TZS": "Tanzanian Shilling",
    "KZT": "Tenge",
    "TTD": "Trinidad and Tobago Dollar",
    "MNT": "Tugrik",
    "TND": "Tunisian Dinar",
    "TRY": "Turkish Lira",
    "AED": "UAE Dirham",
    "USD": "US Dollar",
    "UGX": "Uganda Shilling",
    "COU": "Unidad de Valor Real",
    "CLF": "Unidades de fomento",
    "UYI": "Uruguay Peso en Unidades Indexadas (URUIURUI)",
    "UZS": "Uzbekistan Sum",
    "VUV": "Vatu",
    "KRW": "Won",
    "YER": "Yemeni Rial",
    "JPY": "Yen",
    "CNY": "Yuan Renminbi",
    "ZMK": "Zambian Kwacha",
    "ZWL": "Zimbabwe Dollar",
    "PLN": "Polish Zloty",
}


# Recent operations headers
RECENT_OPERATIONS_HEADERS = [
    "Transaction\nname",
    "Date",
    "Shop/\nPerson",
    "Type of\noperation",
    "Category",
    "Amount",
]

# Planned operations headers
PLANNED_OPERATIONS_HEADERS = [
    "Transaction\nname",
    "Date",
    "Type of\noperation",
    "Amount",
]


CATEGORIES_HEADERS = [
    "Main category",
    "Subcategory",
    "Default operation type",
    "Name",
]

TRANSACTION_TYPES = ["Expense", "Income", "Upcoming"]

ANALYSIS_TYPES = ["Categorical", "Aggregate", "Prognosis"]

CHART_TOOLTIPS = {
    "Categorical": None,
    "Aggregate": None,
    "Prognosis": "The projected account balance is the balance\nafter you receive your salary\nand pay all expenses and projected payments.",
}

# Categorical analysis table headers
CATEGORICAL_HEADERS = [
    "Year-Month",
    "Sub-Category 1",
    "Summary",
]

# Aggregate analysis table headers
AGGREGATE_HEADERS = [
    "Year-Month",
    "Summary revenue",
    "Summary spendings",
    "Difference",
    "Savings %",
]

# Prognosis analysis table headers
PROGNOSIS_HEADERS = [
    "Year-Month",
    "Account balance",
    "Average revenue",
    "Average spendings",
    "Planned expenses",
]

# Sample categories created on login
SAMPLE_CATEGORIES = {
    "0": {
        "1_Main Category": "Home",
        "2_Subcategory": "Food",
        "3_Default Operation Type": "Expense",
        "Name": "Home - Food",
    },
    "1": {
        "1_Main Category": "Home",
        "2_Subcategory": "Rent",
        "3_Default Operation Type": "Expense",
        "Name": "Home - Rent",
    },
    "2": {
        "1_Main Category": "Home",
        "2_Subcategory": "Other",
        "3_Default Operation Type": "Expense",
        "Name": "Home - Other",
    },
    "3": {
        "1_Main Category": "Private",
        "2_Subcategory": "Salary",
        "3_Default Operation Type": "Income",
        "Name": "Private - Salary",
    },
    "4": {
        "1_Main Category": "Private",
        "2_Subcategory": "Vacations",
        "3_Default Operation Type": "Expense",
        "Name": "Private - Vacations",
    },
    "5": {
        "1_Main Category": "Private",
        "2_Subcategory": "Other",
        "3_Default Operation Type": "Expense",
        "Name": "Private - Other",
    },
}

WELCOME_MSG = '<h3>Welcome to FinanList!🎉</h3>\n<p>Take control of your finances with ease—track expenses, manage income, analyze cash flow, and plan ahead.</p><p>✨To get you started, we’ve created some sample categories, which you can find by clicking the<i>"Categories" button on the sidebar</i>. Feel free to customize them to fit your needs!.</p><p>➡️Start by adding your first transaction using "Add Transaction" button!🚀</p>'
