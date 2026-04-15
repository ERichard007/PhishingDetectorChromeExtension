class Scanner {
    constructor() {}

    /** 
    * Public method to perform a virus total scan
    * @param {string[]} links - An array of links extracted from the email body to be scanned.
    */
    virus_total_scan(links) {
        console.log("Given Links: ", links);
    }

    /**
     * Public method to perform a general scan of the email content.
     * @param {string[]} links - An array of links extracted from the email body to be scanned.
     * @param {string} text_content - The text content of the email to be scanned.
     */
    general_scan(links, text_content) {
        //console.log("Given Links: ", links);

        fetch('http://localhost:8080/scan', {
            method: 'POST',
            headers: { 
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "chrome-extension://ljcakhhgcailjgbfdejngbplmbidelfh"
            },
            body: JSON.stringify({ links: links, text: text_content })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Scan Results: ", data);
        })
        .catch(error => {
            console.error("Error occurred during general scan fetch: ", error);
        });
    }

}


chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "general_scan") {
        console.log("Received general_scan message, scanning email..."); 

        const links = request.links;
        const text_content = request.text;
        const scanner = new Scanner();

        scanner.general_scan(links, text_content);

        sendResponse({ message: "general scan started" }); // Send response back to background script to indicate scan has started
    }
});