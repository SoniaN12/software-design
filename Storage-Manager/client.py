#!/usr/bin/env python3
import argparse
import os
import sys
from core import StorageManager, CompressionManager


def main():
    """Command-line interface for the Storage Manager."""
    parser = argparse.ArgumentParser(description="Storage Manager - Clean up and optimize your files")
    default_dir="/Users/aacellular/Desktop/junk"
    parser.add_argument("directory", nargs="?", default=default_dir,help=f"Directory to manage(default:{default_dir})")
    parser.add_argument("--days", type=int, default=30, help="Days to keep files (default: 30)")
    parser.add_argument("--clean-old", action="store_true", help="Delete old files")
    parser.add_argument("--remove-duplicates", action="store_true", help="Remove duplicate files")
    parser.add_argument("--compress", action="store_true", help="Compress images")
    parser.add_argument("--quality", type=int, default=80, help="Compression quality (1-100)")
    parser.add_argument("--keep-original", action="store_true", help="Keep original files when compressing")
    parser.add_argument("--history", action="store_true", help="Show file edit history")
    parser.add_argument("--stats", action="store_true", help="Show storage statistics")
    parser.add_argument("--all", action="store_true", help="Run all operations")

    args = parser.parse_args()

    # Initialize storage manager
    try:
        storage_manager = StorageManager(
            directory=args.directory,
            days_to_keep=args.days,
            file_types=(".jpg", ".jpeg", ".png", ".gif")
        )

        # Initialize compression manager
        compression_manager = CompressionManager(
            quality=args.quality,
            keep_original=args.keep_original
        )
        storage_manager.set_compression_manager(compression_manager)

        print(f"Storage Manager started for: {args.directory}")
        print("-" * 50)

        # Run requested operations
        if args.all or args.stats:
            storage_manager.get_storage_stats()

        if args.all or args.clean_old:
            print("\nCleaning old files...")
            storage_manager.delete_old_files()

        if args.all or args.remove_duplicates:
            print("\nRemoving duplicates...")
            storage_manager.delete_duplicates()

        if args.all or args.compress:
            print("\nCompressing images...")
            storage_manager.compress_images()

        if args.all or args.history:
            print("\nFile edit history:")
            history = storage_manager.check_edit_history()
            for file, mod_time in history.items():
                print(f"  {file}: {mod_time}")

        if not any([args.clean_old, args.remove_duplicates, args.compress,
                    args.history, args.stats, args.all]):
            print("No operations specified. Use --help to see available options.")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())