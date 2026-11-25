import React from 'react';
import ReactDOM from 'react-dom/client';
import '@fontsource-variable/public-sans';
import '@fontsource-variable/source-serif-4';
import { App } from './App';
import './index.css';

// Popover nativo: solo se carga el polyfill donde falta soporte
if (!('popover' in HTMLElement.prototype)) {
  import('@oddbird/popover-polyfill');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
