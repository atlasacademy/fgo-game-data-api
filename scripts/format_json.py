import argparse
from pathlib import Path

import orjson


def format_file(path: Path) -> None:
    print(f"Formatting {path.name} ... ", end="")
    with open(path, "rb") as f:
        content = orjson.loads(f.read())
    orjson_opts = orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE
    with open(path, "wb") as f:
        f.write(orjson.dumps(content, option=orjson_opts))
    print("Done")


def main(input_folder: list[str]) -> None:
    for path in input_folder:
        resolved_path = Path(path).resolve()
        if resolved_path.is_dir():
            for file in resolved_path.rglob("*.json"):
                if file.is_file():
                    format_file(file)
        elif resolved_path.is_file():
            format_file(resolved_path)
        else:
            for file in Path().glob(path):
                if (
                    file.is_file()
                    and file.suffix == ".json"
                    and not (
                        file.name.startswith("nice_") or file.name.startswith("basic_")
                    )
                ):
                    format_file(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format json files.")
    parser.add_argument(
        "input", type=str, nargs="+", help="Pathes to a file or directory."
    )
    args = parser.parse_args()

    main(args.input)
