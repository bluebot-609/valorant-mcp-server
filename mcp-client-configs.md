# MCP Client Configuration Examples

This document provides configuration examples for different MCP clients to use the Valorant MCP Server.

## Claude Desktop

Add to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "valorant": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/<your-username>/valorant-mcp-server.git", "valorant-mcp-server"],
      "env": {
        "VALORANT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### With uvx (preferred)

```json
{
  "mcpServers": {
    "valorant": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/<your-username>/valorant-mcp-server.git", "valorant-mcp-server"],
      "env": {
        "VALORANT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Cline (VS Code Extension)

Add to your Cline configuration:

```json
{
  "mcpServers": {
    "valorant": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/<your-username>/valorant-mcp-server.git", "valorant-mcp-server"],
      "env": {
        "VALORANT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Generic MCP Client

For any MCP-compatible client, call the packaged server via `uvx`:

```bash
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server
```

## Environment Variables

You can also set the API key as an environment variable instead of in the client configuration:

```bash
# Set the API key
export VALORANT_API_KEY="your_api_key_here"

# Run the server
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server
```

## Testing the Connection

Once configured, you can test the MCP server by asking your client to:

1. Get account details for a player
2. Check Valorant service status
3. Get game content information

Example queries:
- "Get account details for TenZ from SEN"
- "What's the current Valorant service status?"
- "Show me the available agents in Valorant"

