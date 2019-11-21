CREATE TYPE IF NOT EXISTS "personal-finance-engine-dev".TransactionType AS ENUM (
  'Income',
  'Expense',
  'Transfer'
);

CREATE TYPE IF NOT EXISTS "personal-finance-engine-dev".AccountType AS ENUM (
  'Credit',
  'Checking',
  'Saving'
);

CREATE TABLE IF NOT EXISTS "personal-finance-engine-dev"."BudgetItems" (
  "id" SERIAL PRIMARY KEY,
  "user_id" varchar,
  "amount" float,
  "description" varchar,
  "transaction_type" TransactionType,
  "frequency" int,
  "sample_date" date,
  "end_date" date,
  "created_at" timestamp,
  "simulation_id" int
);

CREATE TABLE IF NOT EXISTS "personal-finance-engine-dev"."AccountItems" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "balance" float,
  "type" AccountType
);

CREATE TABLE IF NOT EXISTS "personal-finance-engine-dev"."ForecastedDays" (
  "id" int PRIMARY KEY,
  "user_id" varchar,
  "forecast_day" date,
  "total" float,
  "account_totals" json,
  "simulation_id" int
);

CREATE TABLE IF NOT EXISTS "personal-finance-engine-dev"."Simulations" (
  "id" int PRIMARY KEY,
  "user_id" varchar,
  "created_at" timestamp
);

CREATE TABLE IF NOT EXISTS "personal-finance-engine-dev"."Users" (
  "id" varchar PRIMARY KEY,
  "is_paying" boolean,
  "email" varchar,
  "created_at" timestamp,
  "updated_at" timestamp
);

ALTER TABLE "personal-finance-engine-dev"."BudgetItems" ADD FOREIGN KEY ("user_id") REFERENCES "personal-finance-engine-dev"."Users" ("id");

ALTER TABLE "personal-finance-engine-dev"."BudgetItems" ADD FOREIGN KEY ("simulation_id") REFERENCES "personal-finance-engine-dev"."Simulations" ("id");

ALTER TABLE "personal-finance-engine-dev"."ForecastedDays" ADD FOREIGN KEY ("user_id") REFERENCES "personal-finance-engine-dev"."Users" ("id");

ALTER TABLE "personal-finance-engine-dev"."ForecastedDays" ADD FOREIGN KEY ("simulation_id") REFERENCES "personal-finance-engine-dev"."Simulations" ("id");

ALTER TABLE "personal-finance-engine-dev"."Simulations" ADD FOREIGN KEY ("user_id") REFERENCES "personal-finance-engine-dev"."Users" ("id");
