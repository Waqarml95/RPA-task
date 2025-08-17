"""Part 4: Fund Transfer workflow."""

from pathlib import Path
from typing import Dict

import pandas as pd
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.transfer_page import TransferPage
from utils.config_loader import settings
from utils.excel_writer import ExcelWriter
from utils.logging_utils import exception_logger, execution_logger


class TransferWorkflow:
    """Workflow for Part 4: Fund Transfer Operation."""

    def __init__(self, page: Page):
        """Initialize transfer workflow."""
        self.page = page
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.transfer_page = TransferPage(page)

    def ensure_logged_in(self) -> None:
        """Ensure user is logged in."""
        if "/login.jsp" in self.page.url or "Sign Off" not in self.page.content():
            self.login_page.navigate_to_login()
            self.login_page.login(
                settings.credentials.valid.username,
                settings.credentials.valid.password,
            )
            self.page.wait_for_url("**/bank/main.jsp", timeout=5000)

    def execute_fund_transfer(self) -> Dict[str, any]:
        """
        Execute fund transfer (Task 4.1).

        Returns:
            Transfer confirmation details
        """
        try:
            execution_logger.log_test_start("fund_transfer", "part4")

            # Ensure logged in
            self.ensure_logged_in()

            # Navigate to transfer page
            self.dashboard_page.navigate_to_menu("transfer_funds")
            self.page.wait_for_timeout(2000)

            # Get transfer details from settings
            from_account = settings.transfer.from_account
            to_account = settings.transfer.to_account
            amount = settings.transfer.amount

            # Execute transfer
            confirmation = self.transfer_page.execute_transfer(
                from_account,
                to_account,
                amount
            )

            execution_logger.log_validation(
                "transfer_executed",
                f"Transfer ${amount} from {from_account} to {to_account}",
                f"Status: {confirmation.get('status', 'unknown')}",
                confirmation.get("status") == "success",
            )

            execution_logger.log_test_end("fund_transfer", "part4", "passed", 0)

            return confirmation

        except Exception as e:
            execution_logger.log_test_end("fund_transfer", "part4", "failed", 0, str(e))
            exception_logger.log_exception(e, "fund_transfer")

            # Take screenshot on failure
            screenshot_path = self.transfer_page.screenshot("transfer_failed")

            return {
                "status": "failed",
                "message": str(e),
                "screenshot": screenshot_path,
                "from_account": settings.transfer.from_account,
                "to_account": settings.transfer.to_account,
                "amount": settings.transfer.amount,
            }

    def run_all(self, excel_writer: ExcelWriter) -> Dict[str, any]:
        """
        Run all Part 4 tasks.

        Args:
            excel_writer: Excel writer instance

        Returns:
            Results dictionary
        """
        results = {
            "transfer_confirmation": None,
            "success": False,
        }

        try:
            # Task 4.1: Execute fund transfer
            confirmation = self.execute_fund_transfer()
            results["transfer_confirmation"] = confirmation

            # Create DataFrame for Excel
            confirmation_df = pd.DataFrame([{
                "Status": confirmation.get("status", "unknown"),
                "From Account": confirmation.get("from_account", ""),
                "To Account": confirmation.get("to_account", ""),
                "Amount": confirmation.get("amount", ""),
                "Date": confirmation.get("date", ""),
                "Confirmation Number": confirmation.get("confirmation_number", ""),
                "Message": confirmation.get("message", ""),
            }])

            # Write to Excel
            excel_writer.write_df(confirmation_df, "Transfer_Confirmation")

            # Embed screenshot if available
            if confirmation.get("screenshot"):
                screenshot_path = Path(confirmation["screenshot"])
                if screenshot_path.exists():
                    # Add some empty rows first
                    empty_df = pd.DataFrame({"": ["", "", "", ""]})
                    excel_writer.append_df(empty_df, "Transfer_Confirmation")

                    # Embed the screenshot
                    excel_writer.embed_image(
                        screenshot_path,
                        "Transfer_Confirmation",
                        cell="A8",  # Position below the data
                        width=800,
                        height=600
                    )

                    execution_logger.log_action(
                        "embed_screenshot",
                        "Transfer_Confirmation",
                        path=str(screenshot_path)
                    )

            results["success"] = confirmation.get("status") == "success"

        except Exception as e:
            execution_logger.logger.error(f"Part 4 failed: {e}")
            exception_logger.log_exception(e, "part4_workflow")

        return results
