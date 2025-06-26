# C-stpl - PDF Splitter & Printer Tool

## tl;dr

A cross-platform Python tool for splitting large PDF files into smaller chunks and optionally printing them to Windows, Mac, or Linux printers.

## Remarks

C-stpl ist born out of the need to split and print large exam files, that contain individualized exams on our university printer. 

(Example run)[docs/example.md] printing an EvaExam file on our university printer.

If anything does not work, check out the (Troubleshooting)[docs/troubleshooting.md] section.


## Features

- **PDF Splitting**: Split large PDF files into smaller files with specified page counts
- **Cross-Platform Printing**: Print to Windows, Mac, or Linux printers
- **Preview Mode**: Preview split operations without creating files
- **File Management**: Automatic file naming and conflict resolution
- **Progress Tracking**: Real-time progress updates for long operations
- **Flexible Output**: Customizable output directories and file naming

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows**: The tool will automatically use Windows printing APIs if `pywin32` is available, otherwise it falls back to PowerShell commands.

### Dependencies Explained

- `pypdf`: Modern PDF manipulation library
- `pywin32`: Windows-specific printing support (Windows only)
- `argparse`: Command-line interface (built-in)
- `pathlib`: File path handling (built-in)

## Usage

### Basic PDF Splitting

Split a PDF into 8-page chunks (default):
```bash
python main.py document.pdf
```

Split into custom page counts:
```bash
python main.py document.pdf --pages 10
```

Specify output directory:
```bash
python main.py document.pdf --pages 5 --output ./split_files
```

### Preview Mode

Preview the split operation without creating files:
```bash
python main.py document.pdf --pages 8 --preview
```

### Printing

List available printers:
```bash
python main.py --list-printers
```

Split and print to default printer:
```bash
python main.py document.pdf --pages 8 --print
```

Split and print to specific printer:
```bash
python main.py document.pdf --pages 10 --print --printer "HP LaserJet"
```

Print with options:
```bash
python main.py document.pdf --pages 5 --print --print-options "sides=two-sided,copies=2"
```

### Advanced Options

Force overwrite existing files:
```bash
python main.py document.pdf --pages 8 --force
```

Verbose output with detailed progress:
```bash
python main.py document.pdf --pages 8 --verbose
```

## Command-Line Options

| Option            | Description                                   |
| ----------------- | --------------------------------------------- |
| `input_file`      | Input PDF file to split (required)            |
| `--pages`         | Number of pages per split file (default: 8)   |
| `--output`, `-o`  | Output directory for split files              |
| `--print`         | Print split files after creation              |
| `--printer`, `-p` | Specific printer name                         |
| `--preview`       | Preview split plan without creating files     |
| `--list-printers` | List available printers and exit              |
| `--print-options` | Print options as key=value pairs              |
| `--force`         | Overwrite existing files without confirmation |
| `--verbose`, `-v` | Enable verbose output                         |

## Print Options

Available print options (use with `--print-options`):

- `sides`: one-sided, two-sided-long-edge, two-sided-short-edge
- `media`: a4, letter, legal, etc.
- `orientation`: portrait, landscape
- `quality`: draft, normal, high
- `copies`: number of copies (1, 2, 3, etc.)
- `page-ranges`: 1-5, 1,3,5, etc.
- `finishings`: staple-top-left, staple-top-right, staple-bottom-left, staple-bottom-right, staple-dual-left, staple-dual-top, staple-non (explicit disable)

Example:
```bash
--print-options "sides=two-sided,media=a4,copies=3"
```

## Examples

### Basic Splitting Examples

```bash
# Split a 100-page document into 8-page chunks (creates 13 files)
python main.py report.pdf --pages 8

# Split into 5-page chunks with custom output directory
python main.py manual.pdf --pages 5 --output ./manual_parts

# Preview split operation for 12-page chunks
python main.py book.pdf --pages 12 --preview
```

### Printing Examples

```bash
# Split and immediately print all parts
python main.py presentation.pdf --pages 6 --print

# Print to specific printer with duplex settings
python main.py document.pdf --pages 10 --print --printer "Canon Printer" --print-options "sides=two-sided"

# Print multiple copies
python main.py handout.pdf --pages 4 --print --print-options "copies=5"
```

### Advanced Workflow

```bash
# Complete workflow with verbose output
python main.py large_document.pdf --pages 15 --output ./parts --print --printer "Office Printer" --print-options "sides=two-sided,quality=high" --verbose --force
```

## File Naming Convention

Split files are automatically named using the pattern:
```
{original_filename}_part_{number}.pdf
```

Examples:
- `document.pdf` → `document_part_001.pdf`, `document_part_002.pdf`, etc.
- `report.pdf` → `report_part_001.pdf`, `report_part_002.pdf`, etc.

## Platform Support

### Windows
- Uses `win32print` API for direct printer access
- Falls back to PowerShell commands if win32 modules unavailable
- Supports both local and network printers

### macOS
- Uses `lpr` command-line printing
- Supports CUPS printer system
- Full print options support

### Linux
- Uses `lpr`/`lpstat` commands
- Supports CUPS printer system
- Compatible with most Linux distributions

## Error Handling

The tool handles various error conditions:

- **Invalid PDF files**: Corrupted or non-PDF files
- **Missing files**: Non-existent input files
- **Permission errors**: Read/write access issues
- **Printer errors**: Offline printers, invalid printer names
- **Invalid parameters**: Negative page counts, invalid ranges

## Troubleshooting

### Common Issues

**"No printers found"**
- Ensure printers are installed and accessible
- Check printer drivers are properly installed
- On Linux/Mac, ensure CUPS is running

**"Permission denied"**
- Check file/directory permissions
- Run with appropriate user privileges
- Ensure output directory is writable

**"PDF loading failed"**
- Verify PDF file is not corrupted
- Check if PDF is password-protected
- Ensure file is a valid PDF format

**"Import error: win32print"**
- Install pywin32: `pip install pywin32`
- Or use the PowerShell fallback (automatic)

### Debug Mode

Use `--verbose` flag for detailed debugging information:
```bash
python main.py document.pdf --pages 8 --verbose
```

## Performance Notes

- Large PDF files (>100MB) may take several minutes to process
- Memory usage scales with PDF file size
- Printing speed depends on printer and network connectivity
- Use `--preview` to estimate processing time for large files

## License

See license file

## Contributing

Feel free to submit issues, feature requests, or improvements to enhance the tool's functionality. 