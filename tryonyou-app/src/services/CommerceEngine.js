export function showConfirmOverlay() {
  const isConfirmEnabled = import.meta.env.VITE_CHECKOUT_CONFIRM === 'TRUE';
  if (!isConfirmEnabled) return;

  const overlay = document.createElement('div');
  overlay.id = 'divineo-overlay';

  const container = document.createElement('div');
  container.style.cssText = 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 9999; border: 2px solid #D4AF37;';

  const heading = document.createElement('h2');
  heading.style.cssText = 'color: #D4AF37; font-family: serif; letter-spacing: 0.5em; text-transform: uppercase;';
  heading.textContent = 'AJUSTE PERFECTO. COMPRANDO...';

  container.appendChild(heading);
  overlay.appendChild(container);
}
