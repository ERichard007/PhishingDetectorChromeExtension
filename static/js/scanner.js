chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "virus_total_scan") {
        console.log("Received virus_total_scan message, scanning email with VirusTotal..."); 
        
        const links = request.links;

        

        sendResponse({ message: "virus total scan started" }); // Send response back to background script to indicate scan has started
    }
});