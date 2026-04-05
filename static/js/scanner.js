class Scanner {
    constructor() {}

    /**
     * Helper method to apply heuristics to given links and keep only most suspicious for scanning.
     * @param {string[]} links - An array of links extracted from the email body.
     * @return {string[]} An array of links that are deemed most suspicious based on heuristics.
     */
    #url_links_heuristic(links) {
        
    }

    /** 
    * Public method to perform a virus total scan
    * @param {string[]} links - An array of links extracted from the email body to be scanned.
    */
    virus_total_scan(links) {
        console.log("Given Links: ", links);
        
        new_list = this.#url_links_heuristic(links);
    }

}


chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "virus_total_scan") {
        console.log("Received virus_total_scan message, scanning email with VirusTotal..."); 

        const links = request.links;
        const scanner = new Scanner();

        //scanner.virus_total_scan(links);

        sendResponse({ message: "virus total scan started" }); // Send response back to background script to indicate scan has started
    }
});