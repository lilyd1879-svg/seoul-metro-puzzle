"""
Generate the standalone index.html with all styles, scripts, SVG map, and puzzle data.
"""
import json

with open("scripts/final_curated_data.json", "r", encoding="utf-8") as f:
    game_data = json.load(f)

json_data_str = json.dumps(game_data, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>서울 메트로: 마지막 열차 (Seoul Metro: The Missing Route)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #0a0e17;
      --panel-bg: rgba(16, 23, 38, 0.92);
      --card-bg: rgba(26, 38, 64, 0.7);
      --border-color: rgba(64, 93, 140, 0.35);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --accent-amber: #f59e0b;
      --accent-red: #ef4444;
      --font-main: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}

    body {{
      font-family: var(--font-main);
      background-color: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    /* Header */
    header {{
      background: rgba(10, 14, 23, 0.95);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 20;
      backdrop-filter: blur(10px);
    }}

    .logo-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #00A84D, #0052A4);
      color: white;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
      letter-spacing: 1px;
    }}

    .logo-title {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.5px;
      background: linear-gradient(90deg, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .difficulty-tabs {{
      display: flex;
      background: rgba(30, 41, 59, 0.6);
      padding: 3px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      gap: 4px;
    }}

    .diff-btn {{
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .diff-btn:hover {{
      color: var(--text-main);
    }}

    .diff-btn.active[data-diff="쉬움"] {{
      background: #10b981;
      color: white;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }}
    .diff-btn.active[data-diff="중간"] {{
      background: #f59e0b;
      color: white;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }}
    .diff-btn.active[data-diff="어려움"] {{
      background: #ef4444;
      color: white;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }}

    .stage-pills {{
      display: flex;
      gap: 8px;
    }}

    .stage-pill {{
      padding: 5px 12px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: rgba(30, 41, 59, 0.6);
      color: var(--text-muted);
      font-size: 13px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    }}

    .stage-pill:hover {{
      border-color: var(--accent-cyan);
      color: var(--text-main);
    }}

    .stage-pill.active {{
      background: rgba(6, 182, 212, 0.15);
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }}

    /* Main Container */
    .game-layout {{
      display: flex;
      flex: 1;
      height: calc(100vh - 65px);
      position: relative;
    }}

    /* Left Sidebar: Mission & Clues */
    .sidebar {{
      width: 360px;
      background: var(--panel-bg);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      z-index: 10;
      backdrop-filter: blur(12px);
    }}

    .sidebar-header {{
      padding: 20px;
      border-bottom: 1px solid var(--border-color);
    }}

    .stage-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 8px;
      text-transform: uppercase;
    }}

    .stage-title {{
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.3;
    }}

    .stage-story {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    .od-card {{
      margin: 16px 20px;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 14px;
      display: flex;
      align-items: center;
      justify-content: space-around;
    }}

    .od-point {{
      text-align: center;
    }}

    .od-label {{
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}

    .od-label.start {{ color: #10b981; }}
    .od-label.end {{ color: #ef4444; }}

    .od-station {{
      font-size: 16px;
      font-weight: 700;
    }}

    .od-arrow {{
      font-size: 18px;
      color: var(--text-muted);
    }}

    /* Clues Section */
    .clues-section {{
      flex: 1;
      padding: 16px 20px;
      overflow-y: auto;
    }}

    .section-title {{
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .clue-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .clue-item {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: all 0.25s ease;
      position: relative;
    }}

    .clue-item.satisfied {{
      border-color: #10b981;
      background: rgba(16, 185, 129, 0.08);
    }}

    .clue-item.violated {{
      border-color: #ef4444;
      background: rgba(239, 68, 68, 0.08);
    }}

    .clue-top {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }}

    .clue-icon {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: rgba(148, 163, 184, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      flex-shrink: 0;
      margin-top: 1px;
    }}

    .clue-item.satisfied .clue-icon {{
      background: #10b981;
      color: white;
    }}

    .clue-item.violated .clue-icon {{
      background: #ef4444;
      color: white;
    }}

    .clue-text {{
      font-size: 13px;
      line-height: 1.4;
      color: var(--text-main);
    }}

    .clue-status {{
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-muted);
      align-self: flex-end;
    }}

    /* Current Path Stats Bar */
    .current-path-bar {{
      padding: 14px 20px;
      background: rgba(15, 23, 42, 0.95);
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .stats-row {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
    }}

    .stat-badge {{
      background: rgba(51, 65, 85, 0.6);
      padding: 3px 8px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .route-sequence-preview {{
      font-size: 12px;
      color: var(--accent-cyan);
      white-space: nowrap;
      overflow-x: auto;
      padding-bottom: 2px;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* Actions */
    .actions-bar {{
      padding: 16px 20px;
      background: rgba(10, 14, 23, 0.98);
      border-top: 1px solid var(--border-color);
      display: flex;
      gap: 8px;
    }}

    .btn {{
      flex: 1;
      padding: 10px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: rgba(30, 41, 59, 0.8);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }}

    .btn:hover {{
      background: rgba(51, 65, 85, 0.9);
      border-color: rgba(148, 163, 184, 0.5);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #0ea5e9, #3b82f6);
      border: none;
      color: white;
      font-weight: 700;
      box-shadow: 0 0 15px rgba(14, 165, 233, 0.35);
    }}

    .btn-primary:hover {{
      background: linear-gradient(135deg, #38bdf8, #60a5fa);
      box-shadow: 0 0 20px rgba(14, 165, 233, 0.55);
    }}

    /* Canvas / SVG Map Area */
    .map-container {{
      flex: 1;
      position: relative;
      background: radial-gradient(circle at 50% 50%, #111827 0%, #070a11 100%);
      overflow: hidden;
      cursor: grab;
    }}

    .map-container:active {{
      cursor: grabbing;
    }}

    svg#metro-svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    /* Floating Map Controls */
    .map-controls {{
      position: absolute;
      bottom: 24px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 15;
    }}

    .control-btn {{
      width: 38px;
      height: 38px;
      background: var(--panel-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-main);
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      transition: all 0.2s;
    }}

    .control-btn:hover {{
      background: rgba(30, 41, 59, 0.9);
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }}

    /* Guide Pill Overlay */
    .guide-banner {{
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid var(--border-color);
      padding: 8px 18px;
      border-radius: 30px;
      font-size: 13px;
      font-weight: 600;
      backdrop-filter: blur(8px);
      color: var(--accent-cyan);
      box-shadow: 0 4px 16px rgba(0,0,0,0.4);
      pointer-events: none;
      z-index: 15;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Modal */
    .modal-overlay {{
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(3, 7, 18, 0.75);
      backdrop-filter: blur(10px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}

    .modal-overlay.active {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-box {{
      background: #111827;
      border: 1px solid rgba(16, 185, 129, 0.5);
      border-radius: 16px;
      padding: 32px;
      width: 440px;
      text-align: center;
      box-shadow: 0 0 40px rgba(16, 185, 129, 0.25);
      transform: scale(0.95);
      transition: transform 0.3s ease;
    }}

    .modal-overlay.active .modal-box {{
      transform: scale(1);
    }}

    .modal-title {{
      font-size: 24px;
      font-weight: 800;
      color: #10b981;
      margin-bottom: 12px;
    }}

    .modal-desc {{
      font-size: 14px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 24px;
    }}

    .modal-route {{
      background: rgba(31, 41, 55, 0.6);
      border-radius: 8px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: var(--accent-cyan);
      margin-bottom: 24px;
      word-break: keep-all;
    }}

    /* Tooltip */
    #station-tooltip {{
      position: absolute;
      display: none;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid var(--accent-cyan);
      color: white;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      pointer-events: none;
      z-index: 50;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="logo-group">
      <span class="logo-badge">SEOUL METRO</span>
      <h1 class="logo-title">마지막 열차 (The Missing Route)</h1>
    </div>

    <!-- Difficulty Tabs -->
    <div class="difficulty-tabs">
      <button class="diff-btn active" data-diff="쉬움">쉬움</button>
      <button class="diff-btn" data-diff="중간">중간</button>
      <button class="diff-btn" data-diff="어려움">어려움</button>
    </div>

    <!-- Stage Pills -->
    <div class="stage-pills" id="stage-pills-container">
      <!-- Injected by JS -->
    </div>
  </header>

  <!-- Game Layout -->
  <div class="game-layout">
    <!-- Left Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="stage-badge" id="sidebar-diff-badge">쉬움 · 스테이지 1</span>
        <h2 class="stage-title" id="stage-title-text">홍대에서 여의도</h2>
        <p class="stage-story" id="stage-story-text">퇴근 시간 여의도로 향하는 승객의 지름길을 복원하세요.</p>
      </div>

      <!-- Origin & Destination -->
      <div class="od-card">
        <div class="od-point">
          <div class="od-label start">START · 출발</div>
          <div class="od-station" id="od-start-name">홍대입구</div>
        </div>
        <div class="od-arrow">➔</div>
        <div class="od-point">
          <div class="od-label end">DEST · 도착</div>
          <div class="od-station" id="od-end-name">여의도</div>
        </div>
      </div>

      <!-- Clues List -->
      <div class="clues-section">
        <div class="section-title">
          <span>제공된 최소 단서 (Minimal Clues)</span>
          <span style="font-size: 10px; color: var(--accent-cyan);">*단서 1개 제거 시 복수 해</span>
        </div>
        <div class="clue-list" id="clue-list-container">
          <!-- Injected by JS -->
        </div>
      </div>

      <!-- Real-time Path Stats -->
      <div class="current-path-bar">
        <div class="stats-row">
          <span>현재 이동 경로</span>
          <span class="stat-badge" id="current-station-count">1 / 5역</span>
        </div>
        <div class="route-sequence-preview" id="route-preview-text">
          홍대입구
        </div>
        <div class="stats-row" style="margin-top: 4px;">
          <span style="color: var(--text-muted);">환승 횟수: <span id="current-transfers-count" style="color: white; font-weight: 600;">0회</span></span>
          <span style="color: var(--text-muted);">한강 도하: <span id="current-river-count" style="color: white; font-weight: 600;">0회</span></span>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-bar">
        <button class="btn" id="btn-undo">↩ 한 단계 취소</button>
        <button class="btn" id="btn-reset">초기화</button>
        <button class="btn btn-primary" id="btn-check">정답 확인</button>
      </div>
    </aside>

    <!-- Map Area -->
    <main class="map-container" id="map-area">
      <div class="guide-banner" id="guide-banner">
        <span>💡 다음 정차역을 클릭하여 노선을 연결하세요</span>
      </div>

      <svg id="metro-svg" viewBox="150 140 750 540">
        <defs>
          <!-- Han River Glow Filter -->
          <filter id="river-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <!-- Route Line Glow -->
          <filter id="path-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <!-- Han River Path -->
        <g id="han-river-group">
          <!-- River ribbon -->
          <path d="M 100 370 Q 250 370, 360 410 T 500 480 T 670 460 T 950 530 L 950 560 Q 670 490, 500 510 T 360 440 T 100 400 Z"
                fill="rgba(24, 53, 94, 0.45)" stroke="rgba(56, 189, 248, 0.15)" stroke-width="1.5" />
          <text x="360" y="430" fill="rgba(56, 189, 248, 0.25)" font-size="20" font-weight="700" letter-spacing="8">한  강 (HAN RIVER)</text>
        </g>

        <!-- Subway Network Tracks Background -->
        <g id="tracks-layer"></g>

        <!-- User Selected Path Layer -->
        <g id="user-path-layer"></g>

        <!-- Stations Layer -->
        <g id="stations-layer"></g>
      </svg>

      <!-- Zoom / Controls -->
      <div class="map-controls">
        <button class="control-btn" id="btn-zoom-in" title="확대">+</button>
        <button class="control-btn" id="btn-zoom-out" title="축소">−</button>
        <button class="control-btn" id="btn-zoom-reset" title="원래 크기">⟲</button>
        <button class="control-btn" id="btn-hint" title="힌트">💡</button>
      </div>

      <!-- Station Tooltip -->
      <div id="station-tooltip"></div>
    </main>
  </div>

  <!-- Victory Modal -->
  <div class="modal-overlay" id="victory-modal">
    <div class="modal-box">
      <div style="font-size: 48px; margin-bottom: 12px;">🎉</div>
      <h3 class="modal-title">경로 복원 완료!</h3>
      <p class="modal-desc">
        제공된 최소 단서만을 이용하여<br>
        수학적 유일해(Unique Solution)를 정확히 연역해냈습니다!
      </p>
      <div class="modal-route" id="modal-route-display">
        홍대입구 ➔ 합정 ➔ 당산 ➔ 국회의사당 ➔ 여의도
      </div>
      <button class="btn btn-primary" id="btn-next-stage" style="width: 100%; padding: 12px; font-size: 15px;">다음 스테이지로 이동 ➔</button>
    </div>
  </div>

  <script>
    const GAME_DATA = {json_data_str};

    // State
    let currentDifficulty = "쉬움";
    let currentStageIndex = 0;
    let currentStage = null;
    let userPath = [];

    // Pan & Zoom State
    let viewBox = {{ x: 150, y: 140, w: 750, h: 540 }};
    const defaultViewBox = {{ x: 150, y: 140, w: 750, h: 540 }};
    let isPanning = false;
    let panStart = {{ x: 0, y: 0 }};

    // DOM Elements
    const svg = document.getElementById("metro-svg");
    const tracksLayer = document.getElementById("tracks-layer");
    const userPathLayer = document.getElementById("user-path-layer");
    const stationsLayer = document.getElementById("stations-layer");
    const stagePillsContainer = document.getElementById("stage-pills-container");
    const clueListContainer = document.getElementById("clue-list-container");
    const routePreviewText = document.getElementById("route-preview-text");
    const tooltip = document.getElementById("station-tooltip");

    // Sound FX via Web Audio API
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 440, type = 'sine', duration = 0.08) {{
      try {{
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch(e) {{}}
    }}

    function playSuccessChime() {{
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {{
        setTimeout(() => playBeep(freq, 'triangle', 0.25), idx * 120);
      }});
    }}

    // Initialize Network Graph
    const adj = {{}};
    for (const [stName, stData] of Object.entries(GAME_DATA.stations)) {{
      adj[stName] = [];
    }}
    for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
      for (let i = 0; i < seq.length - 1; i++) {{
        const u = seq[i], v = seq[i+1];
        if (adj[u] && adj[v]) {{
          adj[u].push({{ neighbor: v, line: lineName }});
          adj[v].push({{ neighbor: u, line: lineName }});
        }}
      }}
    }}

    // Render Base Tracks Layer
    function renderBaseTracks() {{
      tracksLayer.innerHTML = '';
      for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
        const color = GAME_DATA.line_colors[lineName] || "#999";
        for (let i = 0; i < seq.length - 1; i++) {{
          const u = GAME_DATA.stations[seq[i]];
          const v = GAME_DATA.stations[seq[i+1]];
          if (u && v) {{
            const lineEl = document.createElementNS("http://www.w3.org/2000/svg", "line");
            lineEl.setAttribute("x1", u.x);
            lineEl.setAttribute("y1", u.y);
            lineEl.setAttribute("x2", v.x);
            lineEl.setAttribute("y2", v.y);
            lineEl.setAttribute("stroke", color);
            lineEl.setAttribute("stroke-width", "4");
            lineEl.setAttribute("stroke-linecap", "round");
            lineEl.setAttribute("opacity", "0.55");
            tracksLayer.appendChild(lineEl);
          }}
        }}
      }}
    }}

    // Render Stations Layer
    function renderStations() {{
      stationsLayer.innerHTML = '';
      for (const [stName, stData] of Object.entries(GAME_DATA.stations)) {{
        const isTransfer = stData.lines.length > 1;
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "station-node");
        g.setAttribute("id", `st-${{stName}}`);
        g.style.cursor = "pointer";

        // Station Outer Ring
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", stData.x);
        circle.setAttribute("cy", stData.y);
        circle.setAttribute("r", isTransfer ? "7" : "4.5");
        circle.setAttribute("fill", "#ffffff");
        circle.setAttribute("stroke", isTransfer ? "#0f172a" : "#334155");
        circle.setAttribute("stroke-width", isTransfer ? "3" : "1.5");
        g.appendChild(circle);

        // Station Label
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", stData.x);
        text.setAttribute("y", stData.y - (isTransfer ? 10 : 8));
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("fill", "#cbd5e1");
        text.setAttribute("font-size", isTransfer ? "11" : "9.5");
        text.setAttribute("font-weight", isTransfer ? "700" : "500");
        text.setAttribute("font-family", "Pretendard, sans-serif");
        text.style.textShadow = "0 1px 4px rgba(0,0,0,0.9)";
        text.textContent = stName;
        g.appendChild(text);

        // Events
        g.addEventListener("click", () => handleStationClick(stName));
        g.addEventListener("mouseenter", (e) => showTooltip(e, stName, stData));
        g.addEventListener("mouseleave", hideTooltip);

        stationsLayer.appendChild(g);
      }}
    }}

    function showTooltip(e, name, data) {{
      tooltip.style.display = "block";
      tooltip.innerHTML = `<strong>${{name}}</strong><br><span style="color:#94a3b8; font-size:11px;">${{data.lines.join(", ")}}</span>`;
      moveTooltip(e);
    }}

    function moveTooltip(e) {{
      const rect = svg.getBoundingClientRect();
      tooltip.style.left = (e.clientX + 14) + "px";
      tooltip.style.top = (e.clientY + 14) + "px";
    }}

    function hideTooltip() {{
      tooltip.style.display = "none";
    }}

    // Setup Stage
    function loadStage(diff, index) {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === diff);
      if (!stages[index]) return;

      currentDifficulty = diff;
      currentStageIndex = index;
      currentStage = stages[index];
      userPath = [currentStage.start]; // Start with start station

      // Update Header Pills
      stagePillsContainer.innerHTML = '';
      stages.forEach((s, i) => {{
        const pill = document.createElement("button");
        pill.className = `stage-pill ${{i === index ? 'active' : ''}}`;
        pill.textContent = `스테이지 ${{i + 1}}`;
        pill.addEventListener("click", () => loadStage(diff, i));
        stagePillsContainer.appendChild(pill);
      }});

      // Update Sidebar Info
      document.getElementById("sidebar-diff-badge").textContent = `${{currentStage.difficulty}} · 스테이지 ${{index + 1}}`;
      document.getElementById("sidebar-diff-badge").style.backgroundColor = 
        diff === "쉬움" ? "rgba(16, 185, 129, 0.2)" :
        diff === "중간" ? "rgba(245, 158, 11, 0.2)" : "rgba(239, 68, 68, 0.2)";
      document.getElementById("sidebar-diff-badge").style.color =
        diff === "쉬움" ? "#10b981" :
        diff === "중간" ? "#f59e0b" : "#ef4444";

      document.getElementById("stage-title-text").textContent = currentStage.title;
      document.getElementById("stage-story-text").textContent = currentStage.story;
      document.getElementById("od-start-name").textContent = currentStage.start;
      document.getElementById("od-end-name").textContent = currentStage.end;

      // Render Clues
      renderClues();
      updatePathUI();
      centerViewOnStations([currentStage.start, currentStage.end]);
      playBeep(587.33, 'sine', 0.1);
    }}

    function renderClues() {{
      clueListContainer.innerHTML = '';
      currentStage.clues.forEach((clue, idx) => {{
        const item = document.createElement("div");
        item.className = "clue-item";
        item.id = `clue-item-${{idx}}`;

        item.innerHTML = `
          <div class="clue-top">
            <div class="clue-icon">?</div>
            <div class="clue-text">${{clue.text}}</div>
          </div>
          <div class="clue-status" id="clue-status-${{idx}}">진행 중</div>
        `;
        clueListContainer.appendChild(item);
      }});
    }}

    // Handle Station Click
    function handleStationClick(stName) {{
      const lastStation = userPath[userPath.length - 1];

      // If clicked last station, undo it (unless it's start)
      if (stName === lastStation) {{
        if (userPath.length > 1) {{
          userPath.pop();
          playBeep(330, 'sine', 0.08);
          updatePathUI();
        }}
        return;
      }}

      // If clicked a station already in path, truncate path back to it
      const existingIdx = userPath.indexOf(stName);
      if (existingIdx !== -1) {{
        userPath = userPath.slice(0, existingIdx + 1);
        playBeep(370, 'sine', 0.08);
        updatePathUI();
        return;
      }}

      // Check if stName is adjacent to lastStation
      const isConnected = adj[lastStation].some(edge => edge.neighbor === stName);
      if (!isConnected) {{
        playBeep(180, 'sawtooth', 0.15); // error beep
        highlightInvalidStation(stName);
        return;
      }}

      // Add to path
      userPath.push(stName);
      playBeep(659.25, 'sine', 0.08);
      updatePathUI();

      // Check if reached destination
      if (stName === currentStage.end) {{
        checkVictoryCondition(false);
      }}
    }}

    function highlightInvalidStation(stName) {{
      const g = document.getElementById(`st-${{stName}}`);
      if (g) {{
        const circle = g.querySelector("circle");
        const origStroke = circle.getAttribute("stroke");
        circle.setAttribute("stroke", "#ef4444");
        circle.setAttribute("stroke-width", "5");
        setTimeout(() => {{
          circle.setAttribute("stroke", origStroke);
          circle.setAttribute("stroke-width", GAME_DATA.stations[stName].lines.length > 1 ? "3" : "1.5");
        }}, 400);
      }}
    }}

    // Calculate lines and transfers
    function analyzeUserPath() {{
      if (userPath.length < 2) return {{ transfers: 0, river: 0, lines: [] }};

      let transfers = 0;
      let river = 0;
      let currentLine = null;
      const linesUsed = [];

      // Han River Crossings reference
      const riverPairs = new Set([
        "당산-합정", "합정-당산", "강변-잠실나루", "잠실나루-강변",
        "용산-노량진", "노량진-용산", "옥수-압구정", "압구정-옥수",
        "이촌-동작", "동작-이촌", "여의나루-마포", "마포-여의나루",
        "건대입구-청담", "청담-건대입구"
      ]);

      for (let i = 0; i < userPath.length - 1; i++) {{
        const u = userPath[i], v = userPath[i+1];
        const pair = `${{u}}-${{v}}`;
        if (riverPairs.has(pair)) river++;

        // Find common line between u and v
        const commonLines = adj[u].filter(edge => edge.neighbor === v).map(e => e.line);
        let chosenLine = commonLines[0];
        if (currentLine && commonLines.includes(currentLine)) {{
          chosenLine = currentLine;
        }}

        if (currentLine && chosenLine !== currentLine) {{
          transfers++;
        }}
        currentLine = chosenLine;
        if (!linesUsed.includes(chosenLine)) linesUsed.push(chosenLine);
      }}

      return {{ transfers, river, lines: linesUsed }};
    }}

    // Update Path Visualization & Clue Badges
    function updatePathUI() {{
      userPathLayer.innerHTML = '';
      const analysis = analyzeUserPath();

      // Render glowing user path segments
      for (let i = 0; i < userPath.length - 1; i++) {{
        const u = GAME_DATA.stations[userPath[i]];
        const v = GAME_DATA.stations[userPath[i+1]];
        if (u && v) {{
          // Glowing underline
          const glow = document.createElementNS("http://www.w3.org/2000/svg", "line");
          glow.setAttribute("x1", u.x); glow.setAttribute("y1", u.y);
          glow.setAttribute("x2", v.x); glow.setAttribute("y2", v.y);
          glow.setAttribute("stroke", "#38bdf8");
          glow.setAttribute("stroke-width", "10");
          glow.setAttribute("stroke-linecap", "round");
          glow.setAttribute("opacity", "0.6");
          glow.setAttribute("filter", "url(#path-glow)");
          userPathLayer.appendChild(glow);

          // Solid line
          const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
          line.setAttribute("x1", u.x); line.setAttribute("y1", u.y);
          line.setAttribute("x2", v.x); line.setAttribute("y2", v.y);
          line.setAttribute("stroke", "#f8fafc");
          line.setAttribute("stroke-width", "5");
          line.setAttribute("stroke-linecap", "round");
          userPathLayer.appendChild(line);
        }}
      }}

      // Highlight station markers
      for (const [stName, stData] of Object.entries(GAME_DATA.stations)) {{
        const g = document.getElementById(`st-${{stName}}`);
        if (!g) continue;
        const circle = g.querySelector("circle");
        const isStart = stName === currentStage.start;
        const isEnd = stName === currentStage.end;
        const inPath = userPath.includes(stName);

        if (isStart) {{
          circle.setAttribute("fill", "#10b981");
          circle.setAttribute("stroke", "#ffffff");
          circle.setAttribute("stroke-width", "3");
          circle.setAttribute("r", "9");
        }} else if (isEnd) {{
          circle.setAttribute("fill", "#ef4444");
          circle.setAttribute("stroke", "#ffffff");
          circle.setAttribute("stroke-width", "3");
          circle.setAttribute("r", "9");
        }} else if (inPath) {{
          circle.setAttribute("fill", "#38bdf8");
          circle.setAttribute("stroke", "#0f172a");
          circle.setAttribute("stroke-width", "2.5");
          circle.setAttribute("r", "7");
        }} else {{
          const isTransfer = stData.lines.length > 1;
          circle.setAttribute("fill", "#ffffff");
          circle.setAttribute("stroke", isTransfer ? "#0f172a" : "#334155");
          circle.setAttribute("stroke-width", isTransfer ? "3" : "1.5");
          circle.setAttribute("r", isTransfer ? "7" : "4.5");
        }}
      }}

      // Sidebar Realtime Stats
      document.getElementById("current-station-count").textContent = `${{userPath.length}} / ${{currentStage.path_length}}역`;
      document.getElementById("route-preview-text").textContent = userPath.join(" ➔ ");
      document.getElementById("current-transfers-count").textContent = `${{analysis.transfers}}회`;
      document.getElementById("current-river-count").textContent = `${{analysis.river}}회`;

      // Clue Verification Feedback
      currentStage.clues.forEach((clue, idx) => {{
        const item = document.getElementById(`clue-item-${{idx}}`);
        const status = document.getElementById(`clue-status-${{idx}}`);
        let satisfied = false;
        let violated = false;
        let statusText = "진행 중";

        if (clue.type === "total_stations") {{
          statusText = `${{userPath.length}} / ${{clue.val}}역`;
          if (userPath.length === clue.val) satisfied = true;
          else if (userPath.length > clue.val) violated = true;
        }} else if (clue.type === "transfer_count") {{
          statusText = `현재 ${{analysis.transfers}}회 / 목표 ${{clue.val}}회`;
          if (analysis.transfers === clue.val) satisfied = true;
          else if (analysis.transfers > clue.val) violated = true;
        }} else if (clue.type === "river_crossings") {{
          statusText = `현재 ${{analysis.river}}회 / 목표 ${{clue.val}}회`;
          if (analysis.river === clue.val) satisfied = true;
          else if (analysis.river > clue.val) violated = true;
        }} else if (clue.type === "via_station") {{
          if (userPath.includes(clue.val)) {{
            satisfied = true;
            statusText = `경유 완료 (${{clue.val}})`;
          }} else {{
            statusText = `미경유 (${{clue.val}})`;
          }}
        }} else if (clue.type === "avoid_station") {{
          if (userPath.includes(clue.val)) {{
            violated = true;
            statusText = `위반! (${{clue.val}} 포함됨)`;
          }} else {{
            satisfied = true;
            statusText = `안전 (${{clue.val}} 미포함)`;
          }}
        }}

        item.classList.remove("satisfied", "violated");
        if (satisfied) {{
          item.classList.add("satisfied");
          item.querySelector(".clue-icon").textContent = "✓";
        }} else if (violated) {{
          item.classList.add("violated");
          item.querySelector(".clue-icon").textContent = "✗";
        }} else {{
          item.querySelector(".clue-icon").textContent = "?";
        }}
        status.textContent = statusText;
      }});
    }}

    // Check Victory
    function checkVictoryCondition(manual = true) {{
      const isAtEnd = userPath[userPath.length - 1] === currentStage.end;
      const isCorrectLength = userPath.length === currentStage.path_length;
      const matchesSolution = JSON.stringify(userPath) === JSON.stringify(currentStage.path);

      if (isAtEnd && matchesSolution) {{
        playSuccessChime();
        document.getElementById("modal-route-display").textContent = userPath.join(" ➔ ");
        document.getElementById("victory-modal").classList.add("active");
      }} else if (manual) {{
        playBeep(220, 'sawtooth', 0.2);
        alert("아직 단서 조건을 모두 만족하는 정답 경로가 아닙니다! 단서와 정차역 수를 다시 확인해보세요.");
      }}
    }}

    // Pan & Zoom Implementation
    function updateSvgViewBox() {{
      svg.setAttribute("viewBox", `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.w}} ${{viewBox.h}}`);
    }}

    function centerViewOnStations(stNames) {{
      let minX = 9999, maxX = -9999, minY = 9999, maxY = -9999;
      stNames.forEach(name => {{
        const st = GAME_DATA.stations[name];
        if (st) {{
          minX = Math.min(minX, st.x);
          maxX = Math.max(maxX, st.x);
          minY = Math.min(minY, st.y);
          maxY = Math.max(maxY, st.y);
        }}
      }});
      const cx = (minX + maxX) / 2;
      const cy = (minY + maxY) / 2;
      const w = 600, h = 450;
      viewBox = {{ x: cx - w/2, y: cy - h/2, w, h }};
      updateSvgViewBox();
    }}

    const mapArea = document.getElementById("map-area");
    mapArea.addEventListener("mousedown", (e) => {{
      if (e.target.closest(".station-node")) return;
      isPanning = true;
      panStart = {{ x: e.clientX, y: e.clientY }};
    }});

    window.addEventListener("mousemove", (e) => {{
      if (!isPanning) return;
      const dx = (e.clientX - panStart.x) * (viewBox.w / mapArea.clientWidth);
      const dy = (e.clientY - panStart.y) * (viewBox.h / mapArea.clientHeight);
      viewBox.x -= dx;
      viewBox.y -= dy;
      panStart = {{ x: e.clientX, y: e.clientY }};
      updateSvgViewBox();
    }});

    window.addEventListener("mouseup", () => isPanning = false);

    mapArea.addEventListener("wheel", (e) => {{
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
      const newW = Math.max(300, Math.min(1200, viewBox.w * zoomFactor));
      const newH = Math.max(225, Math.min(900, viewBox.h * zoomFactor));
      viewBox.x += (viewBox.w - newW) / 2;
      viewBox.y += (viewBox.h - newH) / 2;
      viewBox.w = newW;
      viewBox.h = newH;
      updateSvgViewBox();
    }}, {{ passive: false }});

    // Buttons & Controls
    document.getElementById("btn-zoom-in").addEventListener("click", () => {{
      viewBox.w *= 0.85; viewBox.h *= 0.85;
      updateSvgViewBox();
    }});
    document.getElementById("btn-zoom-out").addEventListener("click", () => {{
      viewBox.w *= 1.15; viewBox.h *= 1.15;
      updateSvgViewBox();
    }});
    document.getElementById("btn-zoom-reset").addEventListener("click", () => {{
      viewBox = {{ ...defaultViewBox }};
      updateSvgViewBox();
    }});

    document.getElementById("btn-undo").addEventListener("click", () => {{
      if (userPath.length > 1) {{
        userPath.pop();
        playBeep(330, 'sine', 0.08);
        updatePathUI();
      }}
    }});

    document.getElementById("btn-reset").addEventListener("click", () => {{
      userPath = [currentStage.start];
      playBeep(260, 'sine', 0.1);
      updatePathUI();
    }});

    document.getElementById("btn-check").addEventListener("click", () => checkVictoryCondition(true));

    document.getElementById("btn-hint").addEventListener("click", () => {{
      const sol = currentStage.solution;
      for (let i = 0; i < sol.length; i++) {{
        if (userPath[i] !== sol[i]) {{
          alert(`💡 힌트: 다음 올바른 역은 [${{sol[i]}}]입니다!`);
          return;
        }}
      }}
      alert("현재까지의 경로는 완벽합니다! 계속해서 다음 역으로 나아가세요.");
    }});

    document.getElementById("btn-next-stage").addEventListener("click", () => {{
      document.getElementById("victory-modal").classList.remove("active");
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      if (currentStageIndex + 1 < stages.length) {{
        loadStage(currentDifficulty, currentStageIndex + 1);
      }} else {{
        // Move to next difficulty
        const nextDiff = currentDifficulty === "쉬움" ? "중간" : currentDifficulty === "중간" ? "어려움" : "쉬움";
        document.querySelectorAll(".diff-btn").forEach(b => {{
          b.classList.toggle("active", b.dataset.diff === nextDiff);
        }});
        loadStage(nextDiff, 0);
      }}
    }});

    // Difficulty buttons
    document.querySelectorAll(".diff-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".diff-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        loadStage(btn.dataset.diff, 0);
      }});
    }});

    // Init
    renderBaseTracks();
    renderStations();
    loadStage("쉬움", 0);
  </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("index.html built successfully!")
