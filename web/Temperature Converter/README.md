# Coastal Temperature Converter

A visually premium, highly interactive temperature converter web application designed with a serene, coastal-themed aesthetic. Built using HTML5, CSS3, and Vanilla JavaScript, the application features real-time validation, simultaneous multi-unit conversions, absolute zero safety constraints, and a dynamic weather-state background that transitions smoothly based on the temperature.

---

## Design System and Aesthetics

*   **Color Palette**:
    *   Primary Navy (#1B3A4B): Used for headers, wave dividers, and primary text, evoking deep ocean waters.
    *   Coastal Linen (#F5F0E8): The default warm-neutral background color, representing soft sand.
    *   Coastal Ocean (#297685): Used for active highlights, buttons, and prominent accents.
    *   Coastal Seafoam (#64B5C1) and Aqua (#C9F1F2): Used for cool accents and transitions.
    *   Coastal Coral (#F29F5A): Used for warm highlights and warning/error states.
    *   Seaglass (#A8D5BA): Used for success validation indicators.
*   **Typography**:
    *   Main Headings: Google Font Playfair Display - an elegant, high-contrast serif font.
    *   Subheadings & UI Elements: Google Font Josefin Sans - a clean, geometric sans-serif.
    *   Body Text: Google Font Source Sans 3 - a highly legible, modern sans-serif.
    *   Decorative Accents: Google Font Seaweed Script - a flowing, handwritten-style cursive font.
*   **Textures and Visuals**:
    *   Organic Waves: Custom, responsive SVG wave dividers at the top and bottom of the viewport.
    *   Seaside Details: Animated SVG seagulls floating in the footer area.
    *   Glassmorphism: A frosted-glass card overlay using CSS backdrop-filter for a modern, layered look.
    *   Paper Texture: A subtle vector noise overlay across the page background.

---

## Features and Functionality

1.  **Simultaneous Multi-Unit Conversion**:
    *   Enter a temperature in any unit (Celsius, Fahrenheit, or Kelvin) and see the conversion for all three units updated instantly.
    *   The selected input unit is highlighted, and the conversion formulas are displayed dynamically on each output card.
2.  **Real-Time Input Validation**:
    *   Validates input as you type, displaying a success checkmark or error cross.
    *   Gracefully handles intermediate typing states (like entering a minus sign or decimal point) without flashing premature errors.
3.  **Absolute Zero Enforcement**:
    *   Prevents physically impossible inputs by enforcing absolute zero limits:
        *   Celsius: -273.15 degrees C
        *   Fahrenheit: -459.67 degrees F
        *   Kelvin: 0 K
    *   Displays an explicit, user-friendly error message if a value below absolute zero is entered.
4.  **Dynamic Climate Visualizer**:
    *   Features a horizontal climate gauge that moves a pointer indicator in real time as the temperature changes.
    *   Classifies temperatures into five distinct coastal climate states:
        *   Glacial Deep (Freezing)
        *   Breezy Mist (Cool)
        *   Sandy Shore (Mild)
        *   Warm Sunset (Warm)
        *   Tropical Heat (Hot)
5.  **Smooth Theme Transitions**:
    *   The background overlay changes color dynamically based on the climate state (shifting from icy mist blues to warm sunset oranges and tropical clays), using CSS transitions for fluid color morphing.

---

## Technical Details

*   **Responsive Layout**: Built using CSS Flexbox, Grid, and media queries to ensure a perfect presentation on mobile, tablet, and desktop screens.
*   **Performance**: Pure vanilla implementation with no external frameworks or library dependencies, ensuring fast loading times.
*   **Accessibility**: Proper semantic HTML5 tags, ARIA roles, and keyboard-accessible buttons for the unit selectors.

---

## How to Run the Project

1.  Download or clone this directory.
2.  Open the index.html file directly in any modern web browser (Chrome, Firefox, Safari, Edge).
3.  No local server setup, compilation, or installation is required.
