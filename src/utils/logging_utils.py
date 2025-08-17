"""Logging utilities for structured logging."""

import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from utils.config_loader import settings


class CSVLogHandler:
    """Handler for CSV logging."""

    def __init__(self, log_dir: Path, log_type: str = "execution"):
        """Initialize CSV log handler."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{log_type}_{timestamp}.csv"

        # Initialize CSV with headers
        self.headers = [
            "timestamp",
            "level",
            "module",
            "function",
            "message",
            "context",
            "error",
            "traceback",
        ]

        with open(self.log_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()

    def write(self, log_entry: Dict[str, Any]) -> None:
        """Write log entry to CSV."""
        with open(self.log_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)

            # Prepare row with default values
            row = {header: "" for header in self.headers}

            # Map log entry to CSV columns
            row["timestamp"] = log_entry.get("timestamp", datetime.now().isoformat())
            row["level"] = log_entry.get("level", "INFO")
            row["module"] = log_entry.get("module", "")
            row["function"] = log_entry.get("function", "")
            row["message"] = log_entry.get("event", "")

            # Serialize context as JSON
            context = {
                k: v
                for k, v in log_entry.items()
                if k not in ["timestamp", "level", "module", "function", "event", "exception"]
            }
            if context:
                row["context"] = json.dumps(context)

            # Handle exceptions
            if "exception" in log_entry:
                row["error"] = str(log_entry.get("exception", ""))
                row["traceback"] = log_entry.get("exc_info", "")

            writer.writerow(row)


class StructuredLogger:
    """Structured logger with CSV and console output."""

    def __init__(
        self,
        name: str = "altoro_automation",
        log_dir: Optional[Path] = None,
        log_type: str = "execution",
    ):
        """Initialize structured logger."""
        self.name = name
        self.log_dir = log_dir or Path(settings.output.logs.dir)
        self.csv_handler = CSVLogHandler(self.log_dir, log_type)

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.CallsiteParameterAdder(
                    parameters=[
                        structlog.processors.CallsiteParameter.MODULE,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    ]
                ),
                structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Set up stdlib logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, settings.logging.level),
        )

        self.logger = structlog.get_logger(name)

    def _log_to_csv(self, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Log to CSV file."""
        self.csv_handler.write(event_dict)
        return event_dict

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
        self._log_to_csv({"level": "INFO", "event": message, **kwargs})

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
        self._log_to_csv({"level": "ERROR", "event": message, **kwargs})

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
        self._log_to_csv({"level": "WARNING", "event": message, **kwargs})

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
        self._log_to_csv({"level": "DEBUG", "event": message, **kwargs})

    def exception(self, message: str, exc_info: Any = True, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, exc_info=exc_info, **kwargs)
        self._log_to_csv({
            "level": "ERROR",
            "event": message,
            "exception": str(exc_info) if exc_info else "",
            **kwargs,
        })


class ExecutionLogger:
    """Logger for test execution tracking."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize execution logger."""
        self.logger = StructuredLogger(
            name="execution",
            log_dir=log_dir,
            log_type="execution",
        )
        self.test_results: List[Dict[str, Any]] = []

    def log_test_start(self, test_name: str, part: str) -> None:
        """Log test start."""
        self.logger.info(
            "Test started",
            test_name=test_name,
            part=part,
            start_time=datetime.now().isoformat(),
        )

    def log_test_end(
        self,
        test_name: str,
        part: str,
        status: str,
        duration: float,
        error: Optional[str] = None,
    ) -> None:
        """Log test end."""
        result = {
            "test_name": test_name,
            "part": part,
            "status": status,
            "duration": duration,
            "end_time": datetime.now().isoformat(),
        }

        if error:
            result["error"] = error

        self.test_results.append(result)
        self.logger.info("Test completed", **result)

    def log_action(self, action: str, target: str, **kwargs: Any) -> None:
        """Log user action."""
        self.logger.info(
            "Action performed",
            action=action,
            target=target,
            **kwargs,
        )

    def log_validation(self, validation: str, expected: Any, actual: Any, passed: bool) -> None:
        """Log validation result."""
        self.logger.info(
            "Validation performed",
            validation=validation,
            expected=expected,
            actual=actual,
            passed=passed,
        )

    def log_screenshot(self, name: str, path: str, reason: str) -> None:
        """Log screenshot capture."""
        self.logger.info(
            "Screenshot captured",
            name=name,
            path=path,
            reason=reason,
        )

    def generate_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "passed"])
        failed = len([r for r in self.test_results if r["status"] == "failed"])

        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "execution_time": sum(r["duration"] for r in self.test_results),
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info("Execution summary", **summary)
        return summary


class ExceptionLogger:
    """Logger for exception tracking."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize exception logger."""
        self.logger = StructuredLogger(
            name="exceptions",
            log_dir=log_dir,
            log_type="exceptions",
        )

    def log_exception(
        self,
        exception: Exception,
        context: str,
        screenshot_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Log exception with context."""
        self.logger.exception(
            "Exception occurred",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context=context,
            screenshot_path=screenshot_path,
            exc_info=exception,
            **kwargs,
        )


# Global logger instances
execution_logger = ExecutionLogger()
exception_logger = ExceptionLogger()
