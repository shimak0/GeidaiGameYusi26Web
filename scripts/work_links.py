"""作品フォルダ内の links.txt を検査・変換する共通処理。"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse


LINK_KEYS = ("youtube", "youtube_channel", "x", "instagram", "steam", "website")
MAX_LINKS_BYTES = 16 * 1024
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{6,}$")
SERVICE_HOSTS = {
    "youtube": {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"},
    "youtube_channel": {"youtube.com", "www.youtube.com", "m.youtube.com"},
    "x": {"x.com", "www.x.com", "twitter.com", "www.twitter.com"},
    "instagram": {"instagram.com", "www.instagram.com"},
    "steam": {"store.steampowered.com", "steamcommunity.com", "www.steamcommunity.com"},
}
YOUTUBE_CHANNEL_PATHS = {"channel", "c", "user"}


def youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        else:
            parts = parsed.path.strip("/").split("/")
            candidate = parts[1] if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"} else ""
    else:
        return None
    return candidate if YOUTUBE_ID.fullmatch(candidate) else None


def youtube_embed_url(url: str) -> str:
    video_id = youtube_video_id(url)
    if not video_id:
        raise ValueError("YouTube動画URLから動画IDを取得できません")
    return f"https://www.youtube.com/embed/{video_id}"


def is_youtube_channel_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in SERVICE_HOSTS["youtube_channel"]:
        return False
    parts = parsed.path.strip("/").split("/")
    return bool(
        parts
        and (
            parts[0].startswith("@") and len(parts[0]) > 1
            or len(parts) >= 2 and parts[0] in YOUTUBE_CHANNEL_PATHS and parts[1]
        )
    )


def validate_url(key: str, value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"{key} は https:// から始まるURLを指定してください")
    allowed_hosts = SERVICE_HOSTS.get(key)
    if allowed_hosts and parsed.hostname not in allowed_hosts:
        raise ValueError(f"{key} のURLドメインが正しくありません: {parsed.hostname}")
    if key == "youtube":
        youtube_embed_url(value)
    elif key == "youtube_channel" and not is_youtube_channel_url(value):
        raise ValueError("youtube_channel はYouTubeチャンネルURLを指定してください")


def parse_links_text(text: str) -> dict[str, str]:
    if len(text.encode("utf-8")) > MAX_LINKS_BYTES:
        raise ValueError("links.txt の内容が16KBを超えています")
    links: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"links.txt {line_number}行目に「:」がありません")
        raw_key, raw_value = line.split(":", 1)
        key = raw_key.strip().lower()
        value = raw_value.strip()
        if key == "youtube" and value and is_youtube_channel_url(value):
            key = "youtube_channel"
        if key not in LINK_KEYS:
            raise ValueError(f"links.txt {line_number}行目のキーを認識できません: {key}")
        if key in links:
            raise ValueError(f"links.txt でキーが重複しています: {key}")
        if value:
            validate_url(key, value)
        links[key] = value
    return {key: links.get(key, "") for key in LINK_KEYS}


def parse_links(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    if path.stat().st_size > MAX_LINKS_BYTES:
        raise ValueError("links.txt が16KBを超えています")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("links.txt はUTF-8で保存してください") from error
    return parse_links_text(text)
