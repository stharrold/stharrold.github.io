# Build notes: the blog's YouTube channel (for a post about the blog, #27)

A running log of how the channel was set up: what was decided, what was checked and why. The assets and the record
of what was uploaded are in `assets/youtube/` (its README); the art is made by `scripts/youtube_art.py`. Newest
entries at the bottom.

## A channel of its own (2026-10-29)

The first video is the narrated slide deck for the MSSP early-renewal post (#73). The author's personal channel
(@stharrold) already existed but had no public videos, so there was no audience to keep; a separate channel named
for the blog gives each post an analogous place on YouTube and keeps personal viewing apart. It is a Brand Account
under the site's Google account, so it can have managers later without sharing a login.

- Name **Data Science Demos**, the site's own title (`SITENAME` in `pelicanconf.py`), so the channel looks like the
  blog wherever it appears. Handle **@DSDemos**: "dsdemos" is the short form the blog already used, for its 2016
  example-code repository. Handles are not case-sensitive; the capitals are for reading.
- The person behind it is named in the channel description and links, since a channel named after a site does not
  say who made it.
- Creating the channel accepts YouTube's terms, so the author did it; the agent opened the page and checked the
  typed name and handle by reading the fields.

## The channel picture (2026-10-29)

The idea was the blog's colours with the text "DSDemos". Rendered as YouTube crops it, a circle, and shown at the
sizes YouTube uses (176 px on the channel page, 40 px beside comments, 24 px in the sidebar), "DSDemos" could not be
read at 40 px. The site's existing "DS" monogram (the favicon, added 2026-10-06) stays readable at every size, and
YouTube always shows the channel name beside the picture, so the picture need not spell it. The channel picture is
that monogram at 800 x 800.

`scripts/youtube_art.py` renders it with headless Chrome from an HTML page using the theme's own Lato files, so it
needs no downloads and can be remade if the colours change; the script's output was byte-identical to the preview.

## The banner and the profile (2026-10-29)

- The banner is the blog's title and address on the same navy, with a short teal rule (the site's link colour, used
  only as a rule because as text it is 4.6:1 on the navy). Phones show only the centre 1546 x 423 of the 2560 x 1440
  image, so everything sits inside that box; YouTube's crop preview confirmed it.
- The channel's blog link is untagged. The About panel prints each link's address, and a clean address reads better
  there; few visits will come that way. Links in video descriptions are tagged, since that is where most clicks will
  come from and the YouTube app drops the referrer (the same reason the LinkedIn share was tagged).
- The contact address is a Gmail `+dsdemos` alias. The address is already public in this repository's commits, so
  listing it adds little exposure; the alias lets mail from the listing be filtered, and fake sponsorship offers,
  a common way of phishing channel logins, are easier to recognise.
- The fields were filled by the agent in Claude in Chrome while the author watched, and read back from the page
  before publishing.

## The watermark (2026-10-29)

The idea was two lines of text, "@DSDemos" and "stharrold.github.io". Mocked up at the watermark's real size (about
40 px in a 560 px player, half that on a phone), the address could not be read, and a watermark is not a link: on
desktop it becomes a Subscribe button. So the watermark is the channel picture again, for the entire video; the
address is in each video's description and on the deck's closing slide. A contact sheet of all 26 slides of the
first video, with the watermark's corner marked, showed nothing there to cover.

## Published (2026-10-29)

The author pressed Publish. Checked on the public channel page: picture, name, handle, description, the three links
(YouTube shows the site's own favicon beside the blog link) and the banner, which appeared a minute or two after
Studio had saved it. The upload log in `assets/youtube/README.md` records the sha256 of each image.
