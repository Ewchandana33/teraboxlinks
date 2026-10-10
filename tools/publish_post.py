#!/usr/bin/env python3
"""Publish one Markdown post into this static TeraBox site."""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit


SITE = "https://teraboxlinks.pages.dev"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("image", "http://www.google.com/schemas/sitemap-image/1.1")
ET.register_namespace("atom", ATOM_NS)


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"Error: {message}")


def parse_post(source: Path) -> tuple[dict[str, str], str]:
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Cannot read {source}: {exc}")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail("Post must begin with YAML-style fields between --- lines.")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        fail("Missing closing --- after post fields.")

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            fail(f"Invalid post field: {line}")
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        metadata[key] = value

    required = ("title", "slug", "description", "keyword", "date")
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        fail("Missing required field(s): " + ", ".join(missing))
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["slug"]):
        fail("Slug must use lowercase English letters, numbers, and hyphens.")
    if source.stem != metadata["slug"]:
        fail(f"Markdown filename must match the slug: {metadata['slug']}.md")
    try:
        dt.date.fromisoformat(metadata["date"])
    except ValueError:
        fail("Date must use YYYY-MM-DD.")
    metadata.setdefault("language", "en")
    body = "\n".join(lines[end + 1:]).strip()
    if not body:
        fail("The post body is empty.")
    if len(metadata["description"]) > 170:
        fail("Description is too long (maximum 170 characters).")
    return metadata, body


def safe_link(url: str) -> bool:
    parts = urlsplit(url.strip())
    return (
        not parts.scheme
        or parts.scheme.lower() in {"http", "https", "mailto"}
    ) and not url.strip().lower().startswith(("javascript:", "data:", "vbscript:"))


