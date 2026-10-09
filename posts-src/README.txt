Post publishing
===============

Put one reviewed, ready-to-publish Markdown file per post in this folder.
Use starter/post-template.md for the required front matter and content shape.

When a .md file is committed to the main branch, GitHub Actions runs
tools/publish_post.py and updates the generated posts/<slug>.html page,
posts/index.html, sitemap.xml, feed.xml, and matching site-files mirrors.
The workflow commits those generated files back to main. If Cloudflare Pages
is connected to this branch, it should then build from that commit; verify the
Pages deployment before treating the post as live.
The repository's Actions settings and branch rules must allow the workflow's
GITHUB_TOKEN to write and push commits.

Do not put unfinished drafts here: a commit to main is the publish signal.
Keep drafts in .post-drafts/ until they have been reviewed. The workflow never
deletes published posts when a source file is removed; remove a post manually
only after checking its links and redirects.

For local publishing, run from the repository root:
  python3 tools/publish_post.py --update posts-src/<post-file>.md
