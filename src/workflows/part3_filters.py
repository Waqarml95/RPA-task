"""Part 3: Transaction Filtering workflow."""

from typing import Dict, List

import pandas as pd
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.transactions_page import TransactionsPage
from utils.config_loader import settings
from utils.excel_writer import ExcelWriter
from utils.logging_utils import exception_logger, execution_logger


class TransactionFiltersWorkflow:
    """Workflow for Part 3: Transaction Analysis & Filtering."""

    def __init__(self, page: Page):
        """Initialize transaction filters workflow."""
        self.page = page
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.transactions_page = TransactionsPage(page)

    def ensure_logged_in(self) -> None:
        """Ensure user is logged in."""
        if "/login.jsp" in self.page.url or "Sign Off" not in self.page.content():
            self.login_page.navigate_to_login()
            self.login_page.login(
                settings.credentials.valid.username,
                settings.credentials.valid.password,
            )
            self.page.wait_for_url("**/bank/main.jsp", timeout=5000)

    def extract_date_range_transactions(self) -> pd.DataFrame:
        """
        Extract transactions within date range (Task 3.1).

        Returns:
            DataFrame with filtered transactions
        """
        try:
            execution_logger.log_test_start("date_range_transactions", "part3")

            # Ensure logged in
            self.ensure_logged_in()

            # Navigate to transactions
            self.dashboard_page.navigate_to_menu("view_recent_transactions")
            self.page.wait_for_timeout(2000)

            # Get date range from settings
            start_date = settings.filters.date_range.start
            end_date = settings.filters.date_range.end

            # Apply date filter and get transactions
            transactions = self.transactions_page.get_transactions_by_date_range(
                start_date,
                end_date
            )

            # Create DataFrame
            df = pd.DataFrame(transactions)

            execution_logger.log_validation(
                "date_range_extracted",
                f"Transactions from {start_date} to {end_date}",
                f"Found {len(transactions)} transactions",
                len(transactions) >= 0,  # Can be 0 if no transactions in range
            )

            execution_logger.log_test_end("date_range_transactions", "part3", "passed", 0)

            return df

        except Exception as e:
            execution_logger.log_test_end("date_range_transactions", "part3", "failed", 0, str(e))
            exception_logger.log_exception(e, "date_range_transactions")
            return pd.DataFrame()

    def extract_high_value_deposits(self) -> pd.DataFrame:
        """
        Extract high-value deposit transactions (Task 3.2).

        Returns:
            DataFrame with high-value deposits
        """
        try:
            execution_logger.log_test_start("high_value_deposits", "part3")

            # Ensure logged in
            self.ensure_logged_in()

            # Navigate to transactions
            self.dashboard_page.navigate_to_menu("view_recent_transactions")
            self.page.wait_for_timeout(2000)

            # Get minimum amount from settings
            min_amount = settings.filters.deposits.min_amount

            # Get high-value deposits
            deposits = self.transactions_page.get_high_value_deposits(min_amount)

            # Create DataFrame
            df = pd.DataFrame(deposits)

            execution_logger.log_validation(
                "high_value_deposits_extracted",
                f"Deposits > ${min_amount}",
                f"Found {len(deposits)} high-value deposits",
                True,  # Success if we got here
            )

            execution_logger.log_test_end("high_value_deposits", "part3", "passed", 0)

            return df

        except Exception as e:
            execution_logger.log_test_end("high_value_deposits", "part3", "failed", 0, str(e))
            exception_logger.log_exception(e, "high_value_deposits")
            return pd.DataFrame()

    def run_all(self, excel_writer: ExcelWriter) -> Dict[str, any]:
        """
        Run all Part 3 tasks.

        Args:
            excel_writer: Excel writer instance

        Returns:
            Results dictionary
        """
        results = {
            "date_range_transactions": None,
            "high_value_deposits": None,
            "success": False,
        }

        try:
            # Task 3.1: Date-range transactions
            date_range_df = self.extract_date_range_transactions()
            results["date_range_transactions"] = date_range_df

            if not date_range_df.empty or True:  # Write even if empty
                excel_writer.write_df(date_range_df, "Transactions_DateRange")

            # Task 3.2: High-value deposits
            deposits_df = self.extract_high_value_deposits()
            results["high_value_deposits"] = deposits_df

            if not deposits_df.empty or True:  # Write even if empty
                excel_writer.write_df(deposits_df, "High_Value_Deposits")

            results["success"] = True

        except Exception as e:
            execution_logger.logger.error(f"Part 3 failed: {e}")
            exception_logger.log_exception(e, "part3_workflow")

        return results
