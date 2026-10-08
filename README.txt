TeraBox SEO page package
========================

Purpose
-------
This package adds one honest, useful pilot page for the search intent “TeraBox movie” and a small publishing structure for future, genuinely distinct guides. The page explains that the site is a directory of shared video bundles, not a title-by-title movie catalogue. It does not promise that a particular film is available.

What is included
----------------
site-files/posts/terabox-movie.html  New SEO page; canonical URL: /posts/terabox-movie
site-files/posts/index.html          Small index for the new guide section
site-files/guides.html               Adds a visible internal link to the new guide section
site-files/sitemap.xml               Adds the index and pilot page
site-files/feed.xml                  Adds the pilot page to the existing RSS feed
starter/seo-post-template.html       Draft-only starter; intentionally marked noindex

The existing homepage index.html is deliberately not included or changed. The button on the new article points to https://teraboxlinks.pages.dev/#bundles. A visitor then chooses a bundle and checks the actual files inside TeraBox.

Install into the existing repository
------------------------------------
1. Unzip this archive.
2. Copy the contents of the site-files folder into the repository root, preserving the posts/ directory. Allow guides.html, sitemap.xml, and feed.xml to be updated.
3. Do not copy starter/seo-post-template.html into the published site. Keep it as a working draft outside the deployed files.
4. Preview and deploy through the site's normal Cloudflare Pages/GitHub process. The homepage HTML was not changed by this package.
5. After deploy, open /posts, /posts/terabox-movie, /sitemap.xml, and /feed.xml and verify the HTML/XML response. Then use Google Search Console URL Inspection to request a crawl if Search Console is available to you. Google may still choose not to index a page; a sitemap or request is not a guarantee.

How to add another page
-----------------------
1. Start from a real, distinct query intent—not every spelling or word-order variation.
2. Confirm that the shared bundle really contains the category/title or other unique information the page describes, and that the content is authorized for public sharing.
3. Copy the starter into site-files/posts/<unique-slug>.html. Replace every bracketed placeholder, add useful topic-specific information, set a correct canonical URL, and change robots from noindex to index, follow only after review.
4. Add a real link card to posts/index.html and one sitemap URL. Add an RSS item only for a genuinely new published page.
5. Keep related keyword variants together when they answer the same question. Do not publish pages that differ only by a swapped keyword and all send users to the same destination; that can look like doorway/scaled content and has no ranking guarantee.

Current site notes
------------------
- The existing /terabox-guide already explains how to open a shared TeraBox link; do not create a near-duplicate “TeraBox file link” page.
- The current home page shows generic bundle buttons, not a title-by-title catalogue. The pilot page states that honestly.
- Page language is English to match the existing site and the target query. The explanatory install notes are in this README.
- The connected Google Search Console query data was not available during this preparation, so this package makes no search-volume or ranking claims.
