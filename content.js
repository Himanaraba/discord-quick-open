// Content script - runs on Discord page
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "sendToChat") {
    var data = request.data;

    // Find the message input area
    var textarea = document.querySelector('[role="textbox"]');

    if (!textarea) {
      sendResponse({ success: false, error: "Chat input not found" });
      return;
    }

    try {
      // Focus the textarea
      textarea.focus();

      // Set the value
      textarea.innerHTML = data;

      // Trigger input event to notify Discord
      var inputEvent = new Event('input', { bubbles: true });
      textarea.dispatchEvent(inputEvent);

      // Find and click send button
      var sendButton = document.querySelector('[aria-label="Send a message"]');
      if (sendButton) {
        setTimeout(function() {
          sendButton.click();
          sendResponse({ success: true });
        }, 100);
      } else {
        sendResponse({ success: false, error: "Send button not found" });
      }
    } catch (err) {
      sendResponse({ success: false, error: err.message });
    }
  }
});
