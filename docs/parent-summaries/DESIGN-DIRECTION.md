# Parent Summary Page -- Design Direction

> Design brief for the Quest Craft session recap pages sent to parents.
> This document defines the visual direction, content structure, and technical
> approach. It does NOT contain implementation code.

---

## Context and Constraints

**Audience:** Parents of 9--11-year-old kids in a game development program.
They receive these links via WhatsApp after each session.

**Viewing conditions:**
- Primarily mobile phones (iPhone, Android) opened from WhatsApp
- Quick scan on the go -- parents should "get it" in 30 seconds
- May be forwarded to grandparents, other family, school administrators
- Must load fast on any connection (no large images, no JS frameworks)

**Technical constraints:**
- Single self-contained HTML file (inline CSS, no external stylesheets beyond Google Fonts)
- No JavaScript required -- CSS-only effects
- Google Fonts loaded via CDN `<link>` tag
- No images required (CSS-only textures, gradients, borders, and Unicode/emoji decorations)
- Must render correctly in WhatsApp in-app browser, Safari, Chrome

**Brand context:**
- Program name: **Quest Craft**
- Current game: **Split** -- a 2D pixel-art platformer set in a dark castle
- Tone: enthusiastic but not childish, credible but not corporate
- These kids are doing real engineering work (Git, SSH, AI prompting, game design)
- The parents should feel proud and a little amazed

---

## 1. What Is Wrong with the Current Design

The existing page (`session-1-dream.html`) uses:
- System fonts (`-apple-system, BlinkMacSystemFont, Segoe UI`)
- A single purple accent color (`#7c3aed`) applied uniformly everywhere
- A purple-to-indigo gradient banner that reads as generic SaaS / corporate newsletter
- Flat cards with light gray backgrounds
- Thin gray `border-bottom` section dividers
- 2-column grid that does not stack well on narrow phones
- No texture, no atmosphere, no sense of the game world
- Arrow bullets (`->`) that are functional but not thematic

The result feels like a Notion template or a startup product update. It does
not feel like a recap of an adventure. There is nothing here that says
"your kid just designed a game about a jello cube escaping a dark castle."

---

## 2. Design References (The Vibe)

### Reference A: Dungeon Master's Adventure Log
Think of a leather-bound journal kept by a dungeon master. Aged paper
texture. Handwritten-feeling headings. Sections separated by ornamental
rules rather than hairline borders. Margins decorated with small thematic
marks. The page itself feels like an artifact from the world.

**What to steal:** The sense that the page IS the adventure, not a report
ABOUT the adventure. Warm parchment tones. Decorative section dividers.
A serif or display font for headings that feels hand-lettered.

### Reference B: Hollow Knight / Dead Cells Quest Log UI
In-game journal screens from modern indie metroidvanias. Dark background
with warm highlights. Content presented in framed panels that feel like
they belong in the game world. Status indicators styled as icons rather
than text labels. Information is dense but readable because of strong
typographic hierarchy and controlled color.

**What to steal:** Dark background with warm accent lighting. Bordered
content panels that feel like UI frames. Strong contrast between headings
and body text. The "glowing" quality of highlighted information against
darkness.

### Reference C: Letterpress Children's Book Chapter Pages
Modern high-quality children's publishing (e.g., Ignotofsky's "Women in
Science," Oliver Jeffers' work). Bold display typography. Generous whitespace.
A single strong illustration style carried through repeated motifs. Chapter
numbers or session numbers treated as large decorative elements. Simple
color palette used with confidence.

**What to steal:** The confidence of using 2--3 colors boldly rather than
many colors timidly. Display numbers and headings as visual anchors.
White/light space used as a design element. The feeling that every piece
of text was placed deliberately.

---

## 3. Visual Direction

### Color Palette

Move away from generic tech-purple. Move toward the game's actual world:
a dark castle with torchlight, stone walls, creeping vines, and a jello
cube that glows from within.

#### Primary Palette -- "Castle Interior"

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| **Deep Stone** | Very dark warm gray, almost charcoal | `#1a1a2e` | Page background, deepest containers |
| **Warm Stone** | Dark slate with slight warmth | `#2d2d44` | Card/panel backgrounds |
| **Torchlight** | Warm amber-gold | `#e8a838` | Primary accent, headings, highlights, decorative rules |
| **Torch Glow** | Soft warm cream | `#f5e6c8` | Body text color on dark backgrounds |
| **Jello Green** | Translucent lime-green | `#7ddf64` | Secondary accent, success states, the game's jello identity |
| **Ember** | Deep warm orange-red | `#c44b2b` | Tertiary accent, sparingly -- danger/emphasis |

