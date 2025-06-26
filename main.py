"""
PDF Splitter & Printer Tool
Main entry point with command-line interface.
"""

import argparse
import sys
import pathlib
from typing import Optional, List

from file_manager import FileManager
from pdf_splitter import PDFSplitter
from printer_manager import PrinterManager


def print_progress(current: int, total: int, message: str):
    """Simple progress callback function."""
    percentage = (current / total) * 100
    print(f"[{current}/{total}] ({percentage:.1f}%) {message}")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Split PDF files into smaller chunks and optionally print them",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf --pages 8
  %(prog)s document.pdf --pages 10 --output ./split_files
  %(prog)s document.pdf --pages 5 --print --printer "HP_Printer"
  %(prog)s document.pdf --pages 8 --preview
  %(prog)s --list-printers
        """
    )

    # Positional arguments
    parser.add_argument('input_file', nargs='?',
                        help='Input PDF file to split')

    # Optional arguments
    parser.add_argument('--pages', type=int, default=8,
                        help='Number of pages per split file (default: 8)')
    parser.add_argument('--output', '-o',
                        help='Output directory for split files (default: same as input)')
    parser.add_argument('--print', action='store_true',
                        help='Print split files after creation')
    parser.add_argument('--printer', '-p',
                        help='Printer name (uses default if not specified)')
    parser.add_argument('--preview', action='store_true',
                        help='Preview split plan without creating files')
    parser.add_argument('--list-printers', action='store_true',
                        help='List available printers and exit')
    parser.add_argument('--print-options',
                        help='Print options as key=value pairs (e.g., "sides=two-sided,copies=2")')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing files without confirmation')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    # Handle --list-printers command
    if args.list_printers:
        print_available_printers()
        return 0

    # Validate required arguments
    if not args.input_file:
        parser.error("Input PDF file is required (or use --list-printers)")

    # Validate input file
    input_path = pathlib.Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        return 1

    if args.verbose:
        print(f"Input file: {input_path}")
        print(f"Pages per split: {args.pages}")
        print(f"Output directory: {args.output or 'same as input'}")
        print(f"Print enabled: {args.print}")
        print(f"Preview mode: {args.preview}")

    # Initialize components
    file_manager = FileManager(args.input_file, args.output)
    pdf_splitter = PDFSplitter(args.input_file)

    # Validate input file
    if not file_manager.validate_input():
        return 1

    # Load PDF
    print("Loading PDF file...")
    if not pdf_splitter.load_pdf():
        return 1

    # Show PDF info
    if args.verbose:
        pdf_info = pdf_splitter.get_pdf_info()
        print(f"\nPDF Information:")
        print(f"  Pages: {pdf_info['total_pages']}")
        print(f"  Size: {pdf_info['file_size_mb']:.2f} MB")
        print(f"  Encrypted: {pdf_info['encrypted']}")
        if 'title' in pdf_info and pdf_info['title'] != 'Unknown':
            print(f"  Title: {pdf_info['title']}")

    # Validate split parameters
    is_valid, error_msg = pdf_splitter.validate_split_parameters(args.pages)
    if not is_valid:
        print(f"Error: {error_msg}")
        return 1

    # Preview mode
    if args.preview:
        pdf_splitter.preview_split(args.pages)
        return 0

    # Create output directory
    if not file_manager.create_output_directory():
        return 1

    # Generate output filenames
    total_pages = pdf_splitter.get_total_pages()
    output_files = file_manager.generate_output_filenames(
        total_pages, args.pages)

    # Handle file conflicts
    if not args.force:
        existing_files = [f for f in output_files if f.exists()]
        if existing_files:
            print(
                f"\nWarning: {len(existing_files)} output files already exist:")
            for f in existing_files[:5]:  # Show first 5
                print(f"  {f}")
            if len(existing_files) > 5:
                print(f"  ... and {len(existing_files) - 5} more")

            response = input(
                "\nOverwrite existing files? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Operation cancelled.")
                return 0

    # Handle filename conflicts by renaming
    output_files = file_manager.handle_filename_conflicts(output_files)

    # Split PDF
    print(f"\nSplitting PDF into {len(output_files)} files...")
    success = pdf_splitter.split_pdf(
        args.pages,
        output_files,
        progress_callback=print_progress if args.verbose else None
    )

    if not success:
        print("PDF splitting failed.")
        return 1

    print(f"\n✓ Successfully created {len(output_files)} PDF files")

    # Print files if requested
    if args.print:
        print("\nInitializing printer...")
        printer_manager = PrinterManager()

        # Parse print options
        print_options = {}
        if args.print_options:
            try:
                for option in args.print_options.split(','):
                    key, value = option.split('=')
                    print_options[key.strip()] = value.strip()
            except ValueError:
                print("Warning: Invalid print options format. Using defaults.")
                print_options = {}

        # Validate printer
        if args.printer:
            available_printers = printer_manager.list_printers()
            if args.printer not in available_printers:
                print(f"Warning: Printer '{args.printer}' not found.")
                print(f"Available printers: {', '.join(available_printers)}")
                response = input(
                    "Continue with default printer? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Printing cancelled.")
                    return 0

        # Print files
        print(f"Printing {len(output_files)} files...")
        results = printer_manager.print_multiple_files(
            output_files,
            args.printer,
            print_options,
            progress_callback=print_progress if args.verbose else None
        )

        # Print summary
        successful_prints = sum(
            1 for success, _ in results.values() if success)
        print(
            f"\n✓ Successfully sent {successful_prints}/{len(output_files)} files to printer")

        if successful_prints < len(output_files):
            print("\nFailed prints:")
            for file_path, (success, message) in results.items():
                if not success:
                    print(f"  {pathlib.Path(file_path).name}: {message}")

    # Show summary
    print(f"\n--- Summary ---")
    print(f"Input file: {input_path}")
    print(f"Output files: {len(output_files)}")
    print(f"Output directory: {file_manager.output_dir}")
    if args.print:
        print(f"Print jobs sent: {successful_prints}/{len(output_files)}")

    return 0


def print_available_printers():
    """Print list of available printers."""
    printer_manager = PrinterManager()

    print(f"System: {printer_manager.get_system_type()}")

    printers = printer_manager.list_printers()
    if not printers:
        print("No printers found or unable to list printers.")
        return

    print(f"\nAvailable printers ({len(printers)}):")
    for i, printer in enumerate(printers, 1):
        print(f"  {i}. {printer}")

    # Show default printer
    default_printer = printer_manager.get_default_printer()
    if default_printer:
        print(f"\nDefault printer: {default_printer}")

    # Show print options help
    print(f"\nPrint options (use with --print-options):")
    options_help = printer_manager.get_print_options_help()
    for option, description in options_help.items():
        print(f"  {option}: {description}")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
