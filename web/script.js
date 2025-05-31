const mapRegions = [
    { id: "region1", name: "The Old Well", x: 50, y: 50, width: 80, height: 60 },
    { id: "region2", name: "Mystic Forest Path", x: 180, y: 120, width: 100, height: 70 },
    { id: "region3", name: "Town Entrance", x: 100, y: 220, width: 100, height: 50 }
];

// --- Functions to update UI from Python ---
eel.expose(update_narrative);
function update_narrative(text_line, type = 'normal') {
    // Use "narrativeArea" as both the append target and the scroll container,
    // as per current HTML structure where narrativeArea has overflow-y: auto.
    const narrativeContainer = document.getElementById('narrativeArea');
    const scrollContainer = document.getElementById('narrativeArea'); // Target for scrolling

    if (!narrativeContainer) { // Only need to check one if they are the same
        console.error("Narrative container #narrativeArea not found!");
        return;
    }

    // Remove initial placeholder if it's still there
    const placeholder = narrativeContainer.querySelector('p.italic.text-neutral-400');
    if (placeholder && placeholder.textContent.includes("The air grows heavy")) {
        placeholder.remove();
    }

    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'mb-4'; // Common margin for all entries

    // Sanitize text_line to prevent HTML injection if it's ever sourced from user input directly
    // For now, assuming text_line from Python is safe or simple text.
    // A more robust sanitizer might be needed for arbitrary HTML content.
    const escapeHtml = (unsafe) => {
        if (typeof unsafe !== 'string') {
            console.warn("escapeHtml received non-string input:", unsafe);
            return ''; // Or handle as appropriate
        }
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    };

    let sanitizedText = escapeHtml(text_line);

    switch (type) {
        case 'player_command':
            wrapperDiv.innerHTML = `
                <p class="text-sky-400 font-semibold text-xl flex items-center">
                    <span class="material-icons-round mr-2 text-2xl">person_pin</span>
                    &gt; ${sanitizedText}
                </p>`;
            break;
        case 'command_response':
            // For multi-line, split by the literal '\n' passed from Python
            const responseLines = sanitizedText.split('\\n');
            let responseHtml = '';
            responseLines.forEach(line => {
                 responseHtml += `<p class="text-gray-200 text-lg leading-relaxed md:pl-8 mb-2">${line}</p>`; // Added md:pl-8 for larger screens
            });
            if (responseLines.length > 0 && responseHtml.endsWith('mb-2">')) { // Avoid empty last paragraph if ends with \n
                 responseHtml = responseHtml.slice(0, -7) + '">';
            }
            wrapperDiv.innerHTML = responseHtml;
            break;
        case 'system':
            wrapperDiv.innerHTML = `
                <p class="text-teal-400 italic text-md flex items-center">
                    <span class="material-icons-round mr-2 text-teal-500">settings_suggest</span>
                    ${sanitizedText}
                </p>`;
            break;
        case 'important':
            wrapperDiv.innerHTML = `<p class="text-amber-300 font-semibold text-lg">${sanitizedText}</p>`;
            break;
        case 'normal':
        default:
            const normalLines = sanitizedText.split('\\n');
            let normalHtml = '';
            normalLines.forEach(line => {
                 normalHtml += `<p class="text-gray-200 text-lg leading-relaxed mb-2">${line}</p>`;
            });
             if (normalLines.length > 0 && normalHtml.endsWith('mb-2">')) {
                 normalHtml = normalHtml.slice(0, -7) + '">';
            }
            wrapperDiv.innerHTML = normalHtml;
            break;
    }

    narrativeContainer.appendChild(wrapperDiv);

    // Updated scroll logic using requestAnimationFrame
    if (scrollContainer) { // scrollContainer is narrativeArea
        requestAnimationFrame(() => {
            // It's sometimes useful to run it in the *next* frame after the next frame
            // to ensure all layout calculations are done.
            requestAnimationFrame(() => {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
                console.log(`JS: Scrolled narrativeArea. scrollTop: ${scrollContainer.scrollTop}, scrollHeight: ${scrollContainer.scrollHeight}`);
            });
        });
    }
}

