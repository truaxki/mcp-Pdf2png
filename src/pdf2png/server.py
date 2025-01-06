import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pdf2image import convert_from_path, pdfinfo_from_path
from pdf2image.exceptions import PDFPageCountError
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from tqdm import tqdm

@dataclass
class ConversionConfig:
    dpi: int = 200
    batch_size: int = 10
    max_workers: int = 4
    thread_count: Optional[int] = None
    fmt: str = 'PNG'
    grayscale: bool = False

class PDFConverter:
    def __init__(self, config: ConversionConfig = None):
        self.config = config or ConversionConfig()
        self._validate_config()

    def _validate_config(self):
        if not isinstance(self.config, ConversionConfig):
            raise ValueError("Config must be an instance of ConversionConfig")
        
        # Set thread count if not specified
        if not self.config.thread_count:
            self.config.thread_count = os.cpu_count() or 2

    def _convert_page_batch(self, args: tuple) -> List[str]:
        """Convert a batch of pages to images."""
        pdf_path, start_page, end_page, output_dir = args
        try:
            pages = convert_from_path(
                pdf_path,
                dpi=self.config.dpi,
                first_page=start_page,
                last_page=end_page,
                grayscale=self.config.grayscale,
                thread_count=self.config.thread_count
            )
            
            saved_paths = []
            for i, page in enumerate(pages, start=start_page):
                output_path = os.path.join(output_dir, f"page_{i}.png")
                page.save(output_path, self.config.fmt)
                saved_paths.append(output_path)
                
            return saved_paths
            
        except Exception as e:
            print(f"Error converting pages {start_page}-{end_page}: {str(e)}")
            return []

    def convert(self, pdf_path: str, output_dir: str) -> List[str]:
        """Convert PDF to PNG images using optimized batch processing."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Get total pages
            pdf_info = pdfinfo_from_path(pdf_path)
            total_pages = pdf_info['Pages']

            # Prepare batches
            batches = []
            for start in range(1, total_pages + 1, self.config.batch_size):
                end = min(start + self.config.batch_size - 1, total_pages)
                batches.append((pdf_path, start, end, output_dir))

            # Process batches in parallel
            all_saved_paths = []
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []
                for batch in batches:
                    future = executor.submit(self._convert_page_batch, batch)
                    futures.append(future)

                # Track progress
                for future in tqdm(futures, desc="Converting PDF pages", total=len(futures)):
                    saved_paths = future.result()
                    all_saved_paths.extend(saved_paths)

            return sorted(all_saved_paths)

        except PDFPageCountError as e:
            raise ValueError(f"Error getting PDF page count: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error during conversion: {str(e)}")

# Create the MCP server
server = Server("pdf2png")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="pdf2png",
            description="Converts PDFs to images in PNG format.",
            inputSchema={
                "type": "object",
                "properties": {
                    "read_file_path": {"type": "string"},
                    "write_folder_path": {"type": "string"},
                    "dpi": {
                        "type": "number",
                        "default": 200,
                        "description": "DPI for conversion (default: 200)"
                    },
                    "batch_size": {
                        "type": "number",
                        "default": 10,
                        "description": "Pages per batch (default: 10)"
                    },
                    "max_workers": {
                        "type": "number",
                        "default": 4,
                        "description": "Maximum worker threads (default: 4)"
                    },
                    "grayscale": {
                        "type": "boolean",
                        "default": False,
                        "description": "Convert to grayscale"
                    }
                },
                "required": ["read_file_path", "write_folder_path"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if name != "pdf2png":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    read_file_path = arguments.get("read_file_path")
    write_folder_path = arguments.get("write_folder_path")

    if not read_file_path or not write_folder_path:
        raise ValueError("Missing read_file_path or write_folder_path")

    # Create configuration from arguments with defaults
    config = ConversionConfig(
        dpi=arguments.get("dpi", 200),
        batch_size=arguments.get("batch_size", 10),
        max_workers=arguments.get("max_workers", 4),
        grayscale=arguments.get("grayscale", False)
    )

    # Create converter instance
    converter = PDFConverter(config)

    try:
        # Convert PDF to PNG using optimized converter
        output_files = converter.convert(read_file_path, write_folder_path)

        return [
            types.TextContent(
                type="text",
                text=f"Successfully converted PDF to {len(output_files)} PNG files in {write_folder_path}"
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error converting PDF: {str(e)}"
            )
        ]

async def main():
    """Run the server using stdin/stdout streams."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf2png",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )