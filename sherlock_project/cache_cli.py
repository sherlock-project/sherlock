"""
Sherlock Cache Management CLI

Utility for managing Sherlock's SQLite cache.
"""

import argparse
import sys

from colorama import Fore, Style

from sherlock_project.cache import SherlockCache


def main() -> None:
    """Main entry point for cache management CLI."""
    parser = argparse.ArgumentParser(
        prog="sherlock-cache",
        description="Manage Sherlock's result cache"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Cache management commands",
        required=True
    )
    
    # Clear subcommand
    clear_parser = subparsers.add_parser(
        "clear",
        help="Clear cache entries"
    )
    clear_parser.add_argument(
        "--username",
        help="Clear cache for specific username only"
    )
    clear_parser.add_argument(
        "--site",
        help="Clear cache for specific site only"
    )
    
    # Stats subcommand
    subparsers.add_parser(
        "stats",
        help="Show cache statistics"
    )
    
    # Cleanup subcommand
    subparsers.add_parser(
        "cleanup",
        help="Remove expired cache entries"
    )
    
    args = parser.parse_args()
    
    # Initialize cache
    try:
        cache = SherlockCache()
    except (ValueError, RuntimeError) as e:
        print(f"{Fore.RED}✗{Style.RESET_ALL} Cache initialization failed: {e}")
        sys.exit(1)
    
    # Execute command
    if args.command == "clear":
        username = getattr(args, 'username', None)
        site = getattr(args, 'site', None)
        
        try:
            cache.clear(username=username, site=site)
            
            if username and site:
                print(
                    f"{Fore.GREEN}✓{Style.RESET_ALL} "
                    f"Cleared cache for {username} on {site}"
                )
            elif username:
                print(
                    f"{Fore.GREEN}✓{Style.RESET_ALL} "
                    f"Cleared all cache for username: {username}"
                )
            elif site:
                print(
                    f"{Fore.GREEN}✓{Style.RESET_ALL} "
                    f"Cleared all cache for site: {site}"
                )
            else:
                print(f"{Fore.GREEN}✓{Style.RESET_ALL} Cleared entire cache")
        except ValueError as e:
            print(f"{Fore.RED}✗{Style.RESET_ALL} Error: {e}")
            sys.exit(1)
    
    elif args.command == "stats":
        stats = cache.get_stats()
        print(f"\n{Style.BRIGHT}Cache Statistics:{Style.RESET_ALL}")
        print(f"  Cache Path: {stats['cache_path']}")
        print(f"  Total Entries: {stats['total_entries']}")
        print(
            f"  Valid Entries: "
            f"{Fore.GREEN}{stats['valid_entries']}{Style.RESET_ALL}"
        )
        print(
            f"  Expired Entries: "
            f"{Fore.YELLOW}{stats['expired_entries']}{Style.RESET_ALL}\n"
        )
    
    elif args.command == "cleanup":
        cache.cleanup_expired()
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Cleaned up expired cache entries")
