"""
File Manager Module for PDF Splitter Tool
Handles file operations, directory creation, and naming conventions.
"""

import os
import pathlib
from typing import List, Tuple


class FileManager:
    """Manages file operations for PDF splitting and output handling."""

    def __init__(self, input_file: str, output_dir: str = None):
        """
        Initialize FileManager with input file and output directory.

        Args:
            input_file: Path to the input PDF file
            output_dir: Directory for output files (default: same as input)
        """
        self.input_file = pathlib.Path(input_file)
        self.output_dir = pathlib.Path(
            output_dir) if output_dir else self.input_file.parent
        self.base_name = self.input_file.stem

    def validate_input(self) -> bool:
        """
        Validate that the input PDF file exists and is readable.

        Returns:
            bool: True if file is valid, False otherwise
        """
        if not self.input_file.exists():
            print(f"Error: Input file '{self.input_file}' does not exist.")
            return False

        if not self.input_file.is_file():
            print(f"Error: '{self.input_file}' is not a file.")
            return False

        if self.input_file.suffix.lower() != '.pdf':
            print(f"Warning: '{self.input_file}' may not be a PDF file.")

        return True

    def create_output_directory(self) -> bool:
        """
        Create the output directory if it doesn't exist.

        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return True
        except PermissionError:
            print(
                f"Error: Permission denied creating directory '{self.output_dir}'")
            return False
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return False

    def generate_output_filenames(self, total_pages: int, pages_per_split: int) -> List[pathlib.Path]:
        """
        Generate output filenames for split PDF files.

        Args:
            total_pages: Total number of pages in the input PDF
            pages_per_split: Number of pages per split file

        Returns:
            List of pathlib.Path objects for output files
        """
        num_splits = (total_pages + pages_per_split - 1) // pages_per_split
        output_files = []

        for i in range(num_splits):
            filename = f"{self.base_name}_part_{i+1:03d}.pdf"
            output_path = self.output_dir / filename
            output_files.append(output_path)

        return output_files

    def get_split_ranges(self, total_pages: int, pages_per_split: int) -> List[Tuple[int, int]]:
        """
        Calculate page ranges for each split file.

        Args:
            total_pages: Total number of pages in the input PDF
            pages_per_split: Number of pages per split file

        Returns:
            List of tuples (start_page, end_page) for each split (1-indexed)
        """
        ranges = []
        for start in range(0, total_pages, pages_per_split):
            end = min(start + pages_per_split - 1, total_pages - 1)
            ranges.append((start + 1, end + 1))  # Convert to 1-indexed

        return ranges

    def handle_filename_conflicts(self, output_files: List[pathlib.Path]) -> List[pathlib.Path]:
        """
        Handle filename conflicts by adding suffixes if files already exist.

        Args:
            output_files: List of proposed output file paths

        Returns:
            List of confirmed output file paths without conflicts
        """
        confirmed_files = []

        for file_path in output_files:
            counter = 1
            original_path = file_path

            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                new_name = f"{stem}_{counter}{suffix}"
                file_path = original_path.parent / new_name
                counter += 1

            confirmed_files.append(file_path)

        return confirmed_files

    def cleanup_temp_files(self, file_list: List[pathlib.Path]) -> None:
        """
        Clean up temporary files if needed.

        Args:
            file_list: List of files to remove
        """
        for file_path in file_list:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                print(
                    f"Warning: Could not remove temporary file {file_path}: {e}")

    def get_file_size_mb(self, file_path: pathlib.Path) -> float:
        """
        Get file size in megabytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in MB
        """
        try:
            size_bytes = file_path.stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
