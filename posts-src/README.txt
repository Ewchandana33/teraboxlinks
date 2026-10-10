Post publishing
===============

Put one reviewed, ready-to-publish Markdown file per post directly in this
folder. Copy starter/post-template.md, replace every placeholder, and name the
file exactly <slug>.md, matching the slug field in its front matter.

The front matter is intentionally simple: use only the six single-line fields
shown in the template (title, slug, description, keyword, date, language).
Do not add nested YAML, arrays, or metadata fields the publisher does not use.
The title becomes the page's h1; start the article itself with a short answer,
then use Markdown headings, links, paragraphs, lists, blockquotes, fenced code,
horizontal rules, and simple pipe tables as needed. Body headings are rendered
as h2/h3 and get automatic anchor IDs. Raw HTML is escaped, not run as markup;
use Markdown instead. Avoid nested lists and `|` inside table cells.

Keep the title concise with the main search phrase near the beginning, write
an accurate description under 170 characters, and make the `keyword` match the
topic rather than repeating it unnaturally. Use the real publication date in
YYYY-MM-DD format. Replace all example wording and verify claims, links,
ownership/permission, privacy, and safety before moving a post into this folder.

When a .md file is added, edited, renamed, or deleted here on the main branch,
GitHub Actions reconciles the complete posts-src/ Markdown set with generated
posts/<slug>.html pages, posts/index.html, sitemap.xml, feed.xml, the generated
post manifest, and matching site-files mirrors.
Deleting a Markdown source removes its generated page, listing card, RSS item,
sitemap URL, and matching mirror automatically. Hand-authored pages and
unrelated feed/sitemap entries are retained. The workflow commits those
generated files back to main. A queued run re-fetches the latest branch and
reconciles again if another commit arrives during publishing.

Files in .post-drafts/ are intentionally not published. Move a reviewed draft
into posts-src/ to publish it; delete its posts-src/<slug>.md source to remove
it from generated indexes and pages.

If Cloudflare Pages is connected to this branch, it should then build from the
generated commit; verify the Pages deployment before treating the post as live.
The repository's Actions settings and branch rules must allow the workflow's
GITHUB_TOKEN to write and push commits.

Do not put unfinished drafts here: a commit to main is the publish signal.
This folder is the source of truth only for Markdown-managed posts; keep
hand-authored pages out of posts-src/.

For local publishing, run from the repository root:
  python3 tools/publish_post.py
