import os
from pathlib import Path
import shutil
import re

# ---- CONFIGURATION ----
DEFAULT_SRC = "/Users/weli/Documents/fluka/Projects/MSc"  # Path to base folder containing FLUKA project data
DEFAULT_DEST = "."                                        # Path to where matching files will be copied
OUT_PATTERN = re.compile(r"\d{5}\.out$", re.IGNORECASE)   # Match any filename ending with 5 digits + .out


def files_differ(src, dst):
    """
    Return True if the destination file:
     - does not exist;
     - is a different size; or
     - has an older modification time than the source.
    """
    if not dst.exists():
        return True
    s_stat = src.stat()
    d_stat = dst.stat()
    if s_stat.st_size != d_stat.st_size:
        return True
    return getattr(s_stat, "st_mtime_ns", int(s_stat.st_mtime * 1e9)) > getattr(d_stat, "st_mtime_ns", int(d_stat.st_mtime * 1e9))


def should_take(path, src_base):
    """
    Decide if a file should be processed and classify it.
    Returns one of:
      - 'tab.lis' for files ending with 'tab.lis'
      - 'bnn.lis' for files ending with 'bnn.lis'
      - 'out'     for files ending with 'XXXXX.out'
      - None      if file is to be ignored
    """
    name = path.name.lower()
    if name.endswith("tab.lis"):
        return "tab.lis"
    if name.endswith("bnn.lis"):
        return "bnn.lis"
    if OUT_PATTERN.search(name):  # Match anywhere in the filename if it ends with digits + .out
        return "out"
    return None


def main():
    """
    Walk the source tree, apply filters, and copy matching files to destination while preserving structure.
    """
    src_base = Path(DEFAULT_SRC).expanduser().resolve()
    dest_base = Path(DEFAULT_DEST).expanduser().resolve()

    copied, up_to_date = 0, 0
    type_counts = {"tab.lis": 0, "bnn.lis": 0, "out": 0}

    for root, dirs, files in os.walk(src_base):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for fname in files:
            src = Path(root) / fname
            file_type = should_take(src, src_base)
            if file_type is None:
                continue

            type_counts[file_type] += 1

            # Preserve relative path for destination
            rel = src.relative_to(src_base)
            dst = dest_base / "data" / rel

            if files_differ(src, dst):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"Copied: {rel}")  # Optional: show copied file path
                copied += 1
            else:
                up_to_date += 1

    total = copied + up_to_date
    print(f"\nDone. Considered {total} matching files.")
    print(f"Copied/updated: {copied}")
    print(f"Up-to-date:     {up_to_date}")
    print("\nFile type counts:")
    for ftype, count in type_counts.items():
        print(f"  {ftype}: {count}")

if __name__ == "__main__":
    main()