eel.expose(update_player_stats);
// New signature: added 'name' as the first parameter
function update_player_stats(name, hp, max_hp, mp, max_mp, location) {
    console.log(`JS: update_player_stats called with: Name=${name}, HP=${hp}/${max_hp}, MP=${mp}/${max_mp}, Loc=${location}`);

    const playerNameDisplay = document.getElementById('playerNameValue'); // New element
    console.log("JS: playerNameValue element:", playerNameDisplay);     // New log

    const hpDisplay = document.getElementById('playerHPDisplay');
    console.log("JS: playerHPDisplay element:", hpDisplay);
    const hpBar = document.getElementById('playerHPBar');
    console.log("JS: playerHPBar element:", hpBar);
    const mpDisplay = document.getElementById('playerMPDisplay');
    console.log("JS: playerMPDisplay element:", mpDisplay);
    const mpBar = document.getElementById('playerMPBar');
    console.log("JS: playerMPBar element:", mpBar);
    const locationDisplay = document.getElementById('playerLocationDisplay');
    console.log("JS: playerLocationDisplay element:", locationDisplay);

    if (playerNameDisplay) { // New block to update name
        playerNameDisplay.textContent = name;
    }

    if (hpDisplay) {
        hpDisplay.textContent = `${hp}/${max_hp}`;
    }
    if (hpBar) {
        const hpPercentage = max_hp > 0 ? (hp / max_hp) * 100 : 0;
        console.log("JS: Calculated HP Percentage:", hpPercentage);
        hpBar.style.width = `${hpPercentage}%`;

        // HP Bar Coloring Logic (ensure it's still there)
        hpBar.classList.remove('bg-red-500', 'bg-yellow-500', 'bg-green-500'); // Clear existing color classes
        if (hpPercentage < 25) {
            hpBar.classList.add('bg-red-500');
        } else if (hpPercentage < 60) {
            hpBar.classList.add('bg-yellow-500');
        } else {
            hpBar.classList.add('bg-green-500');
        }
    }

    if (mpDisplay) {
        mpDisplay.textContent = `${mp}/${max_mp}`;
    }
    if (mpBar) {
        const mpPercentage = max_mp > 0 ? (mp / max_mp) * 100 : 0;
        console.log("JS: Calculated MP Percentage:", mpPercentage);
        mpBar.style.width = `${mpPercentage}%`;
        // MP bar styling is primarily via Tailwind in HTML (e.g., bg-blue-500)
    }

    if (locationDisplay) {
        locationDisplay.textContent = location;
    }
    console.log("JS: update_player_stats finished.");
}

const itemDisplayDetails = {
    "Celestial Blade Fragment": { icon: "gpp_good", iconColorClass: "text-yellow-400", textClass: "text-yellow-300 font-semibold" }, // Adjusted textClass
    "Simple Dagger": { icon: "hardware", iconColorClass: "text-gray-400", textClass: "text-gray-300" }, // Changed icon from shield
    "healing herb": { icon: "healing", iconColorClass: "text-green-400", textClass: "text-green-300" }, // Adjusted textClass
    "Mana Potion": { icon: "science", iconColorClass: "text-blue-400", textClass: "text-blue-300" },
    "Key": { icon: "vpn_key", iconColorClass: "text-amber-400", textClass: "text-amber-300" }
    // Add more known items
};
const defaultItemDetail = { icon: "inventory_2", iconColorClass: "text-gray-500", textClass: "text-gray-400" }; // Adjusted default colors

eel.expose(update_inventory);
function update_inventory(inventory_list) {
    const inventoryContainer = document.getElementById('playerInventoryContainer');
    if (!inventoryContainer) {
        console.error("Inventory container #playerInventoryContainer not found!");
        return;
    }

    inventoryContainer.innerHTML = ''; // Clear old items

    if (inventory_list && inventory_list.length > 0) {
        inventory_list.forEach(itemName => {
            const details = itemDisplayDetails[itemName] || { ...defaultItemDetail, displayName: itemName };

            const p = document.createElement('p');
            // Base classes from problem description + specific text class
            p.className = `text-lg ${details.textClass} hover:text-amber-300 hover:font-semibold cursor-pointer transition-all duration-200 flex items-center`;
             // TODO: Add onclick handler for items if they become clickable:
            // p.onclick = () => handleItemClick(itemName);

            const iconSpan = document.createElement('span');
            iconSpan.className = `material-icons-round mr-2 ${details.iconColorClass}`;
            iconSpan.textContent = details.icon;

            p.appendChild(iconSpan);
            p.appendChild(document.createTextNode(" " + itemName)); // Using raw itemName, add space
            inventoryContainer.appendChild(p);
        });
    } else {
        const p = document.createElement('p');
        p.className = 'text-lg text-gray-400 italic'; // Consistent empty message style
        p.textContent = 'Your satchel is empty.';
        inventoryContainer.appendChild(p);
    }
}