def inline_markdown(text: str) -> str:
    escaped = html.escape(text, quote=False)
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

    def link_replacement(match: re.Match[str]) -> str:
        label, url = match.group(1), html.unescape(match.group(2))
        if not safe_link(url):
            return label
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

    escaped = link_pattern.sub(link_replacement, escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_markdown(markdown: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None

    def close_paragraph() -> None:
        if paragraph:
            output.append("<p>" + " ".join(inline_markdown(x) for x in paragraph) + "</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(f"</{list_kind}>")
            list_kind = None

    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            close_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{2,3})\s+(.+)$", stripped)
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if heading:
            close_paragraph()
            close_list()
            level = min(len(heading.group(1)), 3)
            output.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
        elif bullet or numbered:
            close_paragraph()
            kind = "ul" if bullet else "ol"
            if kind != list_kind:
                close_list()
                output.append(f"<{kind}>")
                list_kind = kind
            item = (bullet or numbered).group(1)
            output.append(f"<li>{inline_markdown(item)}</li>")
        else:
            close_list()
            paragraph.append(stripped)
    close_paragraph()
    close_list()
    return "\n".join(output)


def article_html(meta: dict[str, str], body: str) -> str:
    title = html.escape(meta["title"], quote=True)
    description = html.escape(meta["description"], quote=True)
    slug = meta["slug"]
    url = f"{SITE}/posts/{slug}"
    date = meta["date"]
    language = html.escape(meta["language"], quote=True)
    image_url = f"{SITE}/public/images/banner.jpg"
    image_alt = "TeraBox shared-video bundle directory banner"
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": f"{url}#article",
                "headline": meta["title"],
                "description": meta["description"],
                "url": url,
                "mainEntityOfPage": {"@type": "WebPage", "@id": url},
                "datePublished": date,
                "dateModified": date,
                "inLanguage": meta["language"],
                "image": image_url,
                "keywords": [meta["keyword"]],
                "author": {
                    "@type": "Organization",
                    "name": "terabox video link",
                    "url": SITE + "/",
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "terabox video link",
                    "url": SITE + "/",
                    "logo": {
                        "@type": "ImageObject",
                        "url": f"{SITE}/public/images/logo.webp",
                    },
                },
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": SITE + "/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Posts",
                        "item": f"{SITE}/posts",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": meta["title"],
                        "item": url,
                    },
                ],
            },
        ],
    }
    schema = json.dumps(structured, ensure_ascii=False, indent=2).replace("</", "<\\/")
    content = render_markdown(body)
    return f'''<!doctype html>
<!-- Generated from posts-src/{slug}.md; managed by tools/publish_post.py. -->
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="dark">
  <meta name="theme-color" content="#050505">
  <title>{title} | TeraBox Video Link</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta name="author" content="terabox video link">
  <link rel="canonical" href="{url}">
  <link rel="alternate" type="application/rss+xml" title="terabox video link" href="/feed.xml">
  <link rel="icon" href="/public/images/favicon.png" type="image/png">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="terabox video link">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{url}">
   <meta property="og:image" content="{image_url}">
   <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{SITE}/public/images/banner.jpg">
   <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">
  <link rel="stylesheet" href="/legal.css">
  <script type="application/ld+json">{schema}</script>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <main class="legal-shell" id="main-content">
    <article class="post-article">
    <header class="legal-header">
      <a class="brand-link" href="/">
        <span class="brand-logo"><img src="/public/images/logo.webp" width="72" height="72" alt=""></span>
        <span class="brand-name">terabox video link</span>
      </a>
      <h1>{title}</h1>
      <p class="legal-summary">{description}</p>
      <span class="updated-date">Published: {date}</span>
    </header>
    <nav class="legal-navigation" aria-label="Site pages">
      <a href="/">Home</a><a href="/guides">Guides</a><a href="/posts" aria-current="page">Posts</a><a href="/terabox-guide">Setup</a><a href="/troubleshooting">Fixes</a><a href="/safety-guide">Safety</a><a href="/faq">FAQ</a>
    </nav>
    <nav class="breadcrumb" aria-label="Breadcrumb"><ol>
      <li><a href="/">Home</a></li><li><a href="/posts">Posts</a></li><li><span aria-current="page">{title}</span></li>
    </ol></nav>
    <div class="legal-content">
      <div class="legal-card">
        {content}
      </div>
      <section class="legal-card">
        <h2>Browse TeraBox video bundles</h2>
        <p>Visit the homepage to see the available video bundles. Check each shared folder for its current contents and only access material you are authorized to use.</p>
        <a class="home-button" href="/#bundles">View video bundles on the homepage</a>
        <p><a href="/">Go to the homepage</a></p>
      </section>
      <section class="legal-card">
        <h2>More TeraBox guides</h2>
        <div class="guide-grid">
          <a class="guide-card" href="/posts"><strong>All posts</strong><span>Browse the site's TeraBox video guides.</span></a>
          <a class="guide-card" href="/terabox-guide"><strong>Open a shared link</strong><span>Learn how to open a shared TeraBox folder safely.</span></a>
          <a class="guide-card" href="/safety-guide"><strong>Stay safe</strong><span>Read the shared-link safety guide.</span></a>
        </div>
      </section>
    </div>
    </article>
    <footer class="legal-footer">
      <nav class="footer-links" aria-label="Explore guides"><a href="/">Home</a><a href="/posts">Posts</a><a href="/guides">All guides</a><a href="/contact">Contact</a></nav>
      <p>&copy; 2026 terabox video link.</p>
      <p>Independent directory with no official TeraBox affiliation.</p>
    </footer>
  </main>
</body>
</html>
'''


