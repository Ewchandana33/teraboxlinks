Post publishing
===============

Put one reviewed, ready-to-publish Markdown file per post in this folder.
Use starter/post-template.md for the required front matter and content shape.

When a .md file is committed to the main branch, GitHub Actions reconciles the
complete posts-src/ Markdown set with generated posts/<slug>.html pages,
posts/index.html, sitemap.xml, feed.xml, and matching site-files mirrors.
Deleting a Markdown source removes its generated page, listing card, RSS item,
sitemap URL, and matching mirror automatically. Hand-authored pages and
unrelated feed/sitemap entries are retained. The workflow commits those
generated files back to main. If Cloudflare Pages is connected to this branch,
it should then build from that commit; verify the Pages deployment before
treating the post as live.
The repository's Actions settings and branch rules must allow the workflow's
GITHUB_TOKEN to write and push commits.

Do not put unfinished drafts here: a commit to main is the publish signal.
Keep drafts in .post-drafts/ until they have been reviewed. This folder is the
source of truth only for Markdown-managed posts; keep hand-authored pages out
of posts-src/.

For local publishing, run from the repository root:
  python3 tools/publish_post.py
