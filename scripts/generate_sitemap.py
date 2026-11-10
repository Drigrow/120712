"""List the canonical, public HTML pages served from the site root."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://120712.com"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


class CanonicalParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            attrs = dict(attrs)
            if "canonical" in (attrs.get("rel") or "").lower().split():
                self.urls.append(attrs.get("href"))


def build_sitemap():
    urls = ET.Element("urlset", xmlns=NAMESPACE)
    for page in sorted(ROOT.glob("*.html")):
        parser = CanonicalParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parser.close()
        path = "/" if page.name == "index.html" else f"/{page.name}"
        url = ORIGIN + path
        if parser.urls == [url]:
            ET.SubElement(ET.SubElement(urls, "url"), "loc").text = url

    ET.indent(urls, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urls, encoding="unicode") + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check sitemap.xml without rewriting it.")
    args = parser.parse_args()
    sitemap = ROOT / "sitemap.xml"
    expected = build_sitemap()
    if args.check:
        if not sitemap.is_file() or sitemap.read_text(encoding="utf-8") != expected:
            parser.exit(1, "sitemap.xml is stale. Run python3 scripts/generate_sitemap.py.\n")
    else:
        sitemap.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
