import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pdf2image import convert_from_path
import os

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

    # Convert PDF to PNG
    images = convert_from_path(read_file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(write_folder_path, exist_ok=True)
    
    # Save each page as PNG
    output_files = []
    for i, image in enumerate(images):
        output_path = os.path.join(write_folder_path, f'page_{i+1}.png')
        image.save(output_path, 'PNG')
        output_files.append(output_path)

    return [
        types.TextContent(
            type="text",
            text=f"Successfully converted PDF to {len(output_files)} PNG files in {write_folder_path}"
        )
    ]

async def main():
    # Run the server using stdin/stdout streams
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