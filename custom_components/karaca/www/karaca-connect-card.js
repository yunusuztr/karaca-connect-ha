/**
 * Karaca Connect Lovelace Card
 * Functional layer: Antigravity
 * Visual system and integration hardening: Codex
 */

const KARACA_CARD_VERSION = "1.0.7";
const HOLD_DURATION_MS = 900;
const ACTION_TIMEOUT_MS = 10000;
const TEA_FRESHNESS_DURATION_SECONDS = 60 * 60;
const TEA_BREWING_DURATION_SECONDS = 15 * 60;
const FILTER_COFFEE_BREWING_DURATION_SECONDS = 2 * 60;
const FILTER_COFFEE_FRESHNESS_DURATION_SECONDS = 40 * 60;
const BREWING_OVERTIME_WINDOW_SECONDS = 60;
const RING_CIRCUMFERENCE = 590.62;

const MODE_CONFIGS = [
  {
    id: 13,
    label: "Mama Suyu",
    icon: "mdi:baby-bottle",
    targetTemperature: 40,
  },
  {
    id: 2,
    label: "Filtre Kahve",
    icon: "mdi:coffee-maker",
    targetTemperature: 90,
  },
  {
    id: 6,
    label: "Su Kaynatma",
    icon: "mdi:kettle-steam",
    targetTemperature: 100,
  },
  { id: 9, label: "Çay Demleme", icon: "mdi:tea", targetTemperature: 90 },
];

const SETTING_CONFIGS = [
  {
    id: 1,
    label: "Çay Demleme",
    description: "Çay hazır olduğunda bildir",
    icon: "mdi:bell-ring-outline",
  },
  {
    id: 2,
    label: "Filtre Kahve",
    description: "Kahve hazır olduğunda bildir",
    icon: "mdi:bell-ring-outline",
  },
  {
    id: 3,
    label: "Tazelik",
    description: "Tazelik süresi değiştiğinde bildir",
    icon: "mdi:timer-outline",
  },
  {
    id: 4,
    label: "Kapanma",
    description: "Cihaz kapandığında bildir",
    icon: "mdi:power",
  },
  {
    id: 5,
    label: "Su Kalmadı",
    description: "Su haznesi uyarılarını bildir",
    icon: "mdi:water-alert-outline",
  },
  {
    id: 6,
    label: "Anımsatıcılar",
    description: "Cihaz anımsatıcılarını kullan",
    icon: "mdi:bell-cog-outline",
  },
  {
    id: 7,
    label: "Konuşma Sesi",
    description: "Cihazın sesli bildirimlerini kullan",
    icon: "mdi:volume-high",
  },
  {
    id: 8,
    label: "Temizlik",
    description: "Temizlik gerektiğinde bildir",
    icon: "mdi:spray-bottle",
  },
];

