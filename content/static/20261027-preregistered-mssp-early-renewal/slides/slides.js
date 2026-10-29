/* Slide viewer for "Resetting the Target Early", the video deck for the MSSP early-renewal post.
   Reads slides.json (next to this file), built by analysis/mssp-benchmark-ratchet/report/video_slides.py from
   video-slides.pptx. Plain JavaScript: no libraries, fonts or requests beyond this folder. Without JavaScript the
   figure keeps its first slide and the download links. */
(function () {
    "use strict";

    var SCRIPT = document.currentScript;
    var BASE = SCRIPT.src.replace(/[^/]*$/, "");

    function el(tag, attrs, text) {
        var node = document.createElement(tag);
        Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
        if (text) node.textContent = text;
        return node;
    }

    function build(root, data) {
        var n = data.slides.length;
        var i = 0;
        var img = el("img", { width: data.width, height: data.height, decoding: "async", "class": "mssp-slides-img" });
        var stage = el("div", { "class": "mssp-slides-stage" });
        stage.appendChild(img);
        var prev = el("button", { type: "button", "class": "btn btn-outline-secondary btn-sm", "aria-label": "Previous slide" }, "← Previous");
        var next = el("button", { type: "button", "class": "btn btn-outline-secondary btn-sm", "aria-label": "Next slide" }, "Next →");
        var count = el("span", { "class": "mssp-slides-count", "aria-live": "polite" });
        var bar = el("div", { "class": "mssp-slides-bar" });
        bar.appendChild(prev);
        bar.appendChild(count);
        bar.appendChild(next);

        function show(k) {
            i = Math.max(0, Math.min(n - 1, k));
            var s = data.slides[i];
            img.src = BASE + s.image;
            img.alt = "Slide " + (i + 1) + " of " + n + ": " + s.alt;
            count.textContent = (i + 1) + " / " + n;
            prev.disabled = i === 0;
            next.disabled = i === n - 1;
            // Fetch the neighbours now so paging feels instant.
            [i - 1, i + 1].forEach(function (j) {
                if (j >= 0 && j < n) new Image().src = BASE + data.slides[j].image;
            });
        }

        prev.addEventListener("click", function () { show(i - 1); });
        next.addEventListener("click", function () { show(i + 1); });
        stage.addEventListener("click", function (e) {
            var r = stage.getBoundingClientRect();
            show(e.clientX - r.left < r.width / 3 ? i - 1 : i + 1);
        });
        root.addEventListener("keydown", function (e) {
            if (e.key === "ArrowRight" || e.key === "PageDown") { show(i + 1); e.preventDefault(); }
            else if (e.key === "ArrowLeft" || e.key === "PageUp") { show(i - 1); e.preventDefault(); }
            else if (e.key === "Home") { show(0); e.preventDefault(); }
            else if (e.key === "End") { show(n - 1); e.preventDefault(); }
        });
        var x0 = null;
        stage.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
        stage.addEventListener("touchend", function (e) {
            if (x0 === null) return;
            var dx = e.changedTouches[0].clientX - x0;
            x0 = null;
            if (Math.abs(dx) > 40) show(dx < 0 ? i + 1 : i - 1);
        });

        var fallback = root.querySelector(".mssp-slides-fallback");
        if (fallback) fallback.remove();
        root.insertBefore(bar, root.firstChild);
        root.insertBefore(stage, root.firstChild);
        root.setAttribute("tabindex", "0");
        root.setAttribute("aria-roledescription", "slide viewer");
        show(0);
    }

    var root = document.getElementById("mssp-slides");
    if (!root || !window.fetch) return;
    fetch(BASE + "slides.json")
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) { build(root, data); })
        .catch(function () { /* keep the static first slide and the links */ });
})();
