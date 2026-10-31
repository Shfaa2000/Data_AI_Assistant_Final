# FinOps Dynamic Query Feature Contract

## 1. Feature Name

FinOps Dynamic Query Generation and Validation V1

## 2. Problem

The current Narrative V1 reads financial values from a prebuilt
verified Evidence file.

The new feature must allow a user to ask an English financial question,
let Gemini propose a structured query plan and GoogleSQL query, validate
the generated query, execute it safely against an allowed BigQuery
table, and use the verified result to generate an English narrative.

The system must not trust or execute Gemini-generated SQL directly.

## 3. Goal

Convert an English financial question into a safe, validated,
read-only BigQuery query, execute it, transform the result into
Dynamic Evidence, and generate a grounded English answer.

## 4. Input Contract

The client sends only:

```json
{
  "question": "Which AWS service has the highest billed cost?"
}
```
Input Rules
question is required.
question must be a non-empty string.
The first version expects English questions.
The client must not send SQL.
The client must not send a complete prompt.
The client must not send a table name.
The client must not send Gemini API credentials.
The client must not send BigQuery credentials.
The client must not select the Gemini model.
5. Main Processing Flow
English User Question
→ FinOps Query Plan
→ Generated GoogleSQL
→ Structural Validation
→ SQL Safety Validation
→ Semantic Validation
→ BigQuery Dry Run
→ BigQuery Execution
→ Query Result Validation
→ Dynamic Evidence
→ Narrative V1
→ English Answer
6. Responsibilities
Gemini Query Generator

Gemini may:

Understand the user's question.
Identify the financial intent.
Identify required metrics.
Identify required dimensions.
Identify required aggregations.
Identify filters.
Identify a time range.
Identify sorting and limit requirements.
Return a structured FinOps Query Plan.
Propose a GoogleSQL query.

Gemini must not:

Execute the query.
Receive BigQuery credentials.
access BigQuery directly.
Decide by itself that a query is safe.
Change data in BigQuery.
Answer using external financial knowledge.
Backend

The Backend must:

Provide Gemini with the allowed semantic schema.
Receive the FinOps Query Plan and proposed SQL.
Validate the structured output.
Validate tables and columns.
Validate that the query is read-only.
Compare the SQL with the FinOps Query Plan.
Perform a BigQuery Dry Run.
Enforce a maximum bytes billed limit.
Execute only accepted queries.
Validate the query result.
Build Dynamic Evidence.
Pass verified data to Narrative V1.
Return the final response to the client.
Record a safe diagnostic trace.
BigQuery

BigQuery must:

Validate the query during Dry Run.
Execute accepted read-only SQL.
Return query metadata.
Return the actual result rows.
Never expose credentials to Gemini.
7. Query Statuses
ready

The question is clear and supported.

Requirements:

At least one allowed metric exists.
The required dimensions are known.
Filters are valid.
The query can be generated.
needs_clarification

The question is ambiguous.

Example:

What is the cost?

The system must ask whether the user means billed cost,
effective cost, or another available metric.

No SQL may be executed.

unsupported

The question requires data or capabilities that are unavailable.

Examples:

Resource utilization without utilization metrics.
Forecasting without forecasting data.
A provider that does not exist in the allowed dataset.
A metric outside the allowed schema.

No SQL may be executed.

failed

A technical operation failed after a supported request was accepted.

Examples:

Invalid generated SQL.
Dry Run failure.
BigQuery connection failure.
Query result contract failure.
Gemini provider failure.
8. Supported MVP Capabilities

The first version supports:

Total billed cost.
Total effective cost.
Total negative billed cost.
Grouping by provider.
Grouping by service.
Grouping by currency.
Filtering by provider.
Filtering by service.
Filtering by currency.
Simple date ranges after physical date columns are verified.
Top-N queries.
Ascending or descending sorting.
Basic aggregations:
SUM
AVG
MIN
MAX
COUNT
9. MVP Restrictions

The first version does not support:

INSERT.
UPDATE.
DELETE.
DROP.
ALTER.
CREATE.
MERGE.
TRUNCATE.
EXPORT.
Stored procedures.
Multi-statement SQL.
Arbitrary projects or datasets.
Arbitrary table names.
Arbitrary column names.
Joins.
Nested subqueries unless added later.
Forecasting.
Utilization analysis without utilization data.
Unlimited result rows.
Unlimited repair attempts.
10. Allowed Data Sources

