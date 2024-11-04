const videoElement = document.createElement('video');
const canvasElement = document.getElementById('gameCanvas');
const canvasCtx = canvasElement.getContext('2d');
const basketElement = document.getElementById('basket');
const scoreDisplay = document.getElementById('score');
const fingerMessage = document.getElementById('fingerMessage');

let balls = []; // Array to hold multiple balls
let score = 0;
const basketBounds = basketElement.getBoundingClientRect();

canvasElement.width = 640;  // Set canvas width
canvasElement.height = 480; // Set canvas height

// Function to detect if the finger touches the wrist
function checkTouch(landmarks, fingerTipIndex, wristIndex) {
    const wrist = landmarks[wristIndex];
    const fingerTip = landmarks[fingerTipIndex];

    // Calculate Euclidean distance
    const distance = Math.sqrt(Math.pow(wrist.x - fingerTip.x, 2) + Math.pow(wrist.y - fingerTip.y, 2));

    // If distance is very small, consider it a touch
    return distance < 0.1; // Increased threshold for touch detection
}

function onResults(results) {
    requestAnimationFrame(() => {
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

        // Reset finger message
        fingerMessage.innerText = "None";

        const bentFingers = []; // Array to keep track of bent fingers

        if (results.multiHandLandmarks) {
            for (const landmarks of results.multiHandLandmarks) {
                drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 5 });
                drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 2 });
