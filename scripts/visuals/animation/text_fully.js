const top_dir_fully = "results/2024_07_13/fully/";

let messagesFully = [];
let textFullyInitialized = false;
let placeFullyMessageRight = true;


let bubbleColorsFully = [
    '#f6e58d',      // Color 1
    '#7ed6df',     // Color 2
    '#e056fd',    // Color 3
    '#686de0',   // Color 4
    '#c7ecee',   // Color 5
    '#95afc0'    // Color 6
];


const filenameFully = top_dir_fully + "post_process/dialogue.txt";
fetch(filenameFully)
    .then(response => response.text())
    .then(contents => {
        const lines = contents.split('\n');

        lines.forEach((line, index) => {
            if (line.trim()) { // skip empty lines
                let agent = line.substring(0, 7); // Or use line.slice(0, 6);
                messagesFully.push({ agent: agent, text: line.trim() });
            }
        });  
    }).then(c => {
        textFullyInitialized = true;
    })
    .catch(error => {
        console.error('Error loading file:', error);
    });

// Define colors for different agents
let colorsFully = [
    'red',      // Color for Agent 0
    'blue',     // Color for Agent 1
    'green',    // Color for Agent 2
    'black'     // Default color for other text
];

function addMessageFully(text, right) {
    var d = $('#chatMessageList');
    let formattedText = text.replace(/(Reasoning)/g, '<span class="highlight_fully">$1</span>');
    formattedText = formattedText.replace(/(Combination)/g, '<span class="highlight_fully">$1</span>');

    if (right)
        d.append("<div class=\"row message-row\" ><div class='col-md-1'></div><div class='col-md-2'></div><div class='col-md-9 chat-message'>" + formattedText + "</div></div>");
    else
        d.append("<div class=\"row message-row\" ><div class='col-md-9 chat-message'>" + formattedText + "</div><div class='col-md-2'></div><div class='col-md-1'></div></div>");
    d.scrollTop(d.prop("scrollHeight"));
}

document.addEventListener('dataUpdateEvent', function(event){
    addMessageFully(messagesFully[event.detail.index].text, placeFullyMessageRight);
    placeFullyMessageRight = !placeFullyMessageRight;
});

