document.addEventListener('DOMContentLoaded', function() {
    fetch('data.json')
        .then(response => response.json())
        .then(data => displayData(data))
        .catch(error => console.error('Error fetching JSON:', error));
});

function displayData(data) {
    const jsonDisplay = document.getElementById('jsonDisplay');
    data.forEach(item => {
        jsonDisplay.innerHTML += `<p>索引: ${item.idx}<br> 名称: <strong> ${item.name} </strong></p> <p>系列: ${item.series_name} <br> 社团名: <strong> ${item.societies_name} </strong></p> <p>标签: <strong> ${item.tag.join(', ')} </strong></p> <p>CV: <strong> ${item.cv.join(', ')} </strong></p>`;
    });
}
