document.getElementById('bookingForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }

    navigator.geolocation.getCurrentPosition(async function (position) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        const pickupCoords = [position.coords.longitude, position.coords.latitude];
        const dropoffCoords = await getCoordinates(data.dropoff_location);

        const response = await fetch('/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pickup_coords: pickupCoords,
                dropoff_coords: dropoffCoords,
                load_type: data.load_type,
                budget: data.budget
            })
        });

        const result = await response.json();
        displayDrivers(result.drivers);
    });
});

// Function to get coordinates from address
async function getCoordinates(address) {
    const response = await fetch(`https://api.openrouteservice.org/geocode/search?api_key=5b3ce3597851110001cf62486fe24ef5303144a4be207ab42ab9dda9&text=${address}`);
    const data = await response.json();
    return data.features[0].geometry.coordinates;
}

// Function to display drivers
function displayDrivers(drivers) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '';  // Clear previous results

    if (drivers.length === 0) {
        resultDiv.innerHTML = '<p>No drivers available.</p>';
        return;
    }

    const ul = document.createElement('ul');
    drivers.forEach(driver => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>Name:</strong> ${driver.name}<br>
            <strong>Vehicle Type:</strong> ${driver.vehicle_type}<br>
            <strong>Location:</strong> ${driver.location}<br>
            <strong>Distance:</strong> ${driver.distance.toFixed(2)} km<br>
            <strong>Rating:</strong> ${driver.rating}<br>
            <strong>Total Price:</strong> £${driver.total_price.toFixed(2)}
        `;
        ul.appendChild(li);
    });

    resultDiv.appendChild(ul);
}
