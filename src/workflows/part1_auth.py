"""Part 1: Authentication workflow."""

from pathlib import Path
from typing import Dict, Tuple

from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config_loader import settings
from utils.logging_utils import exception_logger, execution_logger


class AuthenticationWorkflow:
    """Workflow for Part 1: Authentication tests."""

    def __init__(self, page: Page):
        """Initialize authentication workflow."""
        self.page = page
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)

    def test_positive_login(self) -> Tuple[bool, str]:
        """
        Test positive login scenario.

        Returns:
            Tuple of (success, dashboard_text)
        """
        try:
            execution_logger.log_test_start("positive_login", "part1")

            # Navigate to login
            self.login_page.navigate_to_login()

            # Perform login with valid credentials
            self.login_page.login(
                settings.credentials.valid.username,
                settings.credentials.valid.password,
            )

            # Wait for dashboard
            self.page.wait_for_url("**/bank/main.jsp", timeout=5000)

            # Verify dashboard
            is_on_dashboard = self.dashboard_page.is_on_dashboard()
            welcome_text = self.dashboard_page.get_welcome_text() if is_on_dashboard else ""

            execution_logger.log_validation(
                "dashboard_loaded",
                "Dashboard with welcome message",
                f"Dashboard: {is_on_dashboard}, Text: {welcome_text}",
                is_on_dashboard,
            )

            execution_logger.log_test_end("positive_login", "part1", "passed", 0)

            return is_on_dashboard, welcome_text

        except Exception as e:
            execution_logger.log_test_end("positive_login", "part1", "failed", 0, str(e))
            exception_logger.log_exception(e, "positive_login")
            raise

    def test_negative_login(self) -> Dict[str, str]:
        """
        Test negative login scenario.

        Returns:
            Dictionary with error details and screenshot path
        """
        try:
            execution_logger.log_test_start("negative_login", "part1")

            # Navigate to login
            self.login_page.navigate_to_login()

            # Perform login with invalid credentials
            self.login_page.login(
                settings.credentials.invalid.username,
                settings.credentials.invalid.password,
            )

            # Wait for error element to appear in DOM
            error_element = self.page.locator("span#_ctl0__ctl0_Content_Main_message, [id*='error'], [class*='error']")
            error_element.wait_for(state="visible", timeout=5000)

            # Capture error text from the element
            error_text = self.login_page.get_error_message()

            # Take screenshot only after error element is visible
            screenshot_path = self.login_page.screenshot("negative_login_error")

            # Verify we're still on login page
            is_still_on_login = not self.login_page.is_login_successful()

            execution_logger.log_validation(
                "login_failed",
                "Error message and stay on login",
                f"Error: {error_text}, On Login: {is_still_on_login}",
                bool(error_text) and is_still_on_login,
            )

            execution_logger.log_test_end("negative_login", "part1", "passed", 0)

            return {
                "error_text": error_text,
                "screenshot_path": screenshot_path,
                "login_failed": is_still_on_login,
            }

        except Exception as e:
            # Take failure screenshot
            screenshot_path = self.login_page.screenshot("negative_login_exception")

            execution_logger.log_test_end("negative_login", "part1", "failed", 0, str(e))
            exception_logger.log_exception(e, "negative_login", screenshot_path)

            return {
                "error_text": str(e),
                "screenshot_path": screenshot_path,
                "login_failed": False,
            }

    def run_all(self) -> Dict[str, any]:
        """
        Run all authentication tests.

        Returns:
            Results dictionary
        """
        results = {
            "positive_login": None,
            "negative_login": None,
        }

        try:
            # Test positive login
            success, dashboard_text = self.test_positive_login()
            results["positive_login"] = {
                "success": success,
                "dashboard_text": dashboard_text,
            }

            # Sign off if logged in
            if success:
                self.dashboard_page.sign_off()
                self.page.wait_for_timeout(1000)

        except Exception as e:
            results["positive_login"] = {
                "success": False,
                "error": str(e),
            }

        try:
            # Test negative login
            results["negative_login"] = self.test_negative_login()

        except Exception as e:
            results["negative_login"] = {
                "error": str(e),
            }

        return results
