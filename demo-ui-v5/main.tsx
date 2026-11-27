// Renders the unchanged Track Mesh desktop source; only '@tauri-apps/api/core' is replaced by mock-core.ts.
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '@trackmesh/App';
import '@trackmesh/styles.css';

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
