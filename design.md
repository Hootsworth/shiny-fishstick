# Design System — "Flow" (HTTPie-style landing page)

A reconstruction of the HTTPie marketing site's visual language: a warm
off-white canvas, punchy "pie green," razor-bold display type, and a signature
motif of circle + pie-slice "blob" shapes scattered across sections like
confetti from the brand mark.

## 1. Color

| Token | Hex | Use |
|---|---|---|
| `--cream` | `#F5F5F0` | Page background (matches HTTPie's actual theme-color) |
| `--ink` | `#16171A` | Primary text, nav pill, footer background |
| `--ink-soft` | `#46474C` | Secondary/body text on cream |
| `--pie-green` | `#3DD56D` | Primary accent — buttons, links, highlight shapes |
| `--pie-green-deep` | `#1F9E4D` | Hover state / shadow on green elements |
| `--paper` | `#FFFFFF` | Card/terminal surfaces on cream |
| `--line` | `#E4E3DC` | Hairline borders/dividers |
| `--code-bg` | `#101113` | Terminal window background |
| `--code-text` | `#E9E9E4` | Terminal body text |

Dark mode swap (toggle in footer, matches source): `--cream → #16171A`,
`--ink → #F5F5F0`, surfaces darken, green stays constant as the one fixed
brand anchor.

## 2. Type

- **Display / headline:** a heavy, slightly condensed geometric grotesk
  (system stack: `"Inter Tight", "Archivo", system-ui, sans-serif` at weight
  800–900). Set in **uppercase** for hero/section headlines with tight
  tracking (`-0.02em`) — this is the single most recognizable HTTPie
  typographic move.
- **Body:** same family, weight 400–500, sentence case, generous line-height
  (1.6) for contrast against the shouty headlines.
- **Code/mono:** `"JetBrains Mono", "SF Mono", monospace` for terminal panes,
  install commands, and inline technical strings.
- **Scale:** 14 / 16 / 18 / 22 / 28 / 44 / 72px — hero headline sits at the
  top of the scale and breaks the grid slightly (line-height 0.95).

## 3. Layout

```
┌────────────────────────────────────────────┐
│  ░ pill navbar, floating, rounded-full ░    │
├────────────────────────────────────────────┤
│   HUGE UPPERCASE HERO HEADLINE              │
│   subhead sentence                          │
│   [Get the app →]  [terminal install pill]  │
│                                              │
│        ╭───────────────────────╮            │
│        │   terminal mockup     │  ◐ blobs   │
│        ╰───────────────────────╯            │
├────────────────────────────────────────────┤
│  changelog / "what's new" ticket card       │
├────────────────────────────────────────────┤
│  product split: Desktop & Web   (image L /  │
│                                   copy R)    │
├────────────────────────────────────────────┤
│  product split: Terminal        (copy L /   │
│                                   $ install) │
├────────────────────────────────────────────┤
│  "Loved by the community" — tweet wall      │
├────────────────────────────────────────────┤
│  "Trusted by the best" — logo strip         │
├────────────────────────────────────────────┤
│  dark CTA band: join community + newsletter │
├────────────────────────────────────────────┤
│  ink footer, 3-column link grid             │
└────────────────────────────────────────────┘
```

Container max-width: `1180px`. Section vertical rhythm: `128px` desktop /
`64px` mobile. Cards and the terminal window use large radii (`24–32px`);
the nav pill and buttons use full pill radius (`999px`) — rounded everywhere
except hairline dividers.

## 4. Signature shapes — the "pie" motif

HTTPie's logo is a pie chart with one green slice missing a bite. The whole
site riffs on this: every section has 1–3 stray **circle** and **pie-slice**
shapes (some solid green, some solid ink, some just an outline ring) placed
off-grid, partially cropped by the viewport edge, behind or beside content.
Rules for using them:

- Never more than 3 per section.
- At least one is cropped by the section edge (bleeds off-screen).
- Vary size dramatically: one large (300–500px) ambient shape low-opacity in
  the background, one small (40–80px) solid "confetti" shape near a heading.
- Solid fills only — no gradients, no drop shadows on the shapes themselves.

## 5. Components

- **Nav:** floating dark pill (`--ink` bg, white text), centered, sits ~24px
  from top, scroll-shrinks slightly. Logo mark = circle with a slice cut out.
- **Primary button:** pill, `--ink` background / cream text, on hover
  inverts to `--pie-green` background / ink text. Arrow glyph `→` suffix.
- **Secondary / install pill:** outlined pill, monospace `$` prefix, tab
  switcher for package managers (apt / brew / pip / …) using an underline
  indicator.
- **Terminal window:** `--code-bg`, 28px radius, traffic-light dots top-left,
  syntax-colored request/response panes, faint top highlight to suggest
  glass.
- **Tweet/quote card:** white card, 20px radius, hairline border, avatar +
  handle row, quoted text, small bird/source icon.
- **Logo strip:** monochrome (ink-on-cream) wordmarks, evenly spaced,
  separated by hairlines, grayscale/low-opacity until hover.

## 6. Motion

- Hero shapes drift very slowly (parallax-style `transform: translateY`) on
  scroll — ambient, not attention-grabbing.
- Buttons: 150ms ease background/color swap, no scale.
- Cards: 4px lift + border color shift to green on hover.
- Respect `prefers-reduced-motion`: disable parallax and lift transitions.

## 7. Voice

Short, declarative, lower-case body copy under shouting uppercase headers.
Talks to developers directly ("you"), avoids marketing fluff — mirrors the
source's own tone ("Making APIs simple and intuitive for those building the
tools of our time.").
