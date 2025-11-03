// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Styles: you said styles live in src/, so import here.
import "./styles.css";

// Map styles (needs the leaflet package installed)
import "leaflet/dist/leaflet.css";

// Fix default marker icon paths in Leaflet (see file stub below)
import "./leafletIconFix";

document.documentElement.setAttribute('data-theme', 'light')
// later you can toggle: document.documentElement.setAttribute('data-theme','dark')

/** Minimal app-wide error boundary to avoid blank screens in production. */
class RootErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(_error: unknown) {
    // TODO: send to your logger if desired
    // console.error('Root error boundary caught:', _error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <h1>Something went wrong.</h1>
          <p>Please refresh the page. If the issue persists, contact support.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

const rootEl = document.getElementById("root");
if (!rootEl) {
  // Provide a visible failure instead of a blank page
  const msg = "Root element #root not found in index.html";
  console.error(msg);
  document.body.innerHTML = `<pre style="padding:16px;font-family:monospace;color:#b91c1c">${msg}</pre>`;
  throw new Error(msg);
}

const root = ReactDOM.createRoot(rootEl as HTMLElement);

root.render(
  <React.StrictMode>
    <RootErrorBoundary>
      <App />
    </RootErrorBoundary>
  </React.StrictMode>
);

// Optional: clean unmount on HMR updates (Vite)
if ((import.meta as any).hot) {
  (import.meta as any).hot.dispose(() => root.unmount());
}
