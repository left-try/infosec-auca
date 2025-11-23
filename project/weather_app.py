import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

import requests

API_KEY = "61e9db23e19a84f35ff5e81283ed4c94"
DB_PATH = os.path.join(os.path.dirname(__file__), "weather.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_requests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            city        TEXT NOT NULL,
            temperature REAL,
            description TEXT,
            raw_json    TEXT,
            created_at  TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def fetch_weather(city: str, units: str = "metric") -> dict:
    if not API_KEY:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not set. Please export/set it and try again."
        )

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    main = data.get("main", {})
    wind = data.get("wind", {})
    weather_list = data.get("weather") or []

    temp = main.get("temp")
    feels_like = main.get("feels_like")
    humidity = main.get("humidity")
    desc = weather_list[0]["description"].title() if weather_list else "N/A"
    wind_speed = wind.get("speed")

    return {
        "temp": temp,
        "feels_like": feels_like,
        "humidity": humidity,
        "desc": desc,
        "wind_speed": wind_speed,
        "units": units,
        "raw": data,
    }


def save_weather(city: str, weather: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO weather_requests (city, temperature, description, raw_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            city,
            weather.get("temp"),
            weather.get("desc"),
            json.dumps(weather.get("raw")),
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def _unit_symbol(units: str) -> str:
    if units == "metric":
        return "°C"
    if units == "imperial":
        return "°F"
    return "K"


def print_weather(city: str, weather: dict):
    units = weather.get("units", "metric")
    sym = _unit_symbol(units)

    print(f"\nWeather in {city}:")
    if weather.get("temp") is not None:
        print(f"  Temperature : {weather['temp']:.1f} {sym}")
    else:
        print("  Temperature : N/A")

    print(f"  Conditions  : {weather.get('desc', 'N/A')}")

    if weather.get("feels_like") is not None:
        print(f"  Feels like  : {weather['feels_like']:.1f} {sym}")
    if weather.get("humidity") is not None:
        print(f"  Humidity    : {weather['humidity']}%")
    if weather.get("wind_speed") is not None:
        print(f"  Wind speed  : {weather['wind_speed']} m/s")

    print()


def print_history(limit: int = 10, city: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = """
        SELECT city, temperature, description, created_at
        FROM weather_requests
    """
    params: list = []

    if city:
        query += " WHERE city = ?"
        params.append(city)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        if city:
            print(f"No history yet for city '{city}'.")
        else:
            print("No history yet.")
        return

    title_city = f" for {city}" if city else ""
    print(f"\nLast {len(rows)} saved requests{title_city}:")
    for c, temp, desc, created_at in rows:
        t_str = f"{temp:.1f} °C" if temp is not None else "N/A"
        print(f"[{created_at}] {c}: {t_str}, {desc}")
    print()


def print_cities():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT city
        FROM weather_requests
        ORDER BY city COLLATE NOCASE
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No cities stored yet.")
        return

    print("\nCities in history:")
    for (city,) in rows:
        print(f"  - {city}")
    print()


def print_stats(city: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if city:
        cur.execute(
            """
            SELECT COUNT(*), MIN(temperature), MAX(temperature), AVG(temperature)
            FROM weather_requests
            WHERE city = ? AND temperature IS NOT NULL
            """,
            (city,),
        )
        row = cur.fetchone()
        conn.close()

        count, t_min, t_max, t_avg = row if row else (0, None, None, None)
        if count == 0:
            print(f"No data for city '{city}'.")
            return

        print(f"\nStats for {city}:")
        print(f"  Records : {count}")
        print(f"  Min temp: {t_min:.1f} °C")
        print(f"  Max temp: {t_max:.1f} °C")
        print(f"  Avg temp: {t_avg:.1f} °C\n")

    else:
        cur.execute(
            """
            SELECT city, COUNT(*), MIN(temperature), MAX(temperature), AVG(temperature)
            FROM weather_requests
            WHERE temperature IS NOT NULL
            GROUP BY city
            ORDER BY city COLLATE NOCASE
            """
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No data for stats yet.")
            return

        print("\nStats per city:")
        for city, count, t_min, t_max, t_avg in rows:
            print(
                f"  {city}: {count} records | "
                f"min {t_min:.1f} °C, max {t_max:.1f} °C, avg {t_avg:.1f} °C"
            )
        print()


def export_history(path: str, city: str | None = None, limit: int | None = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = """
        SELECT city, temperature, description, raw_json, created_at
        FROM weather_requests
    """
    params: list = []

    if city:
        query += " WHERE city = ?"
        params.append(city)

    query += " ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    records = []
    for c, temp, desc, raw_json, created_at in rows:
        try:
            raw = json.loads(raw_json) if raw_json else None
        except json.JSONDecodeError:
            raw = None
        records.append(
            {
                "city": c,
                "temperature": temp,
                "description": desc,
                "created_at": created_at,
                "raw": raw,
            }
        )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(records)} records to {path}")


def clear_history(city: str | None = None, force: bool = False):
    if not force:
        target = f"for city '{city}'" if city else "ALL records"
        ans = input(f"Are you sure you want to delete {target}? (y/N): ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted.")
            return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if city:
        cur.execute("DELETE FROM weather_requests WHERE city = ?", (city,))
    else:
        cur.execute("DELETE FROM weather_requests")
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    print(f"Deleted {deleted} record(s).")


def cmd_current(args) -> int:
    city = args.city or input("Enter city name: ").strip()
    if not city:
        print("City name is required.")
        return 1

    try:
        weather = fetch_weather(city, units=args.units)
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            print("City not found. Please check the spelling.")
        else:
            print("Error from weather API:", e)
        return 1
    except Exception as e:
        print("Unexpected error:", e)
        return 1

    print_weather(city, weather)
    save_weather(city, weather)
    print("Saved to local database.\n")
    return 0


def cmd_history(args) -> int:
    print_history(limit=args.limit)
    return 0


def cmd_city_history(args) -> int:
    print_history(limit=args.limit, city=args.city)
    return 0


def cmd_cities(args) -> int:
    print_cities()
    return 0


def cmd_stats(args) -> int:
    print_stats(city=args.city)
    return 0


def cmd_export(args) -> int:
    export_history(path=args.path, city=args.city, limit=args.limit)
    return 0


def cmd_clear(args) -> int:
    clear_history(city=args.city, force=args.yes)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Terminal-based Weather CLI (OpenWeatherMap + SQLite)"
    )

    subparsers = parser.add_subparsers(dest="command")

    p_current = subparsers.add_parser("current", help="Fetch current weather for a city")
    p_current.add_argument("city", nargs="?", help="City name (e.g. 'Bishkek')")
    p_current.add_argument(
        "-u",
        "--units",
        choices=["metric", "imperial", "standard"],
        default="metric",
        help="Units: metric (°C), imperial (°F), standard (Kelvin). Default: metric.",
    )
    p_current.set_defaults(func=cmd_current)

    p_history = subparsers.add_parser("history", help="Show last N saved weather requests")
    p_history.add_argument(
        "-n", "--limit", type=int, default=10, help="How many entries to show (default: 10)"
    )
    p_history.set_defaults(func=cmd_history)

    p_ch = subparsers.add_parser(
        "city-history", help="Show history filtered by a specific city"
    )
    p_ch.add_argument("city", help="City name")
    p_ch.add_argument(
        "-n", "--limit", type=int, default=10, help="How many entries to show (default: 10)"
    )
    p_ch.set_defaults(func=cmd_city_history)

    p_cities = subparsers.add_parser(
        "cities", help="List all cities that appear in the history"
    )
    p_cities.set_defaults(func=cmd_cities)

    p_stats = subparsers.add_parser(
        "stats", help="Show min / max / average temperature per city or for one city"
    )
    p_stats.add_argument(
        "-c", "--city", help="If provided, show stats only for this city"
    )
    p_stats.set_defaults(func=cmd_stats)

    p_export = subparsers.add_parser(
        "export", help="Export history to a JSON file"
    )
    p_export.add_argument("path", help="Output JSON file path")
    p_export.add_argument(
        "-c", "--city", help="If provided, export only records for this city"
    )
    p_export.add_argument(
        "-n", "--limit", type=int, help="Limit the number of records (most recent first)"
    )
    p_export.set_defaults(func=cmd_export)

    p_clear = subparsers.add_parser(
        "clear", help="Delete history (all records or for a specific city)"
    )
    p_clear.add_argument(
        "-c", "--city", help="If provided, delete only records for this city"
    )
    p_clear.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not ask for confirmation (dangerous!)",
    )
    p_clear.set_defaults(func=cmd_clear)

    return parser


def main():
    init_db()
    parser = build_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        args.command = "current"
        args.city = None
        args.units = "metric"
        return sys.exit(cmd_current(args))

    func = getattr(args, "func", None)
    if not func:
        parser.print_help()
        return sys.exit(1)

    code = func(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
