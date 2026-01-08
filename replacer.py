import os
import argparse

def replace_in_text_case_insensitive(text, old, new):
    """
    Return (new_text, count) replacing old with new, case-insensitive.
    """
    lower_text = text.lower()
    lower_old = old.lower()

    start = 0
    count = 0
    parts = []

    while True:
        idx = lower_text.find(lower_old, start)
        if idx == -1:
            parts.append(text[start:])
            break
        parts.append(text[start:idx])
        parts.append(new)
        start = idx + len(old)
        count += 1

    new_text = "".join(parts)
    return new_text, count


def process_file(path, old, new):
    """
    Replace in file contents, case-insensitive.
    Returns number of replacements, 0 if none or on error.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[FILE ERROR] Cannot read: {path} ({e})")
        return 0

    new_content, count = replace_in_text_case_insensitive(content, old, new)

    if count == 0:
        return 0

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"[FILE ERROR] Cannot write: {path} ({e})")
        return 0

    return count


def rename_case_insensitive(path, old, new):
    """
    Rename file/folder if its name contains old (case-insensitive).
    Returns (new_path or original_path, did_rename, rename_count_in_name).
    """
    dir_name, base = os.path.split(path)
    lower_base = base.lower()
    lower_old = old.lower()

    if lower_old not in lower_base:
        return path, False, 0

    # Replace in the *name* (case-insensitive)
    new_name, rename_count = replace_in_text_case_insensitive(base, old, new)
    new_path = os.path.join(dir_name, new_name)

    # If name unchanged for some reason, skip
    if new_path == path:
        return path, False, 0

    try:
        os.rename(path, new_path)
        return new_path, True, rename_count
    except Exception as e:
        print(f"[RENAME ERROR] {path} -> {new_path} ({e})")
        return path, False, 0


def walk_and_replace(root_dir, old, new):
    total_content_replacements = 0
    total_name_replacements = 0

    # Walk bottom-up so renaming directories is safer
    for current_root, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Process files first: contents + names
        for filename in filenames:
            file_path = os.path.join(current_root, filename)

            # 1. Replace in file content
            content_replaced = process_file(file_path, old, new)

            # 2. Rename file if needed
            new_file_path, renamed, name_replaced = rename_case_insensitive(
                file_path, old, new
            )

            # Per-file summary
            if content_replaced > 0 or renamed:
                print(
                    f"[FILE] {file_path} "
                    f"=> content replacements: {content_replaced}, "
                    f"name replacements: {name_replaced}, "
                    f"renamed: {renamed}"
                )

            total_content_replacements += content_replaced
            total_name_replacements += name_replaced

        # Then process directory names (including current_root’s children)
        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)
            new_dir_path, renamed, name_replaced = rename_case_insensitive(
                dir_path, old, new
            )

            if renamed:
                print(
                    f"[DIR] {dir_path} "
                    f"=> name replacements: {name_replaced}, renamed: {renamed}"
                )
                total_name_replacements += name_replaced

    print("\n=== SUMMARY ===")
    print(f"Total content replacements: {total_content_replacements}")
    print(f"Total name replacements (files + folders): {total_name_replacements}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively, case-insensitively replace a word in file contents "
                    "and in file/folder names, starting from a directory."
    )
    parser.add_argument(
        "directory",
        help="Root directory (start from the folder you described)."
    )
    parser.add_argument("old_word", help="Word to search for (case-insensitive).")
    parser.add_argument("new_word", help="Word to replace with.")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory.")
        return

    walk_and_replace(args.directory, args.old_word, args.new_word)


if __name__ == "__main__":
    main()
