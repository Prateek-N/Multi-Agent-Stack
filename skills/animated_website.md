# Skill: Animated Website

## Purpose

Design and implement a production-quality animated website or web page. Covers entrance
animations, scroll-triggered effects, micro-interactions, page transitions, loading sequences,
and background motion — with performance and accessibility guardrails built in.

This skill is the canonical way to request any animation work across the kit. It picks the
right technology for the project's stack and budget, generates implementation-ready code,
and flags performance traps before they ship.

---

## Trigger Conditions

Invoke this skill when the user's message contains:
- "animate", "animation", "animated website", "motion"
- "scroll effect", "parallax", "fade in", "slide in", "entrance"
- "micro-interaction", "hover effect", "transition", "loading screen"
- "GSAP", "Framer Motion", "Three.js", "Lottie", "CSS keyframe"
- "interactive", "dynamic page", "cinematic", "immersive"
- Any Phase 3 implementation task in `product_design` or `software` domain where
  the `solution_design` artifact includes animation or motion as a requirement

---

## Technology Selection Guide

Pick the stack based on project constraints before writing any code:

| Technology | Use when | Avoid when |
|---|---|---|
| **CSS only** | Simple fade/slide/scale; no JS budget; SSR sites | Sequenced multi-step timelines; scroll scrubbing |
| **CSS + Intersection Observer** | Scroll-triggered entrance animations; no library budget | Complex staggering logic |
| **GSAP** | Complex timelines, scroll scrubbing (ScrollTrigger), SVG morphing | React-only projects (use Framer Motion instead) |
| **Framer Motion** | React/Next.js; layout animations; gesture-driven UI | Non-React stacks |
| **Three.js / R3F** | 3D scenes, WebGL backgrounds, particle systems | Simple 2D effects (overkill) |
| **Lottie** | Designer-exported After Effects animations; icon animations | When file size matters (Lottie JSON can be large) |
| **Web Animations API** | Lightweight imperative control; no library budget | Complex timelines (too verbose) |

---

## Input Expectations

| Input | Required | Description |
|---|---|---|
| `page_description` | Yes | What the page/site does — target audience, purpose, tone |
| `animation_goal` | Yes | What the animation should communicate (e.g., premium, playful, technical) |
| `stack` | Yes | React, Vue, plain HTML/CSS, Next.js, etc. |
| `sections` | No | List of page sections (hero, features, pricing, footer, etc.) |
| `brand_tokens` | No | Colors, fonts, spacing scale |
| `performance_budget` | No | Target Lighthouse score or "no library" constraint |
| `reference_sites` | No | URLs or descriptions of sites with similar motion feel |

**If required input is missing:**
- `page_description` — ask: "What does this page/site do? Who is the audience and what tone should the motion convey?" Do not proceed without this.
- `animation_goal` — ask: "What should the animation communicate — premium, playful, technical, minimal, energetic?" Vague briefs produce vague motion; this field is non-negotiable.
- `stack` — ask: "What is the frontend stack — React, Vue, plain HTML/CSS, Next.js, or something else?" Technology selection depends entirely on this.
- `sections` — assume a standard landing page structure (hero, features, CTA, footer); list these assumptions at the top of the Animation Plan.
- `brand_tokens` — proceed without; use neutral defaults (white background, dark text, `ease-out cubic` easing).
- `performance_budget` — default to "standard budget"; select technology based on complexity alone.
- `reference_sites` — if `animation_goal` is vague (e.g., "make it premium"), ask for 1–2 reference sites before writing any code.

---

## Output Format

```
## Animation Plan: <page or component name>

**Motion language**: <one sentence — e.g., "Smooth, editorial fade-ups with staggered reveals and a subtle parallax hero.">
**Stack selected**: <technology choice + one-line reason>
**Estimated JS weight**: <e.g., "~45 KB gzipped (GSAP core + ScrollTrigger)">
**Reduced-motion fallback**: <yes — all animations disabled via prefers-reduced-motion>

---

### Section Breakdown

| Section | Animation type | Trigger | Duration | Easing |
|---|---|---|---|---|
| Hero | Scale-up + fade text | Page load | 1.2s | ease-out cubic |
| Features | Staggered card slide-up | Scroll enter (20% visible) | 0.6s each, 0.1s stagger | ease-out quart |
| Testimonials | Horizontal marquee | Auto-play, pause on hover | infinite | linear |
| CTA | Pulse ring on button | Idle after 3s | 1.5s loop | ease-in-out |
| Footer | Fade-in | Scroll enter | 0.4s | ease |

---

### Implementation

#### 1. Base CSS setup

```css
/* Reduced motion — always include */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* GPU-composited properties only — do not animate layout properties */
.animate-ready {
  will-change: transform, opacity;
}
```

#### 2. Entrance animation (CSS + Intersection Observer)

```css
.reveal {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Stagger via custom property */
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.2s; }
.reveal:nth-child(4) { transition-delay: 0.3s; }
```

```js
const observer = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      observer.unobserve(e.target); // fire once
    }
  }),
  { threshold: 0.2 }
);
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

