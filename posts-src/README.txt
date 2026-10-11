Post publishing
===============

Put one reviewed, ready-to-publish Markdown file per post directly in this
folder. Copy starter/post-template.md, replace the placeholders, and name the
file exactly <slug>.md, matching the slug field in its front matter.

The publisher safely parses nested YAML. It supports the SEO fields shown in
the starter template: keywords/entities/tags, authors and reviewers, canonical
and breadcrumb URLs, social/cover images, citations, FAQs, robots directives,
and page freshness. Unknown fields, malformed YAML, duplicate keys, invalid
dates, and mismatched filenames fail with a direct error before generated
pages are changed. Use quoted ISO dates (YYYY-MM-DD or an ISO-8601 timestamp).
Do not set draft: true in posts-src/; drafts belong outside this publish folder.

The body supports Markdown headings, links, paragraphs, lists, blockquotes,
fenced code, horizontal rules, and simple pipe tables. Body headings are
rendered as h2/h3 and receive automatic anchor IDs. Raw HTML is escaped except
for the two sanitized presentation wrappers in the template:
<div class="quick-answer-box" id="quick-answer"> and
<div class="key-takeaways">. Never put scripts, event handlers, or arbitrary
HTML in a post. Avoid nested lists and | inside table cells.

Keep titles concise with the main search phrase near the beginning. Write an
accurate description under 170 characters, and use the real publication date.
Replace every example, verify claims and links, and confirm ownership,
permission, privacy, and safety before moving a post into this folder.

When a .md file is added, edited, renamed, or deleted on main, GitHub Actions
tests the publisher and reconciles the complete posts-src/ set with generated
posts/<slug>.html pages, posts/index.html, sitemap.xml, feed.xml, the generated
post manifest, and matching site-files mirrors. It commits those generated
files back to main. Deleting a Markdown source removes its generated page,
listing card, RSS item, sitemap URL, and matching mirror; hand-authored pages
and unrelated feed/sitemap entries are retained.

Cloudflare Pages should deploy from the generated commit when connected to this
branch. Verify its deployment before treating a post as live. Actions settings
and branch rules must allow the workflow's GITHUB_TOKEN to push commits.

Do not put unfinished drafts here: a commit to main is the publish signal.
For local publishing, install dependencies with:
  python3 -m pip install "PyYAML>=6.0.3,<7"
Then run from the repository root:
  python3 tools/publish_post.py
