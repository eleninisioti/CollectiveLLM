// Define messages

const top_dir = "../../../results/2024_07_13/num_trials_3_num_tasks_1_num_steps_200_openended_True_encoded_False_num_distractors_6_depth_1_agent_type_llama3_forbid_repeats_False_retry_6_temperature_1_top_p_0.9_num_agents_6_connectivity_fully-connected_visit_duration_5_visit_prob_0.1_70B/";

let messages = [];


let bubbleColors = [
    '#f6e58d',      // Color 1
    '#7ed6df',     // Color 2
    '#e056fd',    // Color 3
    '#686de0',   // Color 4
    '#c7ecee',   // Color 5
    '#95afc0'    // Color 6
];


const filename = top_dir + "/post_process/dialogue.txt";
fetch(filename)
.then(response => response.text())
.then(contents => {
    const lines = contents.split('\n');

    lines.forEach((line, index) => {
        if (line.trim()) { // skip empty lines
            let agent = line.substring(0, 7); // Or use line.slice(0, 6);
            messages.push({agent: agent, text: line.trim()});
        }
    });
}).then(whatever => {
let right = true;

for (let i = 0; i < messages.length; i++) {
    setTimeout(function () {
        addMessage(messages[i].text, right);
        right = !right;
    }, i * 2000 + 2000*(i>0));
}
})
.catch(error => {
    console.error('Error loading file:', error);
});



//messages = reorderMessages(messages);






// Define colors for different agents
let colors = [
    'red',      // Color for Agent 0
    'blue',     // Color for Agent 1
    'green',    // Color for Agent 2
    'black'     // Default color for other text
];

// Bubble properties
const bubblePadding = 10;
const bubbleRadius = 10;
const bubbleWidth = 250;
const bubbleHeight = 50;
const bubbleMargin = 50;
const agentLabelMargin = 5; // Margin for agent label
const maxMessages = 5; // Maximum number of messages to display at once

function drawBubble(ctx, x, y, width, height, isLeft) {
    ctx.fillStyle = 'white';
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (isLeft) {
        ctx.moveTo(x + bubbleRadius, y);
        ctx.lineTo(x + width - bubbleRadius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + bubbleRadius);
        ctx.lineTo(x + width, y + height - bubbleRadius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - bubbleRadius, y + height);
        ctx.lineTo(x + bubbleRadius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - bubbleRadius);
        ctx.lineTo(x, y + bubbleRadius);
        ctx.quadraticCurveTo(x, y, x + bubbleRadius, y);
    } else {
        ctx.moveTo(x + bubbleRadius, y);
        ctx.lineTo(x + width - bubbleRadius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + bubbleRadius);
        ctx.lineTo(x + width, y + height - bubbleRadius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - bubbleRadius, y + height);
        ctx.lineTo(x + bubbleRadius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - bubbleRadius);
        ctx.lineTo(x, y + bubbleRadius);
        ctx.quadraticCurveTo(x, y, x + bubbleRadius, y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
}

function addMessage(text, right) {
    var d = $('#chatMessageList');
    const chatMessageList = document.getElementById('');

    let formattedText = text.replace(/(Reasoning)/g, '<span class="highlight_fully">$1</span>');
    formattedText = formattedText.replace(/(Combination)/g, '<span class="highlight_fully">$1</span>');

    if (right)
        d.append("<div class=\"row full-width\" ><div class='col-md-4'></div><div class='col-md-3'></div><div class='col-md-4 chat-message'>" + formattedText + "</div></div>");
    else
        d.append("<div class=\"row full-width\" ><div class='col-md-4 chat-message'>" +  formattedText  + "</div><div class='col-md-3'></div><div class='col-md-4'></div></div>");
    d.scrollTop(d.prop("scrollHeight"));
}

/*
$(document).ready(function () {
    console.log("document ready");
    let right = true;

    for (let i = 0; i < messages.length; i++) {
        setTimeout(function () {
            addMessage(messages[i].text, right);
            right = !right;
        }, i * 1000 + 1000);
    }

});
*/
// Initial draw on both text canvases
//drawMessages(ctxText1, canvasText1);
