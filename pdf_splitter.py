"""
PDF Splitter Module
Core functionality for splitting PDF files into smaller chunks.
"""

import pathlib
from typing import List, Tuple, Optional
from pypdf import PdfReader, PdfWriter


class PDFSplitter:
    """Handles PDF splitting operations using pypdf library."""

    def __init__(self, input_file: str):
        """
        Initialize PDFSplitter with input file.

        Args:
            input_file: Path to the input PDF file
        """
        self.input_file = pathlib.Path(input_file)
        self.reader = None
        self.total_pages = 0

    def load_pdf(self) -> bool:
        """
        Load and validate the PDF file.

        Returns:
            bool: True if PDF loaded successfully, False otherwise
        """
        try:
            self.reader = PdfReader(str(self.input_file))
            self.total_pages = len(self.reader.pages)

            if self.total_pages == 0:
                print(f"Error: PDF file '{self.input_file}' has no pages.")
                return False

            print(f"Successfully loaded PDF: {self.total_pages} pages")
            return True

        except Exception as e:
            print(f"Error loading PDF file '{self.input_file}': {e}")
            return False

    def get_total_pages(self) -> int:
        """
        Get the total number of pages in the PDF.

        Returns:
            int: Total number of pages
        """
        return self.total_pages

    def is_encrypted(self) -> bool:
        """
        Check if the PDF is encrypted.

        Returns:
            bool: True if PDF is encrypted
        """
        return self.reader.is_encrypted if self.reader else False

    def get_pdf_info(self) -> dict:
        """
        Get basic information about the PDF.

        Returns:
            dict: PDF metadata and information
        """
        if not self.reader:
            return {}

        info = {
            'total_pages': self.total_pages,
            'encrypted': self.is_encrypted(),
            'file_size_mb': self.input_file.stat().st_size / (1024 * 1024)
        }

        # Try to get metadata
        try:
            metadata = self.reader.metadata
            if metadata:
                info.update({
                    'title': metadata.get('/Title', 'Unknown'),
                    'author': metadata.get('/Author', 'Unknown'),
                    'creator': metadata.get('/Creator', 'Unknown'),
                    'subject': metadata.get('/Subject', 'Unknown')
                })
        except Exception:
            pass  # Metadata not available or readable

        return info

    def validate_split_parameters(self, pages_per_split: int) -> Tuple[bool, str]:
        """
        Validate the split parameters.

        Args:
            pages_per_split: Number of pages per split file

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if pages_per_split <= 0:
            return False, "Pages per split must be greater than 0"

        if pages_per_split >= self.total_pages:
            return False, f"Pages per split ({pages_per_split}) should be less than total pages ({self.total_pages})"

        return True, ""

    def calculate_split_info(self, pages_per_split: int) -> dict:
        """
        Calculate information about the split operation.

        Args:
            pages_per_split: Number of pages per split file

        Returns:
            dict: Split operation information
        """
        num_splits = (self.total_pages + pages_per_split -
                      1) // pages_per_split
        last_split_pages = self.total_pages % pages_per_split
        if last_split_pages == 0:
            last_split_pages = pages_per_split

        return {
            'total_pages': self.total_pages,
            'pages_per_split': pages_per_split,
            'num_splits': num_splits,
            'last_split_pages': last_split_pages,
            'ranges': self._get_page_ranges(pages_per_split)
        }

    def _get_page_ranges(self, pages_per_split: int) -> List[Tuple[int, int]]:
        """
        Get page ranges for each split (1-indexed).

        Args:
            pages_per_split: Number of pages per split file

        Returns:
            List of tuples (start_page, end_page)
        """
        ranges = []
        for start in range(0, self.total_pages, pages_per_split):
            end = min(start + pages_per_split - 1, self.total_pages - 1)
            ranges.append((start + 1, end + 1))  # Convert to 1-indexed
        return ranges

    def split_pdf(self, pages_per_split: int, output_files: List[pathlib.Path],
                  progress_callback: Optional[callable] = None) -> bool:
        """
        Split the PDF into multiple files.

        Args:
            pages_per_split: Number of pages per split file
            output_files: List of output file paths
            progress_callback: Optional callback function for progress updates

        Returns:
            bool: True if split operation was successful
        """
        if not self.reader:
            print("Error: PDF not loaded. Call load_pdf() first.")
            return False

        try:
            ranges = self._get_page_ranges(pages_per_split)

            for i, (start_page, end_page) in enumerate(ranges):
                if progress_callback:
                    progress_callback(i + 1, len(ranges),
                                      f"Creating part {i + 1}")

                writer = PdfWriter()

                # Add pages to the writer (convert to 0-indexed for pypdf)
                for page_num in range(start_page - 1, end_page):
                    writer.add_page(self.reader.pages[page_num])

                # Write the split PDF
                output_file = output_files[i]
                with open(output_file, 'wb') as output_pdf:
                    writer.write(output_pdf)

                print(
                    f"Created: {output_file} (pages {start_page}-{end_page})")

            return True

        except Exception as e:
            print(f"Error during PDF splitting: {e}")
            return False

    def extract_page_range(self, start_page: int, end_page: int, output_file: pathlib.Path) -> bool:
        """
        Extract a specific range of pages to a new PDF file.

        Args:
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed, inclusive)
            output_file: Output file path

        Returns:
            bool: True if extraction was successful
        """
        if not self.reader:
            print("Error: PDF not loaded. Call load_pdf() first.")
            return False

        try:
            if start_page < 1 or end_page > self.total_pages or start_page > end_page:
                print(f"Error: Invalid page range {start_page}-{end_page}")
                return False

            writer = PdfWriter()

            # Add pages to the writer (convert to 0-indexed)
            for page_num in range(start_page - 1, end_page):
                writer.add_page(self.reader.pages[page_num])

            # Write the extracted PDF
            with open(output_file, 'wb') as output_pdf:
                writer.write(output_pdf)

            print(f"Extracted pages {start_page}-{end_page} to: {output_file}")
            return True

        except Exception as e:
            print(f"Error extracting page range: {e}")
            return False

    def preview_split(self, pages_per_split: int) -> None:
        """
        Preview the split operation without actually creating files.

        Args:
            pages_per_split: Number of pages per split file
        """
        if not self.reader:
            print("Error: PDF not loaded. Call load_pdf() first.")
            return

        split_info = self.calculate_split_info(pages_per_split)

        print(f"\n--- Split Preview ---")
        print(f"Input file: {self.input_file}")
        print(f"Total pages: {split_info['total_pages']}")
        print(f"Pages per split: {split_info['pages_per_split']}")
        print(f"Number of output files: {split_info['num_splits']}")
        print(f"Last file will have: {split_info['last_split_pages']} pages")
        print(f"\nPage ranges:")

        for i, (start, end) in enumerate(split_info['ranges']):
            print(
                f"  Part {i+1:03d}: pages {start}-{end} ({end-start+1} pages)")

        print(f"--- End Preview ---\n")
