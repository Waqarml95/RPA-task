#!/usr/bin/env python3
"""Main entry point for AltoroMutual automation."""

import sys
from pathlib import Path

import pandas as pd
import typer
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.table import Table

from utils.config_loader import settings
from utils.excel_writer import ExcelWriter
from utils.logging_utils import execution_logger
from workflows.part1_auth import AuthenticationWorkflow
from workflows.part2_accounts import AccountsWorkflow
from workflows.part3_filters import TransactionFiltersWorkflow
from workflows.part4_transfer import TransferWorkflow
from workflows.part5_cards import CardsWorkflow
from workflows.part6_api import ApiWorkflow

app = typer.Typer()
console = Console()


def run_automation(headless: bool = False):
    """Run complete automation workflow."""
    console.print("[bold green]Starting AltoroMutual Automation[/bold green]")

    # Initialize Excel writer
    excel_path = Path(settings.output.base_dir) / settings.output.excel.filename
    excel_writer = ExcelWriter(str(excel_path))

    with sync_playwright() as playwright:
        # Launch browser
        browser = playwright.chromium.launch(
            headless=headless,
            slow_mo=settings.browser.slow_mo,
        )

        # Create context with viewport
        context = browser.new_context(
            viewport={
                "width": settings.browser.viewport.get("width"),
                "height": settings.browser.viewport.get("width"),
            },
            locale=settings.browser.locale,
            timezone_id=settings.browser.timezone,
        )

        # Create page
        page = context.new_page()

        try:
            # Part 1: Authentication Tests
            console.print("\n[cyan]Running Part 1: Authentication Tests[/cyan]")
            auth_workflow = AuthenticationWorkflow(page)
            auth_results = auth_workflow.run_all()

            # Save authentication results
            auth_df = pd.DataFrame([
                {
                    "Test": "Positive Login",
                    "Result": "Passed" if auth_results.get("positive_login", {}).get("success") else "Failed",
                    "Details": auth_results.get("positive_login", {}).get("dashboard_text", ""),
                    "Screenshot": "",
                },
                {
                    "Test": "Negative Login",
                    "Result": "Passed" if auth_results.get("negative_login", {}).get("login_failed") else "Failed",
                    "Details": auth_results.get("negative_login", {}).get("error_text", ""),
                    "Screenshot": auth_results.get("negative_login", {}).get("screenshot_path", ""),
                }
            ])
            excel_writer.write_df(auth_df, "Part1_Authentication")

            # Part 2: Account Data Extraction
            console.print("\n[cyan]Running Part 2: Account Data Extraction[/cyan]")
            accounts_workflow = AccountsWorkflow(page)
            accounts_results = accounts_workflow.run_all(excel_writer)

            # Part 3: Transaction Analysis & Filtering
            console.print("\n[cyan]Running Part 3: Transaction Analysis & Filtering[/cyan]")
            filters_workflow = TransactionFiltersWorkflow(page)
            filters_results = filters_workflow.run_all(excel_writer)

            # Part 4: Fund Transfer Operation
            console.print("\n[cyan]Running Part 4: Fund Transfer Operation[/cyan]")
            transfer_workflow = TransferWorkflow(page)
            transfer_results = transfer_workflow.run_all(excel_writer)

            # Part 5: Card Information Extraction
            console.print("\n[cyan]Running Part 5: Card Information Extraction[/cyan]")
            cards_workflow = CardsWorkflow(page)
            cards_results = cards_workflow.run_all(excel_writer)

            # Part 6: API Integration & Automation
            console.print("\n[cyan]Running Part 6: API Integration & Automation[/cyan]")
            api_workflow = ApiWorkflow(page)
            api_results = api_workflow.run_all(excel_writer)

            # Save final workbook
            excel_writer.save()

            # Print summary
            console.print("\n[bold green]✓ Automation completed successfully[/bold green]")
            console.print(f"[yellow]Results saved to: {excel_path}[/yellow]")

            # Display summary table
            table = Table(title="Execution Summary")
            table.add_column("Part", style="cyan")
            table.add_column("Status", style="green")

            table.add_row("1. Authentication", "✓ Completed")
            table.add_row("2. Account Extraction", "✓ Completed")
            table.add_row("3. Transaction Filtering", "✓ Completed")
            table.add_row("4. Fund Transfer", "✓ Completed")
            table.add_row("5. Card Products", "✓ Completed")
            table.add_row("6. API Integration", "✓ Completed")

            console.print(table)

        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            execution_logger.logger.error(f"Automation failed: {e}")
            raise
        finally:
            # Clean up
            context.close()
            browser.close()


@app.command()
def run(
    headless: bool = typer.Option(False, "--headless", help="Run browser in headless mode")
):
    """Run the complete AltoroMutual automation."""
    try:
        run_automation(headless)
    except Exception as e:
        console.print(f"[bold red]Automation failed: {e}[/bold red]")
        sys.exit(1)


@app.command()
def info():
    """Display information about the automation."""
    console.print("[bold]AltoroMutual Automation[/bold]")
    console.print("Automates 6 banking operations on the AltoroMutual demo site")
    console.print("\nParts:")
    console.print("1. Authentication Testing")
    console.print("2. Account Data Extraction")
    console.print("3. Transaction Filtering")
    console.print("4. Fund Transfer")
    console.print("5. Card Products")
    console.print("6. API Integration")
    console.print(f"\nOutput: {settings.output.base_dir}/{settings.output.excel.filename}")


if __name__ == "__main__":
    app()
