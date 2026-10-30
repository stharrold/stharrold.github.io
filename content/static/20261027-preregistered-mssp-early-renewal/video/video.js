/* Click-to-load YouTube player for the MSSP early-renewal post. The page shows a poster served from this site (a
   link to the video on YouTube); nothing is requested from YouTube until the reader presses play, which swaps the
   link for a player from youtube-nocookie.com. Without JavaScript the link opens the video on YouTube. Plain
   JavaScript, no libraries. */
(function () {
    "use strict";

    function play(event) {
        var link = event.currentTarget;
        var id = link.getAttribute("data-video-id");
        if (!/^[A-Za-z0-9_-]{11}$/.test(id || "")) return;
        event.preventDefault();
        var frame = document.createElement("iframe");
        frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
        frame.title = link.getAttribute("data-title") || "YouTube video";
        frame.allow = "autoplay; encrypted-media; fullscreen; picture-in-picture";
        frame.allowFullscreen = true;
        // YouTube's embedded player refuses to play without a referrer (error 153); send the origin only.
        frame.referrerPolicy = "strict-origin-when-cross-origin";
        var box = document.createElement("div");
        box.className = "mssp-video-frame";
        box.appendChild(frame);
        link.replaceWith(box);
        frame.focus();
    }

    document.querySelectorAll("a.mssp-video-frame[data-video-id]").forEach(function (link) {
        link.addEventListener("click", play);
    });
})();
