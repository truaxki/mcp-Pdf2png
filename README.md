# PDF to PNG MCP Server

A Model Context Protocol (MCP) server that provides PDF to PNG conversion capabilities. This server allows you to convert PDF documents into PNG images with a simple MCP tool call.

## Prerequisites

This server requires the Model Context Protocol (MCP). If you're new to MCP, start by installing the SDK:
```bash
uv pip install mcp
```

Additional requirements:
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- poppler (required for pdf2image)

### Installing Poppler

- **Windows**: Download and install from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/truaxki/mcp-Pdf2png.git
   cd mcp-Pdf2png
   ```

2. Create and activate a virtual environment:
   ```bash
   uv venv
   # Windows
   .venv\Scripts\activate
   # Unix/macOS
   source .venv/bin/activate
   ```

3. Install the package:
   ```bash
   uv pip install -e .
   ```

## Usage

### 1. Configure MCP Client

Add the server configuration to your `claude_desktop_config.json`. The file is typically located in:
- Windows: `%APPDATA%\Claude Desktop\config\claude_desktop_config.json`
- macOS/Linux: `~/.config/Claude Desktop/config/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pdf2png": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-Pdf2png",
        "run",
        "pdf2png"
      ]
    }
  }
}
```

Note: Replace `/absolute/path/to/mcp-Pdf2png` with the actual path where you cloned the repository.

### 2. Using the Server

The server provides a single tool `pdf2png` with these parameters:
- `read_file_path`: Absolute path to the input PDF file
- `write_folder_path`: Absolute path to the directory where PNG files should be saved

Output:
- Each PDF page is converted to a PNG image
- Files are named `page_1.png`, `page_2.png`, etc.
- Returns a success message with the conversion count

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.