import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


class _LinkParser(HTMLParser):
    """Collect links without requiring an external HTML parser."""

    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


class _TableParser(HTMLParser):
    """Parse the legacy, server-rendered CompOSE catalogue table."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = {"text": [], "hrefs": []}
        elif tag == "a" and self._cell is not None:
            href = dict(attrs).get("href")
            if href:
                self._cell["hrefs"].append(href)

    def handle_data(self, data):
        if self._cell is not None:
            self._cell["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "td" and self._cell is not None:
            self._row.append(
                ("".join(self._cell["text"]).strip(), self._cell["hrefs"])
            )
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


class DownloadCompose:
    base_link = "https://compose.obspm.fr"
    table_link = f"{base_link}/table/"
    table_data_link = f"{base_link}/table/data/"
    target_files = ("eos.t", "eos.nb", "eos.thermo")
    request_timeout = 30

    def __init__(self, download_dir=Path("./downloads/compose")):
        self.download_dir = Path(download_dir)
        self.title_and_link = self.get_title_and_link()

    @staticmethod
    def _links_from_html(document):
        parser = _LinkParser()
        parser.feed(document)
        return parser.hrefs

    @staticmethod
    def _id_from_link(link):
        match = re.search(r"/eos/(\d+)/?(?:[?#].*)?$", link)
        return int(match.group(1)) if match else None

    @classmethod
    def _get_json_catalogue(cls):
        """Read the server-side data feed used by the current CompOSE table."""
        catalogue = {}
        page_size = 100
        start = 0

        while True:
            response = requests.get(
                cls.table_data_link,
                params={
                    "draw": 1,
                    "start": start,
                    "length": page_size,
                    "order[0][column]": 1,
                    "order[0][dir]": "asc",
                    "search[value]": "",
                },
                timeout=cls.request_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            rows = payload.get("data")
            if not isinstance(rows, list):
                raise ValueError("CompOSE catalogue response has no 'data' list")

            for row in rows:
                if len(row) < 2:
                    continue
                links = []
                for value in row:
                    if isinstance(value, str) and "href" in value:
                        links.extend(cls._links_from_html(value))
                for link in links:
                    eos_id = cls._id_from_link(link)
                    if eos_id is not None:
                        if eos_id in catalogue:
                            raise ValueError(f"Duplicate CompOSE EOS id={eos_id}")
                        catalogue[eos_id] = (str(row[1]).strip(), link)
                        break

            start += len(rows)
            total = int(payload.get("recordsFiltered", len(catalogue)))
            if not rows or start >= total:
                break

        return catalogue

    @classmethod
    def _get_legacy_catalogue(cls):
        """Fall back to the table layout used by older CompOSE releases."""
        response = requests.get(cls.table_link, timeout=cls.request_timeout)
        response.raise_for_status()
        parser = _TableParser()
        parser.feed(response.text)

        catalogue = {}
        for row in parser.rows:
            if len(row) < 2:
                continue
            links = [href for _, hrefs in row for href in hrefs]
            for link in links:
                eos_id = cls._id_from_link(link)
                if eos_id is not None:
                    if eos_id in catalogue:
                        raise ValueError(f"Duplicate CompOSE EOS id={eos_id}")
                    catalogue[eos_id] = (row[1][0], link)
                    break
        return catalogue

    @classmethod
    def get_title_and_link(cls):
        print(f"DownloadCompose: Fetching data from {cls.table_link}\n...")
        json_error = None
        try:
            catalogue = cls._get_json_catalogue()
        except (requests.RequestException, ValueError, TypeError) as error:
            json_error = error
            try:
                catalogue = cls._get_legacy_catalogue()
            except (requests.RequestException, ValueError, TypeError) as legacy_error:
                raise RuntimeError(
                    "Unable to load the CompOSE EOS catalogue from either the "
                    f"current data endpoint ({json_error}) or the legacy table "
                    f"({legacy_error})."
                ) from legacy_error

        if not catalogue:
            detail = f" The data endpoint failed with: {json_error}." if json_error else ""
            raise RuntimeError(
                "CompOSE returned an empty EOS catalogue; its website layout or "
                f"service may have changed.{detail}"
            )

        print(
            f"DownloadCompose: Found {len(catalogue)} EOS data sets on "
            f"{cls.table_link}"
        )
        return dict(sorted(catalogue.items()))

    def print_eos_list(self):
        for eos_id, (title, _) in self.title_and_link.items():
            print(f"id = {eos_id:3}, name = {title}")

    def eos_name(self, eos_id: int):
        try:
            return self.title_and_link[eos_id][0]
        except KeyError as error:
            raise ValueError(f"CompOSE EOS id {eos_id} is not in the catalogue") from error

    def eos_download_dir(self, eos_id: int):
        directory = self.download_dir / f"{eos_id:03}"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @classmethod
    def requests_download(cls, url: str, folder, force=False):
        local_filename = Path(folder) / Path(urlparse(url).path).name
        if local_filename.exists() and not force:
            print(f"{local_filename} already exists, skip download {url}")
            return

        with requests.get(
            url, stream=True, allow_redirects=True, timeout=cls.request_timeout
        ) as response:
            response.raise_for_status()
            with open(local_filename, "wb") as output:
                shutil.copyfileobj(response.raw, output)
        print(f"Downloaded {url} to {local_filename}")

    def download_id(self, eos_id: int, force=False):
        try:
            _, detail_link = self.title_and_link[eos_id]
        except KeyError as error:
            raise ValueError(f"CompOSE EOS id {eos_id} is not in the catalogue") from error

        eos_link = urljoin(self.base_link, detail_link)
        response = requests.get(eos_link, timeout=self.request_timeout)
        response.raise_for_status()
        hrefs = self._links_from_html(response.text)
        target_hrefs = [
            href
            for href in hrefs
            if Path(urlparse(href).path).name in self.target_files
        ]
        if not target_hrefs:
            raise RuntimeError(f"No EOS data files were found on {eos_link}")

        directory = self.eos_download_dir(eos_id)
        for href in target_hrefs:
            self.requests_download(
                urljoin(self.base_link, href),
                directory,
                force=force,
            )
        return directory
