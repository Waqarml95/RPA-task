"""Configuration loader using pydantic-settings."""

from pathlib import Path
from typing import Any, Dict, Literal, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrowserConfig(BaseModel):
    """Browser configuration settings."""

    type: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = False
    slow_mo: int = 0
    viewport: Dict[str, int] = {"width": 1920, "height": 1080}
    locale: str = "en-US"
    timezone: str = "America/New_York"


class TimeoutConfig(BaseModel):
    """Timeout configuration settings."""

    default: int = 30000
    navigation: int = 30000
    action: int = 10000
    assertion: int = 5000


class UrlConfig(BaseModel):
    """URL configuration settings."""

    base: str = "https://demo.testfire.net"
    swagger: str = "https://demo.testfire.net/swagger/index.html"
    login: str = "/login.jsp"
    dashboard: str = "/bank/main.jsp"
    accounts: str = "/bank/account.jsp"
    transactions: str = "/bank/transaction.jsp"
    transfer: str = "/bank/transfer.jsp"
    cards: str = "/bank/customize.jsp"


class CredentialSet(BaseModel):
    """Single credential set."""

    username: str
    password: str


class CredentialsConfig(BaseModel):
    """Credentials configuration."""

    valid: CredentialSet
    invalid: CredentialSet
    api: CredentialSet


class TransferConfig(BaseModel):
    """Transfer configuration settings."""

    from_account: str
    to_account: str
    amount: str


class DateRangeConfig(BaseModel):
    """Date range configuration."""

    start: str
    end: str


class DepositsConfig(BaseModel):
    """Deposits filter configuration."""

    min_amount: float


class FiltersConfig(BaseModel):
    """Filters configuration."""

    date_range: DateRangeConfig
    deposits: DepositsConfig
    api_dates: DateRangeConfig


class ExcelConfig(BaseModel):
    """Excel output configuration."""

    filename: str = "AltoroMutual_Automation.xlsx"
    autosize_columns: bool = True
    freeze_panes: str = "A2"


class ScreenshotConfig(BaseModel):
    """Screenshot configuration."""

    dir: str = "output/screenshots"
    format: Literal["png", "jpeg"] = "png"
    full_page: bool = False


class LogConfig(BaseModel):
    """Log output configuration."""

    dir: str = "output/logs"
    format: Literal["csv", "json"] = "csv"


class OutputConfig(BaseModel):
    """Output configuration."""

    base_dir: str = "output"
    excel: ExcelConfig
    screenshots: ScreenshotConfig
    logs: LogConfig


class ArtifactsConfig(BaseModel):
    """Artifacts configuration."""

    dir: str = "artifacts"
    trace: bool = True
    video: bool = True
    har: bool = True
    screenshots_on_failure: bool = True


class RetryConfig(BaseModel):
    """Retry configuration."""

    max_attempts: int = 3
    delay_ms: int = 1000
    backoff_factor: float = 2.0


