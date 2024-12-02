document.getElementById('set-dir-btn').addEventListener('click', async () => {
    const directory = document.getElementById('directory').value;
    try {
        const response = await fetch('/set_directory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory })
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error setting directory: ${errorData.error}`);
        } else {
            const result = await response.json();
            alert(result.message);
            // Fetch and display patterns after directory is set
            fetchPatterns();
        }
    } catch (error) {
        alert(`Error setting directory: ${error}`);
    }
});

async function chooseDirectory() {
    return new Promise((resolve, reject) => {
      pywebview.api.chooseDirectory().then(resolve).catch(reject);
    });
  }

document.getElementById('choose-dir-btn').addEventListener('click', async () => {
    try {
        const directory = await chooseDirectory(); // Call the function to choose the dir

        if (directory) {
          const response = await fetch('/set_directory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory })
          });

          if (!response.ok) {
              const errorData = await response.json();
              alert(`Error setting directory: ${errorData.error}`);
          } else {
              const result = await response.json();
              document.getElementById('directory').value = result.directory; // Update display
              alert(result.message);
              fetchPatterns();
          }
        } else {
          alert('No directory selected.'); // Handle cancellation
        }

    } catch (error) {
        alert(`Error: ${error}`); // Generic error handling
    }



});



async function fetchPatterns() {
    try {
        const response = await fetch('/discover_patterns');
        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error fetching patterns: ${errorData.error}`);
            return; // Stop execution if error
        }
        const patterns = await response.json();
        const patternsDiv = document.getElementById('patterns');
        patternsDiv.innerHTML = "<h2>Discovered Patterns:</h2>";
        if (patterns.length === 0) {
            patternsDiv.innerHTML += "<p>No patterns found.</p>";
        } else {
          const patternList = document.createElement('ul');
          patterns.forEach(pattern => {
            const listItem = document.createElement('li');
            listItem.textContent = `${pattern[0][0]} (${pattern[1]} files)`;
            patternList.appendChild(listItem);
        });
        patternsDiv.appendChild(patternList);

        }

    } catch (error) {
        alert(`Error fetching patterns: ${error}`);
    }
}

document.getElementById('rename-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/rename_files', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
         }); // No body needed for this example

        if (!response.ok) {  // Check for errors
          const errorData = await response.json();
          alert(`Error renaming files: ${errorData.error}`);
          return;
        }

        const result = await response.json();
        let message = `Renamed: ${result.renamed_count}, Failed: ${result.failed_count}`;
        if (result.failed_files && result.failed_files.length > 0) {
            message += "\nFailed Files:\n";
            result.failed_files.forEach(file => {
                message += `${file[0]}: ${file[1]}\n`;
            });
        }

        alert(message);
    } catch (error) {
        alert(`Error renaming files: ${error.message}`);
    }
});