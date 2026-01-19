/*  
===========================================================
  ACCESSIBILITY FEATURES FOR HANDICAPPED USERS (ALL-IN-ONE)
  Works for: Blind, Deaf, Dumb, Low Vision, Motor Impaired
  Creator: ElectroMart Accessibility System
===========================================================
*/

// ================================
// 1. TEXT-TO-SPEECH (FOR BLIND)
// ================================
function speakText(text) {
    let speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;
    window.speechSynthesis.speak(speech);
}

// Read whole page
function readPage() {
    speakText(document.body.innerText);
}

// Stop speech
function stopSpeak() {
    window.speechSynthesis.cancel();
}



// ================================
// 2. FONT SIZE CONTROL (LOW VISION)
// ================================
let fontSize = 16;

function changeFontSize(action) {
    if (action === "increase") fontSize += 5;
    if (action === "decrease") fontSize -= 5;
    if (action === "reset") fontSize = 16;

    document.body.style.fontSize = fontSize + "px";
}



// ================================
// 3. HIGH CONTRAST MODE (COLOR BLIND)
// ================================
let highContrast = false;

function toggleHighContrast() {
    highContrast = !highContrast;

    if (highContrast) {
        document.body.style.background = "black";
        document.body.style.color = "blue";
    } else {
        document.body.style.background = "";
        document.body.style.color = "";
    }
}
// ================================
// 4. VOICE COMMANDS (FOR BLIND & MOTOR IMPAIRED)
// ================================
let recognition;

function startVoiceCommands() {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        alert("Your browser does not support Voice Recognition.");
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = function (event) {
        const command = event.results[0][0].transcript.toLowerCase();
        console.log("Voice Command:", command);
        
        function focusSearchBarUniversal() {
    // Find ANY search box on ANY webpage
    let searchBar = 
        document.querySelector("input[type='search'], input[type='text'][placeholder*='search' i], input[type='text'][name*='search' i], input[type='text'][id*='search' i], input[type='text'][class*='search' i], input[placeholder*='find' i], input[placeholder*='lookup' i]");

    if (searchBar) {
        console.log("Search bar found:", searchBar);
        searchBar.scrollIntoView({ behavior: "smooth", block: "center" });
        setTimeout(() => searchBar.focus(), 300);
    } else {
        alert("No search bar found on this page.");
    }
}


if (command.includes("search")) {
    focusSearchBarUniversal();
}
      if (command.includes("go to homepage")) window.location.href = FLASK_URLS.home;
      if (command.includes("go to product page")) window.location.href = FLASK_URLS.product;
      if (command.includes("go to login page")) window.location.href = FLASK_URLS.signup;
      if (command.includes("go to admin page")) window.location.href = FLASK_URLS.admin;
      if (command.includes("go to cartpage")) window.location.href = FLASK_URLS.cart;
      if (command.includes("go to checkout page")) window.location.href = FLASK_URLS.checkout;
      if (command.includes("order")) window.location.href = FLASK_URLS.order;
      if (command.includes("track the order")) window.location.href = FLASK_URLS.track;
      if (command.includes("go to mobile page")) window.location.href = FLASK_URLS.mobile;
      if (command.includes("go to laptop page")) window.location.href = FLASK_URLS.laptop;
      if (command.includes("go to watch page")) window.location.href = FLASK_URLS.watch;
      if (command.includes("go to earbuds page")) window.location.href = FLASK_URLS.earbuds;
      if (command.includes("go to speaker page")) window.location.href = FLASK_URLS.speaker;
      if (command.includes("read the page")) readPage();
      if (command.includes("stop the reading")) stopSpeak();
      if (command.includes("increase font size")) changeFontSize("increase");
      if (command.includes("decrease font size")) changeFontSize("decrease");
      if (command.includes("reset font size")) changeFontSize("reset");
      if (command.includes("enable dark mode")) toggleHighContrast();
      if (command.includes("disable dark mode")) toggleHighContrast();
      if (command.includes("show sign language")) showSignLanguageHelp();
      if( command.includes("scroll down")) window.scrollBy(0, window.innerHeight);
      if( command.includes("scroll up")) window.scrollBy(0, -window.innerHeight);
      if (command.includes("vibrate")) vibrate();
      if (command.includes("stop listening")) stopVoiceCommands();
    };
}

function stopVoiceCommands() {
    if (recognition) recognition.stop();
}



// ================================
// 5. SIGN LANGUAGE HELP (FOR DEAF USERS)
// ================================
function showSignLanguageHelp() {
    alert("📘 Sign Language Mode:\n\n• search = click I button in keyboard for search products\n• product page = click P button in keyboard for product page\n• login/signup = click S button in keyboard for login/signup\n• admin = click A button in keyboard for admin page\n• Add to Cart = click C button in keyboard for cart\n• Checkout = click D button in keyboard for checkout \n• order = click O button in keyboard for order\n• Track your order = click T button in keyboard for track order\n\n(This is a simple explainer for deaf users.)");
}



// ================================
// 6. KEYBOARD SHORTCUTS (MOTOR IMPAIRED)
// ================================
document.addEventListener("keydown", function (e) {
    if (e.altKey && e.key === "i") document.querySelector("input[type='search']").focus();
    if (e.altKey && e.key === "h") window.location.href = FLASK_URLS.home;
    if (e.altKey && e.key === "p") window.location.href = FLASK_URLS.product;
    if (e.altKey && e.key === "s") window.location.href = FLASK_URLS.signup;
    if (e.altKey && e.key === "a") window.location.href = FLASK_URLS.admin;
    if (e.altKey && e.key === "c") window.location.href = FLASK_URLS.cart;
    if (e.altKey && e.key === "m") window.location.href = FLASK_URLS.mobile;
    if (e.altKey && e.key === "l") window.location.href = FLASK_URLS.laptop;
    if (e.altKey && e.key === "w") window.location.href = FLASK_URLS.watch;
    if (e.altKey && e.key === "e") window.location.href = FLASK_URLS.earbuds;
    if (e.altKey && e.key === "v") window.location.href = FLASK_URLS.speaker;
    if (e.altKey && e.key === "d") window.location.href = FLASK_URLS.checkout;
    if (e.altKey && e.key === "o") window.location.href = FLASK_URLS.order;
    if (e.altKey && e.key === "t") window.location.href = FLASK_URLS.track;
    if (e.altKey && e.key === "r") readPage();
    if (e.altKey && e.key === "x") stopSpeak();
    if (e.altKey && e.key === "+") changeFontSize("increase");
    if (e.altKey && e.key === "-") changeFontSize("decrease");
    if (e.altKey && e.key === "0") changeFontSize("reset");
    if (e.altKey && e.key === "z") startVoiceCommands();
    if (e.altKey && e.key === "q") stopVoiceCommands();
    if (e.altKey && e.key === "k") toggleHighContrast();
    if (e.altKey && e.key === "g") showSignLanguageHelp();
    if (e.altKey && e.key === "b") vibrate();
});
// ================================
// 7. VIBRATION FEEDBACK (MOBILE USERS)
// ================================
function vibrate() {
    if ("vibrate" in navigator) {
        navigator.vibrate(100);
    }
}


