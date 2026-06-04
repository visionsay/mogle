---
name: editorial-promo-video
description: >-
  Build premium, commercial-quality EDITORIAL motion-graphics promo videos with
  HyperFrames (HTML→MP4). Use when creating or editing a HyperFrames promo /
  explainer / brand video in the "MOGLE editorial" style — dark ink palette with
  a coral+gold accent, Pretendard Korean typography, kinetic mask-reveal type,
  film grain + vignette overlays, a numbered process timeline, animated counters,
  and a shimmer logo end-card. Encodes the design tokens, GSAP motion recipes, and
  the vendored-asset / track-per-scene rules that keep renders deterministic and
  lint-clean. Triggers: "promo video", "explainer", "intro video", "전자책/강의/브랜드
  홍보 영상", "HyperFrames 영상", or edits to a composition that uses these tokens.
---

# Editorial Promo Video (HyperFrames)

A reusable recipe for the look & motion of `index.html` in this project. It produces
a 1920×1080 / 30fps editorial promo: dark, typographic, data-driven, with a refined
crossfade rhythm. **Everything here renders deterministically and lints to 0/0.**

> Canonical template: this project's **`index.html`**. The fastest path is to copy it
> and rewrite the copy (text, scene count, colors). The sections below are the *why*
> and the *gotchas* so edits don't break the render.

---

## 0. Non-negotiable HyperFrames rules (learned the hard way)

These four prevent the bugs that silently ruin a render. Apply them every time.

1. **Vendor GSAP and fonts locally — never CDN.** The render/validate headless Chrome
   rejects `cdn.jsdelivr.net` with `net::ERR_CERT_AUTHORITY_INVALID` → `gsap is not
   defined` → blank video. Download once into `assets/`:
   ```bash
   mkdir -p assets/lib assets/fonts
   curl -sL -o assets/lib/gsap.min.js \
     https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js
   curl -sL -o assets/fonts/PretendardVariable.woff2 \
     https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2
   ```
   Then reference them with relative paths:
   ```html
   <script src="assets/lib/gsap.min.js"></script>
   ```
   Verify a font really downloaded (CDN 404s return ~100 bytes of ASCII):
   ```bash
   python3 -c "print(open('assets/fonts/PretendardVariable.woff2','rb').read(4))"  # -> b'wOF2'
   ```

2. **Declare `@font-face` AND use the literal family name** (not a CSS variable).
   The deterministic-font compiler reads `font-family` *statically*; `var(--font)`
   is opaque to it and triggers `No deterministic font mapping`. Use:
   ```css
   @font-face {
     font-family: "Pretendard"; font-weight: 45 920; font-style: normal;
     font-display: block; src: url("assets/fonts/PretendardVariable.woff2") format("woff2-variations");
   }
   html, body { font-family: "Pretendard", sans-serif; }   /* literal, generic fallback only */
   ```
   A non-generic fallback (`-apple-system`, etc.) re-introduces the warning — keep it `sans-serif`.

3. **One track-index per scene** when scenes crossfade. The linter errors on
   `overlapping_clips_same_track`. Each full-screen scene `clip` overlaps its neighbor
   by ~0.2–0.5s for the dissolve, so give them **distinct** `data-track-index`
   (10, 11, 12, …). Higher index renders on top during the overlap = clean dissolve.

4. **Stay deterministic.** No `Math.random()`, `Date.now()`, or network fetches.
   Every timed element needs `class="clip"` + `data-start` + `data-duration` +
   `data-track-index`. Timelines are `{ paused: true }` and registered on
   `window.__timelines["<composition-id>"]`.

---

## 1. Design tokens

```css
:root {
  --ink:       #0e1116;  /* near-black, faint blue */
  --ink-2:     #141922;
  --paper:     #f4efe6;  /* warm cream — primary text */
  --paper-dim: #c9c2b4;  /* secondary text */
  --accent:    #ff5a3c;  /* coral — the ONE highlight color */
  --gold:      #e8b65a;  /* secondary accent (process/gradients) */
  --muted:     #7d8798;  /* kickers, ticks */
  --line:      rgba(244, 239, 230, 0.14);
}
#root {
  background:
    radial-gradient(120% 90% at 18% 12%, #1a212e 0%, rgba(26,33,46,0) 55%),
    radial-gradient(120% 90% at 86% 90%, #1d161a 0%, rgba(29,22,26,0) 50%),
    var(--ink);
}
```

Type scale (1920×1080): hero `124px/800`, statement `96–104px/800`, big number
`128–180px/800` (letter-spacing `-0.04em`), section title `64px/800`, body `24px/400`,
kicker `26px/600` with `letter-spacing: 0.42em; text-transform: uppercase`.
**Rule of thumb:** one accent color, generous negative space, `180px` side padding,
left-aligned editorial blocks (center only the end-card).

---

## 2. Always-on overlays (the "film" look)

Two non-interactive clips spanning the whole composition, on the highest tracks.
Give them ids (`#vignette`, `#grain`) to satisfy `studio_missing_editable_id`.

