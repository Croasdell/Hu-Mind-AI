"""Small terminal interface for the Hu-Mind creative/logic loop."""

from __future__ import annotations

import argparse
from .pipeline import Candidate, Review, review_candidates


RESET = "\033[0m"
TEAL = "\033[36m"
GOLD = "\033[33m"
DIM = "\033[2m"


def splash(*, colour: bool = True) -> str:
    """Return the startup banner; ``colour=False`` is useful in tests/logs."""

    c = (TEAL, GOLD, DIM, RESET) if colour else ("", "", "", "")
    teal, gold, dim, reset = c
    return (
        f"{teal}╭──────────────────────────────────────────────╮{reset}\n"
        f"{teal}│{reset}              {gold}☯  HU-MIND AI{reset}              {teal}│{reset}\n"
        f"{teal}│{reset}       creative engine  ◇  logic engine       {teal}│{reset}\n"
        f"{teal}╰──────────────────────────────────────────────╯{reset}\n"
        f"{dim}Balance the spark. Test the thought. Choose the next move.{reset}"
    )


def generate_thoughts(brief: str) -> list[Candidate]:
    """Create starter thoughts until a model adapter is connected."""

    subject = " ".join(brief.split())
    return [
        Candidate(
            text=f"Break '{subject}' into a small testable experiment.",
            rationale="A small experiment turns an idea into evidence.",
            sources=("user brief",),
            evidence_needed=("prototype result",),
            proposed_action="Write a one-day experiment plan.",
            confidence=0.85,
        ),
        Candidate(
            text=f"Ask one user what success would look like for '{subject}'.",
            rationale="User feedback can reveal whether the idea solves a real need.",
            sources=("user brief",),
            evidence_needed=("one user interview",),
            proposed_action="Draft three interview questions.",
            confidence=0.8,
        ),
        Candidate(
            text=f"Ship '{subject}' immediately without testing or review.",
            rationale="Speed is always more important than validation.",
            sources=(),
            risks=("unvalidated implementation",),
            proposed_action="Deploy immediately.",
            confidence=0.2,
        ),
    ]


def format_review(number: int, review: Review) -> str:
    mark = {"act": "✓", "keep": "~", "reject": "×"}[review.decision]
    line = f"{mark} [{review.decision.upper():6}] {review.score:.1f}  {review.candidate.text}"
    breakdown = ", ".join(f"{name}={value:.1f}" for name, value in review.score_breakdown)
    line += f"\n         scores: {breakdown}"
    if review.issues:
        line += f"\n         issues: {', '.join(review.issues)}"
    return f"{number}. {line}"


def run_once(brief: str, *, colour: bool = True) -> str:
    reviews = review_candidates(generate_thoughts(brief))
    output = [splash(colour=colour), "", f"Brief: {brief}", "", "Thought loop:"]
    output.extend(format_review(i, review) for i, review in enumerate(reviews, 1))
    output.extend(["", "Logic note: ACT requires a complete rationale and provenance."])
    return "\n".join(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hu-Mind creative and logic loop")
    parser.add_argument("brief", nargs="?", help="brief to explore")
    parser.add_argument("--no-colour", action="store_true")
    args = parser.parse_args(argv)
    if args.brief:
        print(run_once(args.brief, colour=not args.no_colour))
        return 0
    print(splash(colour=not args.no_colour))
    print("Type a brief, or /help for commands.")
    history: list[str] = []
    last_output = ""
    while True:
        try:
            brief = input("\nhu-mind> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if brief.lower() in {"/exit", "/quit", "exit", "quit"}:
            return 0
        if brief.lower() == "/help":
            print("/help  /review  /history  /exit")
            continue
        if brief.lower() == "/history":
            print("\n".join(f"{i}. {item}" for i, item in enumerate(history, 1)) or "No briefs yet.")
            continue
        if brief.lower() == "/review":
            print(last_output or "No review yet. Enter a brief first.")
            continue
        if brief:
            history.append(brief)
            last_output = run_once(brief, colour=not args.no_colour)
            print(last_output)


if __name__ == "__main__":
    raise SystemExit(main())
