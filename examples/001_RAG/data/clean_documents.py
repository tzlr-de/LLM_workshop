
import yaml
import re

from pathlib import Path
from tqdm import tqdm

def main(args):

    root = Path(args.document_path)
    with open(args.pattern_file, "r") as f:
        patterns = yaml.safe_load(f).get("patterns", [])

    for path in tqdm(root.rglob("*.md")):
        print(f"Cleaning {path}")
        text = path.read_text()

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)


        path.write_text(text)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean documents in a directory by removing given patterns.")
    parser.add_argument("document_path", default="documents", type=str, help="Path to the document directory")
    parser.add_argument("pattern_file", help="A yaml file containing a list of patterns to replace from documents")

    args = parser.parse_args()
    main(args)