#### Supporting Tones

| Role | Hex | Usage |
|------|-----|-------|
| **Dim Text** | `#9a8e7a` | Secondary/caption text |
| **Border Glow** | `rgba(232, 168, 56, 0.25)` | Subtle panel borders that suggest torchlight |
| **Parchment** | `#f0e4cc` | If a lighter card interior is needed for readability |

#### Rationale
This palette is derived directly from the game world the kids designed:
dark castle stone, flickering torchlight, and the jello cube protagonist.
Every color can be justified by something IN the game. This eliminates the
"generic AI purple" problem entirely.

For the "Exhibition Connection" callout (school/exhibition info), keep a
distinct warm parchment tone (`#f0e4cc` background with `#5a4a2e` text)
so it reads as a different voice -- the educator/program voice -- rather
than the adventure voice.

### Typography

All fonts from Google Fonts CDN.

#### Heading Font: **Cinzel Decorative** (weight 700)
- A display serif with a medieval/engraved quality
- Used ONLY for the main page title ("Quest Craft -- Session 1")
- Loaded at weight 700 only to minimize payload
- Fallback: `Georgia, 'Times New Roman', serif`
- Why: Feels carved in stone. Immediately signals "this is a quest, not a quarterly report."

#### Section Heading Font: **Cinzel** (weights 400, 700)
- The non-decorative companion to Cinzel Decorative
- Used for h2 section headings ("What They Built Today", "Skills Practiced")
- Uppercase with generous letter-spacing (`0.08em`)
- Why: Maintains the medieval register but stays readable at smaller sizes.

#### Body Font: **Source Sans 3** (weights 400, 600)
- Clean, highly readable sans-serif
- Excellent on mobile at 14--16px
- Used for all body text, list items, card descriptions
- Why: Contrasts well with the display serifs. Designed for screen reading.
  Does not fight the decorative headings for attention. Neutral enough to
  feel like clear communication, not decoration.

#### Accent/Game Title Font: **Press Start 2P** (weight 400)
- 8-bit pixel font
- Used ONLY for the game name "SPLIT" when it appears as a feature callout
- Also optionally for small labels like "SESSION 1" or "LEVEL UP"
- Load this at one weight only -- it is decorative and heavy
- Why: Directly references the Dead Cells pixel-art aesthetic the kids chose.
  Creates an instant "this is a video game" signal. Used very sparingly.

#### Font Loading Strategy
```
Cinzel Decorative:wght@700
Cinzel:wght@400;700
Source+Sans+3:wght@400;600
Press+Start+2P
```
Single `<link>` tag, four families. Approximate payload: ~80KB total.
Add `display=swap` to prevent FOIT (flash of invisible text).

### Layout and Spacing

#### Mobile-First Single Column
- `max-width: 640px` centered, `padding: 0 20px`
- No 2-column grids on any screen size. The skills grid in the current design
  breaks on narrow phones (cards become too compressed to read). Use a single
  stacked column of skill cards instead.
- Generous vertical spacing: `24px` between sections, `40px` before major
  new sections (h2 headings)

#### The "Quest Log" Page Structure
The page should feel like opening a journal or quest log, not scrolling a
newsletter. Key structural ideas:

1. **Top Crest / Title Block** -- Centered. Session number rendered large
   and decorative (like a chapter number). Program name above, session
   subtitle below. A thin ornamental horizontal rule underneath -- not a
   plain `border-bottom` but a CSS-drawn decorative line using
   `border-image` or a gradient that fades at both edges.

2. **The Hook** -- A full-width "scroll" or "banner" panel containing the
   one-line summary of what happened. Dark background with torchlight-colored
   text. This replaces the current gradient tagline box.

3. **Stacked Content Sections** -- Each major section (What They Built,
   Skills Practiced, Game Design Concepts) lives in its own "panel" with
   visible borders. The panels should feel like pages pinned to a board
   or entries in a journal, not like SaaS feature cards.

4. **The Game Showcase** -- The game title and description in its own
   special treatment. The word "SPLIT" in Press Start 2P, large. The
   back-of-the-box blurb below in italics. This should feel like a
   featured artifact.

