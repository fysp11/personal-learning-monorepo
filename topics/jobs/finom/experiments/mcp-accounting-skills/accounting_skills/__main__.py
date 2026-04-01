"""MCP Accounting Skills Server — entry point.

Run with: python -m accounting_skills

Exposes three tools via MCP (stdio transport):
1. categorize_transaction — classify a bank transaction to SKR03
2. calculate_vat — deterministic VAT calculation for EU countries
3. create_booking — generate a double-entry journal entry
"""

import json
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .categorizer import categorize_transaction, SKR03_CATEGORIES
from .vat import calculate_vat
from .booking import create_booking_entry


app = Server("accounting-skills")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="categorize_transaction",
            description=(
                "Categorize a bank transaction to a German SKR03 account code. "
                "Returns category, confidence score, and reasoning. "
                "High confidence (>0.85) can be auto-booked; low confidence needs human review."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "merchant_name": {
                        "type": "string",
                        "description": "Name of the merchant/payee",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transaction amount in EUR (gross, including VAT)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Transaction description from the bank statement",
                        "default": "",
                    },
                },
                "required": ["merchant_name", "amount"],
            },
        ),
        Tool(
            name="calculate_vat",
            description=(
                "Calculate VAT for a transaction using deterministic rules. "
                "Supports DE, FR, IT, ES, NL. Handles standard, reduced, exempt, "
                "reverse charge, and Kleinunternehmerregelung."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Gross transaction amount in EUR",
                    },
                    "category_code": {
                        "type": "string",
                        "description": "SKR03 account code from categorization",
                    },
                    "country": {
                        "type": "string",
                        "description": "ISO 2-letter country code (DE, FR, IT, ES, NL)",
                        "default": "DE",
                    },
                    "is_b2b_intra_eu": {
                        "type": "boolean",
                        "description": "Whether this is an intra-EU B2B transaction",
                        "default": False,
                    },
                    "counterparty_vat_id": {
                        "type": "string",
                        "description": "EU VAT ID of counterparty (required for reverse charge)",
                    },
                    "is_small_business": {
                        "type": "boolean",
                        "description": "Whether the business uses Kleinunternehmerregelung §19 UStG",
                        "default": False,
                    },
                },
                "required": ["amount", "category_code"],
            },
        ),
        Tool(
            name="create_booking",
            description=(
                "Create a double-entry bookkeeping record (Buchungssatz) following SKR03. "
                "Debits expense + Vorsteuer, credits bank account. Always balanced."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_date": {
                        "type": "string",
                        "description": "Transaction date in YYYY-MM-DD format",
                    },
                    "description": {
                        "type": "string",
                        "description": "Booking text (Buchungstext)",
                    },
                    "expense_account": {
                        "type": "string",
                        "description": "SKR03 expense account code",
                    },
                    "expense_account_name": {
                        "type": "string",
                        "description": "Human-readable account name",
                    },
                    "gross_amount": {
                        "type": "number",
                        "description": "Total amount paid including VAT",
                    },
                    "net_amount": {
                        "type": "number",
                        "description": "Amount excluding VAT",
                    },
                    "vat_amount": {
                        "type": "number",
                        "description": "VAT portion",
                    },
                    "vat_rate": {
                        "type": "number",
                        "description": "VAT rate (e.g., 0.19, 0.07, 0.0)",
                    },
                },
                "required": [
                    "transaction_date",
                    "description",
                    "expense_account",
                    "expense_account_name",
                    "gross_amount",
                    "net_amount",
                    "vat_amount",
                    "vat_rate",
                ],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "categorize_transaction":
        result = categorize_transaction(
            merchant_name=arguments["merchant_name"],
            amount=arguments["amount"],
            description=arguments.get("description", ""),
        )
        return [TextContent(type="text", text=result.model_dump_json(indent=2))]

    elif name == "calculate_vat":
        result = calculate_vat(
            amount=arguments["amount"],
            category_code=arguments["category_code"],
            country=arguments.get("country", "DE"),
            is_b2b_intra_eu=arguments.get("is_b2b_intra_eu", False),
            counterparty_vat_id=arguments.get("counterparty_vat_id"),
            is_small_business=arguments.get("is_small_business", False),
        )
        return [TextContent(type="text", text=result.model_dump_json(indent=2))]

    elif name == "create_booking":
        result = create_booking_entry(
            transaction_date=arguments["transaction_date"],
            description=arguments["description"],
            expense_account=arguments["expense_account"],
            expense_account_name=arguments["expense_account_name"],
            gross_amount=arguments["gross_amount"],
            net_amount=arguments["net_amount"],
            vat_amount=arguments["vat_amount"],
            vat_rate=arguments["vat_rate"],
        )
        return [TextContent(type="text", text=result.model_dump_json(indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
