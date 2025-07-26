from datetime import date
from typing import List, Optional
from sqlalchemy import text
from DB.connector import get_engine
from KPI.utils.time_utils import get_date_ranges  # Custom util for date filtering
import strawberry

# --- DB Engine ---
engine = get_engine()

# --- Output Types ---
@strawberry.type
class FinancialData:
    title: str
    x: List[str]
    y: List[float]

@strawberry.type
class BreakdownData:
    label: str
    value: float

@strawberry.type
class DrillDownResponse:
    paymentMethods: List[BreakdownData]
    transactionTypes: List[BreakdownData]
    currencies: List[BreakdownData]

# --- Query Root ---
@strawberry.type
class Query:
    @strawberry.field
    def financial_data(
        self,
        filter_type: Optional[str] = "YTD",
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> FinancialData:
        """
        Returns daily revenue time series for the selected period.
        """
        start_date, end_date, _, _ = get_date_ranges(filter_type, start, end)

        sql = text("""
            SELECT 
                DATE(created_at) AS tx_date,
                SUM(amount) AS revenue
            FROM live_transactions
            WHERE created_at BETWEEN :start AND :end
            GROUP BY tx_date
            ORDER BY tx_date
        """)

        with engine.connect() as conn:
            results = conn.execute(sql, {"start": start_date, "end": end_date}).fetchall()

        x = [str(row[0]) for row in results]
        y = [float(row[1]) for row in results]

        return FinancialData(title="Revenue Over Time", x=x, y=y)

    @strawberry.field
    def revenue_breakdown_by_date(self, date: date) -> DrillDownResponse:
        """
        Returns a breakdown of revenue by payment method, transaction type,
        and currency (country code) for the selected date.
        """
        with engine.connect() as conn:
            # Payment Methods
            result_pm = conn.execute(text("""
                SELECT credit_card_type AS label, SUM(amount) AS value
                FROM live_transactions
                WHERE DATE(created_at) = :selected_date
                GROUP BY credit_card_type
            """), {"selected_date": date}).fetchall()

            # Transaction Types
            result_tt = conn.execute(text("""
                SELECT transaction_type AS label, SUM(amount) AS value
                FROM live_transactions
                WHERE DATE(created_at) = :selected_date
                GROUP BY transaction_type
            """), {"selected_date": date}).fetchall()

            # Currencies / Country Code
            result_cur = conn.execute(text("""
                SELECT country_code AS label, SUM(amount) AS value
                FROM live_transactions
                WHERE DATE(created_at) = :selected_date
                GROUP BY country_code
            """), {"selected_date": date}).fetchall()

        def to_breakdown(rows):
            return [
                BreakdownData(label=row[0] or "Unknown", value=float(row[1]))
                for row in rows
            ]

        return DrillDownResponse(
            paymentMethods=to_breakdown(result_pm),
            transactionTypes=to_breakdown(result_tt),
            currencies=to_breakdown(result_cur),
        )

# --- GraphQL Schema ---
schema = strawberry.Schema(query=Query)
