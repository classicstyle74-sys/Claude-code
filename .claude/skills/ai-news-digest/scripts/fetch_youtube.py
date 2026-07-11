#!/usr/bin/env python3
"""YouTube チャンネルの新着動画を RSS 経由で取得する (API キー不要)。

sources.json の youtube_channels に列挙されたハンドル (@xxx) を
チャンネル ID に解決し、各チャンネルの RSS フィードから直近の動画を
JSON で標準出力に返す。

使い方:
    python3 fetch_youtube.py [--hours 36] [--sources path/to/sources.json]
"""
import argparse
import json
import re
import ssl
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = Path(__file__).resolve().parent / ".channel_cache.json"
ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
MEDIA = "{http://search.yahoo.com/mrss/}"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def resolve_channel_id(handle: str, cache: dict) -> str | None:
    """@ハンドルをチャンネル ID (UC...) に解決する。結果はキャッシュ。"""
    if handle in cache:
        return cache[handle]
    if handle.startswith("UC"):
        return handle
    url = f"https://www.youtube.com/{handle}"
    try:
        html = http_get(url).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"warn: {handle} のページ取得に失敗: {e}", file=sys.stderr)
        return None
    m = re.search(r'"channelId":"(UC[0-9A-Za-z_-]{22})"', html)
    if not m:
        m = re.search(r"channel_id=(UC[0-9A-Za-z_-]{22})", html)
    if not m:
        print(f"warn: {handle} のチャンネル ID を特定できず", file=sys.stderr)
        return None
    cache[handle] = m.group(1)
    return m.group(1)


def fetch_feed(channel_id: str, since: datetime) -> list[dict]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    root = ET.fromstring(http_get(url))
    channel_name = root.findtext(f"{ATOM}title", default="")
    videos = []
    for entry in root.iter(f"{ATOM}entry"):
        published = entry.findtext(f"{ATOM}published", default="")
        try:
            dt = datetime.fromisoformat(published)
        except ValueError:
            continue
        if dt < since:
            continue
        link_el = entry.find(f"{ATOM}link")
        media = entry.find(f"{MEDIA}group")
        desc = ""
        if media is not None:
            desc = (media.findtext(f"{MEDIA}description") or "")[:300]
        videos.append(
            {
                "channel": channel_name,
                "title": entry.findtext(f"{ATOM}title", default=""),
                "url": link_el.get("href") if link_el is not None else "",
                "published": published,
                "description": desc,
            }
        )
    return videos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=36,
                        help="この時間内に公開された動画のみ対象 (デフォルト 36)")
    parser.add_argument("--sources", type=Path,
                        default=SKILL_DIR / "sources.json")
    args = parser.parse_args()

    sources = json.loads(args.sources.read_text())
    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    cache = load_cache()

    all_videos: list[dict] = []
    errors: list[str] = []
    for ch in sources.get("youtube_channels", []):
        handle = ch["handle"]
        channel_id = ch.get("channel_id") or resolve_channel_id(handle, cache)
        if not channel_id:
            errors.append(f"{handle}: チャンネル ID 解決失敗")
            continue
        try:
            all_videos.extend(fetch_feed(channel_id, since))
        except Exception as e:
            errors.append(f"{handle}: フィード取得失敗 ({e})")

    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    all_videos.sort(key=lambda v: v["published"], reverse=True)
    json.dump({"since": since.isoformat(), "videos": all_videos,
               "errors": errors},
              sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
