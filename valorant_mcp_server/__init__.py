#!/usr/bin/env python3
"""
Valorant MCP Server - Streamlined Version

A lean Model Context Protocol (MCP) server providing essential Valorant data access.
Focuses on data retrieval; lets LLM handle analysis and orchestration.

Total Tools: 12 (down from 19)
"""

import os
import logging
import requests
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging (default to INFO; can be overridden in main via LOG_LEVEL)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Valorant MCP Server")

# Global API key
api_key = None

def make_api_request(endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """Make a direct HTTP request to the HenrikDev API"""
    if not api_key:
        return {"error": "Valorant API not initialized. Please set API key first."}
    
    url = f"https://api.henrikdev.xyz{endpoint}"
    headers = {
        'accept': 'application/json',
        'Authorization': api_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"error": "API error: Unauthorized - Invalid API key"}
        elif response.status_code == 404:
            return {"error": "API error: Player not found"}
        else:
            return {"error": f"API error: HTTP {response.status_code} - {response.text}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# ============================================================================
# CORE DATA RETRIEVAL TOOLS (10 tools)
# ============================================================================

@mcp.tool()
async def get_account_details(name: str, tag: str, region: str = "na") -> Dict[str, Any]:
    """
    Get account details for a Valorant player.
    
    Essential tool for getting PUUID and account information.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
    
    Returns:
        PUUID, account level, player card, region info
    """
    try:
        endpoint = f"/valorant/v1/account/{name}/{tag}"
        response = make_api_request(endpoint)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        return {
            "puuid": data.get("puuid"),
            "name": data.get("name"),
            "tag": data.get("tag"),
            "card": {
                "id": data.get("card", {}).get("id"),
                "small": data.get("card", {}).get("small"),
                "large": data.get("card", {}).get("large"),
                "wide": data.get("card", {}).get("wide")
            },
            "region": data.get("region"),
            "account_level": data.get("account_level"),
            "last_update": data.get("last_update")
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_match_history_by_name(name: str, tag: str, region: str = "na", size: int = 10) -> Dict[str, Any]:
    """
    Get recent match history for a player.
    
    Returns matches across all game modes with detailed stats.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
        size: Number of matches (default: 10, max: 20)
    
    Returns:
        List of matches with kills, deaths, assists, agents, maps, scores
    """
    try:
        # Get PUUID
        account_endpoint = f"/valorant/v1/account/{name}/{tag}"
        account_response = make_api_request(account_endpoint)
        
        if "error" in account_response:
            return account_response
        
        puuid = account_response.get("data", {}).get("puuid")
        if not puuid:
            return {"error": "Could not retrieve player PUUID"}
        
        # Get matches
        endpoint = f"/valorant/v3/by-puuid/matches/{region}/{puuid}"
        response = make_api_request(endpoint, {"size": size})
        
        if "error" in response:
            return response
        
        matches = response.get("data", [])
        match_list = []
        
        for match in matches:
            metadata = match.get("metadata", {})
            players = match.get("players", {})
            all_players = players.get("all_players", [])
            
            # Find player data
            player_data = None
            for p in all_players:
                if p.get("puuid") == puuid:
                    player_data = p
                    break
            
            match_info = {
                "match_id": metadata.get("matchid"),
                "map": metadata.get("map"),
                "mode": metadata.get("mode"),
                "started_at": metadata.get("game_start_patched"),
                "season_id": metadata.get("season_id"),
                "region": metadata.get("region"),
                "cluster": metadata.get("cluster")
            }
            
            if player_data:
                stats = player_data.get("stats", {})
                match_info.update({
                    "character": player_data.get("character"),
                    "team": player_data.get("team"),
                    "kills": stats.get("kills"),
                    "deaths": stats.get("deaths"),
                    "assists": stats.get("assists"),
                    "score": stats.get("score"),
                    "tier": player_data.get("currenttier_patched")
                })
            
            match_list.append(match_info)
        
        return {
            "player_name": f"{name}#{tag}",
            "region": region,
            "matches": match_list,
            "total_matches": len(match_list)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_match_details(match_id: str, region: str = "na") -> Dict[str, Any]:
    """
    Get detailed information about a specific match.
    
    Provides comprehensive match data including all players' stats.
    
    Args:
        match_id: Match identifier
        region: Region code (ap, na, eu, kr, br, latam)
    
    Returns:
        Match details with all players, rounds, scores
    """
    try:
        endpoint = f"/valorant/v2/match/{match_id}"
        response = make_api_request(endpoint)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        metadata = data.get("metadata", {})
        
        return {
            "match_id": data.get("match_id"),
            "map": metadata.get("map"),
            "mode": metadata.get("mode"),
            "rounds_won": metadata.get("rounds_won"),
            "rounds_lost": metadata.get("rounds_lost"),
            "score": metadata.get("score"),
            "result": metadata.get("result"),
            "date": metadata.get("game_start_patched"),
            "players": [
                {
                    "puuid": player.get("puuid"),
                    "name": player.get("name"),
                    "tag": player.get("tag"),
                    "team": player.get("team"),
                    "character": player.get("character"),
                    "stats": {
                        "kills": player.get("stats", {}).get("kills"),
                        "deaths": player.get("stats", {}).get("deaths"),
                        "assists": player.get("stats", {}).get("assists"),
                        "score": player.get("stats", {}).get("score")
                    }
                } for player in data.get("players", {}).get("all_players", [])
            ]
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_mmr_details_by_name(name: str, tag: str, region: str = "na") -> Dict[str, Any]:
    """
    Get current MMR and rank for a player.
    
    Provides current competitive standing.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
    
    Returns:
        Current rank, ELO, RR, last game MMR change
    """
    try:
        endpoint = f"/valorant/v2/mmr/{region}/{name}/{tag}"
        response = make_api_request(endpoint)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        
        return {
            "player_name": f"{name}#{tag}",
            "region": region,
            "current_tier": data.get("current_tier"),
            "current_tier_patched": data.get("current_tier_patched"),
            "ranking_in_tier": data.get("ranking_in_tier"),
            "mmr_change_to_last_game": data.get("mmr_change_to_last_game"),
            "elo": data.get("elo"),
            "games_needed_for_rating": data.get("games_needed_for_rating"),
            "old": data.get("old"),
            "season": {
                "id": data.get("season", {}).get("id"),
                "short": data.get("season", {}).get("short")
            } if data.get("season") else None
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_mmr_history_by_name(name: str, tag: str, region: str = "na", size: int = 10) -> Dict[str, Any]:
    """
    Get MMR history with match IDs and maps.
    
    Essential for competitive analysis - includes match IDs for each game!
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
        size: Number of history entries (default: 10, max: 20)
    
    Returns:
        MMR history with match IDs, maps, rank changes, dates
    """
    try:
        endpoint = f"/valorant/v1/mmr-history/{region}/{name}/{tag}"
        params = {"size": size}
        response = make_api_request(endpoint, params)
        
        if "error" in response:
            return response
        
        data = response.get("data", [])
        history_list = []
        ranks_seen = set()
        
        for mmr in data:
            history_info = {
                "match_id": mmr.get("match_id"),
                "map": mmr.get("map", {}).get("name"),
                "map_id": mmr.get("map", {}).get("id"),
                "current_tier": mmr.get("currenttier"),
                "current_tier_patched": mmr.get("currenttierpatched"),
                "ranking_in_tier": mmr.get("ranking_in_tier"),
                "mmr_change_to_last_game": mmr.get("mmr_change_to_last_game"),
                "elo": mmr.get("elo"),
                "season_id": mmr.get("season_id"),
                "date": mmr.get("date"),
                "date_raw": mmr.get("date_raw"),
                "images": mmr.get("images", {})
            }
            history_list.append(history_info)
            
            if mmr.get("currenttierpatched"):
                ranks_seen.add(mmr.get("currenttierpatched"))
        
        rank_progression = {
            "ranks_achieved": list(ranks_seen),
            "highest_rank": history_list[0].get("current_tier_patched") if history_list else None,
            "current_rank": history_list[0].get("current_tier_patched") if history_list else None,
            "lowest_elo": min([h.get("elo", 0) for h in history_list]) if history_list else 0,
            "highest_elo": max([h.get("elo", 0) for h in history_list]) if history_list else 0
        }
        
        return {
            "player_name": f"{name}#{tag}",
            "region": region,
            "mmr_history": history_list,
            "total_updates": len(history_list),
            "rank_progression": rank_progression
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_lifetime_matches_by_name(name: str, tag: str, region: str = "na", 
                                     mode: Optional[str] = None, map_filter: Optional[str] = None, 
                                     page: int = 1, size: int = 20) -> Dict[str, Any]:
    """
    Get lifetime match statistics (different API endpoint).
    
    Provides aggregate lifetime stats and match history.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
        mode: Optional game mode filter
        map_filter: Optional map filter
        page: Page number (default: 1)
        size: Matches per page (default: 20)
    
    Returns:
        Lifetime stats and match list
    """
    try:
        endpoint = f"/valorant/v1/lifetime/matches/{region}/{name}/{tag}"
        params = {
            "mode": mode,
            "map": map_filter,
            "page": page,
            "size": size
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        response = make_api_request(endpoint, params)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        matches = data.get("matches", [])
        
        return {
            "player_name": f"{name}#{tag}",
            "region": region,
            "lifetime_stats": {
                "total_matches": data.get("total_matches"),
                "win_rate": data.get("win_rate"),
                "average_score": data.get("average_score"),
                "favorite_agent": data.get("favorite_agent"),
                "favorite_map": data.get("favorite_map")
            },
            "matches": [
                {
                    "match_id": match.get("match_id"),
                    "map": match.get("map"),
                    "mode": match.get("mode"),
                    "result": match.get("result"),
                    "score": match.get("score"),
                    "date": match.get("date")
                } for match in matches
            ],
            "total_matches": len(matches)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_leaderboard(region: str = "na", season: str = "e8a1") -> Dict[str, Any]:
    """
    Get the competitive leaderboard for a region.
    
    Shows top players in region/season.
    
    Args:
        region: Region code (ap, na, eu, kr, br, latam)
        season: Season identifier (default: e8a1)
    
    Returns:
        List of top players with rankings and ratings
    """
    try:
        endpoint = f"/valorant/v2/leaderboard/{region}"
        params = {"season": season}
        response = make_api_request(endpoint, params)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        players = data.get("players", [])
        
        player_list = []
        for player in players:
            player_info = {
                "puuid": player.get("puuid"),
                "game_name": player.get("game_name"),
                "tag_line": player.get("tag_line"),
                "leaderboard_rank": player.get("leaderboard_rank"),
                "ranked_rating": player.get("ranked_rating"),
                "number_of_wins": player.get("number_of_wins"),
                "competitive_tier": player.get("competitive_tier")
            }
            player_list.append(player_info)
        
        return {
            "region": region,
            "season": season,
            "players": player_list,
            "total_players": len(player_list),
            "last_update": data.get("last_update")
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_content(region: str = "na") -> Dict[str, Any]:
    """
    Get game content (agents, maps, weapons).
    
    Essential for understanding game elements.
    
    Args:
        region: Region code (ap, na, eu, kr, br, latam)
    
    Returns:
        All agents, maps, and game content
    """
    try:
        endpoint = "/valorant/v1/content"
        response = make_api_request(endpoint)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        
        return {
            "version": data.get("version"),
            "characters": [
                {
                    "uuid": char.get("uuid"),
                    "display_name": char.get("display_name"),
                    "description": char.get("description"),
                    "display_icon": char.get("display_icon"),
                    "role": {
                        "uuid": char.get("role", {}).get("uuid"),
                        "display_name": char.get("role", {}).get("display_name"),
                        "description": char.get("role", {}).get("description"),
                        "display_icon": char.get("role", {}).get("display_icon")
                    } if char.get("role") else None
                } for char in data.get("characters", [])
            ],
            "maps": [
                {
                    "uuid": map_info.get("uuid"),
                    "display_name": map_info.get("display_name"),
                    "coordinates": map_info.get("coordinates"),
                    "display_icon": map_info.get("display_icon")
                } for map_info in data.get("maps", [])
            ]
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_status(region: str = "na") -> Dict[str, Any]:
    """
    Get Valorant service status.
    
    Checks for maintenance and incidents.
    
    Args:
        region: Region code (ap, na, eu, kr, br, latam)
    
    Returns:
        Service status, maintenance windows, incidents
    """
    try:
        endpoint = "/valorant/v1/status"
        response = make_api_request(endpoint)
        
        if "error" in response:
            return response
        
        data = response.get("data", {})
        
        return {
            "region": region,
            "maintenances": data.get("maintenances", []),
            "incidents": data.get("incidents", [])
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def set_api_key(api_key_input: str) -> Dict[str, Any]:
    """
    Set the API key for Valorant API requests.
    
    Required for authentication.
    
    Args:
        api_key_input: Your HenrikDev API key
    
    Returns:
        Confirmation message
    """
    global api_key
    try:
        api_key = api_key_input
        return {"message": "API key set successfully", "status": "success"}
    except Exception as e:
        logger.error(f"Error setting API key: {e}")
        return {"error": f"Failed to set API key: {str(e)}"}

# ============================================================================
# ADVANCED TOOLS (2 tools)
# ============================================================================

@mcp.tool()
async def get_detailed_competitive_analysis(
    name: str,
    tag: str,
    region: str = "na",
    match_count: int = 10
) -> Dict[str, Any]:
    """
    Get comprehensive competitive analysis by combining MMR history + match details.
    
    This is the most powerful tool for competitive insights.
    Combines two different API endpoints to correlate performance with MMR changes.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
        match_count: Number of matches to analyze (default: 10, max: 20)
    
    Returns:
        Detailed competitive matches with performance + MMR correlation
    """
    try:
        # Get MMR history (has match IDs!)
        mmr_history_endpoint = f"/valorant/v1/mmr-history/{region}/{name}/{tag}"
        mmr_response = make_api_request(mmr_history_endpoint, {"size": match_count})
        
        if "error" in mmr_response:
            return mmr_response
        
        mmr_data = mmr_response.get("data", [])
        
        if not mmr_data:
            return {
                "player": f"{name}#{tag}",
                "message": "No competitive match history found."
            }
        
        # Get PUUID
        account_endpoint = f"/valorant/v1/account/{name}/{tag}"
        account_response = make_api_request(account_endpoint)
        
        if "error" in account_response:
            return account_response
        
        puuid = account_response.get("data", {}).get("puuid")
        
        # Fetch detailed match data for each competitive match
        detailed_matches = []
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_score = 0
        agent_stats = {}
        map_stats = {}
        
        for mmr_entry in mmr_data[:match_count]:
            match_id = mmr_entry.get("match_id")
            if not match_id:
                continue
            
            match_endpoint = f"/valorant/v2/match/{match_id}"
            match_response = make_api_request(match_endpoint)
            
            if "error" not in match_response:
                match_data = match_response.get("data", {})
                players = match_data.get("players", {})
                all_players = players.get("all_players", [])
                
                player_data = None
                for p in all_players:
                    if p.get("puuid") == puuid:
                        player_data = p
                        break
                
                if player_data:
                    stats = player_data.get("stats", {})
                    kills = stats.get("kills", 0)
                    deaths = stats.get("deaths", 0)
                    assists = stats.get("assists", 0)
                    score = stats.get("score", 0)
                    agent = player_data.get("character", "Unknown")
                    
                    map_info = mmr_entry.get("map", {})
                    map_name = map_info.get("name") if isinstance(map_info, dict) else "Unknown"
                    
                    if agent not in agent_stats:
                        agent_stats[agent] = {"matches": 0, "kills": 0, "deaths": 0, "assists": 0, "score": 0}
                    agent_stats[agent]["matches"] += 1
                    agent_stats[agent]["kills"] += kills
                    agent_stats[agent]["deaths"] += deaths
                    agent_stats[agent]["assists"] += assists
                    agent_stats[agent]["score"] += score
                    
                    if map_name not in map_stats:
                        map_stats[map_name] = {"matches": 0, "kills": 0, "deaths": 0, "mmr_change": 0}
                    map_stats[map_name]["matches"] += 1
                    map_stats[map_name]["kills"] += kills
                    map_stats[map_name]["deaths"] += deaths
                    map_stats[map_name]["mmr_change"] += mmr_entry.get("mmr_change_to_last_game", 0)
                    
                    detailed_matches.append({
                        "match_id": match_id,
                        "map": map_name,
                        "agent": agent,
                        "kills": kills,
                        "deaths": deaths,
                        "assists": assists,
                        "kda": round((kills + assists) / max(deaths, 1), 2),
                        "score": score,
                        "mmr_change": mmr_entry.get("mmr_change_to_last_game", 0),
                        "rank": mmr_entry.get("currenttierpatched"),
                        "rr": mmr_entry.get("ranking_in_tier"),
                        "elo": mmr_entry.get("elo"),
                        "date": mmr_entry.get("date"),
                        "result": "Win" if mmr_entry.get("mmr_change_to_last_game", 0) > 0 else "Loss"
                    })
                    
                    total_kills += kills
                    total_deaths += deaths
                    total_assists += assists
                    total_score += score
        
        matches_analyzed = len(detailed_matches)
        overall_stats = {
            "matches": matches_analyzed,
            "avg_kills": round(total_kills / matches_analyzed, 2) if matches_analyzed > 0 else 0,
            "avg_deaths": round(total_deaths / matches_analyzed, 2) if matches_analyzed > 0 else 0,
            "avg_assists": round(total_assists / matches_analyzed, 2) if matches_analyzed > 0 else 0,
            "avg_score": round(total_score / matches_analyzed, 2) if matches_analyzed > 0 else 0,
            "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
            "win_rate": round((len([m for m in detailed_matches if m["result"] == "Win"]) / matches_analyzed * 100), 2) if matches_analyzed > 0 else 0
        }
        
        for agent, stats in agent_stats.items():
            matches = stats["matches"]
            if matches > 0:
                stats["avg_kills"] = round(stats["kills"] / matches, 2)
                stats["avg_deaths"] = round(stats["deaths"] / matches, 2)
                stats["kd_ratio"] = round(stats["kills"] / max(stats["deaths"], 1), 2)
        
        best_agents = sorted(agent_stats.items(), key=lambda x: x[1].get("kd_ratio", 0), reverse=True)
        
        return {
            "player": f"{name}#{tag}",
            "competitive_matches": detailed_matches,
            "overall_stats": overall_stats,
            "agent_performance": dict(best_agents),
            "map_performance": map_stats,
            "current_rank": {
                "rank": mmr_data[0].get("currenttierpatched") if mmr_data else None,
                "elo": mmr_data[0].get("elo") if mmr_data else None,
                "rr": mmr_data[0].get("ranking_in_tier") if mmr_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error in detailed competitive analysis: {e}")
        return {"error": f"Failed to get detailed competitive analysis: {str(e)}"}

@mcp.tool()
async def find_leaderboard_position(
    name: str,
    tag: str,
    region: str = "na",
    season: str = "e8a1"
) -> Dict[str, Any]:
    """
    Find a player's position on the competitive leaderboard.
    
    Searches leaderboard and provides position + nearby players.
    Only works for Immortal 3+ players.
    
    Args:
        name: Player's in-game name
        tag: Player's tag
        region: Region code (ap, na, eu, kr, br, latam)
        season: Season identifier (default: e8a1)
    
    Returns:
        Leaderboard position, rank, nearby players
    """
    try:
        leaderboard_endpoint = f"/valorant/v2/leaderboard/{region}"
        leaderboard_response = make_api_request(leaderboard_endpoint, {"season": season})
        
        if "error" in leaderboard_response:
            return leaderboard_response
        
        leaderboard_data = leaderboard_response.get("data", {})
        players = leaderboard_data.get("players", [])
        
        player_found = None
        player_index = -1
        
        for i, player in enumerate(players):
            if player.get("game_name") == name and player.get("tag_line") == tag:
                player_found = player
                player_index = i
                break
        
        if player_found:
            nearby_players = []
            start_idx = max(0, player_index - 2)
            end_idx = min(len(players), player_index + 3)
            
            for i in range(start_idx, end_idx):
                if i != player_index:
                    nearby_players.append({
                        "rank": players[i].get("leaderboard_rank"),
                        "name": f"{players[i].get('game_name')}#{players[i].get('tag_line')}",
                        "rr": players[i].get("ranked_rating"),
                        "wins": players[i].get("number_of_wins")
                    })
            
            return {
                "found": True,
                "player": f"{name}#{tag}",
                "position": player_found.get("leaderboard_rank"),
                "ranked_rating": player_found.get("ranked_rating"),
                "wins": player_found.get("number_of_wins"),
                "competitive_tier": player_found.get("competitive_tier"),
                "nearby_players": nearby_players,
                "total_leaderboard_players": len(players)
            }
        else:
            mmr_endpoint = f"/valorant/v2/mmr/{region}/{name}/{tag}"
            mmr_response = make_api_request(mmr_endpoint)
            mmr_data = mmr_response.get("data", {})
            
            lowest_lb_player = players[-1] if players else None
            
            return {
                "found": False,
                "player": f"{name}#{tag}",
                "message": "Player not found on leaderboard",
                "current_rank": mmr_data.get("current_tier_patched"),
                "current_elo": mmr_data.get("elo"),
                "leaderboard_info": {
                    "minimum_rank_required": "Immortal 3+",
                    "total_players_on_leaderboard": len(players),
                    "lowest_leaderboard_rr": lowest_lb_player.get("ranked_rating") if lowest_lb_player else None
                }
            }
        
    except Exception as e:
        logger.error(f"Error finding leaderboard position: {e}")
        return {"error": f"Failed to find leaderboard position: {str(e)}"}

def main():
    """Main function to run the MCP server"""
    global api_key
    # Load environment variables from a .env file if present
    load_dotenv()
    # Allow overriding log level from environment
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_name, logging.INFO)
    logging.getLogger().setLevel(level)
    api_key = os.getenv("VALORANT_API_KEY")
    if api_key:
        logger.info("Valorant API initialized with environment API key")
    else:
        logger.warning("No VALORANT_API_KEY environment variable found. Use set_api_key tool to configure.")
    
    mcp.run()


