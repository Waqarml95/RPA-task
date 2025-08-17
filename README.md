# RPA Task

Playwright automation for the AltoroMutual demo banking site that demonstrates web scraping, data extraction, and automated testing capabilities.

## Overview

This project automates 6 key banking operations on the AltoroMutual demo site (https://demo.testfire.net/):

1. **Authentication Testing** - Positive and negative login scenarios
2. **Account Data Extraction** - Scrape user accounts and transaction histories
3. **Transaction Filtering** - Filter transactions by date range and amount
4. **Fund Transfer** - Automated fund transfer with screenshot capture
5. **Card Products Extraction** - Scrape available banking card information
6. **API Integration** - Test API endpoints (returns 404 on demo site)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- 2GB free disk space for browser installation

### Installation

1. **Clone or navigate to the project**
```bash
cd RPA-task
```

2. **Create virtual environment**
```bash
python3 -m venv venv
```

3. **Activate virtual environment**
```bash
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

4. **Install dependencies**
```bash
pip install -e .
```

5. **Install Playwright browsers**
```bash
playwright install chromium
```

## Running the Automation

**Run with visible browser (see automation in action):**
```bash
python src/main.py run
```

**Run in headless mode (runs in background):**
```bash
python src/main.py run --headless
```

**Display information:**
```bash
python src/main.py info
```

## 📁 Output Files Location

All automation outputs are saved in organized directories:

### Excel Report
- **Location**: `output/AltoroMutual_Automation.xlsx`
- **Contents**:
  - Part1_Authentication - Login test results
  - User_Accounts - All user accounts
  - Account_[Number]_History - Transaction history per account
  - Transactions_DateRange - Filtered transactions
  - High_Value_Deposits - Deposits over $100
  - Transfer_Confirmation - Transfer details with screenshot
  - Available_Cards - Card products information
  - API_Accounts - API account data
  - API_Transactions - API transaction data
  - Discrepancies - Web vs API comparison

### Screenshots
- **Location**: `output/screenshots/`
- **Files**:
  - `negative_login_error.png` - Failed login attempt
  - `transfer_confirmation.png` - Transfer completion
  - `transfer_error.png` - Transfer failure (if any)
  - Timestamped screenshots for debugging

### Logs
- **Location**: `output/logs/`
- **Files**:
  - `execution_YYYYMMDD.log` - Detailed execution logs
  - `exceptions_YYYYMMDD.log` - Error logs
  - Structured CSV logs with timestamps

## Configuration

### Environment Variables (.env)
```bash
# Browser settings
HEADLESS=false
BROWSER_TIMEOUT=30000

# Valid credentials
VALID_USERNAME=admin
VALID_PASSWORD=admin

# Invalid credentials for testing
INVALID_USERNAME=admin
INVALID_PASSWORD=wrongpassword

# API credentials
API_USERNAME=jsmith
API_PASSWORD=demo1234

# Transfer details
TRANSFER_FROM_ACCOUNT=800000 Checking
TRANSFER_TO_ACCOUNT=800000 Corporate
TRANSFER_AMOUNT=100000.00

# Date filters (YYYY-MM-DD format)
FILTER_DATE_START=2025-03-01
FILTER_DATE_END=2025-03-08
```

### Settings (config/settings.yaml)
```yaml
browser:
  type: chromium
  headless: false
  humanize: true  # Enable human-like delays

timeouts:
  default: 30000
  navigation: 30000
  action: 10000
```

## Project Structure

```
RPA-task/
├── src/
│   ├── main.py          # CLI entry point
│   ├── pages/           # Page objects (login, dashboard, etc.)
│   ├── workflows/       # Business logic for each part
│   ├── api/            # API client and models
│   └── utils/          # Utilities (Excel, logging, dates)
├── config/
│   └── settings.yaml   # Configuration settings
├── output/
│   ├── AltoroMutual_Automation.xlsx  # Main output file
│   ├── screenshots/    # Screenshot captures
│   └── logs/          # Execution logs
├── tests/             # Test files
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
├── pyproject.toml   # Project configuration
└── README.md        # This file
```

## Command Reference

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
playwright install

# Run the complete automation with visible browser
python src/main.py run

# Run in background (headless)
python src/main.py run --headless

# Display information
python src/main.py info

# View results
open output/AltoroMutual_Automation.xlsx  # macOS
start output\AltoroMutual_Automation.xlsx  # Windows

# Check logs
tail -f output/logs/execution_*.log
```


**Built with Python 3.11, Playwright, and modern automation best practices.**
