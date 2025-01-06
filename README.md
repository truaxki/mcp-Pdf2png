# PDF to PNG MCP Server

A Model Context Protocol (MCP) server that converts PDF files to PNG images.

## Features

- Convert PDF files to high-quality PNG images
- Support for multi-page PDFs
- Automatic output directory creation
- Clear success/failure messages

## Installation

### Prerequisites

- Python 3.10 or higher
- `pdf2image` library (and its dependencies)
- Poppler (required by pdf2image)

### Install via UV

```bash
uv install pdf2png
```

## Configuration

### Claude Desktop Setup

#### Windows
Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf2png": {
      "command": "uvx",
      "args": ["pdf2png"]
    }
  }
}
```

#### Development Setup
For local development, use:

```json
{
  "mcpServers": {
    "pdf2png": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/pdf2png",
        "run",
        "pdf2png"
      ]
    }
  }
}
```

## Usage

The server provides a single tool:

### pdf2png

Converts PDF files to PNG format.

Required arguments:
- `read_file_path`: Path to the input PDF file
- `write_folder_path`: Directory where PNG files will be saved

Example usage in Claude:
```
Please convert my PDF file to PNG:
PDF Location: C:\Users\example\document.pdf
Output Directory: C:\Users\example\output
```

## Development

### Local Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd pdf2png
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
uv sync
```

### Testing

Launch the MCP Inspector for debugging:
```bash
npx @modelcontextprotocol/inspector uv --directory . run pdf2png
```

### Building and Publishing

1. Update dependencies:
```bash
uv sync
```

2. Build package:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

## License

[Insert License Information]