"""Base page object with common functionality."""

import random
import time
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import ElementHandle, Locator, Page, expect

from utils.config_loader import settings
from utils.logging_utils import execution_logger, exception_logger


class BasePage:
    """Base page object with common functionality."""

    def __init__(self, page: Page):
        """Initialize base page."""
        self.page = page
        self.base_url = settings.urls.base
        self.timeout = settings.timeouts.default

    def human_delay(self, min_ms: int = 500, max_ms: int = 1500) -> None:
        """
        Add humanized delay between actions.

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        if not getattr(settings.browser, 'humanize', True):
            return  # Skip delays if humanization is disabled

        delay = random.randint(min_ms, max_ms)
        time.sleep(delay / 1000.0)

    def typing_delay(self, text: str, min_delay: int = 50, max_delay: int = 150) -> None:
        """
        Simulate human-like typing with random delays between characters.

        Args:
            text: Text being typed (for length calculation)
            min_delay: Minimum delay between characters in milliseconds
            max_delay: Maximum delay between characters in milliseconds
        """
        if not getattr(settings.browser, 'humanize', True):
            return  # Skip delays if humanization is disabled

        # Add a small delay per character to simulate typing
        typing_time = len(text) * random.randint(min_delay, max_delay) / 1000.0
        time.sleep(min(typing_time, 2.0))  # Cap at 2 seconds for long text

    def click_delay(self) -> None:
        """Add delay before click actions."""
        self.human_delay(200, 800)

    def form_delay(self) -> None:
        """Add delay between form field interactions."""
        self.human_delay(300, 1000)

    def navigation_delay(self) -> None:
        """Add delay after navigation."""
        self.human_delay(1000, 2500)

    def navigate(self, path: str = "") -> None:
        """
        Navigate to a specific path.

        Args:
            path: Path relative to base URL
        """
        url = f"{self.base_url}{path}" if path else self.base_url
        self.page.goto(url, wait_until="networkidle", timeout=settings.timeouts.navigation)
        self.navigation_delay()  # Add humanized delay after navigation
        execution_logger.log_action("navigate", url)

    def wait_for_load(self, state: str = "networkidle") -> None:
        """
        Wait for page to load.

        Args:
            state: Load state to wait for
        """
        self.page.wait_for_load_state(state, timeout=settings.timeouts.navigation)

    def get_element(self, selector: str) -> Locator:
        """
        Get element by selector with built-in wait.

        Args:
            selector: Element selector

        Returns:
            Locator object
        """
        locator = self.page.locator(selector)
        return locator

    def click(self, selector: str, **kwargs: Any) -> None:
        """
        Click element with logging and humanized delay.

        Args:
            selector: Element selector
            **kwargs: Additional click options
        """
        self.click_delay()  # Add humanized delay before click
        locator = self.get_element(selector)
        locator.click(timeout=settings.timeouts.action, **kwargs)
        execution_logger.log_action("click", selector)

    def fill(self, selector: str, value: str, **kwargs: Any) -> None:
        """
        Fill input field with logging and humanized typing.

        Args:
            selector: Element selector
            value: Value to fill
            **kwargs: Additional fill options
        """
        self.form_delay()  # Add humanized delay before form interaction
        locator = self.get_element(selector)

        # Clear field first with a small delay
        locator.click(timeout=settings.timeouts.action)
        locator.press("Control+a")  # Select all
        self.human_delay(100, 300)  # Brief pause before typing

        # Type with human-like delay
        locator.type(value, delay=random.randint(50, 120))
        self.typing_delay(value)  # Additional typing simulation

        execution_logger.log_action("fill", selector, value=value)

    def type(self, selector: str, value: str, delay: int = 0, **kwargs: Any) -> None:
        """
        Type text with optional delay.

        Args:
            selector: Element selector
            value: Value to type
            delay: Delay between keystrokes in ms
            **kwargs: Additional type options
        """
        locator = self.get_element(selector)
        locator.type(value, delay=delay, timeout=settings.timeouts.action, **kwargs)
        execution_logger.log_action("type", selector, value=value)

    def select_option(self, selector: str, value: str, **kwargs: Any) -> None:
        """
        Select dropdown option.

        Args:
            selector: Element selector
            value: Option value to select
            **kwargs: Additional select options
        """
        locator = self.get_element(selector)
        locator.select_option(value, timeout=settings.timeouts.action, **kwargs)
        execution_logger.log_action("select", selector, value=value)

    def get_text(self, selector: str) -> str:
        """
        Get element text content.

        Args:
            selector: Element selector

        Returns:
            Text content
        """
        locator = self.get_element(selector)
        return locator.text_content() or ""

    def get_value(self, selector: str) -> str:
        """
        Get input value.

        Args:
            selector: Element selector

        Returns:
            Input value
        """
        locator = self.get_element(selector)
        return locator.input_value()

    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if element is visible.

        Args:
            selector: Element selector
            timeout: Custom timeout

        Returns:
            True if visible
        """
        try:
            locator = self.get_element(selector)
            locator.wait_for(state="visible", timeout=timeout or settings.timeouts.assertion)
            return True
        except:
            return False

    def is_enabled(self, selector: str) -> bool:
        """
        Check if element is enabled.

        Args:
            selector: Element selector

        Returns:
            True if enabled
        """
        locator = self.get_element(selector)
        return locator.is_enabled()

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> Locator:
        """
        Wait for selector with specific state.

        Args:
            selector: Element selector
            state: State to wait for
            timeout: Custom timeout

        Returns:
            Locator object
        """
        return self.page.wait_for_selector(
            selector,
            state=state,
            timeout=timeout or self.timeout,
        )

    def screenshot(self, name: str, full_page: bool = False) -> str:
        """
        Take screenshot.

        Args:
            name: Screenshot name
            full_page: Whether to capture full page

        Returns:
            Path to saved screenshot
        """
        screenshot_dir = Path(settings.output.screenshots.dir)
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        filepath = screenshot_dir / f"{name}.{settings.output.screenshots.format}"
        self.page.screenshot(path=str(filepath), full_page=full_page)

        execution_logger.log_screenshot(name, str(filepath), "manual")
        return str(filepath)

    def handle_alert(self, accept: bool = True, prompt_text: Optional[str] = None) -> None:
        """
        Handle JavaScript alerts.

        Args:
            accept: Whether to accept or dismiss
            prompt_text: Text to enter for prompts
        """
        def handler(dialog):
            execution_logger.log_action(
                "handle_alert",
                dialog.message,
                type=dialog.type,
                action="accept" if accept else "dismiss",
            )
            if prompt_text and dialog.type == "prompt":
                dialog.accept(prompt_text)
            elif accept:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", handler)

    def switch_to_frame(self, selector: str) -> None:
        """
        Switch to iframe.

        Args:
            selector: Frame selector
        """
        frame_element = self.page.wait_for_selector(selector)
        frame = frame_element.content_frame()
        if frame:
            self.page = frame
            execution_logger.log_action("switch_to_frame", selector)

    def switch_to_main_frame(self) -> None:
        """Switch back to main frame."""
        if hasattr(self.page, "parent_frame"):
            parent = self.page.parent_frame()
            if parent:
                self.page = parent
                execution_logger.log_action("switch_to_main_frame", "main")

    def assert_text_visible(self, text: str, timeout: Optional[int] = None) -> None:
        """
        Assert text is visible on page.

        Args:
            text: Text to find
            timeout: Custom timeout
        """
        locator = self.page.get_by_text(text)
        expect(locator).to_be_visible(timeout=timeout or settings.timeouts.assertion)
        execution_logger.log_validation("text_visible", text, text, True)

    def assert_element_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Assert element is visible.

        Args:
            selector: Element selector
            timeout: Custom timeout
        """
        locator = self.get_element(selector)
        expect(locator).to_be_visible(timeout=timeout or settings.timeouts.assertion)
        execution_logger.log_validation("element_visible", selector, "visible", True)

    def assert_element_text(self, selector: str, expected_text: str, timeout: Optional[int] = None) -> None:
        """
        Assert element has expected text.

        Args:
            selector: Element selector
            expected_text: Expected text
            timeout: Custom timeout
        """
        locator = self.get_element(selector)
        expect(locator).to_have_text(expected_text, timeout=timeout or settings.timeouts.assertion)
        execution_logger.log_validation("element_text", expected_text, expected_text, True)

    def assert_element_value(self, selector: str, expected_value: str, timeout: Optional[int] = None) -> None:
        """
        Assert input has expected value.

        Args:
            selector: Element selector
            expected_value: Expected value
            timeout: Custom timeout
        """
        locator = self.get_element(selector)
        expect(locator).to_have_value(expected_value, timeout=timeout or settings.timeouts.assertion)
        execution_logger.log_validation("element_value", expected_value, expected_value, True)

    def get_table_data(self, table_selector: str) -> list[dict[str, str]]:
        """
        Extract data from HTML table.

        Args:
            table_selector: Table selector

        Returns:
            List of row dictionaries
        """
        table = self.get_element(table_selector)

        # Get headers
        headers = []
        header_cells = table.locator("thead th").all()
        if not header_cells:
            # Try first row as headers
            header_cells = table.locator("tr").first.locator("th, td").all()

        for cell in header_cells:
            headers.append(cell.text_content() or "")

        # Get rows
        rows = []
        body_rows = table.locator("tbody tr").all()
        if not body_rows:
            # Get all rows except first (header)
            body_rows = table.locator("tr").all()[1:]

        for row in body_rows:
            cells = row.locator("td").all()
            if cells:
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.text_content() or ""
                rows.append(row_data)

        return rows

    def retry_on_failure(self, func: callable, max_attempts: int = 3, delay: int = 1000) -> Any:
        """
        Retry function on failure.

        Args:
            func: Function to retry
            max_attempts: Maximum attempts
            delay: Delay between attempts in ms

        Returns:
            Function result
        """
        last_error = None

        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                last_error = e
                if attempt < max_attempts - 1:
                    self.page.wait_for_timeout(delay)
                    execution_logger.logger.warning(
                        f"Retry attempt {attempt + 1}/{max_attempts}",
                        error=str(e),
                    )

        if last_error:
            raise last_error
