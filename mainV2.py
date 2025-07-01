from contestImageGenerator_V2 import ContestImageGeneratorV2
from rich.prompt import Prompt
from rich.console import Console
import time
import threading
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Generate XKCD-style contest image for Instagram story.")
    parser.add_argument("--contest-id", type=int, help="Unique numeric ID of the contest (e.g., 1234)")
    parser.add_argument("--regex-years", type=str, help="Regex to filter years (e.g., 2022|2023|2024)")
    parser.add_argument("--desc-text", type=str, help="Description text for the contest image")
    parser.add_argument("--override-contest-name", action="store_true", help="Override contest name on the image")
    parser.add_argument("--override-text", type=str, help="Text to replace contest name on the image")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    console = Console()

    # Prompt for missing arguments
    if args.contest_id is None:
        console.print("[dim]This is the unique numeric ID of the contest (e.g., 1234).[/]")
        contest_id = int(Prompt.ask(
            "[bold cyan]Enter contest ID[/]",
            console=console
        ))
        print()
    else:
        contest_id = args.contest_id

    if args.regex_years is None:
        console.print("[dim]This regex will be used to filter years (e.g., 2022|2023|2024 or 2023 or 2023|2023).[/]")
        regex_years = Prompt.ask(
            "[bold cyan]Enter years for regex (e.g. 2022|2023|2024)[/]",
            default="2022|2023|2024",
            console=console
        )
        print()
    else:
        regex_years = args.regex_years

    if args.desc_text is not None:
        desc_text = args.desc_text
    elif (regex_years != "2023" and regex_years != "2022" and regex_years != "2021" and regex_years != "2024" and regex_years != "2022|2023|2024"):
        console.print("[dim]This text will appear as the description on the contest image.[/]")
        desc_text = Prompt.ask(
            "[bold cyan]Enter description text[/]",
            default="TOP 6 - Overall",
            console=console
        )
        print()
    elif (regex_years == "2024"):
        desc_text = "TOP 6 - 2024 Batch"
    elif (regex_years == "2023"):
        desc_text = "TOP 6 - 2023 Batch"
    elif (regex_years == "2022"):
        desc_text = "TOP 6 - 2022 Batch"
    elif (regex_years == "2021"):
        desc_text = "TOP 6 - 2021 Batch"
    elif (regex_years == "2022|2023|2024"):
        desc_text = "TOP 6 - Overall"

    if args.override_contest_name:
        override_contest_name = True
    else:
        console.print("[dim]Choose 'y' if you want to provide a custom contest name for the image.[/]")
        override_contest_name = Prompt.ask(
            "[bold cyan]Override contest name? (y/n)[/]",
            default="n",
            console=console
        ).strip().lower() == "y"
        print()

    if args.override_text is not None:
        override_text = args.override_text
    elif override_contest_name:
        console.print("[dim]This text will replace the contest name on the image.[/]")
        override_text = Prompt.ask(
            "[bold cyan]Enter override text[/]",
            default="CODEFORCES Div. 2 Round 1025",
            console=console
        )
        print()
    else:
        override_text = None

    regex = rf"^({regex_years}).{{9}}$"

    console.print("[green]Generating XKCD-style contest image with the following parameters:[/]")
    console.print(f"contestId: {contest_id}")
    console.print(f"descText: {desc_text}")
    console.print(f"regex: {regex}")
    console.print(f"overrideContestName: {override_contest_name}")
    console.print(f"overrideText: {override_text if override_contest_name else 'N/A'}")

    generator = ContestImageGeneratorV2(
        contestId=contest_id,
        descText=desc_text,
        regex=regex,
        overrideContestName=override_contest_name,
        overrideText=override_text
    )

    start = time.time()
    stop_spinner = False

    def spinner():
        dots = ""
        while not stop_spinner:
            dots = "." if len(dots) >= 3 else dots + "."
            print(f"\r\033[93mProcessing{dots}  \033[0m", end="", flush=True)
            time.sleep(0.5)
        print("\r", end="")

    t = threading.Thread(target=spinner)
    t.start()

    generator.generate()

    stop_spinner = True
    t.join()

    print(f"\033[94mThe operation took {(time.time() - start):.2f} seconds\033[0m") 