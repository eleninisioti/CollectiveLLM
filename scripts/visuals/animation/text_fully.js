const top_dir_fully = "results/2024_07_13/fully/";

let messagesFully = [];
let textFullyInitialized = false;
let placeFullyMessageRight = true;
let textFullyIndex = 0;


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
                let text = line.substring(9).trim(); // Or use line.slice(5).trim();
                messagesFully.push({ agent: agent, text: text.trim() });
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
    '#34ace0',      // Color 1
    '#33d9b2',     // Color 2
    '#ffb142',    // Color 3
    '#ff5252',   // Color 4
    '#706fd3',   // Color 5
    '#ffda79'
];

function addMessageFully(text, right, index) {
    var d = $('#chatMessageList');
    let formattedText = text.replace(/(Reasoning)/g, '<span class="highlight_fully">$1</span>');
    formattedText = formattedText.replace(/(Combination)/g, '<span class="highlight_fully">$1</span>');

    let colorCurrent = colorsFully[index%6];

    if (right)
        d.append("<div class=\"row message-row\"  ><div class='col-md-1'></div><div class='col-md-2'></div><div class='col-md-9 chat-message' style=\"background-color: " + colorCurrent + ";\">" + formattedText + "</div></div>");
    else
        d.append("<div class=\"row message-row\" ><div class='col-md-9 chat-message' style=\"background-color: " + colorCurrent + ";\">" + formattedText + "</div><div class='col-md-2' ></div><div class='col-md-1'></div></div>");
    d.scrollTop(d.prop("scrollHeight"));
}

document.addEventListener('dataUpdateEvent', function(event){
    if(messagesFully.length <= textFullyIndex)
        return;
    addMessageFully(messagesFully[textFullyIndex].text, placeFullyMessageRight, textFullyIndex);
    placeFullyMessageRight = !placeFullyMessageRight;
    textFullyIndex += 1;
});

