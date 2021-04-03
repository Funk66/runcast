from re import search, findall
from collections import namedtuple
from logging import basicConfig, getLogger
from datetime import datetime, timezone
from dateutil import parser
from feedparser import parse
from requests import get
from pathlib import Path

LOG = getLogger(__name__)
TODAY = datetime.now(tz=timezone.utc).date()

Show = namedtuple("Show", ["name", "rss"])
Episode = namedtuple("Episode", ["show", "title", "date", "filepath", "url"])
SHOWS = [
    Show(name="The Daily", rss="https://feeds.simplecast.com/54nAGcIl"),
    Show(name="Money Talks", rss="https://rss.acast.com/theeconomistmoneytalks"),
    Show(
        name="Today in Focus",
        rss="https://www.theguardian.com/news/series/todayinfocus/podcast.xml",
    ),
    # Show(name="Today, Explained", rss="https://feeds.megaphone.fm/VMP5705694065"),
    # Show(name="Philosophize This!", rss="https://philosophizethis.libsyn.com/rss/"),
    # Show(
    # name="The Cloudcast",
    # rss="https://feeds.buzzsprout.com/3195.rss",
    # ),
]


def prompt(total: int) -> list[int]:
    try:
        selection = input("Selection: ")
    except KeyboardInterrupt:
        return []

    if not selection or selection == "0":
        return []
    elif selection == "*":
        return list(range(total))

    indices = set()

    try:
        for spread in findall(r"\d+-\d+", selection):
            start, end = [int(n) for n in spread.split("-")]
            indices.update([i - 1 for i in range(start, end + 1)])
            selection.replace(spread, "")
    except Exception as error:
        LOG.error(f"Error parsing {spread}: {error}")
        return prompt(total)

    for number in findall(r"\d+", selection):
        indices.add(int(number) - 1)

    if (invalid_character := search("[^0-9 ,-]", selection)):
        LOG.error(f"The character {invalid_character} is invalid")
        return prompt(total)
    elif max(indices) > total:
        LOG.error("Selection out of bounds")
        return prompt(total)

    return list(indices)


def select(episodes: list[Episode]) -> list[int]:
    for i, episode in enumerate(episodes):
        if episode.show:
            print(f" \033[92m{i+1:<2}\033[0m {episode.show} - {episode.title}")
        else:
            print(f" \033[92m{i+1:<2}\033[0m {episode.title}")
    return prompt(len(episodes))


def cleanup(path: Path) -> datetime:
    LOG.info("Select episodes to remove")
    player_episodes = []
    dates = []
    for filename in path.iterdir():
        show, title = (
            filename.name.split(" - ", maxsplit=1)
            if " - " in filename.name
            else ["", filename.name]
        )
        download_date = datetime.fromtimestamp(
            filename.stat().st_ctime, tz=timezone.utc
        )
        player_episodes.append(Episode(show, title, download_date, filename, ""))
        dates.append(download_date)

    selection = select(player_episodes)
    for i in selection:
        episode = player_episodes[i]
        LOG.info(f"Removing '{episode.title}'")
        episode.filepath.unlink()

    return max(dates)


def download(since: datetime, path: Path) -> None:
    new_episodes = []
    for show in SHOWS:
        LOG.info(f"Checking {show.name}")
        rss = parse(show.rss)
        for entry in rss["entries"]:
            published = parser.parse(entry["published"])
            if published > since:
                url = next(
                    link["href"]
                    for link in entry["links"]
                    if link["type"].startswith("audio")
                )
                title = entry["title"].strip()
                filepath = path / f"{show} - {title}.mp3"
                new_episodes.append(Episode(show.name, title, published, filepath, url))

    LOG.info("Select episodes to download")
    selection = select(new_episodes)
    for i in selection:
        episode = new_episodes[i]
        LOG.info(f"Downloading '{episode.title}'")
        stream = get(episode.url)
        with open(episode.filepath, "wb") as output:
            output.write(stream.content)


def run() -> None:
    basicConfig(level=20, format="%(message)s")
    player_path = Path("/run/media/guillermo/MSCNMMC/Podcasts")
    if not player_path.exists():
        LOG.warning("Player not mounted")
        exit(0)

    newest_episode_date = cleanup(path=player_path)
    download(since=newest_episode_date, path=player_path)


if __name__ == "__main__":
    run()
