"""
ينظم رحلة FinOps Assistant باستخدام LangGraph،
مع إعادة استخدام Router وQuery وRAG الحاليين.
"""

from typing import TypedDict

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from src.finops_assistant.router import (
    route_question,
)

from src.finops_assistant.service import (
    build_unified_result,
    create_router_client,
    run_query_tool,
    run_rag_tool,
)

# تمثل الحقيبة المشتركة التي تنتقل
# بين جميع Nodes أثناء الرحلة.
class FinOpsGraphState(
    TypedDict,
    # ليس ضروريًا أن تكون جميع الحقول موجودة من البداية.
    total=False,
):
    question: str
    route: str
    reason: str
    clarification_question: str | None
    result: dict


def normalize_question_node(
    state: FinOpsGraphState,
) -> dict:
    question = state.get(
        "question",
        "",
    ).strip()

    if not question:
        raise ValueError(
            "The question is required."
        )

    return {
        "question": question,
    }

# يستدعي Router الحالي ويضيف
# قراره إلى State.
def router_node(
    state: FinOpsGraphState,
) -> dict:
    client, model_name = (
        create_router_client()
    )

    decision = route_question(
        client=client,
        question=state["question"],
        model_name=model_name,
    )

    route_value = getattr(
        
        decision.route,
        "value",
        decision.route,
    )

    return {
        "route": str(
            route_value
        ).strip().lower(),
        "reason": (
            decision.reason or ""
        ),
        "clarification_question": (
            decision.clarification_question
        ),
    }

# يحدد اسم الـNode التالية
# بناءً على قرار Router.
def select_route(
    state: FinOpsGraphState,
) -> str:
    route = state["route"]

    allowed_routes = {
        "query",
        "rag",
        "needs_clarification",
        "unsupported",
    }

    if route not in allowed_routes:
        raise ValueError(
            f"Unsupported route: {route}"
        )

    return route

# يشغل Query Tool الموجودة
# ويحفظ جوابها النهائي في State.
def query_node(
    state: FinOpsGraphState,
) -> dict:
    result = run_query_tool(
        state["question"]
    )

    return {
        "result": result,
    }

# يشغل RAG Tool الموجودة
# ويحفظ جوابها النهائي في State.
def rag_node(
    state: FinOpsGraphState,
) -> dict:
    result = run_rag_tool(
        state["question"]
    )

    return {
        "result": result,
    }


# يبني جواب التوضيح بالشكل
# الموحد المستخدم في المشروع.
def clarification_node(
    state: FinOpsGraphState,
) -> dict:
    answer = (
        state.get(
            "clarification_question"
        )
        or state.get(
            "reason",
            "",
        )
    )

    result = build_unified_result(
        status="needs_clarification",
        route="needs_clarification",
        answer=answer,
    )

    return {
        "result": result,
    }

# يبني جواب السؤال غير المدعوم
# من دون تشغيل Query أو RAG.
def unsupported_node(
    state: FinOpsGraphState,
) -> dict:
    result = build_unified_result(
        status="unsupported",
        route="unsupported",
        answer=state.get(
            "reason",
            "",
        ),
    )

    return {
        "result": result,
    }

# ينشئ Graph ويضيف جميع Nodes.
graph_builder = StateGraph(
    # شكل State التي ستنتقل داخلها
    FinOpsGraphState
)

graph_builder.add_node(
    "normalize",
    normalize_question_node,
)

graph_builder.add_node(
    "router",
    router_node,
)

graph_builder.add_node(
    "query_tool",
    query_node,
)

graph_builder.add_node(
    "rag_tool",
    rag_node,
)

graph_builder.add_node(
    "clarification",
    clarification_node,
)

graph_builder.add_node(
    "unsupported",
    unsupported_node,
)

# يبدأ بتنظيف السؤال ثم ينتقل
# دائمًا إلى Router.
graph_builder.add_edge(
    START,
    "normalize",
)

graph_builder.add_edge(
    "normalize",
    "router",
)


# يختار الفرع التالي حسب
# route الموجودة داخل State.
graph_builder.add_conditional_edges(
    "router",
    select_route,
    {
        "query": "query_tool",
        "rag": "rag_tool",
        "needs_clarification": (
            "clarification"
        ),
        "unsupported": "unsupported",
    },
)

# تنتهي الرحلة بعد تنفيذ
# أي فرع من الفروع النهائية.
graph_builder.add_edge(
    "query_tool",
    END,
)

graph_builder.add_edge(
    "rag_tool",
    END,
)

graph_builder.add_edge(
    "clarification",
    END,
)

graph_builder.add_edge(
    "unsupported",
    END,
)

# يحول مخطط Graph إلى
# تطبيق قابل للتنفيذ.
finops_graph = (
    graph_builder.compile()
)

# يشغل Graph كاملة ويرجع
# العقد الموحد النهائي فقط.
def answer_finops_with_langgraph(
    question: str,
) -> dict:
    final_state = finops_graph.invoke(
        {
            "question": question,
        }
    )

    return final_state["result"]