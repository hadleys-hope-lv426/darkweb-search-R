import asyncio
import aiohttp
import json
import sqlite3
import csv
import argparse
import os
from bs4 import BeautifulSoup
from aiohttp_socks import ProxyConnector

from storage import init_db, save_result

TOR_PROXY = "socks5://127.0.0.1:9050"

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

DB_FILE = os.path.join(RESULTS_DIR, "results.db")
ENGINES_FILE = "search_engines.json"   # your JSON file


async def fetch(session, name, conf, query):
    
    url = conf["url"].format(query=query)
    try:
        async with session.get(url, timeout=30) as resp:
            if resp.status != 200:
                print(f"[!] {name} failed with HTTP {resp.status}")
                return []

            # Handle JSON APIs
            if conf.get("api", False):
                data = await resp.json()
                return [
                    {
                        "engine": name,
                        "title": r.get("title", ""),
                        "link": r.get("link", ""),
                    }
                    for r in data.get("data", [])
                ]

            text = await resp.text()
            soup = BeautifulSoup(text, "lxml")

            results = []
            for tag in soup.select(conf["selector"]):
                link = tag.get(conf["attr"])
                title = tag.get_text(strip=True)
                if link:
                    results.append({"engine": name, "title": title, "link": link})
            return results

    except Exception as e:
        print(f"[!] {name} failed: {e}")
        return []


async def main(query, output_format, engines):
    # Init DB if using SQLite
    conn = None
    if output_format == "sqlite":
        conn = init_db(DB_FILE)

    connector = ProxyConnector.from_url(TOR_PROXY)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, name, conf, query) for name, conf in engines.items()]
        results = await asyncio.gather(*tasks)

    seen = set()
    final_results = []
    for engine_results in results:
        for r in engine_results:
            if r["link"] not in seen:
                seen.add(r["link"])
                final_results.append(r)
                if output_format == "sqlite":
                    save_result(conn, r)

    if output_format == "csv":
        safe_query = query.replace(" ", "_")
        filename = os.path.join(RESULTS_DIR, f"results_{safe_query}.csv")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["engine", "title", "link"])
            writer.writeheader()
            writer.writerows(final_results)
        print(f"✅ Done. Saved {len(final_results)} results to {filename}")
    else:
        print(f"✅ Done. Saved {len(final_results)} results to {DB_FILE}")


if __name__ == "__main__":
    try:
        with open(ENGINES_FILE) as f:
            all_engines = json.load(f)
    except FileNotFoundError:
        print(f"[!] Could not find {ENGINES_FILE}. Make sure it exists.")
        exit(1)

    engine_list = ", ".join(all_engines.keys())

    parser = argparse.ArgumentParser(
        description="darkweb-search-R",
        epilog=f"Available engines: {engine_list}"
    )
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--output", choices=["sqlite", "csv"], default="sqlite",
                        help="Output format (sqlite or csv). Default: sqlite")
    parser.add_argument("--engines", nargs="+",
                        help="Specify one or more engines to use (default: all). "
                             "See list below.")

    args = parser.parse_args()

    if args.engines:
        engines = {name: all_engines[name] for name in args.engines if name in all_engines}
        if not engines:
            print("[!] No valid engines selected. Check names in search_engines.json")
            exit(1)
    else:
        engines = all_engines

    asyncio.run(main(args.query, args.output, engines))
