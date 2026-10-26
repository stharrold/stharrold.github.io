/* Interactive results for the pre-registered MSSP early-renewal study.
   Reads data.json (next to this file), built by analysis/mssp-benchmark-ratchet/report/dashboard_data.py from the
   pipeline's results/. Plain JavaScript and inline SVG: no libraries, fonts or requests beyond this folder. */
(function () {
    "use strict";

    var SCRIPT = document.currentScript;
    var SVGNS = "http://www.w3.org/2000/svg";
    var ROW_H = 36;
    var AXIS_H = 40;

    function el(tag, attrs, children) {
        var node = document.createElement(tag);
        setAttrs(node, attrs);
        append(node, children);
        return node;
    }

    function sv(tag, attrs, children) {
        var node = document.createElementNS(SVGNS, tag);
        setAttrs(node, attrs);
        append(node, children);
        return node;
    }

    function setAttrs(node, attrs) {
        Object.keys(attrs || {}).forEach(function (k) {
            if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
        });
    }

    // Labels come from data.json; insert them as text, never as HTML.
    function append(node, children) {
        [].concat(children === undefined ? [] : children).forEach(function (c) {
            if (c === null || c === undefined || c === false) return;
            if (Array.isArray(c)) return append(node, c);
            node.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
        });
    }

    function num(v) {
        return typeof v === "number" && isFinite(v);
    }

    function fmt(x, digits) {
        if (!num(x)) return "n/a";
        var d = digits === undefined ? (Math.abs(x) >= 10 ? 1 : 2) : digits;
        var s = Number(x).toFixed(d);
        return s.charAt(0) === "-" ? "−" + s.slice(1) : s;
    }

    function pText(p) {
        return p !== null && p !== undefined && p < 0.001 ? "p < 0.001" : "p = " + fmtP(p);
    }

    function fmtP(p) {
        if (p === null || p === undefined) return "n/a";
        return p < 0.001 ? "< 0.001" : fmt(p, 3);
    }

    function niceTicks(lo, hi, count) {
        var span = hi - lo;
        var step = Math.pow(10, Math.floor(Math.log10(span / count)));
        var err = span / count / step;
        step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
        var ticks = [];
        for (var v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) ticks.push(Math.abs(v) < step * 1e-9 ? 0 : v);
        ticks.digits = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
        return ticks;
    }

    function domainOf(values) {
        var vs = values.filter(num).concat([0]);
        var lo = Math.min.apply(null, vs);
        var hi = Math.max.apply(null, vs);
        var pad = (hi - lo || 1) * 0.08;
        return [lo - pad, hi + pad];
    }

    function scale(domain, range) {
        return function (v) {
            return range[0] + ((v - domain[0]) / (domain[1] - domain[0])) * (range[1] - range[0]);
        };
    }

    /* Tooltip: one per dashboard, filled with text nodes; shown on hover and on keyboard focus. */
    function makeTooltip(root) {
        var tip = el("div", { class: "mssp-tip", role: "status", hidden: "" });
        root.appendChild(tip);
        return {
            show: function (target, rows) {
                tip.textContent = "";
                rows.forEach(function (r, i) {
                    append(tip, el("div", { class: i === 0 ? "mssp-tip-value" : "mssp-tip-label" }, r));
                });
                tip.hidden = false;
                var box = root.getBoundingClientRect();
                var t = target.getBoundingClientRect();
                var left = Math.min(Math.max(t.left - box.left, 0), box.width - tip.offsetWidth);
                tip.style.left = left + "px";
                tip.style.top = t.bottom - box.top + 6 + "px";
            },
            hide: function () { tip.hidden = true; }
        };
    }

    function bindTip(node, tip, rows) {
        node.setAttribute("tabindex", "0");
        node.addEventListener("pointerenter", function () { tip.show(node, rows); });
        node.addEventListener("pointerleave", tip.hide);
        node.addEventListener("focus", function () { tip.show(node, rows); });
        node.addEventListener("blur", tip.hide);
    }

    /* Interval rows: one dot (estimate) and a 2px line (95% interval) per row, a zero line, and an optional band
       (the minimum detectable effect, or the prior's 95% range). rows: {label, sub, mean, lo, hi, band, tip, emphasis}. */
    function intervalChart(rows, opts) {
        var width = opts.width;
        // Narrow screens put each row's label above its interval instead of beside it.
        var stacked = width < 560;
        var rowH = stacked ? 58 : ROW_H;
        var left = stacked ? 6 : Math.min(200, Math.round(width * 0.36)) + 8;
        var right = width - 12;
        var all = [];
        rows.forEach(function (r) { all.push(r.lo, r.hi, r.mean); if (r.band) all.push(-r.band, r.band); });
        if (opts.shared && opts.shared.band) all.push(-opts.shared.band, opts.shared.band);
        var dom = domainOf(all);
        var x = scale(dom, [left, right]);
        var plotBottom = rows.length * rowH;
        var height = plotBottom + AXIS_H;
        var svg = sv("svg", { class: "mssp-chart", width: width, height: height, viewBox: "0 0 " + width + " " + height, role: "img", "aria-label": opts.aria });

        var ticks = niceTicks(dom[0], dom[1], Math.max(3, Math.round((right - left) / 80)));
        ticks.forEach(function (t) {
            svg.appendChild(sv("line", { class: t === 0 ? "mssp-zero" : "mssp-grid", x1: x(t), x2: x(t), y1: stacked ? 30 : 0, y2: plotBottom }));
            svg.appendChild(sv("text", { class: "mssp-tick", x: x(t), y: plotBottom + 16, "text-anchor": "middle" }, fmt(t, ticks.digits)));
        });
        if (opts.unit) svg.appendChild(sv("text", { class: "mssp-tick", x: right, y: plotBottom + 34, "text-anchor": "end" }, opts.unit));

        rows.forEach(function (r, i) {
            var top = i * rowH;
            var cy = stacked ? top + 44 : top + rowH / 2;
            var labelY = stacked ? top + 14 : cy + (r.sub ? -2 : 4);
            var g = sv("g", { class: "mssp-row" + (r.emphasis ? " is-emphasis" : "") + (r.muted ? " is-muted" : ""), role: "listitem", "aria-label": r.tip.join(", ") });
            var band = r.band || (opts.shared && opts.shared.band);
            if (band) g.appendChild(sv("rect", { class: "mssp-band", x: x(-band), y: cy - 10, width: x(band) - x(-band), height: 20, rx: 2 }));
            g.appendChild(sv("rect", { class: "mssp-hit", x: 0, y: top, width: width, height: rowH }));
            g.appendChild(sv("text", { class: "mssp-label", x: 0, y: labelY }, r.label));
            if (r.sub) g.appendChild(sv("text", { class: "mssp-sublabel", x: 0, y: labelY + 14 }, r.sub));
            if (num(r.lo) && num(r.hi)) g.appendChild(sv("line", { class: "mssp-interval", x1: x(r.lo), x2: x(r.hi), y1: cy, y2: cy }));
            if (num(r.mean)) g.appendChild(sv("circle", { class: "mssp-dot", cx: x(r.mean), cy: cy, r: 5 }));
            bindTip(g, opts.tip, r.tip);
            svg.appendChild(g);
        });
        return svg;
    }

    /* Event study: estimate and 95% interval by performance year, the reference year at zero. */
    function eventChart(points, opts) {
        var width = opts.width;
        var left = 44;
        var right = width - 12;
        var plotH = 200;
        var all = [];
        points.forEach(function (p) { all.push(p.lo, p.hi, p.mean); });
        var dom = domainOf(all);
        var y = scale(dom, [plotH, 30]);
        var x = scale([points[0].year - 0.5, points[points.length - 1].year + 0.5], [left, right]);
        var svg = sv("svg", { class: "mssp-chart", width: width, height: plotH + AXIS_H, viewBox: "0 0 " + width + " " + (plotH + AXIS_H), role: "img", "aria-label": opts.aria });
        var ticks = niceTicks(dom[0], dom[1], 4);
        ticks.forEach(function (t) {
            svg.appendChild(sv("line", { class: t === 0 ? "mssp-zero" : "mssp-grid", x1: left, x2: right, y1: y(t), y2: y(t) }));
            svg.appendChild(sv("text", { class: "mssp-tick", x: left - 6, y: y(t) + 4, "text-anchor": "end" }, fmt(t, ticks.digits)));
        });
        svg.appendChild(sv("line", { class: "mssp-divider", x1: x(2021.5), x2: x(2021.5), y1: 22, y2: plotH }));
        svg.appendChild(sv("text", { class: "mssp-sublabel", x: x(2021.5) + 4, y: 14 }, "renewal takes effect"));
        points.forEach(function (p) {
            var g = sv("g", { class: "mssp-row" + (p.reference ? " is-muted" : ""), role: "listitem", "aria-label": p.tip.join(", ") });
            g.appendChild(sv("rect", { class: "mssp-hit", x: x(p.year - 0.5), y: 0, width: x(p.year + 0.5) - x(p.year - 0.5), height: plotH }));
            if (!p.reference) g.appendChild(sv("line", { class: "mssp-interval", x1: x(p.year), x2: x(p.year), y1: y(p.lo), y2: y(p.hi) }));
            g.appendChild(sv("circle", { class: "mssp-dot", cx: x(p.year), cy: y(p.mean), r: 5 }));
            g.appendChild(sv("text", { class: "mssp-tick", x: x(p.year), y: plotH + 18, "text-anchor": "middle" }, "PY" + p.year));
            bindTip(g, opts.tip, p.tip);
            svg.appendChild(g);
        });
        svg.appendChild(sv("text", { class: "mssp-tick", x: 0, y: 14 }, opts.unit));
        return svg;
    }

    function table(caption, head, body) {
        return el("details", { class: "mssp-table" }, [
            el("summary", {}, "Table: " + caption),
            el("table", { class: "table table-sm" }, [
                el("thead", {}, el("tr", {}, head.map(function (h) { return el("th", { scope: "col" }, h); }))),
                el("tbody", {}, body.map(function (row) { return el("tr", {}, row.map(function (c) { return el("td", {}, c); })); }))
            ])
        ]);
    }

    function card(title, intro, body) {
        return el("section", { class: "mssp-card" }, [el("h4", {}, title), intro ? el("p", { class: "mssp-intro" }, intro) : null].concat(body));
    }

    function pending(title, what) {
        return card(title, null, [el("p", { class: "mssp-pending" }, "Pending: " + what + " has not run yet.")]);
    }

    function verdictText(v) {
        return v === undefined || v === null ? "" : v;
    }

    /* --- Sections ------------------------------------------------------------------------------------------ */

    function comparisons(data, width, tip) {
        var c = data.comparisons;
        if (!c) return pending("Who renewed early: group comparisons", "the confirmatory stage");
        var rows = c.rows.map(function (r) {
            return {
                label: r.label,
                sub: r.role + ", " + pText(r.p) + (r.verdict ? ": " + r.verdict : ""),
                mean: r.mean,
                lo: r.lo,
                hi: r.hi,
                band: r.mde,
                emphasis: r.role === "primary",
                muted: r.role === "descriptive",
                tip: [fmt(r.mean) + " " + r.unit + " (95% interval " + fmt(r.lo) + " to " + fmt(r.hi) + ")", r.label + ", " + pText(r.p) + (r.verdict ? ", " + r.verdict : "")]
            };
        });
        var charts = el("div", { class: "mssp-multiples", role: "list" });
        rows.forEach(function (row) {
            charts.appendChild(intervalChart([row], { width: width, tip: tip, unit: c.rows[rows.indexOf(row)].unit, aria: row.tip.join(". ") }));
        });
        return card(
            "Who renewed early: group comparisons",
            "Early renewers minus stayers, within cohort and weighted by early renewers per cohort. Dot: posterior mean; line: 95% credible interval; shaded band: the minimum detectable effect at 80% power. Each row has its own axis because the units differ.",
            [
                charts,
                table(
                    "group comparisons",
                    ["Test", "Role", "Estimate", "95% interval", "p (permutation)", "MDE", "n early / stayers", "Verdict"],
                    c.rows.map(function (r) {
                        return [r.label, r.role, fmt(r.mean), fmt(r.lo) + " to " + fmt(r.hi), fmtP(r.p), fmt(r.mde), r.n_early + " / " + r.n_stayer, verdictText(r.verdict)];
                    })
                )
            ]
        );
    }

    function decision(data, width, tip, prior) {
        var h = data.h3;
        if (!h) return pending("H3: decision model", "the confirmatory stage");
        var coefs = h.posterior[prior] || h.posterior.normal;
        var rows = coefs.map(function (r) {
            return {
                label: r.label,
                sub: r.core ? "core, predicted " + r.predicted + (r.test ? ": " + r.test.decision : "") : "adjustment",
                mean: r.mean,
                lo: r.lo,
                hi: r.hi,
                emphasis: r.core,
                muted: !r.core,
                tip: [
                    fmt(r.mean) + " log-odds (95% interval " + fmt(r.lo) + " to " + fmt(r.hi) + ")",
                    r.label + ", P(> 0) = " + fmt(r.p_positive, 2) + (r.test ? ", simulation " + pText(r.test.p) + ", " + r.test.decision : "")
                ]
            };
        });
        var status = h.converged ? "The Bayesian model met its convergence checks." : "The Bayesian model did not meet its convergence checks, so the Firth model decides H3 (plan 5.4).";
        return card(
            "H3: decision model (BASIC-track ACOs)",
            "Logistic regression of early renewal; coefficients are log-odds differences per 2 SD (or per category). Shaded band: the prior's 95% range. Core predictors are decided by direct simulation under the reduced model; adjustment factors are estimates only. " + status,
            [
                el("div", { role: "list" }, intervalChart(rows, { width: width, tip: tip, unit: "log-odds", shared: { band: h.prior_band[prior] }, aria: "H3 coefficients, " + prior + " prior" })),
                table(
                    "H3 coefficients (" + (prior === "normal" ? "Normal(0, 1)" : "Student-t(3, 0, 2.5)") + " prior)",
                    ["Predictor", "Role", "Posterior mean", "95% interval", "P(> 0)", "Simulation p", "Decision"],
                    coefs.map(function (r) {
                        return [r.label, r.core ? "core (" + r.predicted + ")" : "adjustment", fmt(r.mean), fmt(r.lo) + " to " + fmt(r.hi), fmt(r.p_positive, 2), r.test ? fmtP(r.test.p) : "", r.test ? r.test.decision : ""];
                    })
                ),
                el("p", { class: "mssp-note" }, "Power: at a true log-odds difference of 0.5, the 95% interval excluded zero in " + h.power_note + " of simulated datasets, so “undetermined” is the expected verdict.")
            ]
        );
    }

    function effect(data, width, tip) {
        var d = data.h4;
        if (!d) return pending("H4: effect of early renewal on spending", "the difference-in-differences stage");
        var rows = d.estimates.map(function (r) {
            return {
                label: r.label,
                sub: r.role + (r.p !== null ? ", " + pText(r.p) : ""),
                mean: r.mean,
                lo: r.lo,
                hi: r.hi,
                emphasis: r.role === "confirmatory",
                muted: r.role !== "confirmatory",
                tip: [fmt(r.mean) + "%" + (num(r.lo) ? " (95% interval " + fmt(r.lo) + " to " + fmt(r.hi) + ")" : " (point estimate, no interval)"), r.label + (r.p !== null ? ", " + pText(r.p) : "")]
            };
        });
        var eq = d.equivalence;
        var eqText = eq
            ? "Pre-trend equivalence condition: scaled pre-trend bound " + fmt(eq.scaled_bound, 3) + " vs |H4| " + fmt(eq.abs_h4, 3) + " (log points): " + (eq.holds ? "holds, so H4 is read as an effect of the early-renewal package." : "does not hold, so H4 is a difference in spending changes that cannot be told apart from a continuing pre-period trend.")
            : "";
        var body = [
            el("div", { role: "list" }, intervalChart(rows, { width: width, tip: tip, unit: "% difference in spending growth", shared: { band: d.mde_percent }, aria: "H4 estimates" })),
            el("p", { class: "mssp-note" }, eqText)
        ];
        if (d.event_study) {
            var pts = d.event_study.map(function (p) {
                return {
                    year: p.year,
                    mean: p.mean,
                    lo: p.lo,
                    hi: p.hi,
                    reference: p.reference,
                    tip: p.reference ? ["0 (reference year)", "PY" + p.year] : [fmt(p.mean) + "% (95% CI " + fmt(p.lo) + " to " + fmt(p.hi) + ")", "PY" + p.year + ", two-way fixed effects"]
                };
            });
            body.push(el("h5", {}, "Event study (conventional, two-way fixed effects)"));
            body.push(el("div", { role: "list" }, eventChart(pts, { width: width, tip: tip, unit: "% vs PY2021", aria: "Event study by performance year" })));
            body.push(table("event study", ["Year", "Estimate (%)", "95% CI"], d.event_study.map(function (p) {
                return ["PY" + p.year, p.reference ? "0 (reference)" : fmt(p.mean), p.reference ? "" : fmt(p.lo) + " to " + fmt(p.hi)];
            })));
        }
        body.push(table("H4 estimates", ["Estimate", "Role", "% difference", "95% interval", "p"], d.estimates.map(function (r) {
            return [r.label, r.role, fmt(r.mean), num(r.lo) ? fmt(r.lo) + " to " + fmt(r.hi) : "none (point estimate)", fmtP(r.p)];
        })));
        return card(
            "H4: effect of early renewal on spending",
            "Change in log per-capita spending from PY2020-21 to PY2022-24, early renewers minus ACOs not yet renewed, shown as a percent difference in spending growth. Shaded band: the minimum detectable effect.",
            body
        );
    }

    function agreement(data) {
        if (!data.agreement) return pending("Registered vs conventional methods", "the conventional comparison");
        return card(
            "Registered vs conventional methods",
            "Each confirmatory verdict next to the conventional one (OLS with HC2 errors, maximum-likelihood logistic regression, two-way fixed effects). Reported only; disagreements do not change the decisions.",
            [el("table", { class: "table table-sm mssp-agree" }, [
                el("thead", {}, el("tr", {}, ["Claim", "Registered", "Conventional", "Agree"].map(function (h) { return el("th", { scope: "col" }, h); }))),
                el("tbody", {}, data.agreement.map(function (r) {
                    return el("tr", {}, [r.claim, r.confirmatory, r.conventional, r.agree ? "yes" : "no"].map(function (c) { return el("td", {}, c); }));
                }))
            ])]
        );
    }

    function header(data) {
        var nodes = [];
        if (data.synthetic) {
            nodes.push(el("p", { class: "mssp-banner", role: "note" }, [
                el("strong", {}, "Synthetic data. "),
                "These numbers come from a made-up dataset used to build and test the pipeline; they are not CMS results."
            ]));
        }
        var chips = el("ul", { class: "mssp-stages", "aria-label": "Pipeline stages" });
        data.stages.forEach(function (s) {
            chips.appendChild(el("li", { class: s.done ? "is-done" : "" }, [el("span", { "aria-hidden": "true" }, s.done ? "✓ " : "… "), s.name + (s.done ? "" : " (pending)")]));
        });
        nodes.push(chips);
        return nodes;
    }

    /* --- Render ----------------------------------------------------------------------------------------------- */

    function render(root, data) {
        var state = { prior: "normal" };
        var width;

        function draw() {
            width = Math.max(280, Math.floor(root.clientWidth));
            root.textContent = "";
            root.classList.toggle("is-synthetic", !!data.synthetic);
            var tip;
            var controls = el("div", { class: "mssp-controls", role: "group", "aria-label": "Display options" }, [
                el("span", { class: "mssp-control-label" }, "H3 prior"),
                ["normal", "student_t"].map(function (p) {
                    var b = el("button", { type: "button", class: "mssp-seg", "aria-pressed": String(state.prior === p) }, p === "normal" ? "Normal(0, 1)" : "Student-t");
                    b.addEventListener("click", function () { state.prior = p; draw(); root.querySelector('.mssp-seg[aria-pressed="true"]').focus(); });
                    return b;
                })
            ]);
            append(root, header(data));
            root.appendChild(controls);
            tip = makeTooltip(root);
            append(root, [comparisons(data, width, tip), decision(data, width, tip, state.prior), effect(data, width, tip), agreement(data)]);
            root.appendChild(el("p", { class: "mssp-note" }, "Built " + data.built + " from results at commit " + data.commit + "."));
        }

        draw();
        if (window.ResizeObserver) {
            var last = width;
            new ResizeObserver(function () {
                var w = Math.max(280, Math.floor(root.clientWidth));
                if (Math.abs(w - last) > 8) { last = w; draw(); }
            }).observe(root);
        }
    }

    function start() {
        var root = document.getElementById("mssp-dashboard");
        if (!root || !SCRIPT) return;
        var url = SCRIPT.src.replace(/dashboard\.js(\?.*)?$/, "data.json");
        fetch(url)
            .then(function (r) {
                if (!r.ok) throw new Error(r.status + " " + r.statusText);
                return r.json();
            })
            .then(function (data) { render(root, data); })
            .catch(function (err) {
                root.textContent = "";
                root.appendChild(el("p", { class: "mssp-pending" }, "The interactive results could not be loaded (" + err.message + "). The tables in the post have the same numbers."));
            });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
})();
