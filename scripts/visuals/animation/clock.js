


function startClock(){
    const interval = 1000; // Time interval for each update (ms)
    const clockDivider = 6;
    let count = 0;
    const intervalId = setInterval(() => {
        let dataUpdateEvent = new CustomEvent('dataUpdateEvent');
        document.dispatchEvent(dataUpdateEvent);
        if(count == clockDivider){
            let plotUpdateEvent = new CustomEvent('plotUpdateEvent');
            document.dispatchEvent(plotUpdateEvent);
        }
        count++;
    }, interval);
}

$(document).ready(function(){
    const interval = setInterval(() => {
        if (textFullyInitialized && textDynamicInitialized && linePlotInitialized) {
            clearInterval(interval);
            // Gradually update chart with both datasets
            startClock();
        }
    }, 10);
});