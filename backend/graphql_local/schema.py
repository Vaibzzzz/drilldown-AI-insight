import strawberry
from graphql_local.financial_analysis_schema import Query as FinancialQuery
# Import other dashboards as needed

@strawberry.type
class Query(FinancialQuery ):  # Inherit other query classes if needed
    pass

schema = strawberry.Schema(Query)
