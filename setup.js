// Load webhook URL on page load
document.addEventListener('DOMContentLoaded', function() {
  chrome.storage.local.get(['webhook_url'], function(result) {
    if (result.webhook_url) {
      document.getElementById('webhook').value = result.webhook_url;
    }
  });
});

function saveWebhook() {
  var webhookUrl = document.getElementById('webhook').value.trim();
  var statusEl = document.getElementById('status');

  if (!webhookUrl) {
    statusEl.textContent = 'Webhook URL is required';
    statusEl.className = 'status error';
    return;
  }

  if (!webhookUrl.startsWith('https://')) {
    statusEl.textContent = 'Invalid URL format';
    statusEl.className = 'status error';
    return;
  }

  chrome.storage.local.set({ webhook_url: webhookUrl }, function() {
    statusEl.textContent = 'Webhook URL saved successfully!';
    statusEl.className = 'status success';

    // Hide status after 3 seconds
    setTimeout(function() {
      statusEl.className = 'status';
    }, 3000);
  });
}
