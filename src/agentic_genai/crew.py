from __future__ import annotations

from dataclasses import dataclass

from crewai import Agent, Crew, LLM, Process, Task

from agentic_genai.config import Settings
from agentic_genai.tools import search_web


@dataclass
class CrewRunResult:
    research_report: str
    teaching_summary: str


def build_topic_crew(settings: Settings) -> Crew:
    llm = LLM(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.25,
        max_tokens=900,
    )

    research_agent = Agent(
        role="Research Agent",
        goal="Investigate the topic with the discipline and rigor of a senior data analyst.",
        backstory=(
            "You are an analytical researcher who gathers facts, identifies trends, "
            "compares viewpoints, and produces structured notes with source links."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
    )

    summarize_agent = Agent(
        role="Summarize Agent",
        goal="Teach the researched topic clearly like an expert teacher or subject specialist.",
        backstory=(
            "You turn dense research into clear explanations, using a warm teaching style, "
            "simple language, and strong examples without losing accuracy."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=2,
    )

    research_task = Task(
        description=(
            "Research the topic '{topic}'. Use the uploaded PDF context as the primary source, "
            "then use the provided web findings only to add helpful supporting context. "
            "Produce a markdown report with these sections: Overview, Key Facts, Important Trends "
            "or Ideas, Real-World Examples, PDF Evidence, and Sources. Keep the report compact and under 400 words."
            "\n\nUploaded PDF context:\n{pdf_context}"
            "\n\nWeb findings:\n{search_context}"
        ),
        expected_output=(
            "A factual markdown research brief with source links and concise analysis."
        ),
        agent=research_agent,
    )

    summarize_task = Task(
        description=(
            "Use the research report to teach the topic '{topic}' like a subject expert teacher. "
            "Write a student-friendly explanation in markdown with these sections: "
            "What It Means, Why It Matters, Step-by-Step Explanation, and Quick Recap. "
            "Use examples where useful, keep the tone encouraging, and keep the full answer under 300 words."
        ),
        expected_output=(
            "A clear teaching-style explanation based on the research report."
        ),
        agent=summarize_agent,
        context=[research_task],
    )

    return Crew(
        agents=[research_agent, summarize_agent],
        tasks=[research_task, summarize_task],
        process=Process.sequential,
        verbose=False,
    )


def run_topic_crew(
    topic: str,
    settings: Settings,
    pdf_context: str = "No PDF was uploaded. Use web findings as the source material.",
) -> CrewRunResult:
    if not settings.groq_api_key:
        raise ValueError("Missing GROQ_API_KEY. Add it to your environment or .env file.")

    try:
        search_context = search_web(f"{topic} overview trends examples")
    except Exception as exc:
        search_context = f"Web search failed: {exc}"

    crew = build_topic_crew(settings)
    result = crew.kickoff(
        inputs={
            "topic": topic,
            "pdf_context": pdf_context,
            "search_context": search_context,
        }
    )

    tasks_output = getattr(result, "tasks_output", None)
    if tasks_output and len(tasks_output) >= 2:
        research_report = getattr(tasks_output[0], "raw", str(tasks_output[0]))
        teaching_summary = getattr(tasks_output[1], "raw", str(tasks_output[1]))
    else:
        research_report = str(result)
        teaching_summary = str(result)

    return CrewRunResult(
        research_report=research_report,
        teaching_summary=teaching_summary,
    )
