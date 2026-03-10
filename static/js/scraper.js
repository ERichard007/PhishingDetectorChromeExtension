class Scraper {
    constructor() {
        this.email_subject = "";
        this.observer = null;
        this.current_subject = "";

        this.downloaded_emails = new Set();

        this.#email_viewer();
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
     * Private method fired when this.observer
     */
    #on_dom_changed() {
        console.log("DOM changed, checking for email content...");

        const subject = this.#get_email_subject();
        const bodyEl = document.querySelector('.a3s');

        if (!bodyEl || !subject) return;

        bodyEl.setAttribute("tabindex", bodyEl.getAttribute("tabindex") || "0");

        if (subject !== this.current_subject) {
            this.current_subject = subject;
            console.log("new email SUBJECT! ", this.current_subject);
            bodyEl.dataset.scraped = "false";
        }

        if (bodyEl.dataset.scraped === "false") {
            bodyEl.dataset.scraped = "true";

            console.log("Email content found, setting up download trigger...");

            const download = () => { console.log("Downloading email..."); this.scrape(); };

            bodyEl.addEventListener('focus', download, { once: true });
            bodyEl.addEventListener('click', download, { once: true });
        }
    }

    /**
     * Private method that creates an observer to watch for changes in email DOM structure.
     */
    #email_viewer() {
        const target = document.querySelector('div[role="main"]');

        if (!target) {
            setTimeout(() => this.#email_viewer(), 1000);
            return;
        }

        this.observer = new MutationObserver(() => this.#on_dom_changed());
        this.observer.observe(target, { childList: true, subtree: true });

        this.#on_dom_changed();
    }

    /**
     * Public method to initiate the scraping process. It sends a message to the background script to download the email content as a text file.
     */
    scrape() {

        if (this.downloaded_emails.has(this.current_subject)) {
            console.log("Email already downloaded, skipping...");
            return;
        }

        this.downloaded_emails.add(this.current_subject);

        console.log("Preparing to download email with subject:", this.current_subject);
        
        chrome.runtime.sendMessage({type: "download_email", filename: `${this.#get_email_subject()}.txt`, content: this.#get_email_content()}, (response) => {
            console.log("Succesfully downloaded email", response);
        });
    }
}

let scraper = new Scraper();