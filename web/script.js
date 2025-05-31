const mapRegions = [
    { id: "region1", name: "The Old Well", x: 50, y: 50, width: 80, height: 60 },
    { id: "region2", name: "Mystic Forest Path", x: 180, y: 120, width: 100, height: 70 },
    { id: "region3", name: "Town Entrance", x: 100, y: 220, width: 100, height: 50 }
];

// --- Functions to update UI from Python ---
eel.expose(update_narrative);
function update_narrative(text_line) {
    const narrativeArea = document.getElementById('narrativeArea');
    const newLine = document.createElement('p');
    newLine.textContent = text_line;
    narrativeArea.appendChild(newLine);
    narrativeArea.scrollTop = narrativeArea.scrollHeight; // Auto-scroll
}

eel.expose(update_player_stats);
function update_player_stats(hp, max_hp, mp, max_mp, location) {
    document.getElementById('playerHP').textContent = hp;
    document.getElementById('playerMaxHP').textContent = max_hp;
    document.getElementById('playerMP').textContent = mp;
    document.getElementById('playerMaxMP').textContent = max_mp;
    document.getElementById('playerLocation').textContent = location;
}

eel.expose(update_inventory);
function update_inventory(inventory_list) {
    const inventoryList = document.getElementById('playerInventory');
    inventoryList.innerHTML = ''; // Clear old items
    if (inventory_list && inventory_list.length > 0) {
        inventory_list.forEach(item => {
            const listItem = document.createElement('li');
            listItem.textContent = item;
            inventoryList.appendChild(listItem);
        });
    } else {
        const listItem = document.createElement('li');
        listItem.textContent = 'Empty';
        inventoryList.appendChild(listItem);
    }
}

eel.expose(update_skills);
function update_skills(skills_list) {
    const skillsList = document.getElementById('playerSkills');
    skillsList.innerHTML = ''; // Clear old skills
    if (skills_list && skills_list.length > 0) {
        skills_list.forEach(skill => {
            const listItem = document.createElement('li');
            listItem.textContent = skill;
            skillsList.appendChild(listItem);
        });
    } else {
        const listItem = document.createElement('li');
        listItem.textContent = 'No skills';
        skillsList.appendChild(listItem);
    }
}

// --- Map Interaction ---
async function handleMapClick(event) {
    const mapImage = document.getElementById('gameMap');
    const rect = mapImage.getBoundingClientRect();

    // Calculate click coordinates relative to the image
    // Assumes the mapRegions coordinates are based on the naturalWidth/Height of the image (e.g., 300x300 for the SVG)
    const scaleX = mapImage.naturalWidth / mapImage.width;
    const scaleY = mapImage.naturalHeight / mapImage.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    let clickedRegionName = null;

    for (const region of mapRegions) {
        if (x >= region.x && x <= region.x + region.width &&
            y >= region.y && y <= region.y + region.height) {
            clickedRegionName = region.name;
            break;
        }
    }

    if (clickedRegionName) {
        console.log(`JS: Clicked on map region: ${clickedRegionName}`);
        try {
            // Call a Python function, sending the name of the clicked region
            let response = await eel.handle_map_click_py(clickedRegionName)();
            console.log(`JS: Response from Python for map click: ${response}`);
            // Optionally, update narrative or do something with the response
        } catch (error) {
            console.error("JS: Error calling handle_map_click_py:", error);
            update_narrative("Error: Could not process map click with Python. " + error);
        }
    } else {
        console.log("JS: Clicked on map, but not on a defined region. Coordinates (scaled): X=" + x + ", Y=" + y);
    }
}


// --- Function to send command to Python ---
async function sendCommand() {
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value.trim();
    if (command) {
        try {
            await eel.process_player_command_py(command)(); // Call Python
        } catch (error) {
            console.error("JS: Error calling process_player_command_py:", error);
            update_narrative("Error: Could not send command to Python. " + error);
        }
        commandInput.value = ''; // Clear input field
    }
}

// --- Initialization and Event Listeners ---
document.addEventListener('DOMContentLoaded', (event) => {
    const commandInput = document.getElementById('commandInput');
    if(commandInput) {
        commandInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendCommand();
            }
        });
    }

    const gameMapElement = document.getElementById('gameMap');
    if (gameMapElement) {
        // Ensure the naturalWidth/naturalHeight are loaded, especially for SVGs or if image loads slowly
        if (gameMapElement.complete && gameMapElement.naturalWidth !== 0) {
            gameMapElement.addEventListener('click', handleMapClick);
        } else {
            gameMapElement.onload = () => {
                gameMapElement.addEventListener('click', handleMapClick);
            };
        }
    }

    // Signal Python that JS is ready and UI elements are potentially available
    if (eel && typeof eel.js_ready === 'function') {
         console.log("JS: DOMContentLoaded, calling eel.js_ready().");
         eel.js_ready("JavaScript and DOM are ready.")().catch(err => {
            console.error("JS: Error calling eel.js_ready:", err);
         });
         // Set a flag to prevent window.onload from re-triggering if this succeeded
         document.body.dataset.jsReadySignaledByDOMContentLoaded = "true";
    } else {
        console.error("Eel or eel.js_ready not available at DOMContentLoaded. Will try again in window.onload.");
    }
});

window.onload = () => {
    // Only call js_ready from onload if DOMContentLoaded didn't already signal it
    // (e.g. if eel.js loaded after DOMContentLoaded but before window.onload)
    if (eel && typeof eel.js_ready === 'function' && !document.body.dataset.jsReadySignaledByDOMContentLoaded) {
        console.log("JS: window.onload, calling eel.js_ready().");
        eel.js_ready("JavaScript and DOM are ready (onload).")().catch(err => {
            console.error("JS: Error calling eel.js_ready (onload):", err);
        });
    } else if (!document.body.dataset.jsReadySignaledByDOMContentLoaded) {
         console.error("Eel or eel.js_ready not available at window.onload and was not called by DOMContentLoaded.");
    }

    // Re-check map listener attachment in case image wasn't ready during DOMContentLoaded
    const gameMapElement = document.getElementById('gameMap');
    if (gameMapElement && !gameMapElement.onclick) { // Check if listener already attached
         if (gameMapElement.complete && gameMapElement.naturalWidth !== 0) {
            gameMapElement.addEventListener('click', handleMapClick);
            console.log("JS: Attached map click listener during window.onload.");
        } else {
            gameMapElement.onload = () => { // Should have loaded by now, but as a fallback
                gameMapElement.addEventListener('click', handleMapClick);
                console.log("JS: Attached map click listener during gameMapElement.onload (triggered from window.onload).");
            };
        }
    }
};
