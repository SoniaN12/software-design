
import hashlib
import time
import logging
import datetime
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from pickletools import optimize
from PIL import Image
from typing import Dict, Set,List, Optional,Tuple

from sqlalchemy.testing.util import total_size


class CompressionManager:
    """Handles all image compression operations."""
    def __init__(self,quality: int =80, keep_original: bool = False):
        self.quality = quality
        self.keep_original = keep_original
    def compress_image(self, file_path: Path) -> Optional[Tuple[float,float]]:
        """
        Compress a single  image file.

        Args:
        file_path (Path) : Path to the image file to compress

        returns:
        Optional[tuple[float,float]]: Space saved in MB , or None if compression failed
        """
        try:
            if not file_path.exists():
                logging.error(f"File does not exist: {file_path}")
                return None
            img = Image.open(file_path)
            original_size = file_path.stat().st_size / (1024 * 1024) #MB
            # Determine output path
            if self.keep_original:
                output_path = file_path.with_stem(file_path.stem + "_compressed")
            else:
                output_path = file_path

            # saving compressed image
            img.save(output_path,optimize= True, quality= self.quality)

            # calculate space savings
            new_size = output_path.stat().st_size / (1024* 1024)  #MB
            space_saved_mb = original_size - new_size
            space_saved_percent = (space_saved_mb / original_size * 100) if original_size > 0 else 0

            # saving to the logs the sizes of the new compressed files and old file as well as the space saved from compressing the file.
            logging.info(
                f"Compressed image : {output_path} (quality={self.quality})"
                f"| Original={original_size:.2f} MB -> New ={new_size:.2f} MB "
                f"| Saved={space_saved_mb:.2f} MB ({space_saved_percent:.1f}%)"

            )

            return (space_saved_mb, space_saved_percent)
        except Exception as e:
            logging.error(f"failed to compress {file_path}: {e}")
            return None


class StorageManager:
    def __init__(self, directory: str, days_to_keep: int = 30, file_types=(".jpg", ".jpeg", ".png", ".gif"), log_file="storage_manager.log"):
        self.directory = Path(directory)
        self.days_to_keep = days_to_keep
        self.file_types = file_types
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Initialize the logging system."""
        # create logs directory if not exist
        logs_dir = Path.home() / ".storage_manager" / "logs"
        logs_dir.mkdir(parents= True, exist_ok=True)

        log_file_path = logs_dir / self.log_file

        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Storage Manager initialized for directory: {self.directory}")


    def _is_file_old(self,file_path:Path) -> bool:
        """ Checking if file is older than the retention period."""
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        return file_age > timedelta(days=self.days_to_keep)
    def set_compression_manager(self,compression_manager: CompressionManager) -> None:
        """Set the compression manager instance."""
        self.compression_manager = compression_manager

    def _get_file_hash(self,file_path:Path)-> str:
        """Generate MD5 hash for duplicate detection."""
        hasher = hashlib.md5()
        with open(file_path,"rb") as f :
            while chunk := f.read (8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_files(self) -> List[Path]:
        """ Get files in the directory that match the specified file types.
        """
        if not self.directory. exists():
            logging.error(f"Directory does not exist:{self.directory}")
            return []
        return [ file for file in self.directory.iterdir()
                 if file.is_file() and file.suffix.lower()in self.file_types]

    # use case1 cleanup storage permanent deletion

    def delete_old_files(self) -> int:
        """Delete files older than retention period"""
        if not self.directory.exists():
            logging.error(f"Directory does not exist : {self.directory}")
            return
        deleted_files = 0
        for file in self. directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.file_types:
                if self._is_file_old(file):
                    try:
                        file.unlink()
                        deleted_files += 1
                        logging.info(f"Permanently deleted old file: {file}")
                    except Exception as e:
                        logging.info(f"Failed to delete {file}: {e}")
        logging.info(f"Old file cleanup completed. files deleted: {deleted_files}")

# use case 2 duplicate deletion
    def delete_duplicates(self) -> int:
        """Delete duplicate files based on hash content."""
        files= self.get_files()
        seen_hashes = {}
        deleted_files = 0

        for file in self.directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.file_types:
                file_hash = self._get_file_hash(file)
                if file_hash in seen_hashes:
                    try:
                        file.unlink()
                        deleted_files += 1
                        logging.info(f"Deleted duplicate file: {file}")
                        print(f" Deleted duplicate:{file.name}")
                    except  Exception as e:
                        logging.error(f"Failed to delete duplicate {file}: {e}")
                else:
                    seen_hashes[file_hash] =file

        logging.info(f"Duplicate file cleanup completed. Files deleted: {deleted_files}")
    # use case 3 image compression
    def compress_images(self) -> Dict[str, float]:
        """
        Compress images in the directory using the CompressionManager.

        returns:
            Dict[str, float]: Dictionary mapping filenames to space saved in MB
        """
        if not self.compression_manager:
            logging.error("CompressionManager not set. Call set_compression_manager() first.")
            return {}
        files = self.get_files()
        image_files = [ f for f in files if f.suffix.lower() in (".jpg",".jpeg",".png")]
        compression_results = {}
        compressed_files = 0
        total_space_saved = 0.0

        for file in image_files:
            result = self.compression_manager.compress_image(file)
            if result is not None:
                space_saved_mb, space_saved_percent = result
                compression_results[file.name] = (space_saved_mb, space_saved_percent)
                compressed_files += 1
                total_space_saved += space_saved_mb
                print(f"✓ Compressed: {file.name} (saved {space_saved_mb:.2f}MB)")

        print(f"Compressed {compressed_files} images, total saved: {total_space_saved:.2f}MB")
        return compression_results




#USE CASE 4 checking edit history
    def check_edit_history(self) -> Dict[str, str]:
        """
        check the edit history of file in the directory.

        returns:
           Dict[str, str]: Dictionary mapping filenames to last modified timestamp
        """
        files = self.get_files()
        history = {}
        for file in self.directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.file_types:
                last_modified = datetime.fromtimestamp(file.stat().st_mtime)
                history[file.name] = last_modified.strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"Edit history checked: {file} - Last modified:{last_modified}")
        return  history

    def get_storage_stats(self) -> Dict[str, float]:
        """ Getting the storage statistics.
        """
        files =self.get_files()
        total_size = sum(file.stat().st_size for file in files)/ (1024 * 1024)

        stats = {
            "total_files": len(files),
            "total_size_mb": total_size,
            "directory": str(self.directory)
        }

        print(f"storage stats for {self.directory}:")
        print(f" Files:{len(files)}")
        print(f"Total size: {total_size:.2f}MB")

        return stats