class ApiConfig(BaseModel):
    """API configuration."""

    base_url: str = "https://demo.testfire.net/api"
    timeout: int = 10000
    verify_ssl: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["structured", "simple"] = "structured"
    include_timestamp: bool = True
    include_context: bool = True


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment variables
    app_env: str = Field(default="production", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # URL overrides from env
    base_url: Optional[str] = Field(default=None, alias="BASE_URL")
    swagger_url: Optional[str] = Field(default=None, alias="SWAGGER_URL")

    # Browser overrides from env
    headless: Optional[bool] = Field(default=None, alias="HEADLESS")
    browser_timeout: Optional[int] = Field(default=None, alias="BROWSER_TIMEOUT")

    # Credential overrides from env
    valid_username: Optional[str] = Field(default=None, alias="VALID_USERNAME")
    valid_password: Optional[str] = Field(default=None, alias="VALID_PASSWORD")
    invalid_username: Optional[str] = Field(default=None, alias="INVALID_USERNAME")
    invalid_password: Optional[str] = Field(default=None, alias="INVALID_PASSWORD")
    api_username: Optional[str] = Field(default=None, alias="API_USERNAME")
    api_password: Optional[str] = Field(default=None, alias="API_PASSWORD")

    # Transfer overrides from env
    transfer_from_account: Optional[str] = Field(default=None, alias="TRANSFER_FROM_ACCOUNT")
    transfer_to_account: Optional[str] = Field(default=None, alias="TRANSFER_TO_ACCOUNT")
    transfer_amount: Optional[str] = Field(default=None, alias="TRANSFER_AMOUNT")

    # Filter overrides from env
    filter_date_start: Optional[str] = Field(default=None, alias="FILTER_DATE_START")
    filter_date_end: Optional[str] = Field(default=None, alias="FILTER_DATE_END")
    deposit_min_amount: Optional[float] = Field(default=None, alias="DEPOSIT_MIN_AMOUNT")
    api_date_start: Optional[str] = Field(default=None, alias="API_DATE_START")
    api_date_end: Optional[str] = Field(default=None, alias="API_DATE_END")

    # Loaded configuration
    _config: Optional[Dict[str, Any]] = None

    @property
    def browser(self) -> BrowserConfig:
        """Get browser configuration."""
        config = self._get_config()["browser"]
        if self.headless is not None:
            config["headless"] = self.headless
        return BrowserConfig(**config)

    @property
    def timeouts(self) -> TimeoutConfig:
        """Get timeout configuration."""
        config = self._get_config()["timeouts"]
        if self.browser_timeout is not None:
            config["default"] = self.browser_timeout
            config["navigation"] = self.browser_timeout
        return TimeoutConfig(**config)

    @property
    def urls(self) -> UrlConfig:
        """Get URL configuration."""
        config = self._get_config()["urls"]
        if self.base_url:
            config["base"] = self.base_url
        if self.swagger_url:
            config["swagger"] = self.swagger_url
        return UrlConfig(**config)

    @property
    def credentials(self) -> CredentialsConfig:
        """Get credentials configuration."""
        config = self._get_config()["credentials"]

        # Override with env variables if present
        if self.valid_username:
            config["valid"]["username"] = self.valid_username
        if self.valid_password:
            config["valid"]["password"] = self.valid_password
        if self.invalid_username:
            config["invalid"]["username"] = self.invalid_username
        if self.invalid_password:
            config["invalid"]["password"] = self.invalid_password
        if self.api_username:
            config["api"]["username"] = self.api_username
        if self.api_password:
            config["api"]["password"] = self.api_password

        return CredentialsConfig(**config)

    @property
    def transfer(self) -> TransferConfig:
        """Get transfer configuration."""
        config = self._get_config()["transfer"]

        if self.transfer_from_account:
            config["from_account"] = self.transfer_from_account
        if self.transfer_to_account:
            config["to_account"] = self.transfer_to_account
        if self.transfer_amount:
            config["amount"] = self.transfer_amount

        return TransferConfig(**config)

    @property
    def filters(self) -> FiltersConfig:
        """Get filters configuration."""
        config = self._get_config()["filters"]

        if self.filter_date_start:
            config["date_range"]["start"] = self.filter_date_start
        if self.filter_date_end:
            config["date_range"]["end"] = self.filter_date_end
        if self.deposit_min_amount is not None:
            config["deposits"]["min_amount"] = self.deposit_min_amount
        if self.api_date_start:
            config["api_dates"]["start"] = self.api_date_start
        if self.api_date_end:
            config["api_dates"]["end"] = self.api_date_end

        return FiltersConfig(**config)

    @property
    def output(self) -> OutputConfig:
        """Get output configuration."""
        return OutputConfig(**self._get_config()["output"])

    @property
    def artifacts(self) -> ArtifactsConfig:
        """Get artifacts configuration."""
        return ArtifactsConfig(**self._get_config()["artifacts"])

    @property
    def retry(self) -> RetryConfig:
        """Get retry configuration."""
        return RetryConfig(**self._get_config()["retry"])

    @property
    def api(self) -> ApiConfig:
        """Get API configuration."""
        return ApiConfig(**self._get_config()["api"])

    @property
    def logging(self) -> LoggingConfig:
        """Get logging configuration."""
        return LoggingConfig(**self._get_config()["logging"])

    def _get_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self._config is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)
        return self._config


# Global settings instance
settings = Settings()