const CARD_STYLES = `
  :host {
    display: block;
    min-width: 0;
    --karaca-accent: #55d6c8;
    --karaca-accent-rgb: 85, 214, 200;
    --karaca-surface: #151a21;
    --karaca-surface-raised: #1b222b;
    --karaca-line: rgba(255, 255, 255, 0.11);
    --karaca-text: #f4f7fa;
    --karaca-muted: #9ba7b4;
    --karaca-success: #65d89a;
    --karaca-warning: #e5a84d;
    --karaca-danger: #ee625c;
    font-family: var(--primary-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
  }

  * {
    box-sizing: border-box;
    letter-spacing: 0;
  }

  button,
  input,
  select {
    font: inherit;
  }

  ha-card {
    position: relative;
    isolation: isolate;
    display: block;
    width: 100%;
    min-width: 0;
    overflow: hidden;
    border: 1px solid var(--karaca-line);
    border-radius: var(--ha-card-border-radius, 8px);
    color: var(--karaca-text);
    background:
      radial-gradient(circle at 50% 25%, rgba(var(--karaca-accent-rgb), 0.09), transparent 37%),
      var(--karaca-surface);
    box-shadow: var(--ha-card-box-shadow, 0 20px 55px rgba(0, 0, 0, 0.38));
  }

  ha-card::before {
    position: absolute;
    inset: 0;
    z-index: -1;
    content: "";
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.045), transparent 36%);
    pointer-events: none;
  }

  .card-header {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) 42px;
    align-items: center;
    min-height: 72px;
    padding: 14px 16px 8px;
  }

  .device-mark,
  .icon-button {
    position: relative;
    display: grid;
    width: 42px;
    height: 42px;
    place-items: center;
    border-radius: 8px;
    line-height: 0;
  }

  .device-mark {
    width: 38px;
    height: 38px;
    border: 1px solid rgba(var(--karaca-accent-rgb), 0.3);
    border-radius: 50%;
    color: var(--karaca-accent);
    background: rgba(var(--karaca-accent-rgb), 0.09);
  }

  .device-mark ha-icon,
  .icon-button ha-icon,
  .mode-icon ha-icon,
  .setting-icon ha-icon {
    display: block;
    width: 20px;
    height: 20px;
    margin: 0;
    line-height: 0;
    vertical-align: middle;
    --mdc-icon-size: 20px;
  }

  .device-mark ha-icon,
  .icon-button ha-icon {
    position: absolute;
    inset: 50% auto auto 50%;
    transform: translate(-50%, -50%);
  }

  .heading {
    min-width: 0;
    padding: 0 10px;
    text-align: center;
  }

  .heading h1 {
    margin: 0;
    overflow: hidden;
    font-size: 21px;
    font-weight: 760;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .heading p {
    margin: 3px 0 0;
    color: var(--karaca-muted);
    font-size: 12px;
  }

  .icon-button {
    padding: 0;
    border: 1px solid var(--karaca-line);
    color: var(--karaca-muted);
    background: var(--karaca-surface-raised);
    cursor: pointer;
    transition: color 160ms ease, background 160ms ease, border-color 160ms ease;
  }

  .icon-button:hover,
  .icon-button:focus-visible {
    border-color: rgba(var(--karaca-accent-rgb), 0.45);
    color: var(--karaca-accent);
    outline: none;
  }

  .status-zone {
    display: grid;
    place-items: center;
    padding: 8px 18px 22px;
  }

  .status-ring {
    position: relative;
    display: grid;
    width: min(62vw, 250px);
    max-width: 250px;
    aspect-ratio: 1;
    place-items: center;
  }

  .ring-svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
    transform: rotate(-90deg);
  }

  .ring-track,
  .ring-progress,
  .ring-tracer {
    fill: none;
    stroke-width: 7;
  }

  .ring-track {
    stroke: rgba(255, 255, 255, 0.075);
  }

  .ring-progress {
    stroke: var(--karaca-accent);
    stroke-linecap: round;
    stroke-dasharray: ${RING_CIRCUMFERENCE};
    stroke-dashoffset: var(--ring-offset, ${RING_CIRCUMFERENCE});
    filter: drop-shadow(0 0 8px rgba(var(--karaca-accent-rgb), 0.75));
    transition: stroke-dashoffset 500ms ease, stroke 250ms ease;
  }

  .ring-tracer {
    stroke: var(--karaca-accent);
    stroke-linecap: round;
    stroke-dasharray: 105 485;
    filter: drop-shadow(0 0 8px rgba(var(--karaca-accent-rgb), 0.78));
    transform-box: fill-box;
    transform-origin: center;
    will-change: transform;
    animation: karaca-ring-spin 2.3s linear infinite;
  }

  .ring-core {
    position: relative;
    display: grid;
    width: 76%;
    aspect-ratio: 1;
    place-content: center;
    border: 1px solid rgba(var(--karaca-accent-rgb), 0.25);
    border-radius: 50%;
    text-align: center;
    background:
      radial-gradient(circle, rgba(var(--karaca-accent-rgb), 0.13), transparent 66%),
      rgba(7, 11, 15, 0.54);
    box-shadow: inset 0 0 30px rgba(var(--karaca-accent-rgb), 0.08);
  }

  .status-temperature {
    position: absolute;
    top: 8px;
    left: 50%;
    min-width: 38px;
    padding: 2px 7px;
    border: 1px solid rgba(var(--karaca-accent-rgb), 0.24);
    border-radius: 999px;
    color: var(--karaca-accent);
    background: rgba(var(--karaca-accent-rgb), 0.07);
    box-shadow: 0 0 10px rgba(var(--karaca-accent-rgb), 0.1);
    font-size: 10px;
    font-variant-numeric: tabular-nums;
    font-weight: 700;
    line-height: 15px;
    transform: translateX(-50%);
  }

  .status-label {
    margin: 0;
    padding: 0 12px;
    color: var(--karaca-text);
    font-size: 15px;
    font-weight: 680;
    overflow-wrap: anywhere;
  }

  .status-label.accent-label {
    color: var(--karaca-accent);
    text-shadow: 0 0 12px rgba(var(--karaca-accent-rgb), 0.36);
  }

  .status-time {
    min-height: 46px;
    margin-top: 5px;
    color: var(--karaca-text);
    font-size: clamp(35px, 10vw, 46px);
    font-variant-numeric: tabular-nums;
    font-weight: 350;
    line-height: 1;
  }

  .status-time.active-placeholder {
    display: grid;
    place-items: center;
    color: var(--karaca-accent);
    font-size: 24px;
    font-weight: 750;
    text-shadow: 0 0 12px rgba(var(--karaca-accent-rgb), 0.42);
  }

  .status-caption {
    min-height: 14px;
    margin-top: 6px;
    color: var(--karaca-muted);
    font-size: 11px;
    text-transform: uppercase;
  }

  .status-detail {
    min-height: 19px;
    margin-top: 8px;
    padding: 0 12px;
    color: var(--karaca-accent);
    font-size: 13px;
    font-weight: 700;
    overflow-wrap: anywhere;
  }

  ha-card[data-state="fresh"] .status-label,
  ha-card[data-state="fresh"] .status-time,
  ha-card[data-state="fresh"] .status-caption,
  ha-card[data-state="fresh"] .status-detail,
  ha-card[data-state="stale"] .status-label,
  ha-card[data-state="stale"] .status-time,
  ha-card[data-state="stale"] .status-caption,
  ha-card[data-state="stale"] .status-detail {
    transform: translateY(4px);
  }

  .connection-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 24px;
    margin-top: 14px;
    padding: 4px 9px;
    border: 1px solid var(--karaca-line);
    border-radius: 999px;
    color: var(--karaca-muted);
    background: rgba(0, 0, 0, 0.18);
    font-size: 10px;
  }

  .connection-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--karaca-success);
    box-shadow: 0 0 7px rgba(101, 216, 154, 0.7);
  }

  .mode-panel {
    padding: 14px;
    border-top: 1px solid var(--karaca-line);
    background: rgba(255, 255, 255, 0.025);
  }

  .mode-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 7px;
  }

  .mode-button {
    position: relative;
    display: grid;
    min-width: 0;
    min-height: 98px;
    grid-template-rows: 50px minmax(30px, auto);
    justify-items: center;
    align-items: start;
    gap: 7px;
    padding: 8px 4px 7px;
    overflow: hidden;
    border: 1px solid transparent;
    border-radius: 8px;
    color: var(--karaca-muted);
    background: transparent;
    cursor: pointer;
    user-select: none;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
  }

  .mode-button::after {
    position: absolute;
    right: 7px;
    bottom: 4px;
    left: 7px;
    height: 2px;
    border-radius: 999px;
    content: "";
    background: var(--karaca-accent);
    transform: scaleX(0);
    transform-origin: left;
  }

  .mode-button.holding::after {
    animation: karaca-hold-progress ${HOLD_DURATION_MS}ms linear forwards;
  }

  .mode-button:focus-visible {
    border-color: rgba(var(--karaca-accent-rgb), 0.55);
    outline: none;
  }

  .mode-icon {
    display: grid;
    width: 48px;
    height: 48px;
    place-items: center;
    border: 1px solid var(--karaca-line);
    border-radius: 50%;
    color: var(--karaca-muted);
    background: rgba(0, 0, 0, 0.15);
    transition: color 180ms ease, border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
  }

  .mode-label {
    max-width: 100%;
    font-size: 10px;
    font-weight: 650;
    line-height: 1.2;
    text-align: center;
    overflow-wrap: anywhere;
  }

  .mode-button.active {
    color: var(--karaca-text);
    background: rgba(var(--karaca-accent-rgb), 0.055);
  }

  .mode-button.active .mode-icon {
    border-color: rgba(var(--karaca-accent-rgb), 0.75);
    color: var(--karaca-accent);
    background: rgba(var(--karaca-accent-rgb), 0.12);
    box-shadow: 0 0 15px rgba(var(--karaca-accent-rgb), 0.32);
  }

  .mode-button.pending .mode-icon {
    animation: karaca-pending-pulse 1.1s ease-in-out infinite;
  }

  .mode-button:disabled {
    cursor: not-allowed;
    opacity: 0.38;
  }

  .hold-hint {
    min-height: 13px;
    margin: 11px 0 0;
    color: var(--karaca-muted);
    font-size: 10px;
    text-align: center;
  }

  .settings-layer,
  .confirm-layer,
  .message-layer {
    position: absolute;
    inset: 0;
    z-index: 4;
  }

  .settings-layer {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    background: rgba(12, 16, 21, 0.98);
    transform: translateX(102%);
    visibility: hidden;
    transition: transform 230ms ease, visibility 230ms;
  }

  ha-card.settings-open .settings-layer {
    transform: translateX(0);
    visibility: visible;
  }

  .settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 72px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--karaca-line);
  }

  .settings-header h2 {
    margin: 0;
    font-size: 18px;
  }

  .settings-header p {
    margin: 3px 0 0;
    color: var(--karaca-muted);
    font-size: 11px;
  }

  .settings-list {
    display: grid;
    align-content: start;
    gap: 2px;
    padding: 10px 12px 16px;
    overflow-y: auto;
  }

  .setting-row {
    display: grid;
    min-height: 54px;
    grid-template-columns: 34px minmax(0, 1fr) auto;
    align-items: center;
    gap: 8px;
    padding: 7px 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.055);
  }

  .setting-icon {
    display: grid;
    place-items: center;
    color: var(--karaca-muted);
  }

  .setting-name {
    font-size: 12px;
    font-weight: 620;
  }

  .setting-description {
    margin-top: 2px;
    color: var(--karaca-muted);
    font-size: 10px;
  }

  .toggle {
    position: relative;
    width: 42px;
    height: 24px;
    padding: 0;
    border: 0;
    border-radius: 999px;
    background: #343c46;
    cursor: pointer;
    transition: background 160ms ease, opacity 160ms ease;
  }

  .toggle::after {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    content: "";
    background: #dfe5eb;
    transition: transform 160ms ease;
  }

  .toggle[aria-checked="true"] {
    background: var(--karaca-accent);
  }

  .toggle[aria-checked="true"]::after {
    transform: translateX(18px);
  }

  .toggle:disabled {
    cursor: not-allowed;
    opacity: 0.35;
  }

  .confirm-layer {
    display: grid;
    place-items: center;
    padding: 22px;
    background: rgba(8, 12, 16, 0.88);
    backdrop-filter: blur(7px);
  }

  .confirm-panel {
    width: min(100%, 320px);
    padding: 20px;
    border: 1px solid rgba(var(--karaca-accent-rgb), 0.28);
    border-radius: 8px;
    background: #171d24;
    box-shadow: 0 18px 44px rgba(0, 0, 0, 0.42);
    text-align: center;
  }

  .confirm-panel ha-icon {
    width: 34px;
    height: 34px;
    color: var(--karaca-accent);
  }

  .confirm-panel h3 {
    margin: 12px 0 6px;
    font-size: 18px;
  }

  .confirm-panel p {
    margin: 0;
    color: var(--karaca-muted);
    font-size: 12px;
    line-height: 1.45;
  }

  .confirm-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 18px;
  }

  .text-button {
    min-height: 40px;
    padding: 8px 12px;
    border: 1px solid var(--karaca-line);
    border-radius: 8px;
    color: var(--karaca-text);
    background: #222a34;
    cursor: pointer;
  }

  .text-button.primary {
    border-color: rgba(var(--karaca-accent-rgb), 0.5);
    color: #071311;
    background: var(--karaca-accent);
    font-weight: 750;
  }

  .message-layer {
    display: grid;
    place-items: center;
    padding: 24px;
    background: rgba(12, 16, 21, 0.97);
    text-align: center;
  }

  .message-layer ha-icon {
    width: 38px;
    height: 38px;
    color: var(--karaca-warning);
  }

  .message-layer h3 {
    margin: 12px 0 6px;
    font-size: 17px;
  }

  .message-layer p {
    max-width: 310px;
    margin: 0;
    color: var(--karaca-muted);
    font-size: 12px;
    line-height: 1.45;
  }

  .toast {
    position: absolute;
    right: 14px;
    bottom: 14px;
    left: 14px;
    z-index: 8;
    padding: 11px 12px;
    border: 1px solid rgba(var(--karaca-accent-rgb), 0.34);
    border-radius: 8px;
    color: var(--karaca-text);
    background: #11171d;
    box-shadow: 0 9px 24px rgba(0, 0, 0, 0.35);
    font-size: 12px;
    pointer-events: none;
  }

  .action-alert {
    position: absolute;
    right: 14px;
    bottom: 14px;
    left: 14px;
    z-index: 9;
    display: grid;
    grid-template-columns: 30px minmax(0, 1fr) 32px;
    align-items: start;
    gap: 9px;
    padding: 12px;
    border: 1px solid rgba(238, 98, 92, 0.42);
    border-radius: 8px;
    background: #1c1719;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.42);
  }

  .action-alert > ha-icon {
    width: 24px;
    height: 24px;
    color: #ee625c;
  }

  .action-alert h3 {
    margin: 0 0 3px;
    font-size: 13px;
  }

  .action-alert p {
    margin: 0;
    color: var(--karaca-muted);
    font-size: 11px;
    line-height: 1.45;
  }

  .dismiss-alert {
    display: grid;
    width: 32px;
    height: 32px;
    place-items: center;
    padding: 0;
    border: 0;
    border-radius: 8px;
    color: var(--karaca-muted);
    background: transparent;
    cursor: pointer;
  }

  .dismiss-alert ha-icon {
    width: 19px;
    height: 19px;
  }

  ha-card[data-state="fresh"] {
    --karaca-accent: #65d89a;
    --karaca-accent-rgb: 101, 216, 154;
  }

  ha-card[data-state="ready"] {
    --karaca-accent: #55e4df;
    --karaca-accent-rgb: 85, 228, 223;
  }

  ha-card[data-state="stale"] {
    --karaca-accent: #ee625c;
    --karaca-accent-rgb: 238, 98, 92;
  }

  ha-card[data-state="error"] {
    --karaca-accent: #ee625c;
    --karaca-accent-rgb: 238, 98, 92;
  }

  ha-card[data-state="offline"] {
    --karaca-accent: #7e8994;
    --karaca-accent-rgb: 126, 137, 148;
    filter: saturate(0.7);
  }

  ha-card[data-state="idle"] .ring-tracer,
  ha-card[data-state="ready"] .ring-tracer,
  ha-card[data-state="fresh"] .ring-tracer,
  ha-card[data-state="stale"] .ring-tracer,
  ha-card[data-state="error"] .ring-tracer,
  ha-card[data-state="offline"] .ring-tracer {
    display: none;
  }

  ha-card[data-state="ready"] .ring-progress {
    stroke-dashoffset: 0 !important;
  }

  ha-card.animated[data-state="ready"] .ring-progress {
    animation: karaca-ready-glow 2.2s ease-in-out infinite;
  }

  ha-card[data-state="error"] .ring-progress {
    stroke-dasharray: 36 18;
    stroke-dashoffset: 0;
  }

  ha-card[data-state="offline"] .connection-dot {
    background: #7e8994;
    box-shadow: none;
  }

  ha-card:not(.animated) .ring-tracer {
    animation: none;
  }

  @keyframes karaca-ring-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes karaca-ready-glow {
    0%, 100% {
      opacity: 0.72;
      filter: drop-shadow(0 0 5px rgba(var(--karaca-accent-rgb), 0.5));
    }
    50% {
      opacity: 1;
      filter: drop-shadow(0 0 14px rgba(var(--karaca-accent-rgb), 0.95));
    }
  }

  @keyframes karaca-hold-progress {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
  }

  @keyframes karaca-pending-pulse {
    0%, 100% { opacity: 0.55; }
    50% { opacity: 1; }
  }

  @media (max-width: 360px) {
    .card-header {
      grid-template-columns: 38px minmax(0, 1fr) 38px;
      padding-inline: 10px;
    }

    .device-mark,
    .icon-button {
      width: 38px;
      height: 38px;
    }

    .heading h1 {
      font-size: 18px;
    }

    .status-ring {
      width: 220px;
    }

    .mode-panel {
      padding-inline: 8px;
    }

    .mode-grid {
      gap: 3px;
    }

    .mode-label {
      font-size: 9px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 1ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 1ms !important;
    }
  }
`;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeText(value) {
  return String(value ?? "")
    .toLocaleLowerCase("tr-TR")
    .replaceAll("ı", "i")
    .replaceAll("ş", "s")
    .replaceAll("ğ", "g")
    .replaceAll("ü", "u")
    .replaceAll("ö", "o")
    .replaceAll("ç", "c");
}