def update_index(path: Path, meta: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    slug = meta["slug"]
    card = (
        f'<a class="guide-card" href="/posts/{html.escape(slug, quote=True)}">'
        f'<strong>{html.escape(meta["title"])}</strong>'
        f'<span>{html.escape(meta["description"])}</span></a>'
    )
    pattern = re.compile(
        rf'<a class="guide-card" href="/posts/{re.escape(slug)}">.*?</a>',
        re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(lambda _: card, text, count=1)
    else:
        grid = re.search(r'(<div class="guide-grid">)(.*?)(</div>)', text, re.DOTALL)
        if not grid:
            fail(f"Could not find a guide-grid in {path}.")
        text = text[:grid.end(2)] + "\n                    " + card + text[grid.end(2):]
    path.write_text(text, encoding="utf-8")


def update_sitemap(path: Path, slug: str, date: str) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    target = f"{SITE}/posts/{slug}"
    posts_index = f"{SITE}/posts"
    found = None
    for entry in root.findall(f"{{{SITEMAP_NS}}}url"):
        loc = entry.find(f"{{{SITEMAP_NS}}}loc")
        if loc is not None and loc.text == posts_index:
            lastmod = entry.find(f"{{{SITEMAP_NS}}}lastmod")
            if lastmod is None:
                lastmod = ET.SubElement(entry, f"{{{SITEMAP_NS}}}lastmod")
            if not lastmod.text or lastmod.text < date:
                lastmod.text = date
        if loc is not None and loc.text == target:
            found = entry
    if found is None:
        found = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(found, f"{{{SITEMAP_NS}}}loc").text = target
        ET.SubElement(found, f"{{{SITEMAP_NS}}}lastmod").text = date
    else:
        lastmod = found.find(f"{{{SITEMAP_NS}}}lastmod")
        if lastmod is None:
            lastmod = ET.SubElement(found, f"{{{SITEMAP_NS}}}lastmod")
        lastmod.text = date
    tree.write(path, encoding="utf-8", xml_declaration=True)


def update_feed(path: Path, meta: dict[str, str]) -> None:
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    if channel is None:
        fail(f"RSS channel not found in {path}.")
    date = dt.date.fromisoformat(meta["date"])
    pub_date = dt.datetime.combine(date, dt.time(), tzinfo=dt.timezone.utc)
    pub_date_text = pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    build_date = channel.find("lastBuildDate")
    if build_date is None:
        build_date = ET.Element("lastBuildDate")
        language = channel.find("language")
        channel.insert(list(channel).index(language) + 1 if language is not None else 0, build_date)
    build_date.text = pub_date_text

    link = f"{SITE}/posts/{meta['slug']}"
    item = next(
        (entry for entry in channel.findall("item")
         if entry.findtext("link") == link or entry.findtext("guid") == link),
        None,
    )
    if item is None:
        item = ET.Element("item")
        first_item = channel.find("item")
        channel.insert(list(channel).index(first_item) if first_item is not None else len(channel), item)
    for child in list(item):
        item.remove(child)
    ET.SubElement(item, "title").text = meta["title"]
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
    ET.SubElement(item, "pubDate").text = pub_date_text
    ET.SubElement(item, "description").text = meta["description"]
    tree.write(path, encoding="utf-8", xml_declaration=True)


def read_published_slugs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot read generated-post manifest {path}: {exc}")
    if not isinstance(data, list) or any(
        not isinstance(slug, str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug)
        for slug in data
    ):
        fail(f"Invalid generated-post manifest: {path}")
    return set(data)


def set_index_cards(
    path: Path,
    posts: dict[str, tuple[dict[str, str], str]],
    managed_slugs: set[str],
) -> None:
    """Replace generated-post cards while preserving hand-authored guide cards."""
    text = path.read_text(encoding="utf-8")
    grid = re.search(r'(<div class="guide-grid">)(.*?)(</div>)', text, re.DOTALL)
    if not grid:
        fail(f"Could not find a guide-grid in {path}.")

    card_pattern = re.compile(
        r'<a\b(?P<attrs>[^>]*)>.*?</a>',
        re.DOTALL,
    )

    def keep_unmanaged_card(match: re.Match[str]) -> str:
        href = re.search(r'\bhref="/posts/([^"]+)"', match.group("attrs"))
        if href and href.group(1) in managed_slugs:
            return ""
        return match.group(0)

    contents = card_pattern.sub(keep_unmanaged_card, grid.group(2)).rstrip()
    cards = []
    for slug in sorted(
        posts, key=lambda s: (posts[s][0]["date"], s), reverse=True
    ):
        meta = posts[slug][0]
        cards.append(
            f'<a class="guide-card" href="/posts/{html.escape(slug, quote=True)}">'
            f'<strong>{html.escape(meta["title"])}</strong>'
            f'<span>{html.escape(meta["description"])}</span></a>'
        )
    if cards:
        contents += "\n" + "\n".join("                    " + card for card in cards)
    contents += "\n                "
    text = text[:grid.start(2)] + contents + text[grid.end(2):]
    path.write_text(text, encoding="utf-8")


def remove_sitemap_entries(path: Path, slugs: set[str]) -> None:
    if not slugs:
        return
    tree = ET.parse(path)
    root = tree.getroot()
    targets = {f"{SITE}/posts/{slug}" for slug in slugs}
    for entry in list(root.findall(f"{{{SITEMAP_NS}}}url")):
        loc = entry.find(f"{{{SITEMAP_NS}}}loc")
        if loc is not None and loc.text in targets:
            root.remove(entry)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def remove_feed_items(path: Path, slugs: set[str]) -> None:
    if not slugs:
        return
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    if channel is None:
        fail(f"RSS channel not found in {path}.")
    targets = {f"{SITE}/posts/{slug}" for slug in slugs}
    for item in list(channel.findall("item")):
        if item.findtext("link") in targets or item.findtext("guid") in targets:
            channel.remove(item)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def refresh_feed_build_date(path: Path) -> None:
    """Set RSS lastBuildDate from remaining entries, not a deleted newest post."""
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    if channel is None:
        fail(f"RSS channel not found in {path}.")
    dates = []
    for item in channel.findall("item"):
        value = item.findtext("pubDate")
        if value:
            try:
                dates.append(email.utils.parsedate_to_datetime(value))
            except (TypeError, ValueError, OverflowError):
                continue
    build_date = channel.find("lastBuildDate")
    if dates:
        latest = max(dates).astimezone(dt.timezone.utc)
        if build_date is None:
            build_date = ET.Element("lastBuildDate")
            language = channel.find("language")
            channel.insert(list(channel).index(language) + 1 if language is not None else 0, build_date)
        build_date.text = latest.strftime("%a, %d %b %Y %H:%M:%S GMT")
    elif build_date is not None:
        channel.remove(build_date)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def sync_posts(root: Path) -> None:
    """Reconcile generated outputs with the complete posts-src Markdown set."""
    source_dir = root / "posts-src"
    manifest = root / "tools" / "published-posts.json"
    index = root / "posts" / "index.html"
    sitemap = root / "sitemap.xml"
    feed = root / "feed.xml"
    for path in (source_dir, index, sitemap, feed):
        if not path.exists():
            fail(f"Run this from the site repository root; missing: {path.relative_to(root)}")

    # Parse and validate every source before changing any generated output.
    posts: dict[str, tuple[dict[str, str], str]] = {}
    for source in sorted(source_dir.glob("*.md")):
        meta, body = parse_post(source)
        slug = meta["slug"]
        if slug in posts:
            fail(f"Duplicate post slug: {slug}")
        posts[slug] = (meta, body)

    previous_slugs = read_published_slugs(manifest)
    current_slugs = set(posts)
    managed_slugs = previous_slugs | current_slugs

    for slug in current_slugs - previous_slugs:
        article = root / "posts" / f"{slug}.html"
        if article.exists():
            existing = article.read_text(encoding="utf-8")
            if "managed by tools/publish_post.py" not in existing:
                fail(
                    f"Refusing to overwrite untracked page posts/{slug}.html. "
                    "Rename the Markdown slug or add that page to tools/published-posts.json "
                    "only if it was generated from this source."
                )

    # Validate XML before any writes, so malformed indexes cannot cause a
    # partially reconciled site.
    ET.parse(sitemap)
    ET.parse(feed)
    if not re.search(r'<div class="guide-grid">', index.read_text(encoding="utf-8")):
        fail(f"Expected Posts index guide-grid was not found in {index}.")

    # Remove all previously managed cards/items/URLs first, then re-add the
    # complete current source set. Unrelated hand-authored content is retained.
    set_index_cards(index, posts, managed_slugs)
    remove_sitemap_entries(sitemap, managed_slugs)
    remove_feed_items(feed, managed_slugs)

    for slug in sorted(current_slugs, key=lambda s: (posts[s][0]["date"], s)):
        meta, body = posts[slug]
        article = root / "posts" / f"{slug}.html"
        article.parent.mkdir(parents=True, exist_ok=True)
        article.write_text(article_html(meta, body), encoding="utf-8")
        update_sitemap(sitemap, slug, meta["date"])
        update_feed(feed, meta)
    refresh_feed_build_date(feed)

    # A deleted source owns only its generated article page and matching mirror.
    removed_slugs = previous_slugs - current_slugs
    for slug in removed_slugs:
        (root / "posts" / f"{slug}.html").unlink(missing_ok=True)

    staging = root / "site-files"
    if staging.is_dir():
        for slug in removed_slugs:
            (staging / "posts" / f"{slug}.html").unlink(missing_ok=True)
        for relative in (
            *(Path("posts") / f"{slug}.html" for slug in sorted(current_slugs)),
            Path("posts") / "index.html",
            Path("sitemap.xml"),
            Path("feed.xml"),
        ):
            source_file = root / relative
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(sorted(current_slugs), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Reconciled {len(current_slugs)} Markdown post(s); removed {len(removed_slugs)} deleted post(s).")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish a post or reconcile all generated post outputs with posts-src/."
    )
    parser.add_argument(
        "post",
        type=Path,
        nargs="?",
        help="Optional Markdown post file (legacy single-post mode); omit to reconcile all posts-src/ files",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Site repository root (default: current directory)")
    parser.add_argument("--update", action="store_true", help="Allow replacing an existing post with the same slug")
    args = parser.parse_args()

    if sys.version_info < (3, 9):
        fail("Python 3.9 or newer is required.")
    root = args.root.resolve()
    if args.post is None:
        sync_posts(root)
        return 0

    source = args.post.resolve()
    meta, body = parse_post(source)
    article = root / "posts" / f"{meta['slug']}.html"
    targets = [article, root / "posts" / "index.html", root / "sitemap.xml", root / "feed.xml"]
    missing = [str(p.relative_to(root)) for p in targets[1:] if not p.is_file()]
    if missing:
        fail("Run this from the site repository root; missing: " + ", ".join(missing))
    if article.exists() and not args.update:
        fail(f"{article.relative_to(root)} already exists. Use --update only if you intend to replace it.")
    if not re.search(r'<div class="guide-grid">', (root / "posts" / "index.html").read_text(encoding="utf-8")):
        fail("Expected Posts index guide-grid was not found.")
    # Validate both XML inputs before changing any site files.
    ET.parse(root / "sitemap.xml")
    ET.parse(root / "feed.xml")

    manifest = root / "tools" / "published-posts.json"
    published_slugs = read_published_slugs(manifest)

    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text(article_html(meta, body), encoding="utf-8")
    update_index(root / "posts" / "index.html", meta)
    update_sitemap(root / "sitemap.xml", meta["slug"], meta["date"])
    update_feed(root / "feed.xml", meta)

    # The attached project snapshot keeps a staging mirror for copied page files.
    # If present, keep the matching generated files synchronized with the root.
    staging = root / "site-files"
    if staging.is_dir():
        for relative in (
            Path("posts") / f"{meta['slug']}.html",
            Path("posts") / "index.html",
            Path("sitemap.xml"),
            Path("feed.xml"),
        ):
            source_file = root / relative
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(sorted(published_slugs | {meta["slug"]}), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Published files updated:")
    print(f"  posts/{meta['slug']}.html")
    print("  posts/index.html")
    print("  sitemap.xml")
    print("  feed.xml")
    if staging.is_dir():
        print("  site-files/ mirror (where available)")
    print("\nReview the generated page, then commit and deploy the site as usual.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
