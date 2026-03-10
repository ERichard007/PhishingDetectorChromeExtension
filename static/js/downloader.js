chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'download_email') {

        const blob = new Blob([message.content], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        chrome.downloads.download({
            url: url,
            filename: "scraped/" + message.filename,
            saveAs: false
        }, (downloadId) => {
            if (chrome.runtime.lastError) {
                console.error("Download failed:", chrome.runtime.lastError);
                sendResponse({ status: "error", error: chrome.runtime.lastError.message });
            } else {
                sendResponse({ status: "success", downloadId });
            }
        });

        return true;
    }
});