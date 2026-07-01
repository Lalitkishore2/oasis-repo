# KitKat Premium Landing Page

A visually polished, premium static HTML/CSS landing page for the iconic brand **KitKat**, inspired by the spacious, clean, and elegant aesthetic of the minimalist "Live Laugh Love" design layout.

This project is built using **pure HTML5 and CSS3** (no JavaScript) to demonstrate advanced front-end layout, typography, and vector animation techniques.

---

## 🎨 Design System & Aesthetics

*   **Color Palette**:
    *   `Primary Red (#EC2227)`: KitKat's bold brand red, used for CTAs, accents, and the logo.
    *   `Warm Cream (#F9F5F0)`: The primary background color, providing a soft, warm, and premium feel.
    *   `Accent Cream (#F1ECE6)`: Used for section transitions and card backdrops.
    *   `Dark Brown (#3C1E1A)`: The primary text color and footer background, representing rich dark chocolate.
    *   `White (#FFFFFF)`: Used for card backgrounds and logo borders.
*   **Typography**:
    *   *Headings*: Google Font **Fredoka** — a bold, playful, and rounded sans-serif that captures KitKat's friendly brand identity.
    *   *Body Copy*: Google Font **Inter** — a highly legible, clean, and modern geometric sans-serif.
*   **Tactile Textures**: The body features a very subtle, modern dotted grid background, creating a premium paper-like texture.
*   **Organic Frames**: The hero image is nestled in a white, slightly tilted (+2deg) Polaroid-style frame with a soft, warm-shadow backdrop (-3deg), echoing the scrapbook feel of the inspiration layout.
*   **Slanted Section Transitions**: Fully responsive SVG slanted dividers are used to transition between sections (e.g., Features ➔ About and About ➔ Footer), matching the slanted angle of the KitKat logo.

---

## 🚀 Features & Components

1.  **Sticky Navigation Bar**:
    *   Stays pinned to the top of the viewport with a blur backdrop effect (`backdrop-filter`).
    *   Features a pure CSS slanted KitKat oval logo.
    *   **Pure CSS Hamburger Menu**: On mobile viewports (widths under 768px), the text links collapse into a clean hamburger menu. Tapping the menu animates the hamburger into an "X" and slides the menu down smoothly—all without a single line of JavaScript.
2.  **Hero Section**:
    *   Split-column layout containing the brand slogan (*"Have a Break. Have a KitKat."*), a descriptive subheadline, two transition-enabled CTA buttons, and the hero image.
    *   Features scroll indicator dots at the bottom.
3.  **Features Section ("The Anatomy of a Break")**:
    *   A responsive three-column grid highlighting the *Crispy Wafer*, *Velvet Chocolate*, and *The Perfect Snap*.
    *   Utilizes CSS Flexbox with `align-items: stretch` to ensure all cards are **exactly equal in height** at all screen sizes.
    *   Features custom inline SVG icons and lift-up hover transitions.
4.  **About Section ("The Ritual of the Break")**:
    *   An asymmetric layout featuring the brand story with a large red drop-cap on the left.
    *   **Interactive SVG Snapping Animation**: On the right, a custom-designed inline SVG displays two KitKat chocolate fingers. Hovering over the illustration rotates the fingers outward (a satisfying "snap") and triggers red sparkle lines to fade in. All pointer lines and anchor dots are drawn inside the SVG coordinate space to guarantee perfect alignment on all viewports.
5.  **Bold Footer**:
    *   A rich dark brown footer utilizing CSS Grid, containing a brand tagline, hover-active social media links, a newsletter sign-up form with custom inputs, quick links, and centered copyright/legal text.

---

## 📱 Responsiveness

*   Built with a **Mobile-First** mindset using CSS Flexbox and Grid.
*   The page transitions seamlessly at `768px` to stack all sections vertically, resize typography, and toggle the mobile hamburger menu.
*   Verified to have **zero horizontal layout overflow** (`scrollWidth` = `innerWidth`), preventing horizontal scrolling bugs on mobile devices.

---

## 🛠️ How to Run the Project

1.  Download or clone this directory.
2.  Simply double-click the **`index.html`** file to open it directly in any modern web browser (Chrome, Firefox, Safari, Edge).
3.  No local server, compilation, or installation is required!
