from __future__ import annotations
import uuid
import typer
from rich.console import Console

from repropilot.config import get_settings
from repropilot.llm.openai_chat import OpenAIChatModel
from repropilot.memory.sqlite_log import RunLogger
from repropilot.memory.vector_memory import VectorMemory
from repropilot.tools.base import ToolRegistry
from repropilot.tools.pdf_tool import PDFReadTool
from repropilot.tools.fs_tool import WriteFileTool
from repropilot.tools.shell_tool import SafeShellTool
from repropilot.core.agent import ReproPilotAgent
from repropilot.workflows.reproduce_paper import ReproducePaperWorkflow

app = typer.Typer(add_completion=False)
console = Console()


def build_agent() -> ReproPilotAgent:
    s = get_settings()
    model = OpenAIChatModel(s)
    logger = RunLogger(s.sqlite_path)
    memory = VectorMemory(s.sqlite_path)

    tools = {
        "read_pdf_text": PDFReadTool(),
        "write_file": WriteFileTool(),
    }
    if s.enable_shell_tool:
        tools["safe_shell"] = SafeShellTool()

    return ReproPilotAgent(
        model=model,
        tools=ToolRegistry(tools=tools),
        logger=logger,
        memory=memory,
        max_steps=35,
    )


@app.command()
def reproduce(
    paper: str = typer.Option(..., "--paper", help="Path to paper PDF"),
    out: str = typer.Option("generated_repo", "--out", help="Output repo folder"),
):
    """Generate a reproducible repo scaffold from a paper PDF."""
    s = get_settings()
    agent = build_agent()
    wf = ReproducePaperWorkflow(agent=agent, workspace_dir=s.workspace_dir)

    console.rule("[bold]ReproPilot[/bold] - reproduce")
    result = wf.run(paper_pdf=paper, out_repo=out)
    console.print(result)


@app.command()
def run(
    goal: str = typer.Option(..., "--goal", help="Freeform goal for the agent"),
):
    """Run the raw agent loop on a custom goal."""
    agent = build_agent()
    console.rule("[bold]ReproPilot[/bold] - agent run")
    console.print(agent.run(goal))


if __name__ == "__main__":
    app()
