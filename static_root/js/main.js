// FreshCart/staticfiles/js/main.js
// This file contains general JavaScript for the FreshCart application.

/**
 * Scrolls a given slider horizontally by a specified amount.
 * @param {string} sliderId - The ID of the slider container element.
 * @param {number} scrollAmount - The amount to scroll (positive for right, negative for left).
 */
function scrollSlider(sliderId, scrollAmount) {
    const slider = document.getElementById(sliderId);
    if (slider) {
        slider.scrollBy({
            left: scrollAmount,
            behavior: 'smooth' // Smooth scrolling animation
        });
    }
}

// Add event listeners once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add touch swipe functionality for sliders
    document.querySelectorAll('.slider-container').forEach(slider => {
        let isDown = false;
        let startX;
        let scrollLeft;

        slider.addEventListener('mousedown', (e) => {
            isDown = true;
            slider.classList.add('active');
            startX = e.pageX - slider.offsetLeft;
            scrollLeft = slider.scrollLeft;
        });

        slider.addEventListener('mouseleave', () => {
            isDown = false;
            slider.classList.remove('active');
        });

        slider.addEventListener('mouseup', () => {
            isDown = false;
            slider.classList.remove('active');
        });

        slider.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - slider.offsetLeft;
            const walk = (x - startX) * 2; // Adjust scroll speed
            slider.scrollLeft = scrollLeft - walk;
        });

        // Touch events for mobile
        slider.addEventListener('touchstart', (e) => {
            isDown = true;
            startX = e.touches[0].pageX - slider.offsetLeft;
            scrollLeft = slider.scrollLeft;
        }, { passive: true }); // Use passive listener for better scroll performance

        slider.addEventListener('touchend', () => {
            isDown = false;
        });

        slider.addEventListener('touchmove', (e) => {
            if (!isDown) return;
            const x = e.touches[0].pageX - slider.offsetLeft;
            const walk = (x - startX) * 2;
            slider.scrollLeft = scrollLeft - walk;
        });
    });

    // Optional: Implement keyboard navigation for sliders (arrow keys)
    document.addEventListener('keydown', (event) => {
        const activeSlider = document.querySelector('.slider-container:hover'); // Check if a slider is hovered
        if (activeSlider) {
            if (event.key === 'ArrowLeft') {
                activeSlider.scrollBy({ left: -280, behavior: 'smooth' });
            } else if (event.key === 'ArrowRight') {
                activeSlider.scrollBy({ left: 280, behavior: 'smooth' });
            }
        }
    });
});