function parseNumeric(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

class KaracaConnectCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = null;
    this._entitiesDiscovered = false;
    this._discovering = false;
    this._discoveryError = null;
    this._mappedEntities = this._emptyMapping();
    this._showSettings = false;
    this._confirmAction = null;
    this._pendingAction = null;
    this._actionTimer = null;
    this._holdTimer = null;
    this._heldButton = null;
    this._toastMessage = null;
    this._toastTimer = null;
    this._persistentAlert = null;
    this._clockTimer = null;
    this._countdownBaseSeconds = null;
    this._countdownBaseAt = null;
    this._countdownSignature = null;
    this._relevantStateSignature = null;
  }

  static getConfigElement() {
    return document.createElement("karaca-connect-card-editor");
  }

  static getStubConfig() {
    return {
      device_id: "",
      confirm_type: "hold",
      show_freshness: true,
      animation: true,
    };
  }

  setConfig(config) {
    if (!config.device_id) {
      throw new Error("Karaca Connect kartı için bir cihaz seçin.");
    }

    const previousDevice = this._config?.device_id;
    this._config = {
      confirm_type: "hold",
      show_freshness: true,
      animation: true,
      ...config,
    };

    if (previousDevice !== this._config.device_id) {
      this._entitiesDiscovered = false;
      this._discoveryError = null;
      this._mappedEntities = this._emptyMapping();
      this._relevantStateSignature = null;
    }

    this._render();
    if (this._hass && !this._entitiesDiscovered) {
      this._discoverEntities();
    }
  }

  set hass(hass) {
    this._hass = hass;

    if (!this._config) return;
    if (!this._entitiesDiscovered && !this._discovering) {
      this._discoverEntities();
      return;
    }

    const nextSignature = this._createRelevantStateSignature(hass);
    const relevantStateChanged =
      nextSignature !== this._relevantStateSignature;
    this._relevantStateSignature = nextSignature;
    const pendingActionResolved = this._resolvePendingAction();
    this._syncCountdownBase();
    if (relevantStateChanged || pendingActionResolved) {
      this._render();
    } else {
      this._updateClockNodes();
    }
  }

  connectedCallback() {
    this._startClock();
  }

  disconnectedCallback() {
    this._stopClock();
    this._cancelHold();
    clearTimeout(this._actionTimer);
    clearTimeout(this._toastTimer);
  }

  getCardSize() {
    return 6;
  }

  _emptyMapping() {
    return {
      status: null,
      active_mode: null,
      tea_freshness: null,
      modes: {},
      settings: {},
    };
  }

  async _discoverEntities() {
    if (
      this._discovering ||
      this._entitiesDiscovered ||
      !this._hass ||
      !this._config?.device_id
    ) {
      return;
    }

    this._discovering = true;
    this._discoveryError = null;
    this._mappedEntities = this._emptyMapping();

    try {
      const registry = await this._hass.callWS({
        type: "config/entity_registry/list",
      });
      const deviceEntities = registry.filter(
        (entry) =>
          entry.device_id === this._config.device_id &&
          entry.platform === "karaca",
      );

      for (const entry of deviceEntities) {
        const stateObj = this._hass.states[entry.entity_id];
        if (!stateObj) continue;
        this._mapEntity(entry.entity_id, stateObj);
      }

      if (!this._mappedEntities.status) {
        this._discoveryError =
          "Bu cihazın Karaca durum sensörü bulunamadı. Entegrasyonu yeniden başlatıp kartı yenileyin.";
      }
    } catch (error) {
      console.error("Karaca Connect entity discovery failed:", error);
      this._discoveryError =
        "Cihaz varlıkları okunamadı. Home Assistant bağlantısını yenileyin.";
    } finally {
      this._entitiesDiscovered = true;
      this._discovering = false;
      this._syncCountdownBase();
      this._relevantStateSignature = this._createRelevantStateSignature();
      this._render();
    }
  }

  _mapEntity(entityId, stateObj) {
    const role = stateObj.attributes.karaca_role;
    if (role === "status") {
      this._mappedEntities.status = entityId;
      return;
    }
    if (role === "active_mode") {
      this._mappedEntities.active_mode = entityId;
      return;
    }
    if (role === "tea_freshness") {
      this._mappedEntities.tea_freshness = entityId;
      return;
    }
    if (role === "mode_switch") {
      const modeId = parseNumeric(stateObj.attributes.mode_id);
      if (modeId !== null) this._mappedEntities.modes[modeId] = entityId;
      return;
    }
    if (role === "setting_switch") {
      const settingId = parseNumeric(stateObj.attributes.setting_id);
      if (settingId !== null) {
        this._mappedEntities.settings[settingId] = entityId;
      }
      return;
    }

    // Device-scoped compatibility fallback for older role metadata.
    if (entityId.endsWith("_durumu") || entityId.endsWith("_status")) {
      this._mappedEntities.status = entityId;
    } else if (
      entityId.endsWith("_aktif_mod") ||
      entityId.endsWith("_active_mode")
    ) {
      this._mappedEntities.active_mode = entityId;
    } else if (
      entityId.endsWith("_cay_tazeligi") ||
      entityId.endsWith("_tea_freshness")
    ) {
      this._mappedEntities.tea_freshness = entityId;
    } else if (stateObj.attributes.mode_id !== undefined) {
      const modeId = parseNumeric(stateObj.attributes.mode_id);
      if (modeId !== null) this._mappedEntities.modes[modeId] = entityId;
    } else if (stateObj.attributes.setting_id !== undefined) {
      const settingId = parseNumeric(stateObj.attributes.setting_id);
      if (settingId !== null) {
        this._mappedEntities.settings[settingId] = entityId;
      }
    }
  }

  _state(entityId) {
    return entityId ? this._hass?.states?.[entityId] ?? null : null;
  }

  _createRelevantStateSignature(hass = this._hass) {
    const entityIds = [
      this._mappedEntities.status,
      this._mappedEntities.active_mode,
      this._mappedEntities.tea_freshness,
      ...Object.values(this._mappedEntities.modes),
      ...Object.values(this._mappedEntities.settings),
    ]
      .filter(Boolean)
      .sort();

    return entityIds
      .map((entityId) => {
        const stateObj = hass?.states?.[entityId];
        return `${entityId}:${stateObj?.state ?? ""}:${stateObj?.last_updated ?? ""}`;
      })
      .join("|");
  }

  _statusState() {
    return this._state(this._mappedEntities.status);
  }

  _activeModeState() {
    return this._state(this._mappedEntities.active_mode);
  }

  _freshnessState() {
    return this._state(this._mappedEntities.tea_freshness);
  }

  _isOnline() {
    const status = this._statusState();
    if (!status) return false;
    return (
      status.state !== "unavailable" &&
      status.state !== "unknown" &&
      status.attributes.connected !== false
    );
  }

  _isWorking() {
    return MODE_CONFIGS.some((mode) => {
      const stateObj = this._state(this._mappedEntities.modes[mode.id]);
      return stateObj?.state === "on";
    });
  }

  _deriveVisualState() {
    if (!this._isOnline()) return "offline";

    const status = normalizeText(this._statusState()?.state);
    const freshness = normalizeText(this._freshnessState()?.state);
    if (status.startsWith("hata")) return "error";

    if (this._isWaterReadyStatus(status) || this._isBabyWaterReadyStatus(status)) {
      return "ready";
    }

    if (this._isCoffeeReadyStatus(status)) {
      if (this._config?.show_freshness === false) return "ready";
      return this._coffeeFreshnessRemainingSeconds() === 0 ? "stale" : "fresh";
    }

    if (this._isTeaReadyStatus(status)) {
      if (this._config?.show_freshness === false) return "ready";
      if (
        status.includes("bayat") ||
        freshness.includes("bayat") ||
        this._freshnessRemainingSeconds() === 0
      ) {
        return "stale";
      }
      return "fresh";
    }

    if (
      this._isWaterHeatingStatus(status) ||
      this._isBabyWaterHeatingStatus(status) ||
      this._isTeaBrewingStatus(status) ||
      this._isCoffeeBrewingStatus(status) ||
      this._isWorking()
    ) {
      return "working";
    }
    return "idle";
  }

  _isWaterHeatingStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("su kaynatiliyor");
  }

  _isWaterReadyStatus(status = normalizeText(this._statusState()?.state)) {
    return status === "su hazir";
  }

  _isBabyWaterHeatingStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("mama suyu isitiliyor");
  }

  _isBabyWaterReadyStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("mama suyu hazir");
  }

  _isTeaBrewingStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("cay demleniyor");
  }

  _isTeaReadyStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("cay hazir");
  }

  _isCoffeeBrewingStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("filtre kahve demleniyor");
  }

  _isCoffeeReadyStatus(status = normalizeText(this._statusState()?.state)) {
    return status.includes("kahve hazir");
  }

  _statusCountdownSeconds(matchesStatus, durationSeconds) {
    const statusState = this._statusState();
    if (!matchesStatus) return null;

    const startedAt = new Date(
      statusState?.last_changed ?? statusState?.last_updated ?? "",
    ).getTime();
    if (!Number.isFinite(startedAt)) return durationSeconds;

    const elapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    if (elapsed < durationSeconds) return durationSeconds - elapsed;

    const overtime = elapsed - durationSeconds;
    return (
      BREWING_OVERTIME_WINDOW_SECONDS -
      (overtime % BREWING_OVERTIME_WINDOW_SECONDS)
    );
  }

  _teaBrewingCountdownSeconds() {
    return this._statusCountdownSeconds(
      this._isTeaBrewingStatus(),
      TEA_BREWING_DURATION_SECONDS,
    );
  }

  _coffeeBrewingCountdownSeconds() {
    return this._statusCountdownSeconds(
      this._isCoffeeBrewingStatus(),
      FILTER_COFFEE_BREWING_DURATION_SECONDS,
    );
  }

  _parseCountdownSeconds(countdown) {
    if (!countdown || typeof countdown !== "object") return null;

    for (const key of [
      "remainingSeconds",
      "remainingSecond",
      "remaining_seconds",
      "seconds",
    ]) {
      const value = parseNumeric(countdown[key]);
      if (value !== null && value >= 0) return Math.round(value);
    }

    for (const key of [
      "remainingMinutes",
      "remaining_minutes",
      "minutes",
      "minute",
      "value",
    ]) {
      const value = parseNumeric(countdown[key]);
      if (value !== null && value >= 0) return Math.round(value * 60);
    }

    const displayText = String(countdown.displayText ?? "");
    const timeMatch = displayText.match(/(\d{1,2}):(\d{2})/);
    if (timeMatch) {
      return Number(timeMatch[1]) * 60 + Number(timeMatch[2]);
    }

    return null;
  }

  _syncCountdownBase() {
    const statusState = this._statusState();
    const countdown = statusState?.attributes?.countdown;
    const signature = `${statusState?.last_updated ?? ""}:${JSON.stringify(countdown ?? null)}`;
    if (signature === this._countdownSignature) return;
    this._countdownSignature = signature;

    const seconds = this._parseCountdownSeconds(countdown);
    if (seconds === null) {
      this._countdownBaseSeconds = null;
      this._countdownBaseAt = null;
      return;
    }

    this._countdownBaseSeconds = seconds;
    this._countdownBaseAt = Date.now();
  }

  _currentCountdownSeconds() {
    if (
      this._countdownBaseSeconds === null ||
      this._countdownBaseAt === null
    ) {
      return null;
    }
    const elapsed = Math.floor((Date.now() - this._countdownBaseAt) / 1000);
    return Math.max(0, this._countdownBaseSeconds - elapsed);
  }

  _freshnessRemainingSeconds() {
    const freshness = this._freshnessState();
    const freshUntil =
      freshness?.attributes?.fresh_until ??
      this._statusState()?.attributes?.fresh_until;
    if (!freshUntil) return null;

    const target = new Date(freshUntil).getTime();
    if (!Number.isFinite(target)) return null;
    return Math.max(0, Math.round((target - Date.now()) / 1000));
  }

  _coffeeFreshnessRemainingSeconds() {
    const statusState = this._statusState();
    if (!this._isCoffeeReadyStatus()) return null;

    const startedAt = new Date(
      statusState?.last_changed ?? statusState?.last_updated ?? "",
    ).getTime();
    if (!Number.isFinite(startedAt)) {
      return FILTER_COFFEE_FRESHNESS_DURATION_SECONDS;
    }

    const elapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    return Math.max(0, FILTER_COFFEE_FRESHNESS_DURATION_SECONDS - elapsed);
  }

  _targetTemperature() {
    const status = normalizeText(this._statusState()?.state);
    const activeMode = normalizeText(this._activeModeState()?.state);

    if (
      this._isBabyWaterHeatingStatus(status) ||
      this._isBabyWaterReadyStatus(status) ||
      activeMode.includes("mama suyu")
    ) {
      return 40;
    }
    if (
      this._isCoffeeBrewingStatus(status) ||
      this._isCoffeeReadyStatus(status) ||
      activeMode.includes("filtre kahve")
    ) {
      return 90;
    }
    if (
      this._isTeaBrewingStatus(status) ||
      this._isTeaReadyStatus(status) ||
      activeMode.includes("cay demleme")
    ) {
      return 90;
    }
    if (
      this._isWaterHeatingStatus(status) ||
      this._isWaterReadyStatus(status) ||
      activeMode.includes("su kaynatma")
    ) {
      return 100;
    }

    const activeModeConfig = MODE_CONFIGS.find((mode) => {
      const stateObj = this._state(this._mappedEntities.modes[mode.id]);
      return stateObj?.state === "on";
    });
    return activeModeConfig?.targetTemperature ?? null;
  }

  _formatDuration(totalSeconds) {
    if (totalSeconds === null || !Number.isFinite(totalSeconds)) return "--:--";
    const minutes = Math.floor(Math.max(0, totalSeconds) / 60);
    const seconds = Math.max(0, totalSeconds) % 60;
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  _displayModel() {
    const statusState = this._statusState();
    const activeModeState = this._activeModeState();
    const freshnessState = this._freshnessState();
    const visualState = this._deriveVisualState();
    const countdownSeconds = this._currentCountdownSeconds();
    const teaBrewingSeconds = this._teaBrewingCountdownSeconds();
    const coffeeBrewingSeconds = this._coffeeBrewingCountdownSeconds();
    const teaFreshnessSeconds = this._freshnessRemainingSeconds();
    const coffeeFreshnessSeconds = this._coffeeFreshnessRemainingSeconds();
    const isCoffeeReady = this._isCoffeeReadyStatus();
    const freshnessSeconds = isCoffeeReady
      ? coffeeFreshnessSeconds
      : teaFreshnessSeconds;
    const freshnessDuration = isCoffeeReady
      ? FILTER_COFFEE_FRESHNESS_DURATION_SECONDS
      : TEA_FRESHNESS_DURATION_SECONDS;
    const isSimpleWorkingStatus =
      this._isWaterHeatingStatus() || this._isBabyWaterHeatingStatus();
    const targetTemperature = this._targetTemperature();
    const configuredName = this._config?.name?.trim();
    const entityName = statusState?.attributes?.friendly_name
      ?.replace(/\s+Durumu$/u, "")
      .trim();

    let label = statusState?.state ?? "Durum bekleniyor";
    let time = "--:--";
    let caption = visualState === "idle" ? "Hazır" : "";
    let detail = activeModeState?.state ?? "Bir mod seç";
    let ringRatio = 0;
    let accentLabel = false;

    if (visualState === "working") {
      const displayedCountdownSeconds =
        teaBrewingSeconds ?? coffeeBrewingSeconds ?? countdownSeconds;
      if (isSimpleWorkingStatus) {
        time = "";
        caption = "";
        accentLabel = true;
      } else {
        time =
          displayedCountdownSeconds === null
            ? "AKTİF"
            : this._formatDuration(displayedCountdownSeconds);
        caption = displayedCountdownSeconds === null ? "" : "Kalan süre";
      }
      detail = "";
    } else if (visualState === "ready") {
      time = "";
      caption = "";
      detail = "";
      ringRatio = 1;
      accentLabel = true;
    } else if (visualState === "fresh") {
      label = isCoffeeReady ? "Kahve Hazır" : "Çay Hazır";
      time = this._formatDuration(freshnessSeconds);
      caption = "Tazelik süresi";
      detail = "TAZE";
      ringRatio =
        freshnessSeconds === null
          ? 1
          : Math.min(1, freshnessSeconds / freshnessDuration);
    } else if (visualState === "stale") {
      label = isCoffeeReady ? "Kahve Hazır" : "Çay Hazır";
      time = "00:00";
      caption = "Tazelik süresi";
      detail = "BAYAT";
      ringRatio = 0;
    } else if (visualState === "error") {
      caption = "Cihaz uyarısı";
      detail = statusState?.attributes?.last_error ?? "Cihazı kontrol edin";
      ringRatio = 1;
    } else if (visualState === "offline") {
      label = "Bağlantı Yok";
      caption = "Çevrimdışı";
      detail = "Komutlar geçici olarak kapalı";
    }

    if (this._config?.show_freshness === false && visualState === "fresh") {
      detail = activeModeState?.state ?? "Hazır";
    }

    return {
      name: configuredName || entityName || "Karaca Çaysever",
      subtitle: this._config?.subtitle || "Çaysever Robotea Pro",
      label,
      time,
      caption,
      detail,
      visualState,
      online: this._isOnline(),
      ringOffset: RING_CIRCUMFERENCE * (1 - ringRatio),
      freshnessState: freshnessState?.state ?? null,
      targetTemperature,
      accentLabel,
      activePlaceholder:
        visualState === "working" &&
        teaBrewingSeconds === null &&
        coffeeBrewingSeconds === null &&
        countdownSeconds === null,
    };
  }

  async _callModeAction(modeId, turnOn) {
    if (this._pendingAction || !this._hass || !this._isOnline()) {
      if (!this._isOnline()) {
        this._showToast("Cihaz çevrimdışı. Komut gönderilemiyor.");
      }
      return;
    }

    const entityId = this._mappedEntities.modes[modeId];
    if (!entityId) {
      this._showToast("Bu mod cihaz tarafından sunulmuyor.");
      return;
    }

    const service = turnOn ? "turn_on" : "turn_off";
    this._setPendingAction({
      type: "mode",
      key: `mode_${modeId}`,
      modeId,
      turnOn,
      entityId,
      expectedState: turnOn ? "on" : "off",
    });

    try {
      await this._hass.callService("switch", service, {}, { entity_id: entityId });
    } catch (error) {
      this._clearPendingAction();
      this._showToast(`Komut gönderilemedi: ${error.message ?? error}`);
    }
  }

  async _toggleSetting(settingId) {
    if (this._pendingAction || !this._hass || !this._isOnline()) return;

    const entityId = this._mappedEntities.settings[settingId];
    const stateObj = this._state(entityId);
    if (!entityId || !stateObj) {
      this._showToast("Bu ayar cihaz tarafından sunulmuyor.");
      return;
    }

    const turnOn = stateObj.state !== "on";
    this._setPendingAction({
      type: "setting",
      key: `setting_${settingId}`,
      entityId,
      expectedState: turnOn ? "on" : "off",
    });

    try {
      await this._hass.callService(
        "switch",
        turnOn ? "turn_on" : "turn_off",
        {},
        { entity_id: entityId },
      );
    } catch (error) {
      this._clearPendingAction();
      this._showToast(`Ayar değiştirilemedi: ${error.message ?? error}`);
    }
  }

  _setPendingAction(action) {
    clearTimeout(this._actionTimer);
    this._persistentAlert = null;
    this._pendingAction = action;
    this._actionTimer = setTimeout(() => {
      const timedOutAction = this._pendingAction;
      this._pendingAction = null;
      this._actionTimer = null;
      this._showActionTimeout(timedOutAction);
    }, ACTION_TIMEOUT_MS);
    this._render();
  }

  _showActionTimeout(action) {
    if (action?.type === "mode" && action.turnOn) {
      if (action.modeId === 13) {
        this._persistentAlert = {
          title: "Mama Suyu başlatılamadı",
          message:
            "Su sıcaklığı seçilen Mama Suyu sıcaklığının üzerinde olabilir. Suyun soğumasını bekleyip tekrar deneyin.",
        };
      } else {
        this._persistentAlert = {
          title: "Mod başlatılamadı",
          message:
            "Cihaz komutu kabul etmedi veya durum zamanında doğrulanamadı. Karaca uygulamasındaki bildirimi kontrol edin.",
        };
      }
      this._render();
      return;
    }

    if (action?.type === "mode") {
      this._persistentAlert = {
        title: "İşlem durdurulamadı",
        message:
          "Cihazın durumu zamanında doğrulanamadı. Cihazı ve Karaca uygulamasını kontrol edin.",
      };
      this._render();
      return;
    }

    this._showToast("Ayar değişikliği zamanında doğrulanamadı.");
  }

  _resolvePendingAction() {
    if (!this._pendingAction) return false;
    const stateObj = this._state(this._pendingAction.entityId);
    if (stateObj?.state === this._pendingAction.expectedState) {
      this._clearPendingAction(false);
      return true;
    }
    return false;
  }

  _clearPendingAction(render = true) {
    clearTimeout(this._actionTimer);
    this._actionTimer = null;
    this._pendingAction = null;
    if (render) this._render();
  }

  _requestModeAction(modeId, active) {
    const mode = MODE_CONFIGS.find((item) => item.id === modeId);
    const turnOn = !active;

    if (this._config.confirm_type === "dialog") {
      this._confirmAction = {
        modeId,
        turnOn,
        label: mode?.label ?? "Seçili mod",
      };
      this._render();
      return;
    }

    this._callModeAction(modeId, turnOn);
  }

  _startHold(button, modeId, active, pointerId) {
    if (this._pendingAction || button.disabled) return;
    this._cancelHold();
    this._heldButton = button;
    button.classList.add("holding");
    try {
      button.setPointerCapture(pointerId);
    } catch (_error) {
      // Pointer capture is optional on older WebViews.
    }
    this._holdTimer = setTimeout(() => {
      this._holdTimer = null;
      button.classList.remove("holding");
      this._heldButton = null;
      this._requestModeAction(modeId, active);
    }, HOLD_DURATION_MS);
  }

  _cancelHold() {
    clearTimeout(this._holdTimer);
    this._holdTimer = null;
    this._heldButton?.classList.remove("holding");
    this._heldButton = null;
  }

  _showToast(message) {
    clearTimeout(this._toastTimer);
    this._toastMessage = message;
    this._render();
    this._toastTimer = setTimeout(() => {
      this._toastMessage = null;
      this._render();
    }, 4000);
  }

  _startClock() {
    if (this._clockTimer) return;
    this._clockTimer = setInterval(() => this._updateClockNodes(), 1000);
  }

  _stopClock() {
    clearInterval(this._clockTimer);
    this._clockTimer = null;
  }

  _updateClockNodes() {
    if (!this.shadowRoot || !this._config) return;
    const model = this._displayModel();
    const cardNode = this.shadowRoot.querySelector("ha-card");
    if (cardNode?.dataset.state !== model.visualState) {
      this._render();
      return;
    }
    const timeNode = this.shadowRoot.querySelector(".status-time");
    const ringNode = this.shadowRoot.querySelector(".ring-progress");
    if (timeNode) {
      timeNode.textContent = model.time;
      timeNode.classList.toggle(
        "active-placeholder",
        model.activePlaceholder,
      );
    }
    if (ringNode) {
      ringNode.style.setProperty("--ring-offset", String(model.ringOffset));
    }
  }

  _render() {
    if (!this.shadowRoot || !this._config) return;

    if (this._discovering && !this._entitiesDiscovered) {
      this.shadowRoot.innerHTML = `
        <style>${CARD_STYLES}</style>
        <ha-card>
          <div class="message-layer">
            <ha-icon icon="mdi:loading"></ha-icon>
            <h3>Karaca cihazı hazırlanıyor</h3>
            <p>Cihaza ait sensör ve kontroller bulunuyor.</p>
          </div>
          <div style="min-height: 440px"></div>
        </ha-card>
      `;
      return;
    }

    const model = this._displayModel();
    const settingsOpen = this._showSettings ? "settings-open" : "";
    const animationClass =
      this._config.animation !== false &&
      ["working", "ready"].includes(model.visualState)
        ? "animated"
        : "";

    this.shadowRoot.innerHTML = `
      <style>${CARD_STYLES}</style>
      <ha-card
        class="${settingsOpen} ${animationClass}"
        data-state="${model.visualState}"
        aria-label="${escapeHtml(model.name)} kontrol kartı"
      >
        <header class="card-header">
          <div class="device-mark" aria-hidden="true">
            <ha-icon icon="mdi:tea"></ha-icon>
          </div>
          <div class="heading">
            <h1>${escapeHtml(model.name)}</h1>
            <p>${escapeHtml(model.subtitle)}</p>
          </div>
          <button class="icon-button settings-button" type="button" aria-label="Bildirim ayarlarını aç">
            <ha-icon icon="mdi:cog-outline"></ha-icon>
          </button>
        </header>

        <section class="status-zone">
          <div class="status-ring">
            <svg class="ring-svg" viewBox="0 0 210 210" aria-hidden="true">
              <circle class="ring-track" cx="105" cy="105" r="94"></circle>
              <circle
                class="ring-progress"
                cx="105"
                cy="105"
                r="94"
                style="--ring-offset: ${model.ringOffset}"
              ></circle>
              <circle class="ring-tracer" cx="105" cy="105" r="94"></circle>
            </svg>
            <div class="ring-core">
              ${
                model.targetTemperature !== null
                  ? `<div class="status-temperature" title="Hedef sıcaklık">${model.targetTemperature}°C</div>`
                  : ""
              }
              <p class="status-label ${model.accentLabel ? "accent-label" : ""}">${escapeHtml(model.label)}</p>
              ${
                model.time
                  ? `<div class="status-time ${model.activePlaceholder ? "active-placeholder" : ""}">${escapeHtml(model.time)}</div>`
                  : ""
              }
              ${
                model.caption
                  ? `<div class="status-caption">${escapeHtml(model.caption)}</div>`
                  : ""
              }
              ${
                model.detail
                  ? `<div class="status-detail">${escapeHtml(model.detail)}</div>`
                  : ""
              }
            </div>
          </div>
          <div class="connection-pill">
            <span class="connection-dot"></span>
            <span>${model.online ? "Cihaz bağlı" : "Cihaz çevrimdışı"}</span>
          </div>
        </section>

        <section class="mode-panel">
          <div class="mode-grid">
            ${this._renderModes(model.online)}
          </div>
          <p class="hold-hint">
            ${
              this._config.confirm_type === "dialog"
                ? "Bir moda dokunup kart içinden onayla"
                : "Çalıştırmak veya durdurmak için basılı tut"
            }
          </p>
        </section>

        ${this._renderSettings(model.name)}
        ${this._renderConfirm()}
        ${this._renderMessage()}
        ${this._renderActionAlert()}
        ${
          this._toastMessage
            ? `<div class="toast" role="status" aria-live="polite">${escapeHtml(this._toastMessage)}</div>`
            : ""
        }
      </ha-card>
    `;

    this._bindEvents();
  }

  _renderModes(online) {
    return MODE_CONFIGS.map((mode) => {
      const entityId = this._mappedEntities.modes[mode.id];
      const stateObj = this._state(entityId);
      const active = stateObj?.state === "on";
      const pending = this._pendingAction?.key === `mode_${mode.id}`;
      const disabled = !online || !entityId || Boolean(this._pendingAction);
      const actionLabel = active ? "durdur" : "başlat";

      return `
        <button
          class="mode-button ${active ? "active" : ""} ${pending ? "pending" : ""}"
          type="button"
          data-mode-id="${mode.id}"
          data-active="${active}"
          aria-label="${escapeHtml(mode.label)} modunu ${actionLabel}"
          ${disabled ? "disabled" : ""}
        >
          <span class="mode-icon"><ha-icon icon="${mode.icon}"></ha-icon></span>
          <span class="mode-label">${escapeHtml(mode.label)}</span>
        </button>
      `;
    }).join("");
  }

  _renderSettings(deviceName) {
    return `
      <aside class="settings-layer" aria-hidden="${!this._showSettings}">
        <div class="settings-header">
          <div>
            <h2>Bildirim Ayarları</h2>
            <p>${escapeHtml(deviceName)}</p>
          </div>
          <button class="icon-button close-settings" type="button" aria-label="Ayarları kapat">
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        <div class="settings-list">
          ${SETTING_CONFIGS.map((setting) => {
            const entityId = this._mappedEntities.settings[setting.id];
            const stateObj = this._state(entityId);
            const checked = stateObj?.state === "on";
            const pending =
              this._pendingAction?.key === `setting_${setting.id}`;
            const disabled =
              !entityId || !this._isOnline() || Boolean(this._pendingAction);
            return `
              <div class="setting-row">
                <span class="setting-icon"><ha-icon icon="${setting.icon}"></ha-icon></span>
                <div>
                  <div class="setting-name">${escapeHtml(setting.label)}</div>
                  <div class="setting-description">${escapeHtml(setting.description)}</div>
                </div>
                <button
                  class="toggle ${pending ? "pending" : ""}"
                  type="button"
                  role="switch"
                  aria-checked="${checked}"
                  aria-label="${escapeHtml(setting.label)} ayarı"
                  data-setting-id="${setting.id}"
                  ${disabled ? "disabled" : ""}
                ></button>
              </div>
            `;
          }).join("")}
        </div>
      </aside>
    `;
  }

  _renderConfirm() {
    if (!this._confirmAction) return "";
    const verb = this._confirmAction.turnOn ? "başlatmak" : "durdurmak";
    return `
      <div class="confirm-layer" role="dialog" aria-modal="true" aria-label="İşlem onayı">
        <div class="confirm-panel">
          <ha-icon icon="mdi:gesture-tap-button"></ha-icon>
          <h3>${escapeHtml(this._confirmAction.label)}</h3>
          <p>Bu modu ${verb} istediğinizden emin misiniz?</p>
          <div class="confirm-actions">
            <button class="text-button cancel-confirm" type="button">Vazgeç</button>
            <button class="text-button primary approve-confirm" type="button">Onayla</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderMessage() {
    if (!this._discoveryError) return "";
    return `
      <div class="message-layer">
        <ha-icon icon="mdi:alert-circle-outline"></ha-icon>
        <h3>Kart yapılandırılamadı</h3>
        <p>${escapeHtml(this._discoveryError)}</p>
      </div>
    `;
  }

  _renderActionAlert() {
    if (!this._persistentAlert) return "";
    return `
      <div class="action-alert" role="alert" aria-live="assertive">
        <ha-icon icon="mdi:alert-circle-outline"></ha-icon>
        <div>
          <h3>${escapeHtml(this._persistentAlert.title)}</h3>
          <p>${escapeHtml(this._persistentAlert.message)}</p>
        </div>
        <button class="dismiss-alert" type="button" aria-label="Uyarıyı kapat">
          <ha-icon icon="mdi:close"></ha-icon>
        </button>
      </div>
    `;
  }

  _bindEvents() {
    this.shadowRoot
      .querySelector(".settings-button")
      ?.addEventListener("click", () => {
        this._showSettings = true;
        this._render();
      });

    this.shadowRoot
      .querySelector(".close-settings")
      ?.addEventListener("click", () => {
        this._showSettings = false;
        this._render();
      });

    this.shadowRoot
      .querySelector(".dismiss-alert")
      ?.addEventListener("click", () => {
        this._persistentAlert = null;
        this._render();
      });

    this.shadowRoot.querySelectorAll(".toggle").forEach((button) => {
      button.addEventListener("click", () => {
        this._toggleSetting(Number(button.dataset.settingId));
      });
    });

    this.shadowRoot.querySelectorAll(".mode-button").forEach((button) => {
      const modeId = Number(button.dataset.modeId);
      const active = button.dataset.active === "true";

      if (this._config.confirm_type === "dialog") {
        button.addEventListener("click", () => {
          this._requestModeAction(modeId, active);
        });
        return;
      }

      button.addEventListener("pointerdown", (event) => {
        event.preventDefault();
        this._startHold(button, modeId, active, event.pointerId);
      });
      button.addEventListener("pointerup", () => this._cancelHold());
      button.addEventListener("pointercancel", () => this._cancelHold());
      button.addEventListener("pointerleave", () => this._cancelHold());
      button.addEventListener("contextmenu", (event) => event.preventDefault());
    });

    this.shadowRoot
      .querySelector(".cancel-confirm")
      ?.addEventListener("click", () => {
        this._confirmAction = null;
        this._render();
      });

    this.shadowRoot
      .querySelector(".approve-confirm")
      ?.addEventListener("click", () => {
        const action = this._confirmAction;
        this._confirmAction = null;
        this._render();
        if (action) this._callModeAction(action.modeId, action.turnOn);
      });
  }
}

class KaracaConnectCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
    this._devices = [];
    this._loadingDevices = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._loadingDevices && this._devices.length === 0) {
      this._loadDevices();
    } else {
      this._render();
    }
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  async _loadDevices() {
    if (!this._hass || this._loadingDevices) return;
    this._loadingDevices = true;

    try {
      const [entities, devices] = await Promise.all([
        this._hass.callWS({ type: "config/entity_registry/list" }),
        this._hass.callWS({ type: "config/device_registry/list" }),
      ]);
      const karacaDeviceIds = new Set(
        entities
          .filter((entry) => entry.platform === "karaca" && entry.device_id)
          .map((entry) => entry.device_id),
      );

      this._devices = devices
        .filter((device) => karacaDeviceIds.has(device.id))
        .map((device) => ({
          id: device.id,
          name:
            device.name_by_user ||
            device.name ||
            device.model ||
            "Karaca cihaz",
        }))
        .sort((a, b) => a.name.localeCompare(b.name, "tr"));
    } catch (error) {
      console.error("Karaca Connect editor device discovery failed:", error);
      this._devices = [];
    } finally {
      this._loadingDevices = false;
      this._render();
    }
  }

  _configChanged(patch) {
    this._config = { ...this._config, ...patch };
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this._config },
        bubbles: true,
        composed: true,
      }),
    );
    this._render();
  }

  _render() {
    if (!this.shadowRoot) return;
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: 8px 0;
          color: var(--primary-text-color);
          font-family: var(--primary-font-family, sans-serif);
        }
        * { box-sizing: border-box; letter-spacing: 0; }
        .form { display: grid; gap: 14px; }
        label { display: grid; gap: 6px; font-size: 13px; font-weight: 650; }
        select,
        input {
          width: 100%;
          min-height: 42px;
          padding: 8px 10px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          color: var(--primary-text-color);
          background: var(--card-background-color);
        }
        .check-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          min-height: 42px;
          font-size: 13px;
        }
        .check-row input { width: 20px; min-height: 20px; }
        .hint { margin: 0; color: var(--secondary-text-color); font-size: 11px; line-height: 1.4; }
      </style>
      <div class="form">
        <label>
          Karaca cihazı
          <select class="device-select">
            <option value="">Cihaz seçin</option>
            ${this._devices.map((device) => `
              <option value="${escapeHtml(device.id)}" ${device.id === this._config.device_id ? "selected" : ""}>
                ${escapeHtml(device.name)}
              </option>
            `).join("")}
          </select>
        </label>
        <label>
          Kart başlığı (isteğe bağlı)
          <input class="name-input" type="text" value="${escapeHtml(this._config.name ?? "")}" placeholder="Karaca Çaysever">
        </label>
        <label>
          İşlem onayı
          <select class="confirm-select">
            <option value="hold" ${this._config.confirm_type !== "dialog" ? "selected" : ""}>Basılı tut</option>
            <option value="dialog" ${this._config.confirm_type === "dialog" ? "selected" : ""}>Kart içi onay</option>
          </select>
        </label>
        <label class="check-row">
          <span>Tazelik bilgisini göster</span>
          <input class="freshness-check" type="checkbox" ${this._config.show_freshness !== false ? "checked" : ""}>
        </label>
        <label class="check-row">
          <span>Animasyonları kullan</span>
          <input class="animation-check" type="checkbox" ${this._config.animation !== false ? "checked" : ""}>
        </label>
        <p class="hint">Kart, seçilen cihazın Karaca sensör ve anahtarlarını otomatik bulur.</p>
      </div>
    `;

    this.shadowRoot
      .querySelector(".device-select")
      ?.addEventListener("change", (event) => {
        this._configChanged({ device_id: event.target.value });
      });
    this.shadowRoot
      .querySelector(".name-input")
      ?.addEventListener("change", (event) => {
        this._configChanged({ name: event.target.value.trim() });
      });
    this.shadowRoot
      .querySelector(".confirm-select")
      ?.addEventListener("change", (event) => {
        this._configChanged({ confirm_type: event.target.value });
      });
    this.shadowRoot
      .querySelector(".freshness-check")
      ?.addEventListener("change", (event) => {
        this._configChanged({ show_freshness: event.target.checked });
      });
    this.shadowRoot
      .querySelector(".animation-check")
      ?.addEventListener("change", (event) => {
        this._configChanged({ animation: event.target.checked });
      });
  }
}

if (!customElements.get("karaca-connect-card")) {
  customElements.define("karaca-connect-card", KaracaConnectCard);
}

if (!customElements.get("karaca-connect-card-editor")) {
  customElements.define("karaca-connect-card-editor", KaracaConnectCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "karaca-connect-card")) {
  window.customCards.push({
    type: "karaca-connect-card",
    name: "Karaca Connect Card",
    description: "Karaca Çaysever için cihaz kontrollü premium kart.",
    preview: true,
    documentationURL: "https://github.com/yunusuztr/karaca-connect-ha",
  });
}

console.info(
  `%c KARACA-CONNECT-CARD %c ${KARACA_CARD_VERSION} `,
  "color: white; background: #167c75; font-weight: 700;",
  "color: #167c75; background: #dff8f4;",
);
