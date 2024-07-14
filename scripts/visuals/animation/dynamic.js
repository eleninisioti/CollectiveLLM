const canvas2 = document.getElementById('graphCanvas_dynamic');
const ctx2 = canvas2.getContext('2d');

const centerX2 = canvas2.width / 2;
const centerY2 = canvas2.height / 2;
const radius2 = 200; // Radius of the circle

const numNodes2 = 6;
const nodes2 = [];
for (let i = 0; i < numNodes2; i++) {
    const angle = (i / numNodes2) * 2 * Math.PI;
    const x = centerX2 + radius2 * Math.cos(angle);
    const y = centerY2 + radius2 * Math.sin(angle);
    nodes2.push({ x, y });
}

// Connect nodes in pairs
const initialEdges2 = [
    [nodes2[0], nodes2[1]],
    [nodes2[2], nodes2[3]],
    [nodes2[4], nodes2[5]]
];

let edges2 = [...initialEdges2];
let previousEdges = {}; // Track previous edges for each node

let progress2 = 0;
const totalFrames2 = 1000;
const animationDuration = 3000; // 30 seconds
const colorChangeInterval = 500; // 5 seconds
const silentInterval = 500;

let elapsedTime = 0;
let redNodeIndex = Math.floor(Math.random() * numNodes2);
let timeSinceLastUpdate = 0;
let intervalIndex = 0;

function draw2() {
    ctx2.clearRect(0, 0, canvas2.width, canvas2.height);

    // Draw nodes
    nodes2.forEach((node, index) => {
        ctx2.beginPath();
        ctx2.arc(node.x, node.y, 30, 0, Math.PI * 2);
        ctx2.fillStyle = "##6ab04c";

        // Change color of the node at the current index
        ctx2.fillStyle = (index === redNodeIndex) ? '#badc58' : "#6ab04c";
        ctx2.fill();
    });

    // Draw edges
    edges2.forEach(([start, end]) => {
        ctx2.beginPath();
        ctx2.moveTo(start.x, start.y);
        ctx2.lineTo(end.x, end.y);
        ctx2.stroke();
    });

    // Continue the animation loop
    if (progress2 < edges2.length) {
        progress2 += edges2.length / totalFrames2;
        requestAnimationFrame(draw2);
    }
}

// Function to update the red node
function updateRedNode() {

    // Choose a new random red node
    redNodeIndex = Math.floor(Math.random() * numNodes2);

    const currentRedNode = redNodeIndex;
    const availableNodes = nodes2.filter((_, index) => index !== currentRedNode);

    // Save the previous edges for the red node
    previousEdges[currentRedNode] = edges2.filter(edge => edge.includes(nodes2[currentRedNode]));

    // Remove current edges of the red node
    edges2 = edges2.filter(edge => !edge.includes(nodes2[currentRedNode]));

    // Connect the red node to new random nodes
    const newEdges = [];
    while (newEdges.length < 1) { // Connect to two new nodes
        const newNode = availableNodes[Math.floor(Math.random() * availableNodes.length)];
        if (!newEdges.some(edge => edge.includes(newNode))) {
            newEdges.push([nodes2[currentRedNode], newNode]);
        }
    }
    edges2.push(...newEdges);


}

// Function to restore the previous edges when a node turns black
function restorePreviousEdges() {
    const currentRedNode = redNodeIndex;
    if (previousEdges[currentRedNode]) {
        // Remove new edges associated with the current red node
        edges2 = edges2.filter(edge => !edge.includes(nodes2[currentRedNode]));

        // Restore previous edges
        edges2.push(...previousEdges[currentRedNode]);
        delete previousEdges[currentRedNode];
    }
}

// Main draw loop with red node updates
function mainLoop() {
    draw2();

    elapsedTime += 1000 / totalFrames2;


    if ((elapsedTime >= colorChangeInterval) && (intervalIndex===0) ) {
        // Restore previous edges if node was red
        restorePreviousEdges();
        // Update the red node and edges
        updateRedNode();

        elapsedTime = 0;

        intervalndex = 1;


        // Force a redraw after updating the edges
        requestAnimationFrame(draw2);
    }

    if ((elapsedTime >= colorChangeInterval) && (intervalIndex===1)) {

        elapsedTime = 0;

        intervalIndex = 0;

        requestAnimationFrame(draw2);


    }


    setTimeout(mainLoop, 1000 / totalFrames2);
}

document.addEventListener("DOMContentLoaded", function() {
    // Get the canvas element and its context
    const canvas = document.getElementById('graphCanvas_fully');
    const ctx = canvas.getContext('2d');

    // Draw existing content on the canvas here if needed

    // Define text properties
    ctx.font = '24px Arial'; // Font size and family
    ctx.fillStyle = 'black'; // Text color
    ctx.textAlign = 'left'; // Text alignment
    ctx.textBaseline = 'top'; // Text baseline

    // Define the position of the text
    const x = 10; // X position (from left)
    const y = 10; // Y position (from top)

    // Draw the text
    ctx.fillText('Fully-connected group', x, y);

    // If you need to draw more on the canvas, do it here
});

// Start the animation
mainLoop();
