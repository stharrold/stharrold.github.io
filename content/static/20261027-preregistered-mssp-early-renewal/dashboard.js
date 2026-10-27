/* Interactive results for the pre-registered MSSP early-renewal study.
   Reads data.json (next to this file), built by analysis/mssp-benchmark-ratchet/report/dashboard_data.py from the
   pipeline's results/. Plain JavaScript and inline SVG: no libraries, fonts or requests beyond this folder. */
(function () {
    "use strict";

    var SCRIPT = document.currentScript;
    var SVGNS = "http://www.w3.org/2000/svg";
    var ROW_H = 36;
    var AXIS_H = 40;
    var CARD_INSET = 34; // .mssp-card: 1rem padding and a 1px border on each side

    // The results files the dashboard data were built from, pinned to a commit.
    var RESULTS_URL = "https://github.com/stharrold/stharrold.github.io/tree/3da8cd28c6601c45bc7a4da9abf91af62af20722/analysis/mssp-benchmark-ratchet/results";

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

    // Intervals are read against zero, so their domain includes it; levels (spending) pass withoutZero.
    function domainOf(values, withoutZero) {
        var vs = values.filter(num).concat(withoutZero ? [] : [0]);
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

    /* Spending by agreement year: one panel per agreement start year on a shared dollar axis, early renewers in the
       series color and all other ACOs in muted gray, the next agreement's scheduled benchmark years shaded. */
    function spendingChart(points, opts) {
        var years = [];
        points.forEach(function (p) { if (years.indexOf(p.start_year) < 0) years.push(p.start_year); });
        years.sort();
        var side = opts.width >= 640;
        var gap = 16;
        var panelW = side ? Math.floor((opts.width - gap * (years.length - 1)) / years.length) : opts.width;
        var plotH = 150;
        var top = 34;
        var dom = domainOf(points.map(function (p) { return p.mean; }), true);
        var ticks = niceTicks(dom[0], dom[1], 4);
        var kDigits = Math.max(0, -Math.floor(Math.log10((ticks[1] - ticks[0]) / 1000) + 1e-9));
        var wrap = el("div", { class: "mssp-panels" + (side ? " is-side" : "") });
        years.forEach(function (year) {
            var left = 52;
            var right = panelW - 8;
            var x = scale([0.5, 5.5], [left, right]);
            var y = scale(dom, [top + plotH, top]);
            var svg = sv("svg", { class: "mssp-chart", width: panelW, height: top + plotH + AXIS_H, viewBox: "0 0 " + panelW + " " + (top + plotH + AXIS_H), role: "img", "aria-label": opts.aria + ", agreements starting " + year });
            svg.appendChild(sv("text", { class: "mssp-label", x: 0, y: 14 }, "Agreements starting " + year));
            svg.appendChild(sv("rect", { class: "mssp-shade", x: x(2.5), y: top, width: x(5.5) - x(2.5), height: plotH }));
            ticks.forEach(function (t) {
                svg.appendChild(sv("line", { class: "mssp-grid", x1: left, x2: right, y1: y(t), y2: y(t) }));
                svg.appendChild(sv("text", { class: "mssp-tick", x: left - 6, y: y(t) + 4, "text-anchor": "end" }, "$" + fmt(t / 1000, kDigits) + "k"));
            });
            [1, 2, 3, 4, 5].forEach(function (a) {
                svg.appendChild(sv("text", { class: "mssp-tick", x: x(a), y: top + plotH + 16, "text-anchor": "middle" }, String(a)));
            });
            svg.appendChild(sv("text", { class: "mssp-tick", x: right, y: top + plotH + 34, "text-anchor": "end" }, "agreement year"));
            // Muted series first, so the early renewers draw on top.
            [false, true].forEach(function (early) {
                var series = points.filter(function (p) { return p.start_year === year && p.early === early; }).sort(function (a, b) { return a.agreement_year - b.agreement_year; });
                if (!series.length) return;
                var g = sv("g", { class: "mssp-series" + (early ? "" : " is-muted") });
                g.appendChild(sv("polyline", { class: "mssp-line", points: series.map(function (p) { return x(p.agreement_year) + "," + y(p.mean); }).join(" ") }));
                series.forEach(function (p) {
                    var pt = sv("g", { class: "mssp-row" + (early ? "" : " is-muted"), role: "listitem", "aria-label": p.tip.join(", ") });
                    pt.appendChild(sv("rect", { class: "mssp-hit", x: x(p.agreement_year) - 12, y: y(p.mean) - 12, width: 24, height: 24 }));
                    pt.appendChild(sv("circle", { class: "mssp-dot", cx: x(p.agreement_year), cy: y(p.mean), r: 5 }));
                    bindTip(pt, opts.tip, p.tip);
                    g.appendChild(pt);
                });
                svg.appendChild(g);
            });
            wrap.appendChild(svg);
        });
        return wrap;
    }

    function legend(items) {
        return el("ul", { class: "mssp-legend" }, items.map(function (it) {
            return el("li", {}, [el("span", { class: "mssp-swatch" + (it.muted ? " is-muted" : "") + (it.shade ? " is-shade" : ""), "aria-hidden": "true" }), it.label]);
        }));
    }

    function dataTable(head, body, cls) {
        return el("table", { class: "table table-sm" + (cls ? " " + cls : "") }, [
            el("thead", {}, el("tr", {}, head.map(function (h) { return el("th", { scope: "col" }, h); }))),
            el("tbody", {}, body.map(function (row) { return el("tr", {}, row.map(function (c) { return el("td", {}, c); })); }))
        ]);
    }

    // A chart's table view, collapsed under the chart.
    function table(caption, head, body) {
        return el("details", { class: "mssp-table" }, [el("summary", {}, "Table: " + caption), dataTable(head, body)]);
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
        if (!d) return pending("H4: spending after early renewal", "the difference-in-differences stage");
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
            "H4: spending after early renewal",
            "Change in log per-capita spending from PY2020-21 to PY2022-24, early renewers minus ACOs not yet renewed, shown as a percent difference in spending growth. Shaded band: the minimum detectable effect.",
            body
        );
    }

    function agreement(data) {
        if (!data.agreement) return pending("Registered vs conventional methods", "the conventional comparison");
        return card(
            "Registered vs conventional methods",
            "Each confirmatory verdict next to the conventional one (OLS with HC2 errors, maximum-likelihood logistic regression, two-way fixed effects). Reported only; disagreements do not change the decisions.",
            [dataTable(["Claim", "Registered", "Conventional", "Agree"], data.agreement.map(function (r) {
                return [r.claim, r.confirmatory, r.conventional, r.agree ? "yes" : "no"];
            }), "mssp-agree")]
        );
    }

    /* Robustness and exploratory rows: the confirmatory estimate in the series color, the others muted, no verdicts. */
    function estimateRows(rows, unit) {
        return rows.map(function (r) {
            var sub = r.role + (r.converged === false ? ", did not converge" : "") + (num(r.p) ? ", " + pText(r.p) : "");
            return {
                label: r.label,
                sub: sub,
                mean: r.mean,
                lo: r.lo,
                hi: r.hi,
                emphasis: r.role === "confirmatory",
                muted: r.role !== "confirmatory",
                tip: [fmt(r.mean) + " " + unit + " (95% interval " + fmt(r.lo) + " to " + fmt(r.hi) + ")", r.label + ", " + sub]
            };
        });
    }

    function multiples(blocks, width, tip) {
        var out = [];
        blocks.forEach(function (b) {
            out.push(el("h5", {}, b.label));
            out.push(el("div", { role: "list" }, intervalChart(estimateRows(b.rows, b.unit), { width: width, tip: tip, unit: b.unit, aria: b.label })));
        });
        return out;
    }

    function blocksTable(caption, blocks) {
        var body = [];
        blocks.forEach(function (b) {
            b.rows.forEach(function (r) {
                body.push([b.label, r.label, fmt(r.mean), fmt(r.lo) + " to " + fmt(r.hi), num(r.p) ? fmtP(r.p) : "", b.unit]);
            });
        });
        return table(caption, ["Estimate of", "Analysis", "Estimate", "95% interval", "p", "Unit"], body);
    }

    function robustnessSection(data, width, tip) {
        var r = data.robustness;
        if (!r) return pending("Robustness", "the robustness stage");
        return card(
            "Robustness (reported, not used for decisions)",
            "Each confirmatory estimate (blue) followed by the analyses in plan section 5.5 that repeat it (gray), on the same axis. They do not change the section 7 decisions, so none has a verdict. The regressions report intervals only; the Firth fit has its own direct-simulation p. Item 4 (H1 for PY2021) is the PY2021 row of the group comparisons.",
            [
                multiples(r.groups, width, tip),
                blocksTable("robustness, group comparisons", r.groups),
                el("h5", {}, "H3 core coefficients"),
                el("p", { class: "mssp-note" }, "Log-odds per 2 SD (per category for the BASIC level). The Firth model uses the same predictor scaling with the core predictors and cohort only."),
                multiples(r.h3, width, tip),
                blocksTable("robustness, H3", r.h3)
            ]
        );
    }

    var GROUP_NAMES = { early: "Early renewers", leaver: "Leavers", stayer: "Stayers" };

    function money(v) {
        return "$" + Math.round(v).toLocaleString("en-US");
    }

    function exploratorySection(data, width, tip) {
        var x = data.exploratory;
        if (!x) return pending("Exploratory and descriptive", "the exploratory stage");
        var groups = ["early", "leaver", "stayer"].filter(function (g) { return x.groups[g]; });
        var body = [multiples(x.alternative_exposures, width, tip), blocksTable("other measures of the regional pull", x.alternative_exposures)];
        if (x.region) {
            body.push(el("h5", {}, "Census region in the decision model"));
            body.push(el("div", { role: "list" }, intervalChart(estimateRows(x.region.rows, "log-odds"), { width: width, tip: tip, unit: "log-odds", aria: "Census region coefficients" })));
            body.push(el("p", { class: "mssp-note" }, "Region with the largest share of 2021 assigned person-years; Northeast is the reference. ACOs with no region (territories) excluded: " + x.region.excluded_no_region + "."));
        }
        body.push(el("h5", {}, "Leavers alongside early renewers and stayers"));
        body.push(dataTable(["Variable"].concat(groups.map(function (g) { return GROUP_NAMES[g] + ": mean (median), n"; })), Object.keys(x.described).map(function (v) {
            return [x.described[v]].concat(groups.map(function (g) { var s = x.groups[g][v]; return fmt(s.mean) + " (" + fmt(s.median) + "), " + s.n; }));
        })));
        if (x.enhanced.length) {
            body.push(el("h5", {}, "Early renewers already in ENHANCED in PY2021"));
            body.push(el("p", { class: "mssp-note" }, "Renewing could not raise their sharing rate. Each value with its percentile among stayers."));
            body.push(dataTable(["ACO", "Cohort"].concat(Object.keys(x.described).map(function (v) { return x.described[v]; })), x.enhanced.map(function (r) {
                return [r.aco_id, r.cohort].concat(Object.keys(x.described).map(function (v) { return fmt(r[v].value) + " (" + Math.round(r[v].percentile) + "th)"; }));
            })));
        }
        body.push(el("h5", {}, "Who renewed early"));
        body.push(table("ACOs by group, cohort, PY2021 track and 2022 track", ["Group", "Cohort", "PY2021 track", "2022 track", "ACOs"], x.who_renewed.map(function (r) {
            return [GROUP_NAMES[r.grp] || r.grp, r.cohort, r.track_2021, r.track_2022, r.n];
        })));
        body.push(el("h5", {}, "Balance"));
        var bal = x.balance;
        var balGroups = ["early", "leaver", "stayer"].filter(function (g) { return bal.groups[g]; });
        body.push(dataTable(["Characteristic"].concat(balGroups.map(function (g) { return GROUP_NAMES[g] + ": mean, n"; })), Object.keys(bal.labels).map(function (k) {
            return [bal.labels[k]].concat(balGroups.map(function (g) { var s = bal.groups[g][k]; return fmt(100 * s.mean, 1) + "%, " + s.n; }));
        })));
        if (x.spending.length) {
            var pts = x.spending.map(function (p) {
                var py = p.start_year + p.agreement_year - 1;
                return Object.assign({}, p, {
                    tip: [money(p.mean) + " per capita", (p.early ? "Early renewers from 2020 agreements" : "Other ACOs") + ", agreement starting " + p.start_year + ", year " + p.agreement_year + " (PY" + py + ")" + (p.scheduled ? ", scheduled benchmark year" : "") + ", " + p.n + " ACOs"]
                });
            });
            body.push(el("h5", {}, "Per-capita spending by agreement year (5-year agreements)"));
            body.push(legend([{ label: "Early renewers out of a 2020 agreement" }, { label: "Other ACOs", muted: true }, { label: "Scheduled benchmark years (shaded)", shade: true }]));
            body.push(el("div", { role: "list" }, spendingChart(pts, { width: width, tip: tip, aria: "Mean per-capita spending by agreement year" })));
            body.push(el("p", { class: "mssp-note" }, "Agreement years 3-5 are the scheduled benchmark years of the next agreement. Benchmark-year status and tenure cannot be separated here: every ACO reaches its benchmark years in the same agreement years."));
            body.push(table("per-capita spending by agreement year", ["Agreement start", "Agreement year", "Group", "Scheduled benchmark year", "ACOs", "Mean per capita"], x.spending.map(function (p) {
                return [p.start_year, p.agreement_year, p.early ? "Early renewers from 2020" : "Other ACOs", p.scheduled ? "yes" : "no", p.n, money(p.mean)];
            })));
        }
        return card(
            "Exploratory and descriptive",
            "Labeled exploratory in plan section 5.6: the same estimators as above, no predictions and no verdicts. Top: other measures of the regional pull in place of it in H2b and H3 (blue: the confirmatory measure).",
            body
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
        // The stage list only matters while some stage is still running; once all are done it is noise.
        if (data.stages.some(function (s) { return !s.done; })) {
            var chips = el("ul", { class: "mssp-stages", "aria-label": "Pipeline stages" });
            data.stages.forEach(function (s) {
                chips.appendChild(el("li", { class: s.done ? "is-done" : "" }, [el("span", { "aria-hidden": "true" }, s.done ? "✓ " : "… "), s.name + (s.done ? "" : " (pending)")]));
            });
            nodes.push(chips);
        }
        return nodes;
    }

    /* --- Render ----------------------------------------------------------------------------------------------- */

    function render(root, data) {
        var state = { prior: "normal" };
        var width;

        // Charts sit inside a card, so they get the card's content width (its padding and border subtracted).
        function chartWidth() {
            return Math.max(280, Math.floor(root.clientWidth) - CARD_INSET);
        }

        function draw() {
            width = chartWidth();
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
            append(root, [comparisons(data, width, tip), decision(data, width, tip, state.prior), effect(data, width, tip), agreement(data), robustnessSection(data, width, tip), exploratorySection(data, width, tip)]);
            root.appendChild(el("p", { class: "mssp-note" }, [
                "Source: ",
                el("a", { href: RESULTS_URL }, "the committed results files"),
                ", each of which records the commit it ran at; every stage ran with the registered code (commit a4064f5)."
            ]));
        }

        draw();
        if (window.ResizeObserver) {
            var last = width;
            new ResizeObserver(function () {
                var w = chartWidth();
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
