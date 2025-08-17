"""Date utilities for handling different date formats."""

import re
from datetime import datetime
from typing import Literal, Optional

from dateutil.parser import parse
from playwright.sync_api import Page


class DateFormatDetector:
    """Detect and convert date formats."""

    # Common date patterns
    MDY_PATTERNS = [
        r"\d{1,2}/\d{1,2}/\d{4}",  # MM/DD/YYYY or M/D/YYYY
        r"\d{1,2}-\d{1,2}-\d{4}",  # MM-DD-YYYY
        r"\d{1,2}\.\d{1,2}\.\d{4}",  # MM.DD.YYYY
    ]
    
    DMY_PATTERNS = [
        r"\d{1,2}/\d{1,2}/\d{4}",  # DD/MM/YYYY or D/M/YYYY
        r"\d{1,2}-\d{1,2}-\d{4}",  # DD-MM-YYYY
        r"\d{1,2}\.\d{1,2}\.\d{4}",  # DD.MM.YYYY
    ]

    @staticmethod
    def detect_page_date_format(page: Page) -> Literal["MDY", "DMY"]:
        """
        Detect date format used on the page by analyzing existing dates.
        
        Args:
            page: Playwright page object
            
        Returns:
            "MDY" for Month/Day/Year format, "DMY" for Day/Month/Year format
        """
        # Look for dates in common locations
        selectors = [
            "text=/\\d{1,2}[/\\-\\.]\\d{1,2}[/\\-\\.]\\d{4}/",
            "[class*='date']",
            "[id*='date']",
            "td:has-text('/2025')",
            "td:has-text('/2024')",
            "span:has-text('/202')",
        ]
        
        dates_found = []
        for selector in selectors:
            try:
                elements = page.locator(selector).all()
                for element in elements[:5]:  # Check first 5 matches
                    text = element.text_content()
                    if text:
                        # Extract date patterns
                        for pattern in DateFormatDetector.MDY_PATTERNS:
                            matches = re.findall(pattern, text)
                            dates_found.extend(matches)
            except:
                continue
        
        # Analyze found dates to determine format
        for date_str in dates_found:
            parts = re.split(r"[/\-\.]", date_str)
            if len(parts) == 3:
                first, second, third = int(parts[0]), int(parts[1]), int(parts[2])
                
                # If first part > 12, it must be day (DMY)
                if first > 12:
                    return "DMY"
                # If second part > 12, it must be day (MDY)
                elif second > 12:
                    return "MDY"
                # If we have a clear month name nearby, use that as hint
                # For now, default to MDY (US format) as it's more common for US sites
        
        # Default to MDY for US banking sites
        return "MDY"

    @staticmethod
    def to_page_format(date_str: str, format: Literal["MDY", "DMY"]) -> str:
        """
        Convert date string to the specified format.
        
        Args:
            date_str: Input date string (supports various formats)
            format: Target format ("MDY" or "DMY")
            
        Returns:
            Formatted date string as MM/DD/YYYY or DD/MM/YYYY
        """
        # Parse the input date
        try:
            # Try parsing with common formats
            for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                # Use dateutil parser as fallback
                dt = parse(date_str, dayfirst=(format == "DMY"))
        except:
            # If all parsing fails, assume it's already in correct format
            return date_str
        
        # Format according to target
        if format == "MDY":
            return dt.strftime("%m/%d/%Y")
        else:  # DMY
            return dt.strftime("%d/%m/%Y")

    @staticmethod
    def parse_date(date_str: str, format_hint: Optional[Literal["MDY", "DMY"]] = None) -> datetime:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string to parse
            format_hint: Optional format hint
            
        Returns:
            Parsed datetime object
        """
        # First, try to parse ISO format (YYYY-MM-DD) explicitly
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return datetime.strptime(date_str, "%Y-%m-%d")
        
        # Then try other common formats
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Fall back to dateutil parser
        if format_hint:
            dayfirst = format_hint == "DMY"
        else:
            # Try to guess based on the string
            parts = re.split(r"[/\-\.]", date_str)
            if len(parts) == 3:
                first = int(parts[0])
                dayfirst = first > 12
            else:
                dayfirst = False
        
        return parse(date_str, dayfirst=dayfirst)

    @staticmethod
    def format_for_api(date_str: str) -> str:
        """
        Format date for API calls (typically YYYY-MM-DD).
        
        Args:
            date_str: Input date string
            
        Returns:
            Date formatted as YYYY-MM-DD
        """
        dt = DateFormatDetector.parse_date(date_str)
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def format_for_display(dt: datetime, format: str = "%m/%d/%Y") -> str:
        """
        Format datetime for display.
        
        Args:
            dt: Datetime object
            format: strftime format string
            
        Returns:
            Formatted date string
        """
        return dt.strftime(format)


class DateRangeHelper:
    """Helper for date range operations."""

    @staticmethod
    def parse_range(start_str: str, end_str: str) -> tuple[datetime, datetime]:
        """
        Parse date range strings.
        
        Args:
            start_str: Start date string
            end_str: End date string
            
        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        start = DateFormatDetector.parse_date(start_str)
        end = DateFormatDetector.parse_date(end_str)
        return start, end

    @staticmethod
    def is_date_in_range(date_str: str, start_str: str, end_str: str) -> bool:
        """
        Check if date is within range.
        
        Args:
            date_str: Date to check
            start_str: Range start date
            end_str: Range end date
            
        Returns:
            True if date is within range
        """
        date = DateFormatDetector.parse_date(date_str)
        start, end = DateRangeHelper.parse_range(start_str, end_str)
        return start <= date <= end

    @staticmethod
    def format_range_for_api(start_str: str, end_str: str) -> tuple[str, str]:
        """
        Format date range for API calls.
        
        Args:
            start_str: Start date string
            end_str: End date string
            
        Returns:
            Tuple of (start_api_format, end_api_format)
        """
        return (
            DateFormatDetector.format_for_api(start_str),
            DateFormatDetector.format_for_api(end_str),
        )


# Convenience functions
def detect_page_date_format(page: Page) -> Literal["MDY", "DMY"]:
    """Detect date format used on the page."""
    return DateFormatDetector.detect_page_date_format(page)


def to_page_format(date_str: str, format: Literal["MDY", "DMY"]) -> str:
    """Convert date string to page format."""
    return DateFormatDetector.to_page_format(date_str, format)


def parse_date(date_str: str, format_hint: Optional[Literal["MDY", "DMY"]] = None) -> datetime:
    """Parse date string to datetime."""
    return DateFormatDetector.parse_date(date_str, format_hint)


def format_for_api(date_str: str) -> str:
    """Format date for API calls."""
    return DateFormatDetector.format_for_api(date_str)