```css
.vignette { position:absolute; inset:0; pointer-events:none;
  background: radial-gradient(120% 120% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45) 100%); }
.grain { position:absolute; inset:0; pointer-events:none; opacity:.07; mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"); }
```
```html
<div id="vignette" class="vignette clip" data-start="0" data-duration="36" data-track-index="40"></div>
<div id="grain"    class="grain clip"    data-start="0" data-duration="36" data-track-index="41"></div>
```
Keep `data-duration` equal to the root duration whenever you change the total length.

---

## 3. Motion recipes (GSAP, supported props only)

Only tween `opacity, x, y, xPercent, yPercent, scale, scaleX/Y, rotation, width, height,
visibility`. Avoid color/clip-path tweens (non-deterministic on seek). Position param =
absolute seconds.

**Mask rise-in** (the signature kinetic-type reveal). Wrap each line in
`.mask { overflow:hidden }` so the glyphs slide up from behind a hard edge:
```js
const E = "power3.out";
function riseIn(target, at, stagger) {
  tl.from(target, { yPercent: 115, opacity: 0, duration: 0.9, ease: E, stagger: stagger || 0 }, at);
}
```

**Scene crossfade out** (last thing in each non-final scene):
```js
tl.to("#sceneA", { opacity: 0, y: -40, duration: 0.6, ease: "power2.in" }, 4.7);
```

**Numbered process timeline** — a `scaleX` progress line + nodes popping in + cards rising:
```js
tl.to("#c-fill", { scaleX: 1, duration: 4.4, ease: "power1.inOut" }, 11.6); // origin: left
["#c-n1","#c-n2","#c-n3","#c-n4"].forEach((n,i) => {
  const at = 11.7 + i*1.05;
  tl.to(n, { scale: 1, duration: 0.45, ease: "back.out(2)" }, at);
  tl.from("#c-c"+(i+1), { opacity: 0, y: 56, duration: 0.85, ease: E }, at + 0.05);
});
```

**Animated counter** — GSAP only tweens numbers, so drive `textContent` via a proxy
+ `onUpdate` (re-fires correctly on every seeked frame):
```js
document.querySelectorAll("#sceneD .counter").forEach((el, i) => {
  const to = parseInt(el.getAttribute("data-to"), 10), proxy = { v: 0 };
  tl.to(proxy, { v: to, duration: 1.3, ease: "power2.out",
    onUpdate: () => { el.textContent = Math.round(proxy.v); } }, 25.95 + i*0.28);
});
```

**Shimmer end-card** — a `mix-blend-mode:screen` diagonal gradient swept across the logo:
```css
.shimmer { position:absolute; inset:0; mix-blend-mode:screen; transform:translateX(-120%); pointer-events:none;
  background:linear-gradient(100deg, rgba(255,255,255,0) 35%, rgba(255,255,255,.55) 50%, rgba(255,255,255,0) 65%); }
```
```js
tl.fromTo("#e-shimmer", { xPercent: -120 }, { xPercent: 120, duration: 1.1, ease: "power2.inOut" }, 32.0);
```

**End-card hold** — to extend the outro, lengthen the final scene + root + overlays and
fill the held time with a tiny "breath" (1.5% zoom) and an optional second shimmer so the
frame isn't dead-static:
```js
tl.to("#sceneE", { scale: 1.015, duration: 3.0, ease: "sine.inOut" }, 33.0);
```

---

## 4. Scene skeleton & timing

Default 5-act, ~36s structure (adjust freely; keep each scene on its own track):

| Scene | track | time | role |
| --- | --- | --- | --- |
| A cold open | 10 | 0–5s | kicker + accent rule + hero mask-type |
| B promise   | 11 | 5–11s | problem → reframe (dim the setup, pop the payoff) |
| C process   | 12 | 11–25.5s | progress line + numbered cards |
| D proof     | 13 | 25.5–30.5s | 3 animated counters + underline bars |
| E end-card  | 14 | 30.5–36s | CTA line + brand lockup + shimmer + hold |

A timed scene wrapper carries the `clip`/`data-*`; **animate inner elements with GSAP**
(no timing attrs needed on children — visibility follows the wrapper).

---

## 5. Build & verify loop

```bash
npx hyperframes lint        # MUST be 0 errors (0 warnings is the goal)
npx hyperframes validate    # headless-Chrome: "No console errors", text passes WCAG AA
npx hyperframes render --quality high --fps 30 --workers 4 --output out/promo.mp4
```

**Always eyeball the result** — extract representative frames and view them; the font /
layout warnings are sometimes false positives, and only a frame proves Pretendard loaded:
```bash
for t in 2 9 14 27 33; do
  ffmpeg -nostdin -v error -ss $t -i out/promo.mp4 -frames:v 1 docs/frames/frame-${t}s.png -y
done
```
Confirm duration/fps: `ffprobe -v error -show_entries format=duration -show_entries stream=r_frame_rate out/promo.mp4`.

---

## 6. Commercial-use checklist

- **Pretendard** = SIL OFL 1.1 ✓ commercial · **GSAP 3** = free ✓ commercial — both vendored.
- Design, copy, motion = 100% original. **No third-party music/images.**
- For VO/BGM use royalty-free audio or the `/hyperframes-media` skill (Kokoro TTS); add as a
  `<audio class="clip" data-start data-duration data-track-index data-volume>` element. Never
  add copyrighted tracks.
