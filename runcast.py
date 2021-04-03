from collections import namedtuple
from logging import basicConfig, getLogger
from datetime import datetime, timezone, timedelta
from dateutil import parser
from feedparser import parse
from requests import get
from pathlib import Path

LOG = getLogger(__name__)
TODAY = datetime.now(tz=timezone.utc).date()

Show = namedtuple("Show", ["name", "rss"])
SHOWS = [
    Show(name="The Daily", rss="https://feeds.simplecast.com/54nAGcIl"),
    Show(name="Money Talks", rss="https://rss.acast.com/theeconomistmoneytalks"),
    Show(
        name="Today in Focus",
        rss="https://www.theguardian.com/news/series/todayinfocus/podcast.xml",
    ),
    Show(name="Today, Explained", rss="https://feeds.megaphone.fm/VMP5705694065"),
    Show(name="Philosophize This!", rss="https://philosophizethis.libsyn.com/rss/"),
    Show(
        name="The Cloudcast",
        rss="https://feeds.buzzsprout.com/3195.rss",
    ),
]


def run() -> None:
    basicConfig(level=20, format="%(message)s")
    player = Path("/run/media/guillermo/MSCNMMC/Podcasts")
    if not player.exists():
        LOG.warning("Player not mounted")
        exit(0)

    for mp3 in player.iterdir():
        created = datetime.fromtimestamp(mp3.stat().st_ctime, tz=timezone.utc)
        if TODAY - created.date() > timedelta(days=3):
            LOG.info(f"Removing '{mp3.name}'")
            mp3.unlink()

    for show in SHOWS:
        LOG.info(f"Checking {show.name}")
        rss = parse(show.rss)
        episode = rss["entries"][0]
        published = parser.parse(episode["published"])
        url = next(
            link["href"]
            for link in episode["links"]
            if link["type"].startswith("audio")
        )
        target = player / f"{episode['title']}.mp3"
        if published.date() == TODAY and not target.exists():
            LOG.info(f"Downloading '{episode['title']}'")
            stream = get(url)
            with open(target, "wb") as output:
                output.write(stream.content)


if __name__ == "__main__":
    run()
