# clean.py

# A script to clean "edit conflict" files from Proton Drive.

# imports
import argparse
import os
import re
from pathlib import Path
from rich import print
from tqdm import tqdm


def find_files(dir: os.PathLike, verbose: bool = False) -> list[Path]:
    """
    Find files in a directory that match the edit conflict pattern.
    Args:
        dir (os.PathLike): Directory to search.
        verbose (bool): Verbose output.
    Returns:
        list[Path]: List of files that match the edit conflict pattern.
    """

    # compile regular expression for file search
    # regex: (# Edit conflict YYYY-MM-DD <text> #)
    conflict_re = re.compile(r"# Edit conflict \d{4}-\d{2}-\d{2} .* #")

    # make a list to save conflict files
    conflict_list = []

    # walk through the base dir
    for root, dirs, files in tqdm(
        iterable=os.walk(dir),
        desc=f"Searching '{dir}'",
        unit="dir",
        unit_scale=True,
        colour='green',
    ):
        # check if the files match conflict_re
        for file in files:
            full_path = Path(root) / file
            if conflict_re.search(file):
                conflict_list.append(full_path)
                if verbose:
                    print(f"[red]Found conflict file:[/red] {full_path}")
            elif verbose:
                print(f"[green]Skipping file:[/green] {full_path}")

    # return the conflict list to be deleted
    return conflict_list


def remove_files(files: list[Path]) -> None:
    """
    Remove files from the filesystem.
    Args:
        files (list[Path]): List of files to remove.
    """

    # remove the files
    for file in files:
        try:
            os.remove(file)
            print(f"[green]Removed file:[/green] {file}")
        except Exception as e:
            print(f"[red]Error removing file:[/red] {file} - {e}")


if __name__ == "__main__":
    # add arguments
    parser = argparse.ArgumentParser(
        description="Find and remove Proton Drive edit conflict files."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default=None,
        help="Directory to search for conflict files. Defaults to current directory.",
    )
    args = parser.parse_args()

    # check if the directory is set
    if args.dir:
        dir = Path(args.dir)
    else:
        dir = Path('.')

    # check if the directory exists and is a directory
    if not dir.exists() or not dir.is_dir():
        print(f"[red]Directory does not exist:[/red] {dir}")
        exit(1)

    # find the conflicting files
    conflict_list = find_files(dir, args.verbose)

    print(f"Found {len(conflict_list)} conflict files")
    if len(conflict_list) > 0:
        # print the conflicting files
        list_prefix = " - "
        print(list_prefix + f"\n{list_prefix}".join([str(f) for f in conflict_list]))

        # sum the total file size and convert to human readable format
        total_size = sum(f.stat().st_size for f in conflict_list)
        total_size_str = f"{total_size / (1024 ** 2):.2f} MB" if total_size > 1024 ** 2 else f"{total_size / 1024:.2f} KB"

        # query the user y/n to continue with file removal
        user_input = input(f"Do you want to remove these {len(conflict_list)} ({total_size_str}) files? (y/n): ")
        if user_input == 'y':
            # remove the files
            remove_files(conflict_list)
        else:
            print("[red]Aborting file removal.[/red]")
