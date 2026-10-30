Title: Privacy
Status: hidden
Date: 2026-10-06T12:00:00Z
Modified: 2026-10-30T01:45:00Z
Slug: privacy
Authors: Samuel Harrold
Summary: What this site collects and which third-party services it uses.

This is a static site hosted on [GitHub Pages](https://pages.github.com/). It has no accounts or forms, and it doesn't sell or share data. Here is what happens when you visit:

* **Hosting.** GitHub serves the pages and, like any web server, receives your IP address and browser details. See the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).
* **Analytics.** Pages load [Google Analytics 4](https://support.google.com/analytics/answer/11593727) to count visits and see which posts are read: page views, how far a page is scrolled (25, 50, 75 and 90%), clicks on links that leave the site, and clicks that open a notebook export. It sets first-party cookies (`_ga` and `_ga_<ID>`). Google signals and ad personalization are turned off for this site. The events (with a random browser ID, approximate location and device details; Google Analytics 4 [does not log or store IP addresses](https://support.google.com/analytics/answer/2763052)) are exported to a private Google Cloud project and a private archive, where they are kept indefinitely so the site's history is not lost. You can block it with your browser's tracking protection or the [Google Analytics opt-out add-on](https://tools.google.com/dlpage/gaoptout).
* **Comments.** Comment threads use [giscus](https://giscus.app/), which stores comments as GitHub Discussions in the [site's repository](https://github.com/stharrold/stharrold.github.io/discussions). Reading comments loads the giscus widget; posting requires signing in with GitHub, and your comment is public on GitHub. See the [giscus privacy policy](https://github.com/giscus/giscus/blob/main/PRIVACY-POLICY.md). Comments from before 2026 are archived from Disqus as plain text on each post and load nothing from Disqus.
* **Video.** A post with a video shows it as a still image served from this site, with a play button; nothing is requested from YouTube until you press play. Pressing play loads YouTube's player from `youtube-nocookie.com` (YouTube's [privacy-enhanced mode](https://support.google.com/youtube/answer/171780)); from then on YouTube receives your IP address and viewing details and may store information in your browser. See the [Google Privacy Policy](https://policies.google.com/privacy). Without JavaScript, the image is a plain link to the video on YouTube.
* **Math.** Posts with equations load [MathJax](https://www.mathjax.org/) from the jsDelivr CDN, which receives your IP address. See the [jsDelivr privacy policy](https://www.jsdelivr.com/terms/privacy-policy-jsdelivr-net).
* **Notebook exports.** The Jupyter notebook HTML exports linked from posts (files ending in `-full.html`) are standalone pages that load RequireJS and jQuery from [cdnjs](https://cdnjs.com/) and MathJax from jsDelivr. The [marimo](https://marimo.io/) notebook exports linked from posts are standalone pages that load marimo's scripts, styles and fonts from jsDelivr. Neither kind loads analytics or comments.
* **Search and fonts.** Site search ([Pagefind](https://pagefind.app/)) runs entirely in your browser on files served from this site, and fonts are served from this site, so neither contacts a third party.

Questions? Open an issue on the [site's repository](https://github.com/stharrold/stharrold.github.io/issues).
