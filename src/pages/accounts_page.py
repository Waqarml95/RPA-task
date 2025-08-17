"""Accounts page object."""

from typing import Dict, List

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logging_utils import execution_logger


class AccountsPage(BasePage):
    """Accounts page object for AltoroMutual."""

    def __init__(self, page: Page):
        """Initialize accounts page."""
        super().__init__(page)

        # Selectors
        self.account_summary_table = "table#accounts"
        self.account_details_table = "table#transactions"
        self.balance_info = "td.Balance"
        self.account_links = "table#accounts tbody a"
        self.go_button = "input#btnGetAccount"
        self.account_dropdown = "select#listAccounts"
        self.account_info_form = "form#Form1"

    def get_account_summary(self) -> List[Dict[str, str]]:
        """
        Get account summary from accounts page.

        Returns:
            List of account dictionaries with details
        """
        # Wait for accounts table
        self.wait_for_selector(self.account_summary_table)

        # Extract account data
        accounts = []
        rows = self.page.locator(f"{self.account_summary_table} tbody tr").all()

        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 3:
                # Extract account link and details
                account_link = row.locator("a").first
                account_number = account_link.text_content() if account_link else ""

                account_data = {
                    "Account Number": account_number.strip(),
                    "Account Type": cells[1].text_content().strip() if len(cells) > 1 else "",
                    "Balance": cells[2].text_content().strip() if len(cells) > 2 else "",
                    "Status": "Active"  # Default status
                }

                if account_data["Account Number"]:
                    accounts.append(account_data)

        execution_logger.log_action("extract_accounts", "account_summary", count=len(accounts))
        return accounts

    def navigate_to_account_details(self, account_number: str) -> None:
        """
        Navigate to specific account details.

        Args:
            account_number: Account number to view
        """
        # Method 1: Try clicking the account link directly
        try:
            # Human-like pause to scan account list
            self.human_delay(800, 1500)

            account_link = self.page.locator(f"a:has-text('{account_number}')")
            if account_link.count() > 0:
                # Pause before clicking specific account
                self.click_delay()
                account_link.first.click()
                self.wait_for_load()

                # Wait for account details to load
                self.human_delay(1200, 2000)

                execution_logger.log_action("navigate_account", account_number, method="link")
                return
        except:
            pass

        # Method 2: Use dropdown if available
        try:
            if self.is_visible(self.account_dropdown, timeout=2000):
                self.select_option(self.account_dropdown, account_number)
                self.click(self.go_button)
                self.wait_for_load()
                execution_logger.log_action("navigate_account", account_number, method="dropdown")
                return
        except:
            pass

        # Method 3: Navigate via URL if pattern is known
        self.navigate(f"/bank/account.jsp?id={account_number}")
        execution_logger.log_action("navigate_account", account_number, method="url")

    def get_account_history(self, account_number: str) -> List[Dict[str, str]]:
        """
        Get transaction history for specific account.

        Args:
            account_number: Account number

        Returns:
            List of transaction dictionaries
        """
        # Navigate to account if not already there
        if account_number not in self.page.url and account_number not in self.page.content():
            self.navigate_to_account_details(account_number)

        # Wait for transactions table
        transactions = []

        # Try to find transaction table
        if self.is_visible(self.account_details_table, timeout=3000):
            rows = self.page.locator(f"{self.account_details_table} tbody tr").all()

            for row in rows:
                cells = row.locator("td").all()
                if len(cells) >= 3:
                    transaction = {
                        "Date": cells[0].text_content().strip() if cells else "",
                        "Transaction Type": cells[1].text_content().strip() if len(cells) > 1 else "",
                        "Description": cells[2].text_content().strip() if len(cells) > 2 else "",
                        "Amount": cells[3].text_content().strip() if len(cells) > 3 else "",
                    }

                    # Only add if we have meaningful data
                    if transaction["Date"] and transaction["Date"] != "Date":
                        transactions.append(transaction)

        execution_logger.log_action(
            "extract_history",
            account_number,
            transactions=len(transactions)
        )
        return transactions

    def get_all_accounts_with_history(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all accounts and their transaction histories.

        Returns:
            Dictionary mapping account numbers to their histories
        """
        # First get account summary
        accounts = self.get_account_summary()
        all_histories = {}

        for account in accounts:
            account_number = account["Account Number"]
            if account_number:
                # Get history for this account
                history = self.get_account_history(account_number)
                all_histories[account_number] = history

                # Navigate back to accounts page for next account
                self.navigate("/bank/account.jsp")
                self.wait_for_load()

        return all_histories

    def get_account_balance(self, account_number: str) -> str:
        """
        Get current balance for account.

        Args:
            account_number: Account number

        Returns:
            Balance as string
        """
        # Navigate to account
        self.navigate_to_account_details(account_number)

        # Look for balance information
        if self.is_visible(self.balance_info):
            return self.get_text(self.balance_info)

        # Alternative: Look in table
        balance_cells = self.page.locator("td:has-text('$')").all()
        if balance_cells:
            return balance_cells[0].text_content().strip()

        return "0.00"
