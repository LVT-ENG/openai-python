import { api } from '../utils/api.js';

export class CommerceEngine {
  constructor() {
    this.initialized = true;
  }

  processCheckout() {
    // Check if confirm is enabled
    // line 10
    const isConfirmEnabled = import.meta.env.VITE_CHECKOUT_CONFIRM === 'TRUE';
    if (!isConfirmEnabled) return;

    const overlay = document.createElement('div');
    overlay.id = 'divineo-overlay';

    const overlayContainer = document.createElement('div');
    overlayContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 9999; border: 2px solid #D4AF37;';

    const overlayHeading = document.createElement('h2');
    overlayHeading.style.cssText = 'color: #D4AF37; font-family: serif; letter-spacing: 0.5em; text-transform: uppercase;';
    overlayHeading.textContent = 'AJUSTE PERFECTO. COMPRANDO...';

    overlayContainer.appendChild(overlayHeading);
    overlay.appendChild(overlayContainer);

    document.body.appendChild(overlay);
  }
}
