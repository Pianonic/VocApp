(() => {
    'use strict'
  
    const storedTheme = localStorage.getItem('theme') || 'auto' // Default to auto
  
    // Function to set the actual theme attribute (needed if system pref changes while 'auto' is selected)
    const setTheme = (theme) => {
      let themeToSet = theme;
      if (theme === 'auto') {
        themeToSet = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      document.documentElement.setAttribute('data-bs-theme', themeToSet);
    }
  
    // Function to update the dropdown appearance (button icon, active item)
    const updateDropdownUI = (theme) => {
       const themeIcon = document.getElementById('bd-theme-icon');
       const activeBtn = document.querySelector(`.dropdown-item[data-bs-theme-value="${theme}"]`);
       const autoBtn = document.querySelector('.dropdown-item[data-bs-theme-value="auto"]');
  
       // Remove active state from all buttons
       document.querySelectorAll('.dropdown-item').forEach(btn => {
          btn.classList.remove('active');
          btn.setAttribute('aria-pressed', 'false');
       });
  
       // Set active state on the correct button (fallback to 'auto' if invalid theme stored)
       if (activeBtn) {
          activeBtn.classList.add('active');
          activeBtn.setAttribute('aria-pressed', 'true');
       } else {
           autoBtn.classList.add('active');
           autoBtn.setAttribute('aria-pressed', 'true');
           // Consider logging an error or resetting localStorage if the stored theme was invalid
       }
  
       // Update button icon based on the *preference* (light, dark, or auto)
       if (themeIcon) {
           if (theme === 'light') themeIcon.className = 'fas fa-sun me-2';
           else if (theme === 'dark') themeIcon.className = 'fas fa-moon me-2';
           else themeIcon.className = 'fas fa-circle-half-stroke me-2'; // Auto icon
       }
    }
  
    // Initial UI update on page load. The theme itself was already set by the inline script in <head>.
    // We just need to make sure the dropdown reflects the stored preference.
    updateDropdownUI(storedTheme);
  
    // Add event listeners to dropdown items
    document.querySelectorAll('[data-bs-theme-value]')
      .forEach(toggle => {
        toggle.addEventListener('click', () => {
          const theme = toggle.getAttribute('data-bs-theme-value');
          localStorage.setItem('theme', theme); // Save the preference
          setTheme(theme); // Apply the theme (resolves 'auto' if needed)
          updateDropdownUI(theme); // Update the dropdown UI to match preference
        })
      })
  
    // Listener for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      const currentStoredTheme = localStorage.getItem('theme');
      // Only update the running theme if the user preference is 'auto'
      if (currentStoredTheme === 'auto' || !currentStoredTheme) {
         setTheme('auto'); // Re-evaluate 'auto' and apply the corresponding theme
         // The dropdown UI doesn't need changing, as the *preference* remains 'auto'
      }
    })
  
  })()
  