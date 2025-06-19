from contestImageGenerator import ContestImageGenerator
import time
import threading
import sys

if __name__ == "__main__":
    start = time.time()
    generator = ContestImageGenerator(
        contestId=2121,
        descText="TOP 6 - Overall",
        imageSelected=0,
        regex=r"^(2023|2024|2022).{9}$",
        overrideContestName=False,
        overrideText="CODEFORCES Div. 2 Round 1025"
    )
    generator.generate()
    generator = ContestImageGenerator(
        contestId=2109,
        descText="TOP 6 - 2024 Batch",
        imageSelected=1,
        regex=r"^(2024).{9}$",
        overrideContestName=False,
        overrideText="CODEFORCES Div. 2 Round 1025"
    )
    generator.generate()
    generator = ContestImageGenerator(
        contestId=2121,
        descText="TOP 6 - 2023 Batch",
        imageSelected=2,
        regex=r"^(2023).{9}$",
        overrideContestName=False,
        overrideText="CODEFORCES Div. 2 Round 1025"
    )
    generator.generate()
    generator = ContestImageGenerator(
        contestId=2121,
        descText="TOP 6 - 2022 Batch",
        imageSelected=3,
        regex=r"^(2022).{9}$",
        overrideContestName=False,
        overrideText="CODEFORCES Div. 2 Round 1025"
    )
    generator.generate()

    # stop_spinner = False

    # def spinner():
    #     dots = ""
    #     while not stop_spinner:
    #         dots = "." if len(dots) >= 3 else dots + "."
    #         print(f"\r\033[93mProcessing{dots}  \033[0m", end="", flush=True)
    #         time.sleep(0.5)
    #     print("\r", end="")

    # t = threading.Thread(target=spinner)
    # t.start()

    # generator.generate()
    # stop_spinner = True

    # t.join()

    print(f"\033[94mThe operation took {(time.time() - start):.2f} seconds\033[0m")
