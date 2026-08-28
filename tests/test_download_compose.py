import io

import pytest
import requests

from EOSgenerators import download_compose
from EOSgenerators.download_compose import DownloadCompose


class FakeResponse:
    def __init__(self, *, text="", json_data=None, status_code=200, content=b""):
        self.text = text
        self._json_data = json_data
        self.status_code = status_code
        self.raw = io.BytesIO(content)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        if self._json_data is None:
            raise ValueError("not JSON")
        return self._json_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def _catalogue_row(eos_id, name):
    return [
        1,
        name,
        "Cold Neutron Star EoS",
        f'<a href="/eos/{eos_id}">details</a>',
    ]


def test_current_catalogue_api_is_paginated(monkeypatch):
    rows = [_catalogue_row(316, "SPG(M2) Crust NS EoS"), _catalogue_row(317, "EOS B")]
    starts = []

    def fake_get(url, **kwargs):
        assert url == DownloadCompose.table_data_link
        start = kwargs["params"]["start"]
        starts.append(start)
        page = rows[start : start + 1]
        return FakeResponse(
            json_data={
                "recordsFiltered": len(rows),
                "data": page,
            }
        )

    monkeypatch.setattr(download_compose.requests, "get", fake_get)

    catalogue = DownloadCompose.get_title_and_link()

    assert starts == [0, 1]
    assert catalogue[316] == ("SPG(M2) Crust NS EoS", "/eos/316")


def test_legacy_catalogue_fallback(monkeypatch):
    legacy_html = """
    <table>
      <tr class="odd">
        <td>1</td><td>Legacy EOS</td><td><a href="/eos/316">details</a></td>
      </tr>
    </table>
    """

    def fake_get(url, **kwargs):
        if url == DownloadCompose.table_data_link:
            return FakeResponse(status_code=500)
        assert url == DownloadCompose.table_link
        return FakeResponse(text=legacy_html)

    monkeypatch.setattr(download_compose.requests, "get", fake_get)

    catalogue = DownloadCompose.get_title_and_link()

    assert catalogue == {316: ("Legacy EOS", "/eos/316")}


def test_empty_catalogue_is_reported_when_instance_is_created(monkeypatch):
    monkeypatch.setattr(
        download_compose.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            json_data={"recordsFiltered": 0, "data": []}
        ),
    )

    with pytest.raises(RuntimeError, match="empty EOS catalogue"):
        DownloadCompose()


def test_download_id_downloads_required_files_and_returns_directory(
    monkeypatch, tmp_path
):
    detail_html = """
    <a href="/download/model/eos.t">table</a>
    <a href="/download/model/eos.nb">density</a>
    <a href="/download/model/eos.thermo">thermodynamics</a>
    <a href="/download/model/eos.pdf">documentation</a>
    """

    def fake_get(url, **kwargs):
        if url == "https://compose.obspm.fr/eos/316":
            return FakeResponse(text=detail_html)
        filename = url.rsplit("/", 1)[-1]
        return FakeResponse(content=filename.encode())

    monkeypatch.setattr(download_compose.requests, "get", fake_get)
    downloader = object.__new__(DownloadCompose)
    downloader.download_dir = tmp_path
    downloader.title_and_link = {316: ("SPG(M2) Crust NS EoS", "/eos/316")}

    directory = downloader.download_id(316)

    assert directory == tmp_path / "316"
    assert sorted(path.name for path in directory.iterdir()) == [
        "eos.nb",
        "eos.t",
        "eos.thermo",
    ]
    assert (directory / "eos.t").read_bytes() == b"eos.t"


def test_download_id_reports_unknown_catalogue_id(tmp_path):
    downloader = object.__new__(DownloadCompose)
    downloader.download_dir = tmp_path
    downloader.title_and_link = {}

    with pytest.raises(ValueError, match="EOS id 316 is not in the catalogue"):
        downloader.download_id(316)
