document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let valid = true;

            // Perform form-specific validation
            const title = form.querySelector('input[name="title"]');
            if (title && title.value.trim() === '') {
                valid = false;
                alert('Title is required.');
            }

            const startingBid = form.querySelector('input[name="starting_bid"]');
            if (startingBid && isNaN(startingBid.value)) {
                valid = false;
                alert('Starting bid must be a valid number.');
            }

            // Add more validation rules as needed

            if (!valid) {
                event.preventDefault(); // Prevent form submission
            }
        });
    });
});
