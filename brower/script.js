document.addEventListener('DOMContentLoaded', function() {
    fetch('data.json')
        .then(response => response.json())
        .then(data => displayData(data))
        .catch(error => console.error('Error fetching JSON:', error));
});

function displayData(data) {
    const jsonDisplay = document.getElementById('jsonDisplay');
    data.forEach(item => {
        jsonDisplay.innerHTML += item.
    });
}
