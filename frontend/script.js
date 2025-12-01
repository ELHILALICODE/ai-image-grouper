// Define global variables
let imageUpload;
let imageGroupsContainer;
const backendUrl = 'http://localhost:3000/api/upload';

document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded! DOM Content Loaded.');
    imageUpload = document.getElementById('image-upload');
    imageGroupsContainer = document.getElementById('image-groups');
    console.log('Elements initialized:', { imageUpload, imageGroupsContainer });
});

async function processImages() {
    console.log('ProcessImages function called!');
    const processBtn = document.getElementById('process-btn');
    
    const files = imageUpload.files;
    if (files.length === 0) {
        alert('Please select images to process.');
        return;
    }

    const formData = new FormData();
    for (const file of files) {
        formData.append('images', file);
    }

    // Clear previous results and show loading state
    imageGroupsContainer.innerHTML = '<p>Processing images...</p>';
    processBtn.disabled = true;

    try {
        console.log('Sending request to backend...');
        const response = await fetch(backendUrl, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const groups = await response.json();
        console.log('Frontend received groups:', groups);
        displayImageGroups(groups);

    } catch (error) {
        console.error('Error processing images:', error);
        imageGroupsContainer.innerHTML = `<p>Error processing images: ${error.message}</p>`;
    } finally {
        processBtn.disabled = false;
    }
}

function displayImageGroups(groups) {
    console.log('Displaying groups...');
    imageGroupsContainer.innerHTML = ''; // Clear loading message

    if (Object.keys(groups).length === 0) {
        imageGroupsContainer.innerHTML = '<p>No groups were formed. All images are unique.</p>';
        return;
    }

    let groupIndex = 1;
    for (const key in groups) {
        console.log(`Rendering group: ${key}`);
        const imagePaths = groups[key];
        if (imagePaths.length > 0) {
            const groupElement = document.createElement('div');
            groupElement.classList.add('image-group');

            const groupTitle = document.createElement('h3');
            groupTitle.textContent = `Group ${groupIndex++}`;
            groupElement.appendChild(groupTitle);

            const imageGrid = document.createElement('div');
            imageGrid.classList.add('image-grid');
            
            imagePaths.forEach(imagePath => {
                const img = document.createElement('img');
                const imgUrl = `http://localhost:3000/uploads/${encodeURIComponent(imagePath)}`;
                console.log(`Adding image: ${imgUrl}`);
                img.src = imgUrl;
                img.alt = `Grouped Image`;
                img.onerror = function() {
                    console.error(`Failed to load image: ${this.src}`);
                    this.alt = 'Failed to load image';
                    this.style.border = '2px solid red';
                };
                imageGrid.appendChild(img);
            });

            groupElement.appendChild(imageGrid);
            imageGroupsContainer.appendChild(groupElement);
        }
    }
}