5. **Footer as Seal** -- A centered, minimal footer that feels like a
   wax seal or stamp at the bottom of a letter. Not a gray divider line
   with small text.

### Texture and Atmosphere (CSS Only)

#### Page Background
Do not use a flat color. Use a subtle CSS radial gradient to simulate
vignetting (darker at edges, slightly lighter in center), giving the feel
of torchlight illuminating the center of a stone wall:

```
background: radial-gradient(ellipse at 50% 0%, #2d2d44 0%, #1a1a2e 70%);
```

Optionally layer a very subtle repeating CSS noise pattern using a tiny
inline SVG data URI for texture. This gives the surface a "stone grain"
feel without loading an image file:

```css
background-image:
  url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200'
    xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E
    %3CfeTurbulence type='fractalNoise' baseFrequency='0.65'
    numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E
    %3Crect width='100%25' height='100%25' filter='url(%23n)'
    opacity='0.03'/%3E%3C/svg%3E"),
  radial-gradient(ellipse at 50% 0%, #2d2d44 0%, #1a1a2e 70%);
```

#### Panel / Card Borders
Instead of `border: 1px solid #e9d5ff` (the current lilac), use a
double-line border treatment reminiscent of old manuscripts or game UI
frames:

```css
.panel {
  border: 2px solid rgba(232, 168, 56, 0.3);
  outline: 1px solid rgba(232, 168, 56, 0.1);
  outline-offset: 3px;
  border-radius: 4px;
}
```

This creates a subtle "double frame" effect -- the panel feels bordered
and intentional, like a UI element in a game, without requiring images.

#### Section Dividers
Replace `border-bottom: 1px solid #e5e5e5` with a fading gradient line:

```css
.divider {
  height: 1px;
  background: linear-gradient(
    to right,
    transparent 0%,
    rgba(232, 168, 56, 0.5) 20%,
    rgba(232, 168, 56, 0.5) 80%,
    transparent 100%
  );
  margin: 32px 0;
}
```

Optionally, place a small centered Unicode ornament above the line
(e.g., a diamond `\u25C6` or a fleuron `\u2767`) in the Torchlight color.

#### Glowing Accents
For the game title "SPLIT" and other key highlights, use `text-shadow`
to create a soft glow effect suggesting the jello cube's translucent,
lit-from-within quality:

```css
.game-title {
  color: #7ddf64;
  text-shadow:
    0 0 10px rgba(125, 223, 100, 0.4),
    0 0 30px rgba(125, 223, 100, 0.15);
}
```

#### List Bullets
Replace the current `->` arrow with themed markers. Options:
- A small sword or dagger Unicode character (`\u2694` crossed swords)
- A diamond / lozenge (`\u25C6`)
- A small star (`\u2726` four-pointed star)
- A torch emoji (`\U+1F525` fire) -- but only if emoji rendering is acceptable

Recommended: Use `\u25C6` (small diamond) in the Torchlight amber color.
It is universally supported, does not rely on emoji rendering, and reads
as a game UI bullet point.

---

## 4. Content Structure and Information Flow

### Section Order (top to bottom)

```
 1. TITLE BLOCK
    - "Quest Craft" (program identity, small)
    - "Session 1" (large, decorative -- the chapter number)
    - Session subtitle: "Dream -- Designing a Video Game with AI"
    - Date and participants

 2. THE HOOK (full-width banner)
    - Bold one-line summary: what happened today, in parent-friendly language
    - Supporting sentence underneath
    - This is the only thing some parents will read. Make it count.

 3. THE GAME (featured showcase)
    - Game title "SPLIT" in pixel font, large, with glow
    - Back-of-the-box blurb in italics
    - This section exists because the GAME is the point. Parents should
      see and feel what their kid created.

 4. WHAT THEY BUILT (accomplishments list)
    - 4-5 bullet points, each one sentence
    - Concrete and specific ("Named the game and wrote marketing copy")
    - Diamond bullet markers in amber

 5. SKILLS UNLOCKED (stacked skill cards)
    - Reframed as "skills unlocked" rather than "skills practiced" --
      use game language, not school language
    - Single column stack (NOT a 2-column grid)
    - Each card: skill name in bold amber, one-sentence explanation below
    - 4-6 cards depending on the session

 6. GAME DESIGN CONCEPTS (optional, session-dependent)
    - Only include when there are notable design concepts to highlight
    - Presented as a list, same diamond bullets
    - Bold the concept name, follow with the explanation

 7. ILLUMINATE CONNECTION (callout box)
    - Distinct visual treatment: parchment background, different border color
    - This is the "how this maps to school" section for parents who need
      educational justification
    - Clearly separated visually from the adventure narrative above

 8. VIDEO LINK (if available)
    - Prominent, centered call-to-action
    - Styled as a "play" button or a framed invitation
    - Caption below in dim text

 9. CLOSING QUOTE (optional)
    - A memorable moment or line from the session
    - Centered, italic, in the Torch Glow cream color
    - Decorative quote marks (large, in amber, as CSS ::before/::after)

10. FOOTER / SEAL
    - Team credits: "Built by Ethan (9), Eins (11), Nathan (9) & Andrew (11)"
    - Program identifier and exhibition date
    - "Next session:" preview line
    - Styled compactly, centered, in dim text
    - A small ornamental mark above (diamond, fleuron, or horizontal rule)
```

