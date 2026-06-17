document.getElementById("btn").addEventListener("click", function() {
  console.log("Button clicked");

  // Send message to background script
  chrome.runtime.sendMessage({ action: "extract" }, function(response) {
    console.log("Background response:", response);

    if (chrome.runtime.lastError) {
      console.error("Error:", chrome.runtime.lastError);
      alert("Error: " + chrome.runtime.lastError.message);
    } else {
      alert("実行中...");
      setTimeout(function() {
        window.close();
      }, 1000);
    }
  });
});
