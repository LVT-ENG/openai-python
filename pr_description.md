🔒 Fix DOM-Based XSS via innerHTML

🎯 **What:** The vulnerability fixed is a DOM-Based XSS in `tryonyou-app/src/services/CommerceEngine.js` caused by using `innerHTML` to create a checkout overlay.
⚠️ **Risk:** The use of `innerHTML` can potentially allow attackers to inject malicious scripts into the application if dynamic user data is ever incorporated, putting the codebase and its users at risk.
🛡️ **Solution:** The fix eliminates the vulnerability by replacing `innerHTML` with safe DOM manipulation methods such as `document.createElement`, `style.cssText` and `textContent`.
