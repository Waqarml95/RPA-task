"""Part 2: Account Data Extraction workflow."""

from typing import Dict, List

import pandas as pd
from playwright.sync_api import Page

from pages.accounts_page import AccountsPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config_loader import settings
from utils.excel_writer import ExcelWriter
from utils.logging_utils import exception_logger, execution_logger


class AccountsWorkflow:
    """Workflow for Part 2: Account Data Extraction."""

    def __init__(self, page: Page):
        """Initialize accounts workflow."""
        self.page = page
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.accounts_page = AccountsPage(page)

    def ensure_logged_in(self) -> None:
        """Ensure user is logged in."""
        if "/login.jsp" in self.page.url or "Sign Off" not in self.page.content():
            self.login_page.navigate_to_login()
            self.login_page.login(
                settings.credentials.valid.username,
                settings.credentials.valid.password,
            )
            self.page.wait_for_url("**/bank/main.jsp", timeout=5000)

    def extract_user_accounts(self) -> pd.DataFrame:
        """
        Extract user account information (Task 2.1).

        Returns:
            DataFrame with account information
        """
        try:
            execution_logger.log_test_start("extract_accounts", "part2")

            # Ensure logged in
            self.ensure_logged_in()

            # Extract accounts from dashboard first
            accounts = []

            # Look for account table on dashboard
            if self.page.locator("table#accounts").count() > 0:
                account_rows = self.page.locator("table#accounts tbody tr").all()

                for row in account_rows:
                    cells = row.locator("td").all()
                    if len(cells) >= 3:
                        # Get account link
                        account_link = row.locator("a").first
                        account_number = ""
                        if account_link.count() > 0:
                            account_number = account_link.text_content().strip()

                        # Get other details
                        account_data = {
                            "Account Number": account_number,
                            "Account Type": cells[1].text_content().strip() if len(cells) > 1 else "",
                            "Balance": cells[2].text_content().strip() if len(cells) > 2 else "",
                            "Status": "Active"
                        }

                        if account_data["Account Number"]:
                            accounts.append(account_data)
                            execution_logger.log_action(
                                "extract_account",
                                account_number,
                                type=account_data["Account Type"],
                                balance=account_data["Balance"]
                            )

            # If no accounts found, navigate to accounts page
            if not accounts:
                self.dashboard_page.navigate_to_menu("view_account_summary")
                self.page.wait_for_timeout(2000)

                # Try again on accounts page
                if self.page.locator("table").count() > 0:
                    tables = self.page.locator("table").all()
                    for table in tables:
                        rows = table.locator("tbody tr").all()
                        for row in rows:
                            cells = row.locator("td").all()
                            if len(cells) >= 2:
                                account_data = {
                                    "Account Number": cells[0].text_content().strip() if cells else "",
                                    "Account Type": cells[1].text_content().strip() if len(cells) > 1 else "",
                                    "Balance": cells[2].text_content().strip() if len(cells) > 2 else "",
                                    "Status": "Active"
                                }
                                if account_data["Account Number"] and account_data["Account Number"] not in ["Account", ""]:
                                    accounts.append(account_data)

            # Create DataFrame
            df = pd.DataFrame(accounts)

            execution_logger.log_validation(
                "accounts_extracted",
                "Account list",
                f"Found {len(accounts)} accounts",
                len(accounts) > 0,
            )

            execution_logger.log_test_end("extract_accounts", "part2", "passed", 0)

            return df

        except Exception as e:
            execution_logger.log_test_end("extract_accounts", "part2", "failed", 0, str(e))
            exception_logger.log_exception(e, "extract_accounts")
            return pd.DataFrame()

    def extract_account_histories(self) -> Dict[str, pd.DataFrame]:
        """
        Extract transaction history for each account (Task 2.2).

        Returns:
            Dictionary mapping account numbers to DataFrames
        """
        try:
            execution_logger.log_test_start("extract_histories", "part2")

            # Ensure logged in
            self.ensure_logged_in()

            # Get all accounts first
            accounts_df = self.extract_user_accounts()

            if accounts_df.empty:
                execution_logger.log_test_end("extract_histories", "part2", "failed", 0, "No accounts found")
                return {}

            # Extract history for each account
            all_histories = {}

            for _, account in accounts_df.iterrows():
                account_number = account.get("Account Number", "")

                if account_number:
                    try:
                        # Click on the account link to view details
                        account_link = self.page.locator(f"a:has-text('{account_number}')").first
                        if account_link.count() > 0:
                            account_link.click()
                            self.page.wait_for_load_state("networkidle")
                            self.page.wait_for_timeout(1000)

                            # Extract transaction history from the page
                            transactions = []

                            # Define transaction data structure (static)
                            TRANSACTION_FIELDS = ["Date", "Transaction Type", "Description", "Amount"]

                            # Look for transaction table
                            if self.page.locator("table#transactions").count() > 0:
                                tx_rows = self.page.locator("table#transactions tbody tr").all()

                                for row in tx_rows:
                                    cells = row.locator("td").all()
                                    if len(cells) >= 3:
                                        # Create transaction data using predefined fields
                                        tx_data = {}
                                        for idx, field in enumerate(TRANSACTION_FIELDS):
                                            tx_data[field] = (
                                                cells[idx].text_content().strip()
                                                if idx < len(cells) else ""
                                            )

                                        # Skip header rows
                                        if tx_data["Date"] and tx_data["Date"].lower() != "date":
                                            transactions.append(tx_data)

                            # Alternative: look for any table with transaction-like data
                            elif self.page.locator("table").count() > 0:
                                tables = self.page.locator("table").all()
                                for table in tables:
                                    # Skip if it's the accounts table
                                    if table.get_attribute("id") == "accounts":
                                        continue

                                    rows = table.locator("tr").all()
                                    for row in rows[1:]:  # Skip header
                                        cells = row.locator("td").all()
                                        if len(cells) >= 3:
                                            tx_data = {
                                                "Date": cells[0].text_content().strip() if cells else "",
                                                "Transaction Type": cells[1].text_content().strip() if len(cells) > 1 else "Transaction",
                                                "Description": cells[2].text_content().strip() if len(cells) > 2 else "",
                                                "Amount": cells[3].text_content().strip() if len(cells) > 3 else cells[2].text_content().strip() if len(cells) > 2 else "",
                                            }

                                            # Check if it looks like transaction data
                                            if tx_data["Date"] and ("/" in tx_data["Date"] or "-" in tx_data["Date"]):
                                                transactions.append(tx_data)

                            # Convert to DataFrame
                            if transactions:
                                df_history = pd.DataFrame(transactions)
                            else:
                                # Create empty DataFrame with expected columns
                                df_history = pd.DataFrame(columns=["Date", "Transaction Type", "Description", "Amount"])

                            all_histories[account_number] = df_history

                            execution_logger.log_action(
                                "account_history",
                                account_number,
                                transactions=len(transactions),
                            )

                            # Go back to accounts page
                            self.page.go_back()
                            self.page.wait_for_timeout(1000)

                    except Exception as e:
                        execution_logger.logger.warning(f"Failed to get history for {account_number}: {e}")
                        all_histories[account_number] = pd.DataFrame()

            execution_logger.log_validation(
                "histories_extracted",
                "All account histories",
                f"Extracted history for {len(all_histories)} accounts",
                len(all_histories) > 0,
            )

            execution_logger.log_test_end("extract_histories", "part2", "passed", 0)

            return all_histories

        except Exception as e:
            execution_logger.log_test_end("extract_histories", "part2", "failed", 0, str(e))
            exception_logger.log_exception(e, "extract_histories")
            return {}

    def run_all(self, excel_writer: ExcelWriter) -> Dict[str, any]:
        """
        Run all Part 2 tasks.

        Args:
            excel_writer: Excel writer instance

        Returns:
            Results dictionary
        """
        results = {
            "accounts": None,
            "histories": {},
            "success": False,
        }

        try:
            # Task 2.1: Extract user accounts
            accounts_df = self.extract_user_accounts()
            results["accounts"] = accounts_df

            if not accounts_df.empty:
                # Write to Excel
                excel_writer.write_df(accounts_df, "User_Accounts")

                # Task 2.2: Extract account histories
                histories = self.extract_account_histories()
                results["histories"] = histories

                # Write each history to separate sheet
                for account_number, history_df in histories.items():
                    sheet_name = f"Account_{account_number}_History"
                    # Truncate sheet name if too long
                    if len(sheet_name) > 31:
                        sheet_name = f"Acc_{account_number[:20]}_Hist"

                    excel_writer.write_df(history_df, sheet_name)

                results["success"] = True

        except Exception as e:
            execution_logger.logger.error(f"Part 2 failed: {e}")
            exception_logger.log_exception(e, "part2_workflow")

        return results