The first version may access only explicitly allowed tables.

Initial allowed table:

data-ai-assistant-training.cloud_finops.billing_pipeline_day2

The physical table and column names must be verified against
BigQuery INFORMATION_SCHEMA before real query execution is enabled.

11. Semantic Schema

The initial semantic metrics are:

billed_cost
effective_cost
negative_billed_cost

The initial semantic dimensions are:

provider
service
currency

The initial aggregations are:

sum
avg
min
max
count

The semantic field names do not automatically guarantee that the
physical BigQuery columns use the same names.

A verified physical column mapping will be added after reading
BigQuery INFORMATION_SCHEMA.

12. SQL Safety Rules

A generated query must:

Use GoogleSQL.
Be read-only.
Contain one query statement only.
Use only an allowed table.
Use only allowed columns.
Use approved aggregations.
Use parameters for user-provided values.
Apply an output row limit.
Pass local validation.
Pass semantic validation.
Pass BigQuery Dry Run.
Stay below the maximum bytes billed limit.

A generated query must be rejected before execution if any safety
rule fails.

13. Semantic Validation Rules

The Backend must verify that:

Requested metrics appear in the SQL.
Requested dimensions appear in SELECT or GROUP BY.
Required filters appear in the query.
Requested aggregation matches the SQL.
Top-N questions include sorting and a limit.
Highest-value questions use descending order.
Lowest-value questions use ascending order.
Time-based questions use the verified date column.
The SQL meaning matches the FinOps Query Plan.
14. Dry Run Rules

Before execution, the Backend must perform a BigQuery Dry Run.

The Dry Run must:

Validate SQL syntax.
Validate referenced tables.
Validate referenced columns.
Estimate bytes processed.
Reject queries that exceed the configured limit.

Dry Run success does not prove that the SQL semantically answers
the user's question.

15. Query Result Validation

The Backend must validate:

Returned column names.
Returned value types.
Maximum row count.
Required metrics.
Currency when applicable.
Empty result handling.
Unexpected null values.
Result shape expected by the Query Plan.

An empty result must not be converted into an invented answer.

16. Dynamic Evidence

A successful BigQuery result becomes per-request Dynamic Evidence.

Dynamic Evidence may contain:

User question.
FinOps Query Plan.
Query identifier or hash.
BigQuery Job ID.
Source table.
Referenced columns.
Execution timestamp.
Bytes processed.
Result schema.
Result rows or normalized metrics.
Currency.
Limitations.
Verification status.

Dynamic Evidence must not overwrite Latest Verified Evidence.

17. Narrative Generation

Narrative V1 receives only verified Dynamic Evidence.

The narrative must:

Be written in clear English.
Use only the supplied Dynamic Evidence.
Not invent financial values.
Preserve currencies and values.
Return unsupported when the evidence is insufficient.
Pass Pydantic validation.
Pass numeric grounding.
18. Repair Policy

If Gemini proposes invalid SQL:

Reject the SQL before execution.
Create a safe validation error.
Return only allowed schema information to Gemini.
Allow a maximum of two repair attempts.
Stop if the query remains invalid.

The system must never execute a rejected query.

19. Security Rules

The system must not expose:

Gemini API Key.
BigQuery credentials.
Environment variables.
Internal thought signatures.
Sensitive table data.
Full internal prompts in client responses.
Unrestricted schema metadata.

Gemini receives only the schema required for the supported use case.

20. Testing Strategy

The system must use:

Unit tests.
Fake Gemini responses.
Fake query plans.
Fake BigQuery execution for most tests.
Negative SQL tests.
Semantic validation tests.
Golden question tests.
Limited real Gemini smoke tests.
Limited real BigQuery integration tests.

Fake Gemini tests validate the application pipeline but do not prove
that real Gemini will generate correct queries.

21. Definition of Done

The feature is complete when:

A user submits an English financial question.
Gemini returns a structured FinOps Query Plan.
Gemini proposes GoogleSQL.
The Backend validates the query.
BigQuery Dry Run succeeds.
The Backend executes the accepted query.
The result becomes Dynamic Evidence.
Narrative V1 generates an English answer.
Validation and grounding succeed.
The client receives the answer and provenance.
Unsafe and unsupported questions are rejected safely.
Tests pass without requiring real Gemini for every run.