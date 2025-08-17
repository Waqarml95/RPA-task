"""Login page object following PEP 8 standards."""

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.constants import ERROR_MESSAGES, LOGIN_SELECTORS
from utils.logging_utils import execution_logger


class LoginPage(BasePage):
    """Login page object for AltoroMutual demo banking site."""

    def __init__(self, page: Page):
        """
        Initialize login page with selectors from constants.

        Args:
            page: Playwright page object
        """
        super().__init__(page)

        # Use selectors from constants for better maintainability
        self.username_input = LOGIN_SELECTORS["username"]
        self.password_input = LOGIN_SELECTORS["password"]
        self.login_button = LOGIN_SELECTORS["submit"]
        self.error_message = LOGIN_SELECTORS["error"]
        self.login_form = LOGIN_SELECTORS["form"]

    def navigate_to_login(self) -> None:
        """Navigate to login page."""
        self.navigate("/login.jsp")
        self.wait_for_selector(self.login_form)

    def login(self, username: str, password: str) -> None:
        """
        Perform login action with humanized delays.

        Args:
            username: Username to enter
            password: Password to enter
        """
        # Fill credentials with natural flow
        self.fill(self.username_input, username)

        # Human-like pause before switching to password field
        self.human_delay(400, 900)

        self.fill(self.password_input, password)

        # Pause before clicking login (user thinking/verifying)
        self.human_delay(800, 1500)

        # Click login
        self.click(self.login_button)

        execution_logger.log_action("login", "login_form", username=username)

    def get_error_message(self) -> str:
        """
        Get login error message.

        Returns:
            Error message text
        """
        if self.is_visible(self.error_message, timeout=2000):
            return self.get_text(self.error_message)
        return ""

    def is_login_successful(self) -> bool:
        """
        Check if login was successful.

        Returns:
            True if redirected to dashboard
        """
        # Check if we're on the main page
        return "/bank/main.jsp" in self.page.url

    def assert_login_error(self, expected_error: str) -> None:
        """
        Assert login error message.

        Args:
            expected_error: Expected error text
        """
        actual_error = self.get_error_message()
        if expected_error not in actual_error:
            raise AssertionError(f"Expected error '{expected_error}' not found. Got: '{actual_error}'")

        execution_logger.log_validation("login_error", expected_error, actual_error, True)
