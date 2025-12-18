from __future__ import annotations
import textwrap
from dataclasses import dataclass
from pathlib import Path

from repropilot.core.agent import ReproPilotAgent


@dataclass
class ReproducePaperWorkflow:
    agent: ReproPilotAgent
    workspace_dir: str

    def run(self, paper_pdf: str, out_repo: str) -> str:
        ws = Path(self.workspace_dir).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        paper = Path(paper_pdf).resolve()
        out = Path(out_repo).resolve()
        out.mkdir(parents=True, exist_ok=True)

        required_files = [
            out / "README.md",
            out / "CITATION.cff",
            out / ".gitignore",
            out / "requirements.txt",
            out / "configs" / "default.yaml",
            out / "src" / "train.py",
            out / "src" / "eval.py",
            out / "src" / "data.py",
            out / "tests" / "test_imports.py",
            out / "reports" / "reproducibility_report.md",
        ]

        req_list = "\n".join(f"- {p.as_posix()}" for p in required_files)

        goal = textwrap.dedent(f"""
        You are running inside a tool loop.

        CRITICAL RULES:
        - You must respond ONLY with JSON objects (type=tool_call or type=final).
        - You MUST create ALL required files using the write_file tool.
        - You MUST NOT return type="final" until every required file exists on disk.

        Paper path: {paper.as_posix()}
        Output repo: {out.as_posix()}

        Required files to create:
        {req_list}

        Steps:
        1) Call read_pdf_text on the paper.
        2) Extract: problem, dataset, model, metrics, training details, eval protocol.
        3) Use write_file to create EVERY required file listed above.
        - Put real, runnable placeholder code (not empty files).
        - README must include: setup, where to put data, how to train/eval, how to reproduce.
        4) Use safe_shell to verify:
        - python -m compileall "{out.as_posix()}"
        - python -m pytest -q "{out.as_posix()}"
        5) Only then return type="final" with a short summary of what you created.
        """).strip()

        result = self.agent.run(goal=goal)

        missing = [p for p in required_files if not p.exists()]
        if missing:
            missing_list = "\n".join(f"- {p.as_posix()}" for p in missing)
            followup = textwrap.dedent(f"""
            You returned final too early. These files are still missing:

            {missing_list}

            Create ALL missing files now using write_file, then rerun:
            - python -m compileall "{out.as_posix()}"
            - python -m pytest -q "{out.as_posix()}"

            Do NOT return type="final" until they exist.
            """).strip()
            result = self.agent.run(goal=followup)

        return result

