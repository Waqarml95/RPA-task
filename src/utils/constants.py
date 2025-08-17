"""Application-wide constants following PEP 8 standards."""

# Transaction field names
TRANSACTION_FIELDS = ["Date", "Transaction Type", "Description", "Amount"]

# Account field names  
ACCOUNT_FIELDS = ["Account Number", "Account Type", "Balance", "Status"]

# API field mappings
API_ACCOUNT_FIELDS = {
    "account_id": "Account ID",
    "account_number": "Account Number", 
    "account_type": "Account Type",
    "balance": "Balance",
    "available_balance": "Available Balance",
    "status": "Status",
    "currency": "Currency"
}

API_TRANSACTION_FIELDS = {
    "transaction_id": "Transaction ID",
    "account_id": "Account ID",
    "date": "Date",
    "amount": "Amount",
    "transaction_type": "Type",
    "description": "Description",
    "balance_after": "Balance After",
    "status": "Status"
}

# Selectors
LOGIN_SELECTORS = {
    "form": "form#login",
    "username": "#uid",
    "password": "#passw",
    "submit": "input[name='btnSubmit']",
    "error": "span#_ctl0__ctl0_Content_Main_message"
}

DASHBOARD_SELECTORS = {
    "welcome": "h1",
    "accounts_table": "table#accounts",
    "menu_prefix": "a[id='MenuHyperLink"
}

TRANSFER_SELECTORS = {
    "from_account": "select#fromAccount",
    "to_account": "select#toAccount",
    "amount": "input#transferAmount",
    "submit": "input[type='submit'][value='Transfer']",
    "confirmation": "span#_ctl0__ctl0_Content_Main_postResp"
}

# Error messages
ERROR_MESSAGES = {
    "login_failed": "Login Failed: We're sorry, but this username or password was not found",
    "transfer_failed": "Transfer failed",
    "insufficient_funds": "Insufficient funds",
    "invalid_account": "Invalid account"
}

# Date formats
DATE_FORMATS = {
    "mdy": "%m/%d/%Y",
    "dmy": "%d/%m/%Y", 
    "iso": "%Y-%m-%d",  # Standard ISO format used by the website
    "ymd": "%Y-%m-%d",
    "api": "%Y-%m-%d"
}

# Timeout values (milliseconds)
TIMEOUTS = {
    "short": 2000,
    "medium": 5000,
    "long": 10000,
    "navigation": 30000
}

# Human delay ranges (milliseconds)
HUMAN_DELAYS = {
    "click": (200, 800),
    "typing": (50, 120),
    "form_field": (300, 1000),
    "navigation": (1000, 2500),
    "thinking": (800, 1500),
    "verification": (1500, 3000),
    "reading": (600, 1200)
}

# File paths
OUTPUT_PATHS = {
    "excel": "output/AltoroMutual_Automation.xlsx",
    "screenshots": "output/screenshots",
    "logs": "output/logs",
    "artifacts": "output/artifacts"
}

# Excel sheet names
EXCEL_SHEETS = {
    "authentication": "Part1_Authentication",
    "user_accounts": "User_Accounts",
    "date_range": "Transactions_DateRange",
    "high_deposits": "High_Value_Deposits",
    "transfer": "Transfer_Confirmation",
    "cards": "Available_Cards",
    "api_accounts": "API_Accounts",
    "api_transactions": "API_Transactions",
    "api_filtered": "API_Transactions_DateFiltered",
    "discrepancies": "Discrepancies"
}

# Test data
TEST_CREDENTIALS = {
    "valid": {
        "username": "admin",
        "password": "admin"
    },
    "invalid": {
        "username": "admin", 
        "password": "wrongpassword"
    },
    "api": {
        "username": "jsmith",
        "password": "demo1234"
    }
}

# Transfer details
TRANSFER_CONFIG = {
    "from_account": "800000 Checking",
    "to_account": "800000 Corporate",
    "amount": "100000.00"
}

# Filter configurations
FILTER_CONFIG = {
    "date_range": {
        "start": "01/03/2025",
        "end": "03/08/2025"
    },
    "api_dates": {
        "start": "01/01/2025",
        "end": "31/03/2025"
    },
    "min_deposit": 100.0
}