const skillDisplayDetails = {
    "Meditate": { displayName: "Dhyana (Meditate)", icon: "self_improvement", colorClass: "text-sky-400" },
    "Power Attack": { displayName: "Vajra Strike (Power Attack)", icon: "bolt", colorClass: "text-red-500" }
    // Add other known skills here
};
const defaultSkillDetail = { displayName: "Unknown Skill", icon: "star", colorClass: "text-gray-400" };

eel.expose(update_skills);
function update_skills(skills_list) {
    const skillsContainer = document.getElementById('playerSkillsContainer'); // Ensure this ID exists in main.html
    if (!skillsContainer) {
        console.error("Skill container #playerSkillsContainer not found!");
        return;
    }

    skillsContainer.innerHTML = ''; // Clear old skills

    if (skills_list && skills_list.length > 0) {
        skills_list.forEach(skillName => {
            // Attempt to find specific details, fallback to skillName itself or default for unknown structure
            let details;
            if (typeof skillName === 'string') { // Assuming skills_list is an array of strings
                details = skillDisplayDetails[skillName] || { ...defaultSkillDetail, displayName: skillName };
            } else { // Fallback if skillName is not a string as expected (e.g. an object)
                console.warn("Skill item is not a string, using default display:", skillName);
                details = { ...defaultSkillDetail, displayName: "Invalid Skill Data" };
            }


            const p = document.createElement('p');
            p.className = 'text-lg text-gray-300 hover:text-amber-300 hover:font-semibold cursor-pointer transition-all duration-200 flex items-center';
            // TODO: Add onclick handler for skills if they become clickable:
            // p.onclick = () => handleSkillClick(skillName);

            const iconSpan = document.createElement('span');
            iconSpan.className = `material-icons-round mr-2 ${details.colorClass}`;
            iconSpan.textContent = details.icon;

            p.appendChild(iconSpan);
            p.appendChild(document.createTextNode(" " + details.displayName)); // Added a space for better separation
            skillsContainer.appendChild(p);
        });
    } else {
        const p = document.createElement('p');
        p.className = 'text-lg text-gray-400 italic'; // Consistent with the placeholder in HTML
        p.textContent = 'No divine skills known.';
        skillsContainer.appendChild(p);
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
    console.log("JS DEBUG: sendCommand() function execution started.");
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value.trim();
    if (command) {
        update_narrative(command, 'player_command'); // Display player's command
        try {
            await eel.process_player_command_py(command)(); // Call Python
        } catch (error) {
            console.error("JS: Error calling process_player_command_py:", error);
            update_narrative("Error: Could not send command to Python. " + error);
        }
        commandInput.value = ''; // Clear input field
    }
    console.log("JS DEBUG: sendCommand() function execution finished.");
}

// --- Initialization and Event Listeners ---
document.addEventListener('DOMContentLoaded', (event) => {
    const commandInput = document.getElementById('commandInput');
    if(commandInput) {
        commandInput.addEventListener('keypress', function (e) { // 'e' is the event object
            if (e.key === 'Enter') {
                console.log("JS DEBUG: Enter key pressed in commandInput, attempting to call sendCommand(). Event type: " + e.type);
                e.preventDefault();
                sendCommand();
            }
        });
    }

    const sendCmdButton = document.getElementById('sendCommandButton');
    if (sendCmdButton) {
        sendCmdButton.addEventListener('click', function(event) { // Wrap to access event
            console.log("JS DEBUG: SendCommandButton clicked, attempting to call sendCommand(). Event type: " + event.type);
            sendCommand();
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
