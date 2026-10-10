import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
PUBLISHER = REPOSITORY / "tools" / "publish_post.py"


def markdown(slug: str, title: str | None = None) -> str:
    title = title or slug.replace("-", " ").title()
    return f"""---
title: "{title}"
slug: "{slug}"
description: "Description for {slug}."
keyword: "keyword"
date: "2026-10-08"
language: "en"
---

Content for {slug}.
"""


class PublishReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ("posts-src", "posts", "tools", "site-files/posts"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        (self.root / "posts-src" / "active-post.md").write_text(
            markdown("active-post"), encoding="utf-8"
        )
        (self.root / "tools" / "published-posts.json").write_text(
            json.dumps(["active-post", "deleted-post"]), encoding="utf-8"
        )
        (self.root / "posts" / "index.html").write_text(
            """<div class="guide-grid">
<a class="guide-card" href="/terabox-guide">Static guide</a>
<a class="guide-card" href="/posts/active-post">Old active card</a>
<a class="guide-card" href="/posts/deleted-post">Deleted card</a>
</div>
""",
            encoding="utf-8",
        )
        (self.root / "posts" / "active-post.html").write_text("old generated page")
        (self.root / "posts" / "deleted-post.html").write_text("deleted generated page")
        (self.root / "posts" / "manual-post.html").write_text("manual page")
        (self.root / "feed.xml").write_text(
            """<?xml version="1.0"?>
<rss version="2.0"><channel>
<title>Site feed</title>
<lastBuildDate>Fri, 09 Oct 2026 00:00:00 GMT</lastBuildDate>
<item><title>Old active</title><link>https://teraboxlinks.pages.dev/posts/active-post</link><guid>https://teraboxlinks.pages.dev/posts/active-post</guid><pubDate>Thu, 08 Oct 2026 00:00:00 GMT</pubDate></item>
<item><title>Deleted</title><link>https://teraboxlinks.pages.dev/posts/deleted-post</link><guid>https://teraboxlinks.pages.dev/posts/deleted-post</guid><pubDate>Fri, 09 Oct 2026 00:00:00 GMT</pubDate></item>
<item><title>Static</title><link>https://teraboxlinks.pages.dev/about</link><guid>https://teraboxlinks.pages.dev/about</guid><pubDate>Thu, 01 Oct 2026 00:00:00 GMT</pubDate></item>
</channel></rss>
""",
            encoding="utf-8",
        )
        (self.root / "sitemap.xml").write_text(
            """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://teraboxlinks.pages.dev/posts/active-post</loc><lastmod>2026-10-08</lastmod></url>
<url><loc>https://teraboxlinks.pages.dev/posts/deleted-post</loc><lastmod>2026-10-08</lastmod></url>
<url><loc>https://teraboxlinks.pages.dev/posts/manual-post</loc></url>
</urlset>
""",
            encoding="utf-8",
        )
        (self.root / "site-files" / "posts" / "active-post.html").write_text("old active mirror")
        (self.root / "site-files" / "posts" / "deleted-post.html").write_text("deleted mirror")
        (self.root / "site-files" / "posts" / "manual-post.html").write_text("manual mirror")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_sync(self) -> None:
        subprocess.run(
            [sys.executable, str(PUBLISHER), "--root", str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_deletion_removes_only_source_managed_outputs_and_addition_publishes(self) -> None:
        (self.root / "posts-src" / "deleted-post.md").unlink(missing_ok=True)
        self.run_sync()

        self.assertFalse((self.root / "posts" / "deleted-post.html").exists())
        self.assertFalse((self.root / "site-files" / "posts" / "deleted-post.html").exists())
        self.assertFalse("/posts/deleted-post" in (self.root / "posts" / "index.html").read_text())
        self.assertFalse("/posts/deleted-post" in (self.root / "feed.xml").read_text())
        self.assertFalse("/posts/deleted-post" in (self.root / "sitemap.xml").read_text())
        self.assertIn(
            "<lastBuildDate>Thu, 08 Oct 2026 00:00:00 GMT</lastBuildDate>",
            (self.root / "feed.xml").read_text(),
        )
        self.assertTrue((self.root / "posts" / "manual-post.html").exists())
        self.assertTrue((self.root / "site-files" / "posts" / "manual-post.html").exists())
        self.assertIn("/terabox-guide", (self.root / "posts" / "index.html").read_text())

        (self.root / "posts-src" / "new-post.md").write_text(
            markdown("new-post", "New Post"), encoding="utf-8"
        )
        self.run_sync()
        for output in ("posts/new-post.html", "site-files/posts/new-post.html"):
            self.assertTrue((self.root / output).exists(), output)
        self.assertIn("/posts/new-post", (self.root / "posts" / "index.html").read_text())
        self.assertIn("/posts/new-post", (self.root / "feed.xml").read_text())
        self.assertIn("/posts/new-post", (self.root / "sitemap.xml").read_text())
        self.assertEqual(
            json.loads((self.root / "tools" / "published-posts.json").read_text()),
            ["active-post", "new-post"],
        )

    def test_empty_source_folder_removes_all_managed_posts_but_not_manual_pages(self) -> None:
        (self.root / "posts-src" / "active-post.md").unlink()
        (self.root / "posts-src" / "deleted-post.md").unlink(missing_ok=True)
        self.run_sync()
        self.assertFalse((self.root / "posts" / "active-post.html").exists())
        self.assertFalse((self.root / "site-files" / "posts" / "active-post.html").exists())
        self.assertNotIn("/posts/active-post", (self.root / "feed.xml").read_text())
        self.assertNotIn("/posts/active-post", (self.root / "sitemap.xml").read_text())
        self.assertTrue((self.root / "posts" / "manual-post.html").exists())
        self.assertEqual(
            json.loads((self.root / "tools" / "published-posts.json").read_text()), []
        )

    def test_posts_index_visible_and_structured_dates_advance_with_post_update(self) -> None:
        (self.root / "posts-src" / "active-post.md").write_text(
            markdown("active-post").replace(
                'date: "2026-10-08"', 'date: "2026-10-10"'
            ),
            encoding="utf-8",
        )
        (self.root / "posts" / "index.html").write_text(
            """<script type="application/ld+json">
{"@graph":[{"datePublished":"2026-10-08","dateModified":"2026-10-09"}]}
</script>
<span class="updated-date">Updated: October 9, 2026</span>
<div class="guide-grid">
<a class="guide-card" href="/posts/active-post">Old active card</a>
</div>
""",
            encoding="utf-8",
        )
        (self.root / "sitemap.xml").write_text(
            """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://teraboxlinks.pages.dev/posts</loc><lastmod>2026-10-09</lastmod></url>
<url><loc>https://teraboxlinks.pages.dev/posts/active-post</loc><lastmod>2026-10-08</lastmod></url>
</urlset>
""",
            encoding="utf-8",
        )

        self.run_sync()

        index = (self.root / "posts" / "index.html").read_text(encoding="utf-8")
        self.assertIn('"dateModified":"2026-10-10"', index)
        self.assertIn("Updated: October 10, 2026", index)
        sitemap_path = self.root / "sitemap.xml"
        sitemap_text = sitemap_path.read_text(encoding="utf-8")
        sitemap_root = ET.parse(sitemap_path).getroot()
        namespaces = {
            "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        posts_index_url = next(
            entry
            for entry in sitemap_root.findall("s:url", namespaces)
            if entry.findtext("s:loc", namespaces=namespaces)
            == "https://teraboxlinks.pages.dev/posts"
        )
        self.assertEqual(
            posts_index_url.findtext("s:lastmod", namespaces=namespaces),
            "2026-10-10",
        )
        post_url = next(
            entry
            for entry in sitemap_root.findall("s:url", namespaces)
            if entry.findtext("s:loc", namespaces=namespaces)
            == "https://teraboxlinks.pages.dev/posts/active-post"
        )
        self.assertEqual(post_url.findtext("s:lastmod", namespaces=namespaces), "2026-10-10")
        image = post_url.find("image:image", namespaces)
        self.assertIsNotNone(image)
        self.assertEqual(
            image.findtext("image:loc", namespaces=namespaces),
            "https://teraboxlinks.pages.dev/public/images/banner.jpg",
        )
        self.assertEqual(image.findtext("image:title", namespaces=namespaces), "Active Post")
        self.assertIn("\n  <url>\n", sitemap_text)
        self.assertNotIn("</url><url>", sitemap_text)

    def test_generated_article_has_complete_schema_and_semantic_heading(self) -> None:
        self.run_sync()
        article = (self.root / "posts" / "active-post.html").read_text(encoding="utf-8")
        article_start = article.index('<article class="post-article">')
        article_end = article.index("</article>", article_start)
        self.assertIn("<h1>Active Post</h1>", article[article_start:article_end])
        self.assertIn('property="og:image:alt"', article)
        self.assertIn('name="twitter:image:alt"', article)

        script = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            article,
            re.DOTALL,
        )
        self.assertIsNotNone(script)
        schema = json.loads(script.group(1))
        graph = schema["@graph"]
        posting = next(item for item in graph if item["@type"] == "BlogPosting")
        breadcrumb = next(item for item in graph if item["@type"] == "BreadcrumbList")
        self.assertEqual(
            posting["publisher"]["logo"]["url"],
            "https://teraboxlinks.pages.dev/public/images/logo.webp",
        )
        self.assertEqual(
            posting["image"],
            "https://teraboxlinks.pages.dev/public/images/banner.jpg",
        )
        self.assertEqual(
            [item["position"] for item in breadcrumb["itemListElement"]],
            [1, 2, 3],
        )
        self.assertEqual(
            breadcrumb["itemListElement"][-1]["item"],
            "https://teraboxlinks.pages.dev/posts/active-post",
        )

    def test_existing_movie_article_has_social_alt_and_publisher_logo(self) -> None:
        article = (REPOSITORY / "posts" / "terabox-movie.html").read_text(
            encoding="utf-8"
        )
        script = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            article,
            re.DOTALL,
        )
        self.assertIsNotNone(script)
        schema = json.loads(script.group(1))
        posting = next(
            item for item in schema["@graph"] if item["@type"] == "BlogPosting"
        )
        breadcrumb = next(
            item for item in schema["@graph"] if item["@type"] == "BreadcrumbList"
        )
        self.assertIn('property="og:image:alt"', article)
        self.assertIn('name="twitter:image:alt"', article)
        self.assertTrue(posting["publisher"]["logo"]["url"].endswith("/logo.webp"))
        self.assertEqual(
            [item["position"] for item in breadcrumb["itemListElement"]],
            [1, 2, 3, 4],
        )
        article_start = article.index('<article class="post-article">')
        article_end = article.index("</article>", article_start)
        self.assertIn("<h1>", article[article_start:article_end])


if __name__ == "__main__":
    unittest.main()
