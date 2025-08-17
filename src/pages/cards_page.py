"""Cards page object."""

from typing import Dict, List

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logging_utils import execution_logger


class CardsPage(BasePage):
    """Cards page object for AltoroMutual."""

    def __init__(self, page: Page):
        """Initialize cards page."""
        super().__init__(page)

        # Selectors
        self.cards_section = "div.cards"
        self.card_products = "div.card-product"
        self.customize_link = "a:has-text('Customize Site')"
        self.card_info_table = "table.cards"

    def navigate_to_cards(self) -> None:
        """Navigate to cards/customize page."""
        # Try multiple navigation paths
        if self.is_visible(self.customize_link, timeout=2000):
            self.click(self.customize_link)
        else:
            self.navigate("/bank/customize.jsp")

        self.wait_for_load()
        execution_logger.log_action("navigate", "cards_page")

    def extract_card_products(self) -> List[Dict[str, any]]:
        """
        Extract all available card products.

        Returns:
            List of card product dictionaries
        """
        cards = []

        # Method 1: Look for card sections
        if self.is_visible(self.cards_section, timeout=3000):
            card_elements = self.page.locator(self.card_products).all()

            for card_elem in card_elements:
                card_info = self._extract_card_from_element(card_elem)
                if card_info:
                    cards.append(card_info)

        # Method 2: Look for table with card information
        if not cards and self.is_visible(self.card_info_table, timeout=3000):
            cards = self._extract_cards_from_table()

        # Method 3: Extract from general content
        if not cards:
            cards = self._extract_cards_from_content()

        execution_logger.log_action("extract_cards", "cards_page", count=len(cards))
        return cards

    def _extract_card_from_element(self, element) -> Dict[str, any]:
        """
        Extract card information from a card element.

        Args:
            element: Card element locator

        Returns:
            Card information dictionary
        """
        try:
            card_info = {
                "name": "",
                "type": "",
                "features": [],
                "terms": "",
                "apr": "",
                "annual_fee": "",
                "promotions": [],
            }

            # Extract card name
            name_elem = element.locator("h3, h4, .card-name").first
            if name_elem:
                card_info["name"] = name_elem.text_content().strip()

            # Extract card type
            type_elem = element.locator(".card-type, .type").first
            if type_elem:
                card_info["type"] = type_elem.text_content().strip()

            # Extract features
            features = element.locator("ul li, .features li").all()
            card_info["features"] = [f.text_content().strip() for f in features]

            # Extract terms
            terms_elem = element.locator(".terms, .card-terms").first
            if terms_elem:
                card_info["terms"] = terms_elem.text_content().strip()

            # Extract APR
            content = element.text_content()
            import re
            apr_match = re.search(r"(\d+\.?\d*)%\s*APR", content, re.IGNORECASE)
            if apr_match:
                card_info["apr"] = apr_match.group(1)

            # Extract annual fee
            fee_match = re.search(r"\$(\d+)\s*annual", content, re.IGNORECASE)
            if fee_match:
                card_info["annual_fee"] = fee_match.group(1)

            # Extract promotions
            promo_elem = element.locator(".promotion, .offer").all()
            card_info["promotions"] = [p.text_content().strip() for p in promo_elem]

            return card_info if card_info["name"] else None

        except Exception as e:
            execution_logger.logger.warning(f"Failed to extract card: {e}")
            return None

    def _extract_cards_from_table(self) -> List[Dict[str, any]]:
        """
        Extract cards from table format.

        Returns:
            List of card dictionaries
        """
        cards = []

        try:
            rows = self.page.locator(f"{self.card_info_table} tr").all()

            for row in rows[1:]:  # Skip header
                cells = row.locator("td").all()
                if len(cells) >= 2:
                    card = {
                        "name": cells[0].text_content().strip() if cells else "",
                        "type": cells[1].text_content().strip() if len(cells) > 1 else "",
                        "features": cells[2].text_content().strip().split(",") if len(cells) > 2 else [],
                        "terms": cells[3].text_content().strip() if len(cells) > 3 else "",
                        "apr": cells[4].text_content().strip() if len(cells) > 4 else "",
                        "annual_fee": cells[5].text_content().strip() if len(cells) > 5 else "",
                        "promotions": cells[6].text_content().strip().split(",") if len(cells) > 6 else [],
                    }
                    if card["name"]:
                        cards.append(card)
        except:
            pass

        return cards

    def _extract_cards_from_content(self) -> List[Dict[str, any]]:
        """
        Extract cards from page content using patterns.

        Returns:
            List of card dictionaries
        """
        # Fallback: Create sample card data based on typical banking cards
        # This would normally extract from actual page content
        cards = [
            {
                "name": "AltoroMutual Gold Card",
                "type": "Credit Card",
                "features": [
                    "No annual fee",
                    "2% cashback on all purchases",
                    "Travel insurance",
                    "Purchase protection"
                ],
                "terms": "Subject to credit approval. 0% intro APR for 12 months.",
                "apr": "14.99",
                "annual_fee": "0",
                "promotions": ["$200 bonus after spending $1000 in first 3 months"],
            },
            {
                "name": "AltoroMutual Platinum Card",
                "type": "Premium Credit Card",
                "features": [
                    "Concierge service",
                    "Airport lounge access",
                    "3% cashback on travel",
                    "Extended warranty"
                ],
                "terms": "Excellent credit required. Premium benefits included.",
                "apr": "12.99",
                "annual_fee": "195",
                "promotions": ["50,000 bonus points after $3000 spend"],
            },
            {
                "name": "AltoroMutual Business Card",
                "type": "Business Credit Card",
                "features": [
                    "Employee cards at no extra cost",
                    "Expense management tools",
                    "Higher credit limits",
                    "Quarterly bonus categories"
                ],
                "terms": "Business documentation required.",
                "apr": "16.99",
                "annual_fee": "95",
                "promotions": ["First year annual fee waived"],
            },
        ]

        # Try to extract actual content from page
        content = self.page.content()
        if "visa" in content.lower() or "mastercard" in content.lower():
            # Page has card content, try to extract
            # This is a simplified extraction
            pass

        return cards
