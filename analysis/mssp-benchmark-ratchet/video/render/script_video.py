# Video narration, one entry per visible slide, in video order.
# Each entry is a list of (clip_label, text). Multi-part slides reveal one step per clip.
SCRIPT = [
    (
        "open-hook",
        [
            (
                "01",
                """In January 2022, twenty-nine groups of doctors and hospitals did something odd. They quit their Medicare contracts early and signed new ones, which reset the targets Medicare uses to decide whether they earn a share of savings.

Two thirds of them ended up with a lower target. A harder one.

So why do it? I ran a study to find out, and I wrote down the rules before I looked at the data. Here's what I found.""",
            )
        ],
    ),
    (
        "cover",
        [
            (
                "02",
                """I'm Samuel Harrold, and this is a pre-registered study of public Medicare data. You don't need any background in healthcare or statistics to follow along.""",
            )
        ],
    ),
    (
        "hook",
        [
            (
                "03",
                """First, a familiar idea. Imagine your boss sets next year's sales target from what you sold this year. You crush it, and your reward is a harder target.

Do too well today, and tomorrow gets tougher. Economists call this a ratchet, because it only clicks one way.

Medicare has its own version of this, and it's the key to the whole puzzle.""",
            )
        ],
    ),
    (
        "aco",
        [
            (
                "04",
                """Here's the program. It's called the Medicare Shared Savings Program, and the groups in it are called ACOs, short for accountable care organizations. That's the one acronym you need. An ACO is just a group of doctors and hospitals.

Medicare adds up the total cost of care for each group's patients. If it comes in under a target, the group keeps part of the savings.

It's big: five hundred eleven groups, covering about twelve point six million people with Medicare.""",
            )
        ],
    ),
    (
        "deal",
        [
            (
                "05",
                """Let's use one made-up example with round numbers.

Medicare sets this group's target at eleven thousand dollars per patient per year. The group's patients actually cost ten thousand five hundred. That's five hundred dollars saved per patient, or seven and a half million dollars across fifteen thousand patients.

How much does the group keep? On the common track, up to half: about three point seven five million. On the top track, called ENHANCED, seventy-five percent: about five point six million.

Same savings, almost two million dollars more. Remember that gap.""",
            )
        ],
    ),
    (
        "catch",
        [
            (
                "06",
                """Now the catch. The target doesn't stay put. When a group signs a new contract, Medicare rebuilds the target, starting from the group's own recent spending.

Our group spent ten thousand five hundred, so its new target starts there: five hundred dollars lower. Save money, and your next target gets harder. That's the ratchet.

If that were the whole story, no successful group would ever want a reset. But there's a second part.""",
            )
        ],
    ),
    (
        "region",
        [
            (
                "07",
                """Next, Medicare nudges the target toward what similar patients cost in the group's region.

Say comparable patients nearby cost twelve thousand dollars. That's fifteen hundred more than our group spent. The first time, the rules move the target thirty-five percent of the way toward the region. Thirty-five percent of fifteen hundred is five hundred twenty-five dollars.

So a group in an expensive area gets a boost. How much room a group has for that boost is what I'll call the regional pull. It's the main thing this study measured.""",
            )
        ],
    ),
    (
        "cancel-example",
        [
            ("08a", """Let's add the two parts. Start at ten thousand five hundred, from the group's own spending."""),
            ("08b", """Add five hundred twenty-five for the region."""),
            (
                "08c",
                """The new target is eleven thousand and twenty-five dollars. The old one was eleven thousand. Almost exactly where it started. The penalty for saving and the bonus for an expensive area cancel out.

I picked these numbers on purpose. Keep this picture in mind, because the real data looked a lot like it.""",
            ),
        ],
    ),
    (
        "exit",
        [
            (
                "09",
                """So here's the puzzle. Contracts normally last five years, but a group could quit early and immediately sign a new one.

Renewing early did two things at once. First, it reset the target sooner. Second, for groups on the main track, it was the only way to move up to the top track, ENHANCED, before their contract ran out. That's the one that keeps seventy-five percent of savings, though it also means owing back up to seventy-five percent of any losses.

Two changes, one decision.""",
            )
        ],
    ),
    (
        "counts",
        [
            (
                "10",
                """I looked at three hundred thirty-four groups whose contracts started in mid-2019 or January 2020.

Twenty-nine renewed early, on January first, 2022. I'll call them early renewers, in orange. Two hundred seventy-seven stayed put: the stayers, in blue. And twenty-eight left the program.

So what made those twenty-nine different? One caution: twenty-nine is a small number, and I'll be upfront about what that limits.""",
            )
        ],
    ),
    (
        "motives",
        [
            (
                "11",
                """There are two suspects.

Suspect A: a better target. Maybe a reset would have raised their target, giving them more room to earn savings.

Suspect B: a bigger share. Maybe they wanted the seventy-five percent track, and renewing early was the only door.

The trouble is, both came with the same decision, so no test can fully pull them apart. But one of these suspects doesn't hold up the way you'd expect. Before we get there, here's how I made sure I couldn't fool myself.""",
            )
        ],
    ),
    (
        "shot",
        [
            (
                "12",
                """Before I looked at a single spending number, I wrote down every question I'd ask, every test I'd run, and the exact words I'd use for each possible result. Then I posted it publicly. It's called pre-registration.

Think of calling your shot in pool: eight ball, corner pocket.

Why bother? Because these files are public, and if you slice data enough ways, something will look exciting just by chance. Researchers fall into that trap without meaning to. Calling the shot means you can tell a planned test from a lucky find.""",
            )
        ],
    ),
    (
        "how-shot",
        [
            (
                "13",
                """And you can check it. The plan was registered on OSF, the Open Science Framework, which stamps the time itself, on October twenty-sixth, 2026. The analysis code refused to open any spending file until that registration existed. And I tested everything first on fake data with known answers planted in it.

Reviews of the plan before registration also caught a real flaw: my first main test was quietly just a restatement of past savings. Catching that before the plan was locked, instead of after, is the whole point.""",
            )
        ],
    ),
    (
        "rebuild",
        [
            (
                "14",
                """One more check before the results. Medicare doesn't publish what a group's target would have been after a reset, so I rebuilt it from public files.

I tested the rebuild on one hundred one groups where Medicare did publish the answer. It passed the bar I'd set in advance: it ranked groups almost exactly the way Medicare did, and the typical miss was one point six percent.""",
            )
        ],
    ),
    (
        "ranges",
        [
            (
                "15a",
                """Now, how to read the results. Each one is a best guess, the dot, and a range of plausible values, the bar. Ask one question: does the bar cross zero?

Here, the best guess is plus three point four, and the whole bar sits above zero. That's a clear difference.""",
            ),
            (
                "15b",
                """Here, the best guess is minus half a point, and the bar crosses zero. That doesn't prove there's no difference. It means we can't tell it apart from none. You'll see both of these again in a minute.""",
            ),
        ],
    ),
    (
        "f1-region",
        [
            (
                "16",
                """Finding one, the main question. Were early renewers in places where care costs more than their target?

Yes. The gap was bigger than for stayers, by about three point four percent of the target. That's roughly three hundred eighty-five dollars per patient per year. It passed the test I set in advance, and by my own rule it counts as evidence for suspect A, the better target.

Case closed? Not quite. That's only one of the two parts.""",
            )
        ],
    ),
    (
        "f2-savers",
        [
            (
                "17",
                """Finding two. Early renewers were already beating their targets, by more than stayers.

In 2020 they saved about six point four percent of their target, against four point six for stayers, and the gap held in 2021 too. That comes straight from Medicare's own reports.

And remember the catch: a reset restarts from your own spending. For strong savers, that part cuts the target. So one part helps them more, and the other hurts them more.""",
            )
        ],
    ),
    (
        "f3-cancel",
        [
            (
                "18a",
                """Here's what happens when you put them together. The blue bar is the regional boost. Early renewers stood to gain a little over one and a half points more than stayers.""",
            ),
            ("18b", """The orange bar is the own-spending catch. They stood to lose about two points more, because they'd been saving more."""),
            (
                "18c",
                """Add them up, and you get the grey bar: about minus half a point, with a range that crosses zero. The boost and the penalty cancel. It's our eleven thousand and twenty-five example, in real data.""",
            ),
            (
                "18d",
                """After the study, I checked what actually happened, using Medicare's published 2022 targets. Early renewers' new targets came in about one point three percent lower on average, and two thirds of them went down. That check wasn't in the original plan, so I'm labeling it as an add-on. But it agrees.

So on average, a reset didn't hand these groups a better target.""",
            ),
        ],
    ),
    (
        "f4-share",
        [
            (
                "19",
                """Finding four is about suspect B, the bigger share.

Of the twenty-seven early renewers on the main track, twenty-six moved up to the seventy-five percent track. And sixteen of them were already at the main track's top level, one short step away.

In a model of who renewed, being at a higher level stood out, along with the regional pull. One caution: that model rests on just twenty-four groups, so trust the direction, not the exact size.""",
            )
        ],
    ),
    (
        "f5-after",
        [
            (
                "20a",
                """Finding five: did renewing change spending? Compared with groups that hadn't renewed yet, early renewers' spending growth was about the same: minus zero point four percent, with a range from minus four to plus two and a half.""",
            ),
            (
                "20b",
                """So we can rule out a drop bigger than about four percent, or a rise bigger than about two and a half. But I can't call it "no effect." I had only one earlier period to compare trends, during COVID, and a trend that started before renewal could hide a small effect. My plan said not to call it an effect in that case, so I don't.""",
            ),
        ],
    ),
    (
        "cansay",
        [
            (
                "21",
                """So what can this study say? It shows which groups chose to reset, what a reset stood to do to their targets, and that spending didn't shift by more than a few percent.

What it can't say: that renewing caused anything, since groups chose for themselves; which suspect was the real reason; or what any of this cost Medicare.""",
            )
        ],
    ),
    (
        "bestread",
        [
            (
                "22",
                """So why did they hit reset? On average, not for a better target. Their targets mostly went down. But nearly all of them got the bigger share, and many were one step away.

For a low-cost group that's already saving, keeping seventy-five percent instead of fifty can be worth more than a small drop in the target.

That's my reading, not a tested result. But it fits how Medicare wrote the rules: if you wanted the bigger share mid-contract, a reset came with it.""",
            )
        ],
    ),
    (
        "fineprint",
        [
            (
                "23",
                """A few limits. The biggest: these are the 2022 rules. For contracts starting in 2024 or later, Medicare gives groups credit for past savings, so the trade-off may look different today.

The numbers are small. My rebuilt targets are good for averages, rough for single groups. Thirty-nine smaller groups couldn't be measured, because Medicare hides tiny counts for privacy. And there was only one earlier period, during COVID.""",
            )
        ],
    ),
    (
        "ai-use",
        [
            (
                "24",
                """A quick disclosure. An AI tool, Claude Code from Anthropic, proposed this topic and drafted the analysis plan, the code, and most of the written post, and separate AI instances reviewed them. I chose among its options, registered the plan, ran the analysis, and I'm responsible for the results. The slides and script for this video were drafted with Claude's help too.

Because the plan was public before any result existed, you can check it either way.""",
            )
        ],
    ),
    (
        "takeaways",
        [
            (
                "25",
                """Three things to remember.

One: the groups that reset early were low-cost compared with their neighbors, and already saving more.

Two: a reset didn't raise their targets on average. The bigger seventy-five percent share is the likelier draw.

Three, and this goes far beyond Medicare: write down your rules before you look, and people can trust your answer, even when it's messy.""",
            )
        ],
    ),
    (
        "more",
        [
            (
                "26",
                """If you want to dig in, the full write-up, the registered plan and the code are all linked in the description.

And if you've ever had a target ratchet up on you, tell me about it in the comments. Thanks for watching.""",
            )
        ],
    ),
]
