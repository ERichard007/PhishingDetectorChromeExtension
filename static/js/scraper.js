class Scraper {
    constructor() {
        this.email_subject = "";
    }

    /**
    * Private method to extract email subject.
    * @returns {string} The sanitized email subject for use as a filename.
    */
    #get_email_subject() {
        const subject_element = document.querySelector('h2.hP');
        if (subject_element) {
            return subject_element.innerText.replace(/[^a-z0-9 ]/gi, '_');
        }
        return "unknown_subject";
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

    scrape() {
        chrome.runtime.sendMessage({type: "download_email", filename: `${this.#get_email_subject()}.txt`, content: this.#get_email_content()}, (response) => {
            console.log("Succesfully downloaded email", response);
        });
    }
}

let scraper = new Scraper();
scraper.scrape();