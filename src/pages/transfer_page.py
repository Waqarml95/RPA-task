"""Transfer page object."""

import re
from datetime import datetime
from typing import Dict, Optional

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logging_utils import execution_logger


class TransferPage(BasePage):
    """Transfer page object for AltoroMutual."""

    def __init__(self, page: Page):
        """Initialize transfer page."""
        super().__init__(page)

        # Selectors
        self.from_account_select = "select#fromAccount"
        self.to_account_select = "select#toAccount"
        self.amount_input = "input#transferAmount"
        self.transfer_button = "input[type='submit'][value='Transfer']"
        self.confirmation_message = "span#_ctl0__ctl0_Content_Main_postResp"
        self.confirmation_area = "div.content"

        # Alternative selectors
        self.alt_from_select = "select[name='fromAccount']"
        self.alt_to_select = "select[name='toAccount']"
        self.alt_amount_input = "input[name='amount']"
        self.alt_transfer_button = "button:has-text('Transfer')"

    def navigate_to_transfer(self) -> None:
        """Navigate to transfer page."""
        self.navigate("/bank/transfer.jsp")
        self.wait_for_load()
        execution_logger.log_action("navigate", "transfer_page")

    def select_from_account(self, account: str) -> None:
        """
        Select source account for transfer.

        Args:
            account: Account identifier (e.g., "800000 Checking")
        """
        try:
            # Human-like pause to read form
            self.human_delay(600, 1200)

            # Get available options first
            if self.is_visible(self.from_account_select, timeout=2000):
                select_element = self.page.locator(self.from_account_select)

                # Pause to look at dropdown
                self.click_delay()
                options = select_element.locator("option").all()

                # Find matching option
                for option in options:
                    option_text = option.text_content()
                    option_value = option.get_attribute("value")

                    # Try to match by partial text
                    if account in option_text or (option_value and account.split()[0] in option_value):
                        # Pause to consider selection
                        self.human_delay(300, 700)
                        select_element.select_option(value=option_value)
                        execution_logger.log_action("select_from_account", account)
                        return

                # If no exact match, select first available account
                if len(options) > 1:  # Skip the first "Select Account" option
                    self.human_delay(300, 700)
                    select_element.select_option(index=1)
                    execution_logger.log_action("select_from_account", "first_available")
        except Exception as e:
            execution_logger.logger.warning(f"Could not select from account: {e}")

    def select_to_account(self, account: str) -> None:
        """
        Select destination account for transfer.

        Args:
            account: Account identifier (e.g., "800000 Corporate")
        """
        try:
            # Human-like pause between form fields
            self.form_delay()

            # Get available options first
            if self.is_visible(self.to_account_select, timeout=2000):
                select_element = self.page.locator(self.to_account_select)

                # Pause to look at second dropdown
                self.click_delay()
                options = select_element.locator("option").all()

                # Find matching option
                for option in options:
                    option_text = option.text_content()
                    option_value = option.get_attribute("value")

                    # Try to match by partial text or account type
                    if "corporate" in account.lower() and option_text and "corporate" in option_text.lower():
                        # Pause to consider selection
                        self.human_delay(400, 800)
                        select_element.select_option(value=option_value)
                        execution_logger.log_action("select_to_account", account)
                        return
                    elif account in option_text or (option_value and account.split()[0] in option_value):
                        self.human_delay(400, 800)
                        select_element.select_option(value=option_value)
                        execution_logger.log_action("select_to_account", account)
                        return

                # If no exact match, select second available account (different from source)
                if len(options) > 2:
                    self.human_delay(400, 800)
                    select_element.select_option(index=2)
                    execution_logger.log_action("select_to_account", "second_available")
        except Exception as e:
            execution_logger.logger.warning(f"Could not select to account: {e}")

    def enter_amount(self, amount: str) -> None:
        """
        Enter transfer amount.

        Args:
            amount: Amount to transfer (e.g., "100000.00")
        """
        # Human-like pause before entering amount (thinking)
        self.form_delay()

        # Remove any formatting from amount
        clean_amount = amount.replace("$", "").replace(",", "")

        if self.is_visible(self.amount_input, timeout=2000):
            self.fill(self.amount_input, clean_amount)
        elif self.is_visible(self.alt_amount_input, timeout=2000):
            self.fill(self.alt_amount_input, clean_amount)

        # Pause after entering amount (double-checking)
        self.human_delay(800, 1500)

        execution_logger.log_action("enter_amount", clean_amount)

    def submit_transfer(self) -> None:
        """Submit the transfer with final confirmation delay."""
        # Critical pause before final submit (human verification)
        self.human_delay(1500, 3000)

        if self.is_visible(self.transfer_button, timeout=2000):
            self.click(self.transfer_button)
        elif self.is_visible(self.alt_transfer_button, timeout=2000):
            self.click(self.alt_transfer_button)
        else:
            # Try submitting form
            self.page.keyboard.press("Enter")

        self.wait_for_load()

        # Wait for response processing (realistic server response time)
        self.human_delay(2000, 4000)

        execution_logger.log_action("submit_transfer", "transfer_form")

    def get_confirmation_details(self) -> Dict[str, str]:
        """
        Get transfer confirmation details.

        Returns:
            Dictionary with confirmation details
        """
        confirmation = {
            "status": "unknown",
            "message": "",
            "confirmation_number": "",
            "from_account": "",
            "to_account": "",
            "amount": "",
            "date": "",
        }

        # Check for confirmation message
        if self.is_visible(self.confirmation_message, timeout=3000):
            message = self.get_text(self.confirmation_message)
            confirmation["message"] = message

            # Check if transfer was successful
            if "successfully" in message.lower() or "completed" in message.lower():
                confirmation["status"] = "success"

                # Try to extract confirmation number
                conf_match = re.search(r"confirmation\s*#?\s*:?\s*(\w+)", message, re.IGNORECASE)
                if conf_match:
                    confirmation["confirmation_number"] = conf_match.group(1)
            else:
                confirmation["status"] = "failed"

        # Try to get additional details from page
        content = self.page.content()

        # Extract amounts
        amount_match = re.search(r"\$?([\d,]+\.?\d*)", content)
        if amount_match:
            confirmation["amount"] = amount_match.group(1)

        # Get current date
        confirmation["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        execution_logger.log_action("get_confirmation", "transfer", status=confirmation["status"])
        return confirmation

    def execute_transfer(self, from_account: str, to_account: str, amount: str) -> Dict[str, str]:
        """
        Execute complete transfer operation.

        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transfer amount

        Returns:
            Confirmation details dictionary
        """
        try:
            # Navigate to transfer page
            self.navigate_to_transfer()

            # Fill transfer form
            self.select_from_account(from_account)
            self.select_to_account(to_account)
            self.enter_amount(amount)

            # Submit transfer
            self.submit_transfer()

            # Get confirmation
            confirmation = self.get_confirmation_details()

            # Add input details to confirmation
            confirmation["from_account"] = from_account
            confirmation["to_account"] = to_account
            confirmation["amount"] = amount

            # Take screenshot
            screenshot_path = self.screenshot("transfer_confirmation")
            confirmation["screenshot"] = screenshot_path

            return confirmation

        except Exception as e:
            execution_logger.logger.error(f"Transfer failed: {e}")
            # Return failure confirmation
            return {
                "status": "failed",
                "message": str(e),
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "screenshot": self.screenshot("transfer_error"),
            }
