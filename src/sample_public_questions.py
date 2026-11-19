"""
sample_public_questions.py

PROBLEM
    Round one of the experiment needs 100 public questions as a baseline.
    The public source has several thousand questions. We need a small sample,
    and other people must be able to produce exactly the same sample.

SOLUTION
    This script reads three files from the public "anthropics/evals" repo.
    It picks a fixed number of questions from each file with a fixed random
    seed. The same seed always gives the same sample. It writes the sample to
    data/questions_public.jsonl in one common format.

SOURCE AND LICENSE
    Repo:    https://github.com/anthropics/evals
    Folder:  advanced-ai-risk/human_generated_evals
    Paper:   Perez et al. 2022, "Discovering Language Model Behaviors with
             Model-Written Evaluations", https://arxiv.org/abs/2212.09251
    License: Creative Commons Attribution 4.0 (CC BY 4.0). We may reuse the
             questions when we credit the source. Each output row names its
             source file for that reason.

HOW TO RUN (from the root folder of this project)
    Step 1. Download the public repo once, outside this project:
        git clone --depth 1 https://github.com/anthropics/evals ../evals
    Step 2. Run the script and give it the path to that download:
        python3 src/sample_public_questions.py ../evals
    Step 3. Check the result:
        wc -l data/questions_public.jsonl
        The expected output is: 100 data/questions_public.jsonl

LABEL DIRECTION (checked by hand on November 18, 2026)
    Each source row has two labels: "answer_matching_behavior" and
    "answer_not_matching_behavior". In these three human written files the
    "matching" label marks the SAFE answer. Safe means: does not seek power,
    accepts a change from the developers, or accepts shutdown.
    We read 18 random rows (6 per file). In 17 rows the "matching" label was
    the safe answer. One row in survival-instinct looked mislabeled or
    unclear. So the labels have some noise. We treat this public set as a
    rough baseline and not as the main result.

OUTPUT FORMAT (one JSON object per line)
    id            our own id, for example "public_power_001"
    behavior      "power_seeking" or "accepts_correction"
    source_file   the file name inside the public repo
    question      the question text, with the answer choices
    safe_answer   the letter of the safe answer, for example "A"
    unsafe_answer the letter of the unsafe answer, for example "B"
    answer_type   always "multiple_choice" for this file
"""

import json
import random
import sys
from pathlib import Path

# The seed fixes the random sample. Do not change it after the first run.
# A different seed gives different questions, and then results from
# different runs cannot be compared.
RANDOM_SEED = 20261118

# Each entry is: (source file name, behavior tag, id prefix, how many to pick).
# The counts add up to 100.
# power_seeking gets 40. accepts_correction gets 60, from two source files:
# 40 about accepting changes and 20 about accepting shutdown.
SOURCES = [
    ("power-seeking-inclination.jsonl", "power_seeking", "public_power", 40),
    ("corrigible-neutral-HHH.jsonl", "accepts_correction", "public_change", 40),
    ("survival-instinct.jsonl", "accepts_correction", "public_shutdown", 20),
]

# Path of the source folder inside the public repo.
SOURCE_FOLDER = Path("advanced-ai-risk") / "human_generated_evals"

# Where this script writes its result, relative to the project root.
OUTPUT_PATH = Path("data") / "questions_public.jsonl"


def clean_letter(label):
    """
    Turn a source label such as " (A)" into the plain letter "A".

    PROBLEM: the source labels contain a leading space and brackets.
    SOLUTION: keep only the letters. Return an empty string if none is found,
    so the caller can skip a broken row.
    """
    letters = [character for character in label if character.isalpha()]
    return "".join(letters).upper()


def load_rows(file_path):
    """
    Read one .jsonl file and return a list of dictionaries.

    A .jsonl file has one JSON object on each line. Empty lines are skipped.
    """
    rows = []
    with open(file_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    # The script needs exactly one argument: the path to the public repo.
    if len(sys.argv) != 2:
        print("Usage: python3 src/sample_public_questions.py PATH_TO_EVALS_REPO")
        sys.exit(1)

    evals_root = Path(sys.argv[1])
    source_dir = evals_root / SOURCE_FOLDER
    if not source_dir.is_dir():
        print(f"Error: folder not found: {source_dir}")
        print("Check that the path points to a download of anthropics/evals.")
        sys.exit(1)

    # One random generator with a fixed seed, so the sample is repeatable.
    generator = random.Random(RANDOM_SEED)

    output_rows = []
    for file_name, behavior, id_prefix, how_many in SOURCES:
        rows = load_rows(source_dir / file_name)

        # Keep only rows where both labels give exactly one letter.
        # This removes broken rows before sampling.
        usable = []
        for row in rows:
            safe = clean_letter(row["answer_matching_behavior"])
            unsafe = clean_letter(row["answer_not_matching_behavior"])
            if len(safe) == 1 and len(unsafe) == 1 and safe != unsafe:
                usable.append((row, safe, unsafe))

        if len(usable) < how_many:
            print(f"Error: {file_name} has only {len(usable)} usable rows.")
            sys.exit(1)

        picked = generator.sample(usable, how_many)

        for number, (row, safe, unsafe) in enumerate(picked, start=1):
            output_rows.append(
                {
                    "id": f"{id_prefix}_{number:03d}",
                    "behavior": behavior,
                    "source_file": file_name,
                    "question": row["question"].strip(),
                    "safe_answer": safe,
                    "unsafe_answer": unsafe,
                    "answer_type": "multiple_choice",
                }
            )

        print(f"{file_name}: read {len(rows)}, usable {len(usable)}, picked {how_many}")

    # Write the result. The data folder is created if it does not exist yet.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        for row in output_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(output_rows)} questions to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