### Visual Hierarchy Rules

1. **The game title "SPLIT"** should be the single most visually dominant
   element on the page. It is in pixel font, large, with a glow. This
   anchors the entire page around what the kids made.

2. **The hook/summary** is the second most prominent element. Bold, large
   text. If a parent reads ONLY this, they should understand what happened.

3. **Section headings** (h2) are in Cinzel, uppercase, letter-spaced, in
   amber. They are clear structural landmarks but do not compete with the
   game title or the hook.

4. **Body text** is Source Sans 3, 15px on mobile, cream-on-dark. It is
   comfortable to read but intentionally secondary to the structural elements.

5. **The Exhibition box** is visually distinct (light background) so parents
   can identify the "school connection" at a glance, but it does not dominate.

---

## 5. Mobile-First Specifications

### Typography Scale (Mobile)

| Element | Font | Size | Weight | Line Height |
|---------|------|------|--------|-------------|
| Program name ("Quest Craft") | Cinzel | 13px | 400 | 1.2 |
| Session number ("Session 1") | Cinzel Decorative | 28px | 700 | 1.1 |
| Session subtitle | Source Sans 3 | 15px | 400 | 1.4 |
| Hook headline | Source Sans 3 | 18px | 600 | 1.3 |
| Hook supporting text | Source Sans 3 | 15px | 400 | 1.5 |
| Game title ("SPLIT") | Press Start 2P | 28px | 400 | 1.2 |
| Game blurb | Source Sans 3 | 14px italic | 400 | 1.6 |
| Section heading (h2) | Cinzel | 14px uppercase | 700 | 1.3 |
| Body / list text | Source Sans 3 | 15px | 400 | 1.6 |
| Skill card name | Source Sans 3 | 14px | 600 | 1.3 |
| Skill card detail | Source Sans 3 | 13px | 400 | 1.5 |
| Exhibition box | Source Sans 3 | 13px | 400 | 1.5 |
| Footer | Source Sans 3 | 11px | 400 | 1.4 |

### Touch Targets
- Video link / CTA: minimum 44px tall, padded generously
- No interactive elements otherwise (this is a read-only recap page)

### Viewport and Rendering
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
- Test in WhatsApp in-app browser (both iOS and Android)
- `max-width: 640px` with `margin: 0 auto` -- centers on tablets/desktop
- `padding: 24px 20px` -- comfortable thumb margins on phone
- Ensure no horizontal scroll on 320px wide screens

### Performance
- Total page weight target: under 100KB (HTML + inline CSS + font requests)
- Google Fonts are the only external requests
- No images to load
- Page should render meaningfully within 1 second on 3G

---

## 6. Specific CSS Techniques

### Decorative Section Headings with Ornamental Lines
```css
h2 {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #e8a838;
  text-align: center;
  margin: 40px 0 20px;
  position: relative;
}

h2::before,
h2::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 20%;
  height: 1px;
  background: linear-gradient(
    to var(--dir, right),
    rgba(232, 168, 56, 0.5),
    transparent
  );
}
h2::before { right: 100%; margin-right: 12px; --dir: right; }
h2::after  { left: 100%;  margin-left: 12px;  --dir: left;  }
```
This places a fading amber line on each side of the heading text, creating
a centered ornamental divider. If the heading text wraps on mobile, the
lines simply extend from the text edges.

