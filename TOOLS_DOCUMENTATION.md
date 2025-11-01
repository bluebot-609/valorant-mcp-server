# Valorant MCP Server - Tool Reference

This document describes the tools exposed by the Valorant MCP Server and their typical inputs/outputs. All tools return JSON-serializable dictionaries.

Total tools: 12

## 1) get_account_details
- **Params**: `name`, `tag`, `region="na"`
- **Returns**: `puuid`, `name`, `tag`, `card`, `region`, `account_level`, `last_update`

## 2) get_match_history_by_name
- **Params**: `name`, `tag`, `region="na"`, `size=10`
- **Returns**: `matches[]` with `map`, `mode`, `started_at`, and player stats (kills, deaths, assists, score, tier)

## 3) get_match_details
- **Params**: `match_id`, `region="na"`
- **Returns**: `map`, `mode`, `rounds_won/lost`, `score`, `date`, `players[]` with per-player stats

## 4) get_mmr_details_by_name
- **Params**: `name`, `tag`, `region="na"`
- **Returns**: `current_tier`, `current_tier_patched`, `ranking_in_tier`, `mmr_change_to_last_game`, `elo`, optional `season`

## 5) get_mmr_history_by_name
- **Params**: `name`, `tag`, `region="na"`, `size=10`
- **Returns**: `mmr_history[]` including `match_id`, `map`, `current_tier(_patched)`, `ranking_in_tier`, `mmr_change_to_last_game`, `elo`, `season_id`, `date`

## 6) get_lifetime_matches_by_name
- **Params**: `name`, `tag`, `region="na"`, `mode=None`, `map_filter=None`, `page=1`, `size=20`
- **Returns**: `lifetime_stats` and `matches[]` with basic summaries

## 7) get_leaderboard
- **Params**: `region="na"`, `season="e8a1"`
- **Returns**: `players[]` with `leaderboard_rank`, `ranked_rating`, `wins`, `competitive_tier`

## 8) get_content
- **Params**: `region="na"`
- **Returns**: `characters[]` and `maps[]` metadata

## 9) get_status
- **Params**: `region="na"`
- **Returns**: `maintenances[]`, `incidents[]`

## 10) set_api_key
- **Params**: `api_key_input`
- **Returns**: confirmation message

## 11) get_detailed_competitive_analysis
- **Params**: `name`, `tag`, `region="na"`, `match_count=10`
- **Returns**: `competitive_matches[]`, `overall_stats`, `agent_performance`, `map_performance`, `current_rank`

## 12) find_leaderboard_position
- **Params**: `name`, `tag`, `region="na"`, `season="e8a1"`
- **Returns**: whether found on leaderboard; if found, `position`, `ranked_rating`, `wins`, nearby players

---

## Notes & Best Practices
- Prefer small `size`/`match_count` for quick checks (5–10). Use larger values for deeper analysis.
- Some players may not have ranked data; handle empty histories gracefully.
- API errors are returned as `{ "error": "..." }` with descriptive messages.

## Troubleshooting
- Unauthorized → verify `VALORANT_API_KEY` is set or call `set_api_key`.
- Player not found → check `name`, `tag`, and `region`.
- Rate limits or network errors → retry after a short delay.

Built with FastMCP and the HenrikDev API.

