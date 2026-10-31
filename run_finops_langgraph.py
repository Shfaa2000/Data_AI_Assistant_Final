# واجهة CLI تقرأ سؤال المستخدم، تستدعي رحلة LangGraph، ثم تعرض النتيجة الموحدة أو الخطأ.

import json

from src.finops_assistant.langgraph_service import (
    answer_finops_with_langgraph,
)

def main() -> int:
    question = input(
        "Enter a FinOps question: "
    )

    try:
        result = (
            answer_finops_with_langgraph(
                question
            )
        )

        print()
        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        return 0

    except Exception as error:
        print()
        print("FinOps LangGraph: FAIL")
        print(
            f"Error type: "
            f"{type(error).__name__}"
        )
        print(
            f"Error message: {error}"
        )

        return 1

if __name__ == "__main__":
    raise SystemExit(
        main()
    )