### Double-Frame Panel Effect
```css
.panel {
  background: rgba(45, 45, 68, 0.6);
  border: 1.5px solid rgba(232, 168, 56, 0.25);
  border-radius: 4px;
  padding: 20px;
  position: relative;
}
.panel::before {
  content: '';
  position: absolute;
  inset: -4px;
  border: 1px solid rgba(232, 168, 56, 0.08);
  border-radius: 6px;
  pointer-events: none;
}
```
The `::before` pseudo-element creates a faint outer frame, giving the
panel a "game UI frame" quality without images.

### Glowing Game Title
```css
.game-title {
  font-family: 'Press Start 2P', monospace;
  font-size: 28px;
  color: #7ddf64;
  text-align: center;
  text-shadow:
    0 0 8px rgba(125, 223, 100, 0.5),
    0 0 24px rgba(125, 223, 100, 0.2),
    0 0 48px rgba(125, 223, 100, 0.08);
  letter-spacing: 0.15em;
  margin: 24px 0 12px;
}
```

### Decorative Blockquote (for the game blurb and closing quote)
```css
.quote {
  position: relative;
  font-style: italic;
  color: #f5e6c8;
  padding: 0 24px;
  text-align: center;
  line-height: 1.6;
}
.quote::before {
  content: '\201C';  /* left double quotation mark */
  font-family: 'Cinzel Decorative', Georgia, serif;
  font-size: 48px;
  color: rgba(232, 168, 56, 0.3);
  position: absolute;
  top: -16px;
  left: 0;
}
```

### Skill Cards (Stacked, Not Grid)
```css
.skill-card {
  background: rgba(45, 45, 68, 0.4);
  border-left: 3px solid #e8a838;
  padding: 12px 16px;
  margin-bottom: 10px;
  border-radius: 0 4px 4px 0;
}
.skill-card .name {
  font-family: 'Source Sans 3', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #e8a838;
}
.skill-card .detail {
  font-size: 13px;
  color: #c4b8a0;
  margin-top: 4px;
  line-height: 1.5;
}
```
The left amber border creates a "quest log entry" feel. Stacking vertically
ensures every card is readable on the narrowest phones.

### Themed List Bullets
```css
.quest-list {
  list-style: none;
  padding: 0;
}
.quest-list li {
  padding: 6px 0 6px 24px;
  position: relative;
  font-size: 15px;
  line-height: 1.6;
  color: #f5e6c8;
}
.quest-list li::before {
  content: '\25C6';  /* black diamond */
  position: absolute;
  left: 0;
  color: #e8a838;
  font-size: 10px;
  top: 10px;
}
```

### Exhibition Callout (Parchment Style)
```css
.illuminate {
  background: #f0e4cc;
  border: 1px solid #d4c4a0;
  border-radius: 4px;
  padding: 16px 18px;
  color: #3a3020;
  font-size: 13px;
  line-height: 1.5;
}
.illuminate strong {
  color: #6b4c1e;
}
```
The warm parchment stands out against the dark page as a distinct "educator
voice" section. It does not clash because parchment is thematically consistent
with the castle/medieval register.

### Video Link CTA
```css
.video-cta {
  display: block;
  text-align: center;
  background: rgba(232, 168, 56, 0.12);
  border: 1.5px solid rgba(232, 168, 56, 0.35);
  border-radius: 6px;
  padding: 18px 20px;
  margin: 24px 0;
  text-decoration: none;
  transition: background 0.2s ease;
}
.video-cta:hover {
  background: rgba(232, 168, 56, 0.2);
}
.video-cta .label {
  font-family: 'Source Sans 3', sans-serif;
  font-weight: 600;
  font-size: 15px;
  color: #e8a838;
}
.video-cta .caption {
  font-size: 12px;
  color: #9a8e7a;
  margin-top: 4px;
}
```

### Subtle CSS Animation (Optional)
A very gentle "torch flicker" on the page title only, to reinforce the
atmosphere without being distracting:

```css
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.92; }
}
.page-title {
  animation: flicker 4s ease-in-out infinite;
}
```
This is extremely subtle -- a barely perceptible brightness shift that
registers unconsciously as "warmth" or "life." If it causes any rendering
issues on mobile, remove it. It is purely optional.

---

## 7. Accessibility Notes

- All text on dark backgrounds must meet WCAG AA contrast (4.5:1 for body,
  3:1 for large text). The proposed `#f5e6c8` on `#1a1a2e` has a contrast
  ratio of approximately 11:1 -- well above AA.
