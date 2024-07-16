const top_dir = "results/2024_07_13/dynamic/";

let messagesDynamic = [];
let textDynamicInitialized = false;
let placeDynamicMessageRight = true;
let textDynamicIndex = 0;


let colorsDynamic = [
    '#34ace0',      // Color 1
    '#33d9b2',     // Color 2
    '#ffb142',    // Color 3
    '#ff5252',   // Color 4
    '#706fd3',   // Color 5
    '#ffda79'
];

const filename = top_dir + "post_process/dialogue.txt";
fetch(filename)
    .then(response => response.text())
    .then(contents => {
        const lines = contents.split('\n');

        lines.forEach((line, index) => {
            if (line.trim()) { // skip empty lines
                let agent = line.substring(0, 7); // Or use line.slice(0, 6);
                let text = line.substring(9).trim(); // Or use line.slice(5).trim();
                messagesDynamic.push({ agent: agent, text: text.trim() });
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

function addMessageDynamic(text, right, index) {
    var d = $('#chatMessageListDynamic');
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
    if(messagesDynamic.length <= textFullyIndex)
        return;
    addMessageDynamic(messagesDynamic[textDynamicIndex].text, placeDynamicMessageRight,textDynamicIndex);
    placeDynamicMessageRight = !placeDynamicMessageRight;
    textDynamicIndex += 1;
});
