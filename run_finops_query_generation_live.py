"""
واجهة CLI بسيطة لرحلة FinOps Assistant.

تقرأ سؤال المستخدم من Terminal، وترسله إلى Assistant Service،
ثم تعرض النتيجة المنظمة دون أن تكرر منطق Gemini أو BigQuery.
"""

from src.finops_query.assistant_service import (
    FinOpsAssistantResult,
    answer_finops_question,
)
import json


# يعرض ملخص الرحلة المالية
def print_assistant_result(
    result: FinOpsAssistantResult,
) -> None:
    plan = (
        result.query_generation.plan
        .model_dump(
            mode="json",
            exclude_none=True,
        )
    )

    print("Assistant Core: PASS")
    print(f"Status: {result.status}")
    print(
        f"Question: "
        f"{result.user_question}"
    )
    print(
        f"Model: "
        f"{result.model_name}"
    )
    print(
        f"BigQuery source: "
        f"{result.allowed_table}"
    )
    print(
        f"Location: "
        f"{result.location}"
    )

    print()
    print("Query Plan:")
    print(
        f"  Intent: "
        f"{plan['intent']}"
    )

    metrics = plan.get(
        "metrics",
        [],
    )

    if metrics:
        metric_text = ", ".join(
            (
                f"{metric['aggregation']}"
                f"({metric['name']})"
            )
            for metric in metrics
        )

        print(
            f"  Metrics: {metric_text}"
        )

    dimensions = plan.get(
        "dimensions",
        [],
    )

    if dimensions:
        print(
            "  Dimensions: "
            + ", ".join(dimensions)
        )

    filters = plan.get(
        "filters",
        [],
    )

    if filters:
        print("  Filters:")

        for filter_item in filters:
            print(
                "    - "
                f"{filter_item['column']} "
                f"{filter_item['operator']} "
                f"{filter_item['value']}"
            )

    time_range = plan.get(
        "time_range"
    )

    if time_range:
        print(
            "  Time range: "
            f"{time_range['start']} "
            "to "
            f"{time_range['end']}"
        )

    if plan.get("sort_by"):
        print(
            "  Sort: "
            f"{plan['sort_by']} "
            f"{plan['sort_direction']}"
        )

    if dimensions:
        print(
            f"  Limit: "
            f"{plan['limit']}"
        )

    proposal = (
        result.query_generation
        .sql_proposal
    )

    if proposal is None:
        print()
        print("SQL Proposal: SKIPPED")
        print(f"Message: {result.message}")
        return

    print()
    print("SQL Proposal:")
    print(proposal.sql)

    if proposal.parameters:
        print("Parameters:")

        for parameter in (
            proposal.parameters
        ):
            data_type = getattr(
                parameter.data_type,
                "value",
                parameter.data_type,
            )

            print(
                "  - "
                f"{parameter.name} "
                f"({data_type}) = "
                f"{parameter.value}"
            )

    print()
    print("Validation:")
    print("  Local SQL validation: PASS")

    if result.dry_run_report:
        print("  BigQuery Dry Run: PASS")
        print(
            "  Estimated bytes: "
            f"{result.dry_run_report.total_bytes_processed}"
        )

    if result.status == "dry_run_only":
        print()
        print(result.message)
        return

    print("  BigQuery execution: PASS")
    print(
        "  Query result validation: PASS"
    )

    evidence = result.dynamic_evidence

    if evidence is not None:
        evidence_payload = (
            evidence.model_dump(
                mode="json"
            )
        )

        print()
        print("Dynamic Evidence:")
        print(
            "  Columns: "
            + ", ".join(
                evidence_payload[
                    "columns"
                ]
            )
        )
        print(
            "  Row count: "
            f"{evidence_payload['row_count']}"
        )
        print("  Rows:")
        print(
            json.dumps(
                evidence_payload["rows"],
                indent=2,
                ensure_ascii=False,
            )
        )

    final_answer = (
        result.final_answer
    )

    if final_answer is not None:
        print()
        print(
            "Final answer generation: PASS"
        )
        print(
            "Final answer validation: PASS"
        )
        print()
        print("Final Answer:")
        print(final_answer.answer)

        if (
            final_answer
            .evidence_references
        ):
            print()
            print(
                "Grounding References:"
            )

            for reference in (
                final_answer
                .evidence_references
            ):
                print(
                    "  - Row "
                    f"{reference.row_index}: "
                    + ", ".join(
                        reference.columns
                    )
                )

# يقرأ السؤال ويستدعي القلب المشترك ثم يعرض النتيجة.
def main() -> int:
    user_question = input(
        "Enter an English financial question: "
    ).strip()

    if not user_question:
        print("FinOps assistant: FAIL")
        print("Error type: ValueError")
        print("Error message: The user question is required.")
        return 1

    try:
        result = answer_finops_question(user_question)
    except Exception as exc:
        print("FinOps assistant: FAIL")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error message: {exc}")
        return 1

    print_assistant_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

