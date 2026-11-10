"""Generate the English static homepage from the bilingual index.html."""

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://120712.com/"
ENGLISH_URL = ORIGIN + "en.html"
TITLE = "Luo Tianyi"


def replace_required(source, original, replacement):
    if original not in source:
        raise ValueError(f"Missing expected markup in index.html: {original}")
    return source.replace(original, replacement, 1)


def build_homepage(source):
    head, body = source.split("</head>", 1)
    head = replace_required(
        head, '<html lang="zh-Hans" data-lang="zh" data-home>',
        '<html lang="en" data-lang="en" data-home>',
    )
    head = replace_required(
        head, f'<link rel="canonical" href="{ORIGIN}" />',
        f'<link rel="canonical" href="{ENGLISH_URL}" />',
    )
    head = re.sub(r"<title>[^<]*</title>", f"<title>{TITLE}</title>", head, count=1)

    meta_pattern = re.compile(r'(<meta (?:name|property)="([^"]+)"\s+content=")([^"]*)(")')
    description = next(match[3] for match in meta_pattern.finditer(head) if match[2] == "description")
    description = description.rsplit(" | ", 1)[-1]
    localized_meta = {
        "description": description,
        "og:title": TITLE,
        "og:description": description,
        "og:image:alt": "Luo Tianyi V3 character art",
        "og:url": ENGLISH_URL,
        "og:locale": "en_US",
        "og:locale:alternate": "zh_CN",
        "twitter:title": TITLE,
        "twitter:description": description,
        "twitter:image:alt": "Luo Tianyi V3 character art",
    }
    head = meta_pattern.sub(lambda m: m[1] + localized_meta.get(m[2], m[3]) + m[4], head)

    schema_pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
    schema = schema_pattern.search(head)
    data = json.loads(schema[2])
    data.update(name=TITLE, description=description, url=ENGLISH_URL, inLanguage="en")
    schema_json = json.dumps(data, ensure_ascii=False, indent=2)
    schema_body = "\n".join("  " + line for line in schema_json.splitlines())
    head = schema_pattern.sub(lambda m: f"{m[1]}\n{schema_body}\n  {m[3]}", head, count=1)

    body = replace_required(
        body, 'id="langToggle" href="en.html" hreflang="en"',
        'id="langToggle" href="./" hreflang="zh-Hans"',
    )
    body = re.sub(r'href="(picture|updates)\.html"', r'href="\1.html?lang=en"', body)

    def english_labels(match):
        tag, label = match[0], match[1]
        return re.sub(r'\b(aria-label|title)="[^"]*"', lambda attr: f'{attr[1]}="{label}"', tag)

    body = re.sub(r'<[^<>]* data-label-en="([^"]+)"[^<>]*>', english_labels, body)
    output = head + "</head>" + body
    banner = "<!-- Generated from index.html by scripts/generate_english_homepage.py. -->"
    return output.replace("<!DOCTYPE html>\n", f"<!DOCTYPE html>\n{banner}\n", 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check en.html without rewriting it.")
    args = parser.parse_args()
    page = ROOT / "en.html"
    expected = build_homepage((ROOT / "index.html").read_text(encoding="utf-8"))
    if args.check:
        if not page.is_file() or page.read_text(encoding="utf-8") != expected:
            parser.exit(1, "en.html is stale. Run python3 scripts/generate_english_homepage.py.\n")
    else:
        page.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
