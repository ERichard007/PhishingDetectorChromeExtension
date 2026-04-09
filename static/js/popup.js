

console.log("Content script loaded, setting up event listeners...");    

const scanBtn = document.getElementById('scan_btn');
const autoScanToggle = document.getElementById('auto_scanning_toggle');

chrome.storage.local.get(['autoScanEnabled'], (data) => {
    autoScanToggle.checked = data.autoScanEnabled || false;
});


scanBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { message: "scan_email" });
    });
});

autoScanToggle.addEventListener('change', (event) => {
    chrome.storage.local.set( { autoScanEnabled: event.target.checked } );

    if (event.target.checked) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, { message: "enable_auto_scan" });
        });
    } else {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, { message: "disable_auto_scan" });
        });
    }
});
