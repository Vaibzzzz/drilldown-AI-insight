from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry

# REST Routers
from API.API_Dashboard import router as dashboard_router
from API.financial_analysis_service import router as financial_analysis_router
from API.operational_ef import router as operational_efficiency_router
from API.DemoGraphic import router as demographic_router
from API.risk_and_fraud_management import router as risk_and_fraud_router
from API.customer_insight import router as customer_insight_router
from API.report import router as report_router

# GraphQL Schema
from graphql_local.financial_analysis_schema import Query  # This includes your `drillDown` field

# ─── Setup FastAPI ───────────────────────────────────────────────
app = FastAPI(title="A360 Prototype Dashboard API")

# ─── CORS Middleware ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REST API Routes ─────────────────────────────────────────────


# ─── Mount Correct GraphQL Schema ────────────────────────────────
schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
