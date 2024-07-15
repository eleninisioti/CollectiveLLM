const top_dir = "results/2024_07_13/dynamic/";

let messagesDynamic = [];
let textDynamicInitialized = false;
let placeDynamicMessageRight = true;
let textDynamicIndex = 0;


let bubbleColors = [
    '#f6e58d',      // Color 1
    '#7ed6df',     // Color 2
    '#e056fd',    // Color 3
    '#686de0',   // Color 4
    '#c7ecee',   // Color 5
    '#95afc0'    // Color 6
];


const filename = top_dir + "post_process/dialogue.txt";
fetch(filename)
    .then(response => response.text())
    .then(contents => {
        const lines = contents.split('\n');

        lines.forEach((line, index) => {
            if (line.trim()) { // skip empty lines
                let agent = line.substring(0, 7); // Or use line.slice(0, 6);
                messagesDynamic.push({ agent: agent, text: line.trim() });
            }
        });
    }).then(c => {
        textDynamicInitialized = true;
    })
    .catch(error => {
        console.error('Error loading file:', error);
    });


// Define colors for different agents
let colors = [
    'red',      // Color for Agent 0
    'blue',     // Color for Agent 1
    'green',    // Color for Agent 2
    'black'     // Default color for other text
];

function addMessageDynamic(text, right) {
    var d = $('#chatMessageListDynamic');
    let formattedText = text.replace(/(Reasoning)/g, '<span class="highlight_fully">$1</span>');
    formattedText = formattedText.replace(/(Combination)/g, '<span class="highlight_fully">$1</span>');

    if (right)
        d.append("<div class=\"row message-row\" ><div class='col-md-1'></div><div class='col-md-2'></div><div class='col-md-9 chat-message'>" + formattedText + "</div></div>");
    else
        d.append("<div class=\"row message-row\" ><div class='col-md-9 chat-message'>" + formattedText + "</div><div class='col-md-2'></div><div class='col-md-1'></div></div>");
    d.scrollTop(d.prop("scrollHeight"));
}

document.addEventListener('dataUpdateEvent', function(event){
    if(messagesDynamic.length <= textFullyIndex)
        return;
    addMessageDynamic(messagesDynamic[textDynamicIndex].text, placeDynamicMessageRight);
    placeDynamicMessageRight = !placeDynamicMessageRight;
    textDynamicIndex += 1;
});
