"""Dashboard page object."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Dashboard page object for AltoroMutual."""

    def __init__(self, page: Page):
        """Initialize dashboard page."""
        super().__init__(page)

        # Selectors
        self.welcome_message = "h1"
        self.account_summary = "table#accounts"
        self.menu_items = {
            "view_account_summary": "a[id='MenuHyperLink1']",
            "view_recent_transactions": "a[id='MenuHyperLink2']",
            "transfer_funds": "a[id='MenuHyperLink3']",
            "search_news": "a[id='MenuHyperLink4']",
            "customize_site": "a[id='MenuHyperLink5']",
            "contact_us": "a[href*='feedback']",
            "sign_off": "a[href*='logout']",
        }
        self.account_links = "table#accounts a"

    def is_on_dashboard(self) -> bool:
        """Check if on dashboard page."""
        return "/bank/main.jsp" in self.page.url and self.is_visible(self.welcome_message)

    def get_welcome_text(self) -> str:
        """Get welcome message text."""
        return self.get_text(self.welcome_message)

    def navigate_to_menu(self, menu_item: str) -> None:
        """
        Navigate to menu item with humanized delay.

        Args:
            menu_item: Key from menu_items dict
        """
        # Pause to scan the menu (human behavior)
        self.human_delay(500, 1200)

        if menu_item in self.menu_items:
            self.click(self.menu_items[menu_item])

            # Wait for page to load after navigation
            self.human_delay(1000, 2000)
        else:
            raise ValueError(f"Unknown menu item: {menu_item}")

    def get_account_summary(self) -> list[dict[str, str]]:
        """
        Get account summary from dashboard.

        Returns:
            List of account dictionaries
        """
        return self.get_table_data(self.account_summary)

    def click_account(self, account_number: str) -> None:
        """
        Click on specific account link.

        Args:
            account_number: Account number to click
        """
        account_link = f"a:has-text('{account_number}')"
        self.click(account_link)

    def sign_off(self) -> None:
        """Sign off from the application."""
        self.click(self.menu_items["sign_off"])
