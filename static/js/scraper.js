class Scraper {
    constructor() {
        this.observer = null;
        this.downloaded_emails = new Set();
        this.email_click_listener = this.#on_email_click.bind(this); 
    }

    /**
     * Private method to return a table containing emails to tie click events to.
     * @returns {HTMLTableElement|null} The email table element.
     */
    #get_email_table() {
        const table_element = document.querySelector('table.F.cf.zt'); // gmail email table element
        if (table_element) {
            return table_element;
        }
        return null;
    }

    /**
    * Private method to extract email subject.
    * @returns {string|null} The sanitized email subject for use as a filename.
    */
    #get_email_subject() {
        const subject_element = document.querySelector('h2.hP'); // gmail subject element
        if (subject_element) {
            return subject_element.innerText.replace(/[^a-z0-9]/gi, '_'); // sanitize subject
        }
        return null;
    }

    /**
     * Private method to extract email body content.
     * @returns {string|null} The email body text, or null if not found.
     */
    #get_email_content() {
        const email_body_element = document.querySelector('.a3s');
        if (!email_body_element) return null;

        return email_body_element.innerText;
    }

    /**
     * Private method fired when an email is clicked. It checks if the email content is loaded and then initiates the scraping process.
     */
    #on_email_click() {
        console.log("Email clicked, checking for content...");

        const subject = this.#get_email_subject();
        const bodyEl = document.querySelector('.a3s');

        if (!bodyEl || !subject) { // email is not open or content not loaded yet
            console.log("Timeout: No body or subject found!");
            setTimeout(() => this.#on_email_click(), 100); // retry after delay
            return;
        }

        console.log("Downloading email..."); 
        this.scrape();
    }

    /**
     * Private method fired when this.observer detects changes in the email DOM structure.
     */
    #on_dom_changed() {
        console.log("DOM changed, checking for email content...");

        const email_table = this.#get_email_table();

        try {
            console.log("Email table found, setting up click listener...");
            email_table.removeEventListener('click', this.email_click_listener); // prevent multiple listeners
            email_table.addEventListener('click', this.email_click_listener);
        } catch (error) {
            console.error("Error with on_dom_changed email_table ---> ", error);
        }
    }

    /**
     * Private method to extract all links from the email body. It looks for anchor tags within the email content and returns an array of their href attributes.
     * @return {string[]} An array of links extracted from the email body.
     */
    #get_links_from_email() {
        const body_el = document.querySelector('.a3s');
        if (!body_el) return [];

        const links = body_el.querySelectorAll('a');
        return Array.from(links).map(link => link.href);
    }

    /**
     * Private method to extract text content from the email body.
     * @returns {string}
     */
    #get_text_from_email() {
        const body_el = document.querySelector('.a3s');
        if (!body_el) return "";

        return body_el.innerText;
    }

    /**
     * Public method that creates an observer to watch for changes in email DOM structure. (enables auto scanning)
     */
    email_viewer(enable = true) {

        if (enable) {
            const target = document.querySelector('div[role="main"]'); // Gets container where emails stored

            if (!target) { // timeout if target not found, likely because Gmail is still loading
                console.log("Timeout, no target")
                setTimeout(() => this.email_viewer(), 2000);
                return;
            }

            this.observer = new MutationObserver(() => this.#on_dom_changed()); // Create observer to watch for changes in email DOM structure
            this.observer.observe(target, { childList: true, subtree: true });

            this.#on_dom_changed(); // Initial check in case email content already loaded when observer starts
        }else{
            const email_table = this.#get_email_table();
            
            this.observer.disconnect();
            email_table.removeEventListener('click', this.email_click_listener);
        }
    }

    /**
     * Public method to initiate the scraping process. It sends a message to the background script to download the email content as a text file.
     */
    scrape() {

        const subject = this.#get_email_subject();

        if (!subject) {
            console.error("No subject found, cannot scrape email.");
            return;
        }else if (this.downloaded_emails.has(subject)) {
            console.log("Email already downloaded, skipping...");
            return;
        }

        this.downloaded_emails.add(subject);

        console.log("Preparing to download email with subject:", subject);

        const links = this.#get_links_from_email();
        //console.log("Extracted links from email:", links);

        const text_content = this.#get_text_from_email();
        //console.log("Extracted text content from email:", text_content);

        chrome.runtime.sendMessage({ message: "general_scan", links: links, text: text_content }, (response) => {
            if (response) {
                console.log("Response from background script:", response.message);
            }else{
                console.error("No response from background script.");
            }
        });
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "scan_email") {
        console.log("Received scan_email message, initializing Scraper...");    
        scraper.scrape();
    } else if (request.message === "enable_auto_scan") {
        console.log("Received enable_auto_scan message, initializing Scraper...");
        scraper.email_viewer();
    } else if (request.message === "disable_auto_scan") {
        console.log("Received disable_auto_scan message, disconnecting Scraper observer...");
        scraper.email_viewer(false);
    }
});

const scraper = new Scraper();

chrome.storage.local.get(['autoScanEnabled'], (data) => {
    if (data.autoScanEnabled) {
        console.log("Received enable_auto_scan message, initializing Scraper...");
        scraper.email_viewer();
    }
});
