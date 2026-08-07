from typing import Any

from langgraph.graph import END, START, StateGraph

from engines.common.agent_report_generation_node import AgentReportGenerationNode
from engines.common.report_persistence_node import ReportPersistenceNode
from engines.common.research_graph_runtime import (
    SECTION_SUMMARY_LOOP_MAPPING,
    ResearchRunContext,
    route_after_section_summary,
)
from engines.insight_agent.nodes.evidence_reranking_node import EvidenceRerankingNode
from engines.insight_agent.nodes.evidence_retrieval_node import EvidenceRetrievalNode
from engines.insight_agent.nodes.section_evidence_routing_node import (
    SectionEvidenceRoutingNode,
)
from engines.insight_agent.nodes.section_preparation_node import SectionPreparationNode
from engines.insight_agent.nodes.section_summary_node import SectionSummaryNode
from engines.insight_agent.state import InsightState


def build_graph(ctx: ResearchRunContext) -> Any:
    """构建并编译私域舆情智能体的 LangGraph 工作流。"""
    graph = StateGraph(InsightState)  # type: ignore
    graph.add_node("retrieve_evidence", EvidenceRetrievalNode(ctx))  # type: ignore
    graph.add_node("rerank_evidence", EvidenceRerankingNode(ctx))  # type: ignore
    graph.add_node("route_section_evidence",SectionEvidenceRoutingNode(ctx))  # type: ignore
    graph.add_node("prepare_sections", SectionPreparationNode(ctx))  # type: ignore
    graph.add_node("summarize_sections", SectionSummaryNode(ctx))  # type: ignore
    graph.add_node("generate_agent_report",AgentReportGenerationNode(ctx))  # type: ignore
    graph.add_node("persist_agent_report",ReportPersistenceNode(ctx))  # type: ignore
    graph.add_edge(START, "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "rerank_evidence")
    graph.add_edge("rerank_evidence", "route_section_evidence")
    graph.add_edge("route_section_evidence", "prepare_sections")
    graph.add_edge("prepare_sections", "summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING,
    )
    graph.add_edge("generate_agent_report", "persist_agent_report")
    graph.add_edge("persist_agent_report", END)
    return graph.compile()