#### 3. Hero entrance (GSAP timeline)

```js
import gsap from 'gsap';

const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

tl.from('.hero-headline', { opacity: 0, y: 48, duration: 1 })
  .from('.hero-sub',      { opacity: 0, y: 24, duration: 0.8 }, '-=0.6')
  .from('.hero-cta',      { opacity: 0, scale: 0.9, duration: 0.6 }, '-=0.4');
```

#### 4. Scroll-scrubbed parallax (GSAP ScrollTrigger)

```js
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

gsap.to('.hero-bg', {
  yPercent: -30,
  ease: 'none',
  scrollTrigger: {
    trigger: '.hero',
    start: 'top top',
    end: 'bottom top',
    scrub: true,
  },
});
```

#### 5. Framer Motion card stagger (React)

```tsx
import { motion } from 'framer-motion';

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 32 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] } },
};

export function FeatureGrid({ features }) {
  return (
    <motion.ul variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}>
      {features.map(f => (
        <motion.li key={f.id} variants={item}>
          {f.title}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

#### 6. Loading screen

```css
.loader {
  position: fixed; inset: 0;
  background: #0a0a0a;
  display: grid; place-items: center;
  z-index: 9999;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}

.loader.hidden { opacity: 0; visibility: hidden; }

.loader-bar {
  width: 160px; height: 2px;
  background: #222;
  border-radius: 2px;
  overflow: hidden;
}

.loader-bar::after {
  content: '';
  display: block;
  height: 100%;
  background: #fff;
  animation: load 1.4s ease-in-out infinite;
}

@keyframes load {
  0%   { width: 0%; margin-left: 0; }
  50%  { width: 100%; margin-left: 0; }
  100% { width: 0%; margin-left: 100%; }
}
```

---

### Performance Checklist

- [ ] Only animate `transform` and `opacity` (never `width`, `height`, `top`, `left`)
- [ ] Add `will-change: transform` only on elements actively animating (remove after animation)
- [ ] All entrance animations use `once: true` / `unobserve()` — no repeated triggers
- [ ] `prefers-reduced-motion` media query disables all motion
- [ ] GSAP ScrollTrigger instances killed on component unmount (React/Vue)
- [ ] Total animation JS budget: ≤ 60 KB gzipped unless 3D/WebGL is required
- [ ] Lottie files ≤ 150 KB; lazy-loaded below the fold

---

### Accessibility

- All animated elements retain focus and keyboard navigability
- No animation relies on color alone to convey state
- Auto-playing carousels and marquees pause on `hover` and `focus`
- Loading screens resolve within 3 seconds or expose a skip option
```

---

## Rules

- Always include a `prefers-reduced-motion` block — no exceptions.
- Never animate `width`, `height`, `margin`, `padding`, `top`, `left`, or `bottom` — use
  `transform: translate/scale` instead to stay on the compositor thread.
- If the user only specifies a vibe (e.g., "make it look premium"), ask for 1–2 reference sites
  before writing code. Vague briefs produce vague motion.
- When GSAP ScrollTrigger is used in a React/Vue SPA, always include the cleanup call
  (`ScrollTrigger.getAll().forEach(t => t.kill())`) in the component unmount hook.
- Output code must be copy-paste ready — no pseudocode, no `// TODO` placeholders.
- After the implementation block, always append a Performance Checklist (pre-filled based
  on the techniques used) and an Accessibility section.
- If Three.js or WebGL is selected, warn: "3D scenes can drop to 20 fps on mid-range mobile
  — always test on a real device and provide a 2D fallback."

---

## Token Cost Tier

**Medium** for CSS/Intersection Observer implementations (no file reads required).  
**High** for GSAP or Framer Motion integrations that touch existing component files.  
**High** for Three.js / WebGL scenes (full repo scan needed to assess bundle impact).

Compression hint: if the animation is isolated to a single new component, scope context to
that file only. If touching the global CSS bundle or app entry point, request a repo summary first.
