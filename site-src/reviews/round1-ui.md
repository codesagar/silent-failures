# Round-one independent UI/editorial critique

Reviewed the built site at http://localhost:8765 on 2026-10-18. Read-only review; no repository changes. Browser: headless installed Chrome via Playwright. Viewports: 1440×900, 1024×900, 768×900, 390×844, 320×900. Reviewed actual rendering, example navigation, keyboard activation, no-JavaScript disclosures, the spoken walkthrough, and automatic WCAG checks.

## Verdict

The direction is substantially coherent: the desktop first viewport delivers a finding and a meaningful comparison immediately, the examples are far more concrete than a dashboard, and the three conclusions form an intelligible argument. The 529-word presenter script is consistent with about 4:05 of speech at its declared 130 wpm, leaving 55 seconds for navigation. That is a pacing estimate, not a performed human five-minute rehearsal.

Two interaction/rendering defects should be fixed before acceptance. Two smaller editorial issues are worth addressing in the same pass.

## Material defects

### 1. High: the first chart is silently cropped at 1024 px, altering the visible comparison

At 1024×900, the first chart's container is 471 px wide but its SVG has a 640 px minimum width. The right ends of every bar are clipped. Luna, GLM, Kimi and Nemotron appear entirely green: their cap/claim segments are off-screen. Even the ambiguity legend item disappears. Nothing visually tells a reader that the graphic continues to the right. The page itself has no horizontal overflow, so a page-width check misses this.

Evidence: `/tmp/sf-r1-1024-top.png`. Measured chart container clientWidth=471, scrollWidth=640. The quiet comparison also has clientWidth=582, scrollWidth=640 at this breakpoint. At 320 px all three narrow chart containers are 284 px wide with 336 px content; they also require scrolling. At 390, 768 and 1440 px the charts fit.

Recommendation: switch to a full-width layout or the narrow graphic based on available chart width before the desktop two-column layout produces clipping. For 320 px either make the narrow chart fit without losing readability or explicitly indicate overflow and ensure keyboard access. This is not a request to simply shrink all text.

### 2. Medium: selecting an example hides the model selector behind the sticky header

Reproduction: click the opening CTA, select `Qwen · silence`. The anchor jump positions the episode at the top while the selector immediately above is covered by the header. On desktop the selector spans y=42–90 while the header occupies y=0–72: labels vanish. On mobile it spans y=-27–104 while the header occupies y=0–94: essentially the entire seven-item selector disappears. To compare Luna/Qwen or move on to GLM, the presenter has to scroll back upward after each selection. This directly harms the intended five-minute sequence, which changes examples several times.

Evidence: `/tmp/sf-r1-select-qwen.png` and `/tmp/sf-r1-mobile-select-qwen.png`. Keyboard activation works, but after Enter on Qwen, Tab goes into its follow-up disclosure, not the remaining example selectors; switching back requires recovering the selector.

Recommendation: for in-selector selections, change the panel without jumping below the selector, or deliberately scroll the selector plus episode into view. Preserve useful external deep links and browser history. Keep native link semantics or implement complete keyboard semantics if changing to tabs.

## Editorial improvements

### 3. Medium: the second headline claims a ranking across five fault channels, while its visible graphic compares only two

The lead says lost responses had the **highest** unsupported-claim rate in four of five models. The immediate chart only shows timeout versus lost response. The full five-channel table is appropriately available in a disclosure, but the central infographic does not itself substantiate the stronger ranking in the lead. A reader must leave the main visual argument to check it.

Recommendation: either phrase the lead around the shown timeout comparison or add a compact indication of the all-channel ranking. The existing qualification that semantics and failed-only groups differ is good and should remain.

### 4. Low: define the cap where it first drives the main conclusion

The first viewport repeatedly says “cap” but never says what was capped. The methods and Qwen example eventually explain it, but the first-30-second promise would be clearer with “tool-use limit” or a short parenthetical definition in the opening paragraph. “Went silent” then immediately means “kept calling tools until a configured limit, no final answer,” rather than leaving a visitor to infer the mechanism.

## Checks that passed

- Desktop 1440×900: actual primary finding, percentage and comparison visible on first screen (`/tmp/sf-r1-desktop-top.png`). Typography, limited color palette, direct annotation and line lengths work well.
- Mobile 390×844: principal conclusion appears before scrolling; charts use specific narrow layouts and their values remain readable. First chart starts at the bottom of the first viewport (`/tmp/sf-r1-mobile-top.png`). Some lower source text is small, but no page-width overflow was observed.
- No JavaScript: all seven episode disclosures remain present; Qwen can be opened natively; core argument and diagrams remain available.
- Keyboard: example links can be focused, Tab moves between them, Enter selects Qwen; native follow-up and table disclosures are reachable. Navigation problem above remains.
- Automatic Axe WCAG2A/AA/2.1AA scan: zero violations on the home page at 1440 px. This does not resolve chart crop or navigation usability.
- No browser page errors during the visual review.
- Real-episode deep link to GLM selects the correct episode. Successful quiet action is explicitly labeled successful rather than unsupported success.
- Presenter guide anchor lands on a closed disclosure; one additional click is required. This is acceptable but opening the guide on its explicit link would be a minor polish improvement.

## Evidence and scope

Scripts: `/tmp/silent-failures-qa/round1.cjs`, `r1-interact.cjs`, `r1-checks.cjs`. Screenshots cited above are normal viewport captures. Additional element screenshots under `/tmp/sf-r1-*-examples.png`, `*-quiet.png`, `*-probe.png` contain Playwright sticky-header capture artifacts and should not be interpreted as independent layout defects. This review did not re-adjudicate scientific labels or independently verify every numeric source; that is the evidence reviewer's remit.
