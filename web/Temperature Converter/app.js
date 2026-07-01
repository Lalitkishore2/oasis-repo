/**
 * Coastal Temperature Converter - JavaScript Logic
 * Implements real-time validation, absolute zero checks, and dynamic coastal theme transitions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- DOM Elements ---
  const tempInput = document.getElementById('tempInput');
  const validationIndicator = document.getElementById('validationIndicator');
  const errorMessage = document.getElementById('errorMessage');
  const convertBtn = document.getElementById('convertBtn');
  
  const unitTabs = document.querySelectorAll('.unit-tab');
  
  const climateBadge = document.getElementById('climateBadge');
  const gaugePointer = document.getElementById('gaugePointer');
  const bgOverlay = document.getElementById('bgOverlay');
  
  const valC = document.getElementById('valC');
  const valF = document.getElementById('valF');
  const valK = document.getElementById('valK');
  
  const cardC = document.getElementById('cardC');
  const cardF = document.getElementById('cardF');
  const cardK = document.getElementById('cardK');

  // --- State Variables ---
  let currentUnit = 'C'; // Default input unit
  let inputValue = '';   // Current input string

  // --- SVG Icons for Validation ---
  const checkIcon = `
    <svg viewBox="0 0 24 24" fill="none" stroke="#a8d5ba" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  `;

  const crossIcon = `
    <svg viewBox="0 0 24 24" fill="none" stroke="#f29f5a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  `;

  // --- Climate States Mapping (Celsius) ---
  const climateStates = [
    { limit: 0, name: 'Glacial Deep (Freezing)', color: '#dbe9f6', pointerColor: '#297685', badgeBg: 'rgba(41, 118, 133, 0.15)', badgeText: '#1b3a4b' },
    { limit: 15, name: 'Breezy Mist (Cool)', color: '#d8f5f6', pointerColor: '#64b5c1', badgeBg: 'rgba(100, 181, 193, 0.2)', badgeText: '#1b3a4b' },
    { limit: 25, name: 'Sandy Shore (Mild)', color: '#f5f0e8', pointerColor: '#afbcc5', badgeBg: 'rgba(132, 121, 104, 0.15)', badgeText: '#847968' },
    { limit: 38, name: 'Warm Sunset (Warm)', color: '#fdf0df', pointerColor: '#f29f5a', badgeBg: 'rgba(242, 159, 90, 0.2)', badgeText: '#8c6b4d' },
    { limit: Infinity, name: 'Tropical Heat (Hot)', color: '#ebdcd0', pointerColor: '#8c6b4d', badgeBg: 'rgba(140, 107, 77, 0.2)', badgeText: '#8c6b4d' }
  ];

  // --- Event Listeners ---
  tempInput.addEventListener('input', handleInput);
  convertBtn.addEventListener('click', handleConvertClick);

  unitTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Set active tab
      unitTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-checked', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-checked', 'true');

      // Update state
      currentUnit = tab.getAttribute('data-unit');
      
      // Update highlights on output cards
      updateCardHighlights();

      // Trigger re-validation and conversion
      processTemperature(true);
    });
  });

  // --- Main Logic Functions ---

  /**
   * Handles user typing in the input field.
   * Performs real-time validation without being overly aggressive (allows typing negative/decimal signs).
   */
  function handleInput(e) {
    inputValue = e.target.value.trim();
    
    // If empty, clear errors and reset outputs
    if (inputValue === '') {
      clearValidation();
      resetOutputs();
      return;
    }

    // Real-time validation
    processTemperature(false);
  }

  /**
   * Handles clicking the "Convert" button.
   * Performs strict validation and triggers conversion + focus animations.
   */
  function handleConvertClick() {
    inputValue = tempInput.value.trim();

    if (inputValue === '') {
      showError('Please enter a temperature value to convert.');
      tempInput.focus();
      return;
    }

    processTemperature(true);
    
    // Add a button click animation
    convertBtn.style.transform = 'scale(0.97)';
    setTimeout(() => {
      convertBtn.style.transform = '';
    }, 150);
  }

  /**
   * Validates input, performs conversion if valid, and updates the UI.
   * @param {boolean} isFinalCheck - If true, treats incomplete inputs (like "-" or ".") as errors.
   */
  function processTemperature(isFinalCheck = false) {
    const value = tempInput.value.trim();

    if (value === '') {
      resetOutputs();
      return;
    }

    // 1. Numeric Validation (Regex check)
    // Allows negative sign, digits, and single decimal point
    const numericRegex = /^-?\d*\.?\d*$/;
    if (!numericRegex.test(value)) {
      showError('Please enter a valid number (e.g., 25, -12.5).');
      return;
    }

    // Handle intermediate typing states (e.g. just "-" or ".")
    if (value === '-' || value === '.' || value === '-.') {
      if (isFinalCheck) {
        showError('Please enter a complete numeric value.');
      } else {
        // Clear outputs but don't show red error yet during typing
        resetOutputs();
      }
      return;
    }

    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) {
      showError('Invalid numeric input.');
      return;
    }

    // 2. Absolute Zero Check
    let isAbsoluteZeroViolated = false;
    let limitStr = '';

    if (currentUnit === 'C' && numericValue < -273.15) {
      isAbsoluteZeroViolated = true;
      limitStr = '-273.15°C';
    } else if (currentUnit === 'F' && numericValue < -459.67) {
      isAbsoluteZeroViolated = true;
      limitStr = '-459.67°F';
    } else if (currentUnit === 'K' && numericValue < 0) {
      isAbsoluteZeroViolated = true;
      limitStr = '0 K';
    }

    if (isAbsoluteZeroViolated) {
      showError(`Temperature cannot be below absolute zero (${limitStr}).`);
      return;
    }

    // If we passed all validations:
    showSuccess();
    
    // 3. Perform Calculations
    const results = calculateConversions(numericValue, currentUnit);

    // 4. Update UI Outputs
    displayResults(results);

    // 5. Update Climate Visualizer and Background
    updateClimateTheme(results.C);
  }

  /**
   * Performs the conversion calculations between Celsius, Fahrenheit, and Kelvin.
   */
  function calculateConversions(value, unit) {
    let C, F, K;

    switch (unit) {
      case 'C':
        C = value;
        F = (value * 9/5) + 32;
        K = value + 273.15;
        break;
      case 'F':
        C = (value - 32) * 5/9;
        F = value;
        K = (value - 32) * 5/9 + 273.15;
        break;
      case 'K':
        C = value - 273.15;
        F = (value - 273.15) * 9/5 + 32;
        K = value;
        break;
    }

    return { C, F, K };
  }

  /**
   * Formats and displays the calculation results.
   */
  function displayResults(results) {
    // Format numbers: round to 2 decimal places, remove trailing zeros where appropriate
    const format = (val) => {
      // If absolute zero is extremely close, make sure it displays correctly
      if (Math.abs(val) < 1e-10) return '0';
      return Number(val.toFixed(2)).toString();
    };

    valC.textContent = format(results.C);
    valF.textContent = format(results.F);
    valK.textContent = format(results.K);

    // Add brief animations to the output values
    [valC, valF, valK].forEach(el => {
      el.style.transform = 'scale(1.05)';
      el.style.transition = 'transform 0.15s ease';
      setTimeout(() => {
        el.style.transform = 'scale(1)';
      }, 150);
    });
  }

  /**
   * Updates the background color and the climate gauge based on Celsius temperature.
   */
  function updateClimateTheme(celsiusTemp) {
    // Find matching climate state
    const state = climateStates.find(s => celsiusTemp <= s.limit) || climateStates[climateStates.length - 1];

    // Update dynamic background color (transitions smoothly via CSS)
    bgOverlay.style.backgroundColor = state.color;

    // Update Climate Status Badge
    climateBadge.textContent = state.name;
    climateBadge.style.backgroundColor = state.badgeBg;
    climateBadge.style.color = state.badgeText;

    // Update Gauge Pointer Position
    // Map -50°C to 50°C to 0% to 100%
    const minTemp = -50;
    const maxTemp = 50;
    let percentage = ((celsiusTemp - minTemp) / (maxTemp - minTemp)) * 100;
    
    // Clamp percentage between 0 and 100
    percentage = Math.max(0, Math.min(100, percentage));

    gaugePointer.style.left = `${percentage}%`;
    gaugePointer.style.borderColor = state.pointerColor;
  }

  /**
   * Updates the active/highlighted card based on the selected input unit.
   */
  function updateCardHighlights() {
    cardC.classList.remove('highlight');
    cardF.classList.remove('highlight');
    cardK.classList.remove('highlight');

    if (currentUnit === 'C') cardC.classList.add('highlight');
    if (currentUnit === 'F') cardF.classList.add('highlight');
    if (currentUnit === 'K') cardK.classList.add('highlight');
  }

  // --- Helper UI Functions ---

  function showError(msg) {
    errorMessage.textContent = msg;
    tempInput.classList.remove('is-valid');
    tempInput.classList.add('is-invalid');
    validationIndicator.innerHTML = crossIcon;
    resetOutputs();
  }

  function showSuccess() {
    errorMessage.textContent = '';
    tempInput.classList.remove('is-invalid');
    tempInput.classList.add('is-valid');
    validationIndicator.innerHTML = checkIcon;
  }

  function clearValidation() {
    errorMessage.textContent = '';
    tempInput.classList.remove('is-invalid', 'is-valid');
    validationIndicator.innerHTML = '';
  }

  function resetOutputs() {
    valC.textContent = '--';
    valF.textContent = '--';
    valK.textContent = '--';
    
    // Reset background and gauge to default "Mild Sand" state
    updateClimateTheme(20); 
  }

  // Initialize card highlights and default state
  updateCardHighlights();
  resetOutputs();
});
