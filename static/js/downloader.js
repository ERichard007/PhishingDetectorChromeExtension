chrome.runtime.onMessage.addListener((message) => {
    if (message.type == 'download_email') {

        const blob = new Blob([message.content], {type: 'text/plain'});
        const url = "data:text/plain;charset=utf-8," + encodeURIComponent(message.content);

        chrome.downloads.download({
            url: url,
            filename: "scraped/" + message.filename,
            saveAs: false
        });
    }
});