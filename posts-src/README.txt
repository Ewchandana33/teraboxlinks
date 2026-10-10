Post publishing
===============

Put one reviewed, ready-to-publish Markdown file per post directly in this
folder. Copy starter/post-template.md, replace every placeholder, and name the
file exactly <slug>.md, matching the slug field in its front matter.

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
