"""Downloads Astronomy Picture of the Day into a directory .../apod/[yyyy-mm] using one of NASA's public APIs"""

import datetime
import json
import os
import sys

import requests
import wget


def _page_json() -> dict:
    """Get Astronomy Picture Of the Day (APOD) JSON response from API"""
    # No API key is actually required for APOD unless you send a lot of requests
    headers = {"api_key": "DEMO_KEY"}
    res = requests.get("https://api.nasa.gov/planetary/apod", headers)
    res.raise_for_status()
    return res.json()


def _download_dir(basedir: str) -> str:
    """
    Ensure download path exists, making one or two directories as needed.
    Files will be downloaded e.g. <basedir>/apod/<month>/<image>.jpg
    """
    download_path = os.path.join(basedir, "apod")
    subdir = os.path.join(download_path, datetime.datetime.now().strftime("%Y-%m"))
    os.makedirs(subdir, exist_ok=True)
    return subdir


def _download(page_json: dict, download_dir: str) -> None:
    """
    Given an API response and a download destination directory, downloads
    the Astronomy Picture Of the Day and its corresponding metadata.
    """
    download_url = page_json["hdurl"]
    basename = os.path.basename(download_url)
    file_name, _ = os.path.splitext(basename)
    image_path = os.path.join(download_dir, basename)
    info_path = os.path.join(download_dir, f"{file_name}.json")

    wget.download(download_url, image_path)
    with open(info_path, "w+") as f:
        json.dump(page_json, f)


def main():
    download_dir = _download_dir(os.path.dirname(__file__))
    try:
        page_json = _page_json()
    except requests.HTTPError as e:
        print(f"Failed to query API: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        _download(page_json, download_dir)
    except ValueError as e:
        print(f"Failed to download image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
