const canvas1 = document.getElementById('graphCanvas_fully');
const ctx1 = canvas1.getContext('2d');

const centerX1 = canvas1.width / 2;
const centerY1 = canvas1.height / 2;
const radius1 = 120; // Radius of the circle

const numNodes1 = 6;
const nodes1 = [];
for (let i = 0; i < numNodes1; i++) {
    const angle = (i / numNodes1) * 2 * Math.PI;
    const x = centerX1 + radius1 * Math.cos(angle);
    const y = centerY1 + radius1 * Math.sin(angle);
    nodes1.push({ x, y });
}

const edges1 = [];
for (let i = 0; i < nodes1.length; i++) {
    for (let j = i + 1; j < nodes1.length; j++) {
        edges1.push([nodes1[i], nodes1[j]]);
    }
}

let progress1 = 0;
const totalFrames1 = 100;
function draw1() {
    ctx1.clearRect(0, 0, canvas1.width, canvas1.height);

    // Draw nodes
    nodes1.forEach(node => {
        ctx1.beginPath();
        ctx1.arc(node.x, node.y, 25, 0, Math.PI * 2);
        ctx1.fillStyle = "#ff7979"; // Set fill color to blue
        ctx1.fill();
    });

    // Draw edges
    for (let i = 0; i < Math.min(edges1.length, Math.floor(progress1)); i++) {
        const [start, end] = edges1[i];
        ctx1.beginPath();
        ctx1.moveTo(start.x, start.y);
        ctx1.lineTo(end.x, end.y);
        ctx1.stroke();
    }

    if (progress1 < edges1.length) {
        progress1 += edges1.length / totalFrames1;
        requestAnimationFrame(draw1);
    }
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

// Initial draw
draw1();
