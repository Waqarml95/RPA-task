"""Transactions page object."""

from typing import Dict, List, Optional

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.date_utils import detect_page_date_format, parse_date, to_page_format
from utils.logging_utils import execution_logger


class TransactionsPage(BasePage):
    """Transactions page object for AltoroMutual."""

    def __init__(self, page: Page):
        """Initialize transactions page."""
        super().__init__(page)

        # Selectors
        self.transactions_table = "table#transactions"
        self.date_from_input = "input#startDate"
        self.date_to_input = "input#endDate"
        self.amount_min_input = "input#minAmount"
        self.amount_max_input = "input#maxAmount"
        self.transaction_type_select = "select#transactionType"
        self.submit_button = "input[type='submit'][value='Submit']"
        self.go_button = "input#btnGetAccount"
        self.account_select = "select#listAccounts"

        # Alternative selectors
        self.alt_submit = "button:has-text('Submit')"
        self.alt_filter_button = "input[value='Filter']"

    def navigate_to_transactions(self) -> None:
        """Navigate to transactions page."""
        self.navigate("/bank/transaction.jsp")
        self.wait_for_load()
        execution_logger.log_action("navigate", "transactions_page")

    def apply_date_filter(self, start_date: str, end_date: str) -> None:
        """
        Apply date range filter to transactions.

        Args:
            start_date: Start date (will be converted to yyyy-mm-dd format)
            end_date: End date (will be converted to yyyy-mm-dd format)
        """
        # Convert dates to ISO format (yyyy-mm-dd) which the site expects
        # Parse the input dates
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)

        # Format as yyyy-mm-dd
        start_formatted = start_dt.strftime("%Y-%m-%d")
        end_formatted = end_dt.strftime("%Y-%m-%d")

        # Fill date inputs with correct format
        if self.is_visible(self.date_from_input, timeout=2000):
            self.fill(self.date_from_input, start_formatted)

        if self.is_visible(self.date_to_input, timeout=2000):
            self.fill(self.date_to_input, end_formatted)

        # Submit filter
        self._submit_filter()

        execution_logger.log_action(
            "apply_date_filter",
            "transactions",
            start_date=start_formatted,
            end_date=end_formatted,
            format="ISO (YYYY-MM-DD)"
        )

    def apply_amount_filter(self, min_amount: Optional[float] = None, max_amount: Optional[float] = None) -> None:
        """
        Apply amount filter to transactions.

        Args:
            min_amount: Minimum transaction amount
            max_amount: Maximum transaction amount
        """
        if min_amount is not None and self.is_visible(self.amount_min_input, timeout=2000):
            self.fill(self.amount_min_input, str(min_amount))

        if max_amount is not None and self.is_visible(self.amount_max_input, timeout=2000):
            self.fill(self.amount_max_input, str(max_amount))

        self._submit_filter()

        execution_logger.log_action(
            "apply_amount_filter",
            "transactions",
            min_amount=min_amount,
            max_amount=max_amount
        )

    def filter_by_type(self, transaction_type: str) -> None:
        """
        Filter transactions by type.

        Args:
            transaction_type: Type of transaction (Deposit, Withdrawal, etc.)
        """
        if self.is_visible(self.transaction_type_select, timeout=2000):
            self.select_option(self.transaction_type_select, transaction_type)
            self._submit_filter()

        execution_logger.log_action("filter_by_type", transaction_type)

    def get_filtered_transactions(self) -> List[Dict[str, str]]:
        """
        Get currently displayed transactions after filtering.

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Wait for table to load
        if self.is_visible(self.transactions_table, timeout=5000):
            rows = self.page.locator(f"{self.transactions_table} tbody tr").all()

            for row in rows:
                cells = row.locator("td").all()
                if cells and len(cells) >= 3:
                    # Skip header rows
                    first_cell = cells[0].text_content().strip()
                    if first_cell and first_cell.lower() != "date":
                        transaction = {
                            "Date": first_cell,
                            "Type": cells[1].text_content().strip() if len(cells) > 1 else "",
                            "Description": cells[2].text_content().strip() if len(cells) > 2 else "",
                            "Amount": cells[3].text_content().strip() if len(cells) > 3 else "",
                        }
                        transactions.append(transaction)

        execution_logger.log_action("get_transactions", "filtered", count=len(transactions))
        return transactions

    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, str]]:
        """
        Get transactions within date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of transactions
        """
        self.navigate_to_transactions()
        self.apply_date_filter(start_date, end_date)
        return self.get_filtered_transactions()

    def get_high_value_deposits(self, min_amount: float = 100.0) -> List[Dict[str, str]]:
        """
        Get deposit transactions above specified amount.

        Args:
            min_amount: Minimum deposit amount

        Returns:
            List of high-value deposit transactions
        """
        self.navigate_to_transactions()

        # First filter by type
        self.filter_by_type("Deposit")

        # Then apply amount filter
        self.apply_amount_filter(min_amount=min_amount)

        # Get results
        all_transactions = self.get_filtered_transactions()

        # Double-check filtering (in case UI filtering isn't working properly)
        deposits = []
        for tx in all_transactions:
            # Check if it's a deposit and meets amount criteria
            if "deposit" in tx.get("Type", "").lower() or "deposit" in tx.get("Description", "").lower():
                # Parse amount
                amount_str = tx.get("Amount", "0").replace("$", "").replace(",", "")
                try:
                    amount = float(amount_str)
                    if amount >= min_amount:
                        deposits.append(tx)
                except:
                    pass

        execution_logger.log_action(
            "get_high_value_deposits",
            "filtered",
            min_amount=min_amount,
            count=len(deposits)
        )
        return deposits

    def _submit_filter(self) -> None:
        """Submit filter form."""
        # Try different submit buttons
        if self.is_visible(self.submit_button, timeout=1000):
            self.click(self.submit_button)
        elif self.is_visible(self.alt_submit, timeout=1000):
            self.click(self.alt_submit)
        elif self.is_visible(self.alt_filter_button, timeout=1000):
            self.click(self.alt_filter_button)
        elif self.is_visible(self.go_button, timeout=1000):
            self.click(self.go_button)
        else:
            # Try pressing Enter
            self.page.keyboard.press("Enter")

        self.wait_for_load()
        self.page.wait_for_timeout(1000)  # Give time for results to load