- The `#e8a838` amber on `#1a1a2e` has a contrast ratio of approximately
  6.5:1 -- passes AA for all sizes.
- The `#9a8e7a` dim text on `#1a1a2e` has a contrast ratio of approximately
  4.1:1 -- passes AA for text 18px and above. For smaller caption text,
  consider lightening to `#a89e8a` (~5:1).
- The Exhibition box uses dark text on a light background -- standard
  readability.
- Decorative elements (`::before`, `::after`, ornamental characters) should
  use `aria-hidden` or be placed via CSS content (which is inherently
  decorative to screen readers).
- Press Start 2P at 28px is readable but should not be used for body text
  (it is a display face, not a reading face).

---

## 8. What This Changes From the Current Design

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Background** | White (`body` default) | Dark stone gradient with subtle texture |
| **Text color** | Dark gray on white | Warm cream on dark |
| **Accent color** | Purple `#7c3aed` | Amber torchlight `#e8a838` + jello green `#7ddf64` |
| **Heading font** | System sans-serif | Cinzel / Cinzel Decorative (medieval serif) |
| **Body font** | System sans-serif | Source Sans 3 (clean, readable) |
| **Game title** | 20px bold purple | 28px Press Start 2P with green glow |
| **Layout** | 2-column skill grid | Single column throughout (mobile-first) |
| **Section dividers** | Gray `border-bottom` | Fading amber gradient lines with ornaments |
| **Cards/panels** | Light gray `#f8f8f8` | Translucent dark panels with amber border |
| **List bullets** | Purple arrow `->` | Amber diamond `\u25C6` |
| **Overall feel** | Corporate newsletter / SaaS update | Quest log / adventure journal |
| **Emotional register** | "Here is your child's progress report" | "Your kid just went on an adventure" |

---

## 9. Template Adaptation Notes

The TEMPLATE.html placeholder structure maps to the new design as follows:

| Template Placeholder | New Design Element |
|---------------------|--------------------|
| `[N]` (session number) | Large Cinzel Decorative chapter number |
| `[SESSION_TITLE]` | Subtitle under the session number |
| `[DATE]` and `[KIDS_PRESENT]` | Small text in the title block |
| `[ONE_LINE_HEADLINE]` | The Hook banner -- bold, 18px |
| `[SUPPORTING_DETAIL]` | Second line in the Hook, regular weight |
| Game box (title + desc) | Featured showcase with pixel font title + italic blurb |
| `[ACCOMPLISHMENT_N]` | Diamond-bulleted quest list items |
| `[SKILL_N_NAME/DETAIL]` | Left-bordered stacked skill cards |
| `[HOW_THIS_SESSION_MAPS]` | Parchment-style Exhibition callout |
| `[VIDEO_DESCRIPTION]` | Video CTA block |
| `[MEMORABLE_QUOTE]` | Decorative centered quote with large quote marks |
| `[NEXT_SESSION_PREVIEW]` | Footer seal section |

No new content sections need to be invented. The redesign reorganizes and
reskins the same information.

---

## 10. Implementation Priority

If building incrementally:

1. **First:** Dark background, new fonts loaded, color palette applied, single-column layout. This alone transforms the page.
2. **Second:** Panel borders, skill card styling, decorative section dividers, themed list bullets. This establishes the quest-log feel.
3. **Third:** Game title glow, decorative quote marks, double-frame panels, subtle texture. This adds atmosphere and polish.
4. **Optional:** Torch flicker animation, SVG noise texture. These are refinements and can be skipped without loss.

---

## 11. Free Resources Referenced

| Resource | URL | Purpose |
|----------|-----|---------|
| Google Fonts -- Cinzel Decorative | `fonts.google.com/specimen/Cinzel+Decorative` | Display heading font |
| Google Fonts -- Cinzel | `fonts.google.com/specimen/Cinzel` | Section heading font |
| Google Fonts -- Source Sans 3 | `fonts.google.com/specimen/Source+Sans+3` | Body text font |
| Google Fonts -- Press Start 2P | `fonts.google.com/specimen/Press+Start+2P` | Pixel/game display font |
| CSS SVG noise texture | Inline SVG data URI (see Section 6) | Stone grain texture, no external file needed |
| Unicode ornamental characters | Built into all fonts | Decorative bullets and dividers |

No external image files, icon libraries, or JavaScript libraries are required.

---

*This document is a design brief. Implementation as HTML/CSS is a separate step.*
