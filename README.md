# Valorant MCP Server

A Model Context Protocol (MCP) server that provides access to Valorant game data using the unofficial Valorant API.

## Features

- **Player Information**: Get account details, MMR, and match history
- **Match Data**: Detailed match information and statistics
- **Game Content**: Agents, maps, weapons, and other game assets
- **Service Status**: Check Valorant service status and maintenance
- **Leaderboards**: Competitive rankings and leaderboards

## Prerequisites

- Python 3.11 or higher
- A Valorant API key from [HenrikDev API](https://docs.henrikdev.xyz)
- Internet connection for API requests

## Installation

### Option 1: Run via uvx (Recommended)

No local environment setup required. `uvx` runs the packaged console script directly.

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run from GitHub (replace with your repo URL)
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server

# Windows (PowerShell)
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server
```

Optionally set an API key in the environment first (or use the `set_api_key` tool at runtime):

```bash
export VALORANT_API_KEY="your_api_key_here"
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server
```

### Option 2: Local UV/Pip environment

```bash
# Clone and setup
git clone https://github.com/<your-username>/valorant-mcp-server.git
cd valorant-mcp-server

# With UV
uv venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or with pip
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# Environment
cp env.example .env  # Windows: copy env.example .env
# Edit .env and add your VALORANT_API_KEY
```

## Usage

### Running the Server

```bash
# Recommended: uvx from git
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server

# Locally (if you've installed deps)
python server.py
```

**Note**: The server will start and wait for MCP client connections. It will show a warning if no API key is set, but you can still use the `set_api_key` tool to configure it at runtime.

### Using with MCP Clients

#### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

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

#### Cline (VS Code Extension)

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

#### Generic MCP Client

Use the packaged command with uvx:

```bash
uvx --from git+https://github.com/<your-username>/valorant-mcp-server.git valorant-mcp-server
```

## Available Tools

- **get_account_details(name, tag, region="na")**: Basic account info (PUUID, level, card, region).
- **get_match_history_by_name(name, tag, region="na", size=10)**: Recent matches with per-game stats.
- **get_match_details(match_id, region="na")**: Full details for a specific match.
- **get_mmr_details_by_name(name, tag, region="na")**: Current competitive tier, ELO, RR.
- **get_mmr_history_by_name(name, tag, region="na", size=10)**: Competitive MMR history with match IDs.
- **get_lifetime_matches_by_name(name, tag, region="na", mode=None, map_filter=None, page=1, size=20)**: Aggregate lifetime stats and list of matches.
- **get_leaderboard(region="na", season="e8a1")**: Top players for a region/season.
- **get_content(region="na")**: Agents, maps, and other content.
- **get_status(region="na")**: Service status and incidents.
- **set_api_key(api_key_input)**: Set HenrikDev API key at runtime.
- **get_detailed_competitive_analysis(name, tag, region="na", match_count=10)**: Correlate MMR history with match stats.
- **find_leaderboard_position(name, tag, region="na", season="e8a1")**: Locate a player on the leaderboard (Immortal 3+).

## Testing

You can validate connectivity by launching the server via `uvx` and connecting from your MCP client (Claude Desktop/Cline/Cursor). Use the `get_status` and `get_content` tools to confirm responses.

## Configuration

### Environment Variables

- `VALORANT_API_KEY`: Your Valorant API key (required)

### API Key Setup

You can set your API key in two ways:

1. **Environment Variable**: Set `VALORANT_API_KEY` in your environment
2. **Runtime**: Use the `set_api_key` tool to configure it at runtime

## Project Structure

```
valorant-mcp-server/
├── server.py               # MCP server implementation (FastMCP)
├── pyproject.toml          # Package metadata + console script
├── requirements.txt        # Python dependencies (for local installs)
├── env.example             # Environment variables template
├── mcp-client-configs.md   # Client configuration examples
├── TOOLS_DOCUMENTATION.md  # Detailed tool docs
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## API Integration

This server uses:

- **[HenrikDev API](https://docs.henrikdev.xyz)** - The core API service for Valorant data
- **[Direct HTTP Requests](https://requests.readthedocs.io/)** - Python requests library for API calls
- **[FastMCP](https://github.com/jlowin/fastmcp)** - MCP framework

## Error Handling

The server includes comprehensive error handling for:

- Invalid API keys
- Rate limiting
- Network errors
- Invalid player names or regions
- Service unavailability

All errors are logged and returned in a structured format.

## Development

### Adding New Tools

To add new Valorant API endpoints:

1. Create a new function decorated with `@mcp.tool()`
2. Add proper error handling with try/catch blocks
3. Use the global `valo_api` instance
4. Return structured data using Pydantic models
5. Update this README with the new tool documentation

### Code Quality

```bash
# Install development tools
pip install black isort mypy flake8

# Format code
black server.py test_server.py
isort server.py test_server.py

# Type checking
mypy server.py

# Linting
flake8 server.py test_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Henrik-3](https://github.com/Henrik-3) for the unofficial Valorant API
- [raimannma](https://github.com/raimannma) for the Python wrapper
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework