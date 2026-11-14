"""
Build the complete, bug-free standalone index.html with:
- Full Metropolitan Railway Network (21 lines including GTX-A, Seohae, Light Rails, KTX, ITX, Mugunghwa)
- Non-overlapping optimized station labels with text halos
- Full map default view + Official Seoul Metro Map photo viewer (assets/seoul_metro_map.jpg)
- Exact DP transfer calculation in JS
- 39 certified minimal unique stages across 4 difficulty tiers (쉬움, 중간, 어려움, 초고난이도)
- LocalStorage clear tracking & fixed tooltip/hint bugs
"""

import json

with open("scripts/full_game_data.json", "r", encoding="utf-8") as f:
    game_data = json.load(f)

json_data_str = json.dumps(game_data, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>서울 메트로: 마지막 열차 — 수도권 광역 철도 논리 퍼즐</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070a11;
      --panel-bg: rgba(13, 19, 33, 0.94);
      --card-bg: rgba(24, 35, 58, 0.72);
      --border-color: rgba(64, 93, 140, 0.38);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --accent-amber: #f59e0b;
      --accent-red: #ef4444;
      --accent-purple: #a855f7;
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
      background: rgba(9, 13, 22, 0.96);
      border-bottom: 1px solid var(--border-color);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 20;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .logo-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #00A84D, #0052A4);
      color: white;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
      letter-spacing: 0.8px;
    }}

    .logo-title {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.5px;
      background: linear-gradient(90deg, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .difficulty-tabs {{
      display: flex;
      background: rgba(30, 41, 59, 0.65);
      padding: 3px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      gap: 4px;
    }}

    .diff-btn {{
      padding: 6px 13px;
      font-size: 12.5px;
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
      background: #10b981; color: white; box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }}
    .diff-btn.active[data-diff="중간"] {{
      background: #f59e0b; color: white; box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }}
    .diff-btn.active[data-diff="어려움"] {{
      background: #ef4444; color: white; box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }}
    .diff-btn.active[data-diff="초고난이도"] {{
      background: linear-gradient(135deg, #a855f7, #ec4899);
      color: white;
      box-shadow: 0 0 14px rgba(168, 85, 247, 0.5);
    }}

    .official-map-btn {{
      padding: 7px 13px;
      font-size: 12.5px;
      font-weight: 700;
      border-radius: 8px;
      border: 1px solid rgba(56, 189, 248, 0.5);
      background: rgba(14, 165, 233, 0.15);
      color: #38bdf8;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .official-map-btn:hover {{
      background: rgba(14, 165, 233, 0.3);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
    }}

    /* Main Layout */
    .game-layout {{
      display: flex;
      flex: 1;
      height: calc(100vh - 58px);
      position: relative;
      overflow: hidden;
    }}

    /* Left Sidebar */
    .sidebar {{
      width: 375px;
      background: var(--panel-bg);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      z-index: 10;
      backdrop-filter: blur(12px);
    }}

    .stage-selector-bar {{
      padding: 10px 16px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(9, 13, 22, 0.75);
    }}

    .stage-nav-btn {{
      padding: 6px 10px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: rgba(30, 41, 59, 0.75);
      color: var(--text-main);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .stage-nav-btn:hover {{
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }}

    .stage-select {{
      flex: 1;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 12.5px;
      font-family: var(--font-main);
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}

    .stage-select:focus {{
      border-color: var(--accent-cyan);
    }}

    .sidebar-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-color);
    }}

    .stage-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
    }}

    .stage-title {{
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 6px;
    }}

    .stage-story {{
      font-size: 12.5px;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    .od-card {{
      margin: 12px 18px;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      align-items: center;
      justify-content: space-around;
    }}

    .od-point {{ text-align: center; }}
    .od-label {{ font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 3px; }}
    .od-label.start {{ color: #10b981; }}
    .od-label.end {{ color: #ef4444; }}
    .od-station {{ font-size: 15.5px; font-weight: 700; }}
    .od-arrow {{ font-size: 18px; color: var(--text-muted); }}

    .clues-section {{
      flex: 1;
      padding: 12px 18px;
      overflow-y: auto;
    }}

    .section-title {{
      font-size: 11.5px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .clue-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .clue-item {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      transition: all 0.25s ease;
    }}

    .clue-item.satisfied {{
      border-color: #10b981;
      background: rgba(16, 185, 129, 0.1);
    }}

    .clue-item.violated {{
      border-color: #ef4444;
      background: rgba(239, 68, 68, 0.1);
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

    .clue-item.satisfied .clue-icon {{ background: #10b981; color: white; }}
    .clue-item.violated .clue-icon {{ background: #ef4444; color: white; }}

    .clue-text {{ font-size: 12.5px; line-height: 1.4; }}
    .clue-status {{ font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); align-self: flex-end; }}

    .current-path-bar {{
      padding: 12px 18px;
      background: rgba(15, 23, 42, 0.96);
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .stats-row {{ display: flex; justify-content: space-between; font-size: 12px; }}
    .stat-badge {{ background: rgba(51, 65, 85, 0.7); padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }}
    .route-sequence-preview {{ font-size: 11.5px; color: var(--accent-cyan); white-space: nowrap; overflow-x: auto; padding-bottom: 2px; font-family: 'JetBrains Mono', monospace; }}

    .actions-bar {{
      padding: 12px 18px;
      background: rgba(9, 13, 22, 0.98);
      border-top: 1px solid var(--border-color);
      display: flex;
      gap: 8px;
    }}

    .btn {{
      flex: 1;
      padding: 9px;
      font-size: 12.5px;
      font-weight: 600;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: rgba(30, 41, 59, 0.85);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }}

    .btn:hover {{ background: rgba(51, 65, 85, 0.95); border-color: rgba(148, 163, 184, 0.5); }}
    .btn-primary {{ background: linear-gradient(135deg, #0ea5e9, #3b82f6); border: none; color: white; font-weight: 700; box-shadow: 0 0 14px rgba(14, 165, 233, 0.35); }}
    .btn-primary:hover {{ background: linear-gradient(135deg, #38bdf8, #60a5fa); box-shadow: 0 0 20px rgba(14, 165, 233, 0.55); }}

    /* Map Container */
    .map-container {{
      flex: 1;
      position: relative;
      background: radial-gradient(circle at 50% 50%, #0f172a 0%, #050811 100%);
      overflow: hidden;
      cursor: grab;
    }}

    .map-container:active {{ cursor: grabbing; }}
    svg#metro-svg {{ width: 100%; height: 100%; display: block; }}

    /* Floating Map Controls */
    .map-controls {{
      position: absolute;
      bottom: 20px;
      right: 20px;
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
      font-size: 17px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
      transition: all 0.2s;
    }}

    .control-btn:hover {{ border-color: var(--accent-cyan); color: var(--accent-cyan); }}

    /* Legend Box */
    .legend-panel {{
      position: absolute;
      top: 16px;
      right: 20px;
      background: var(--panel-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 10px 14px;
      z-index: 15;
      max-width: 240px;
      backdrop-filter: blur(10px);
    }}

    .legend-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      color: var(--text-main);
    }}

    .legend-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px 10px;
      margin-top: 8px;
      font-size: 11px;
    }}

    .legend-grid.collapsed {{ display: none; }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 5px;
      color: var(--text-muted);
    }}

    .legend-swatch {{
      width: 12px;
      height: 4px;
      border-radius: 2px;
      flex-shrink: 0;
    }}

    /* Guide Pill */
    .guide-banner {{
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid var(--border-color);
      padding: 7px 16px;
      border-radius: 30px;
      font-size: 12.5px;
      font-weight: 600;
      backdrop-filter: blur(8px);
      color: var(--accent-cyan);
      box-shadow: 0 4px 16px rgba(0,0,0,0.4);
      pointer-events: none;
      z-index: 15;
    }}

    /* Fixed Tooltip */
    #station-tooltip {{
      position: fixed;
      display: none;
      background: rgba(13, 19, 33, 0.96);
      border: 1px solid var(--accent-cyan);
      color: white;
      padding: 7px 12px;
      border-radius: 8px;
      font-size: 12px;
      pointer-events: none;
      z-index: 999;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      line-height: 1.4;
    }}

    /* Modals */
    .modal-overlay {{
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(3, 7, 18, 0.82);
      backdrop-filter: blur(10px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .modal-overlay.active {{ opacity: 1; pointer-events: auto; }}

    .modal-box {{
      background: #111827;
      border: 1px solid rgba(16, 185, 129, 0.5);
      border-radius: 16px;
      padding: 32px;
      width: 440px;
      text-align: center;
      box-shadow: 0 0 40px rgba(16, 185, 129, 0.25);
    }}

    .modal-title {{ font-size: 22px; font-weight: 800; color: #10b981; margin-bottom: 10px; }}
    .modal-desc {{ font-size: 13.5px; color: var(--text-muted); line-height: 1.6; margin-bottom: 20px; }}
    .modal-route {{ background: rgba(31, 41, 55, 0.7); border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: var(--accent-cyan); margin-bottom: 22px; word-break: keep-all; }}

    /* Official Full Map Modal */
    .official-map-modal {{
      width: 92vw;
      height: 90vh;
      background: #0f172a;
      border: 1px solid var(--border-color);
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    .official-map-header {{
      padding: 12px 20px;
      background: #090d16;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .official-map-body {{
      flex: 1;
      overflow: auto;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #ffffff;
      padding: 10px;
    }}

    .official-map-body img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      cursor: zoom-in;
      transition: transform 0.2s ease;
    }}

    .official-map-body img.zoomed {{
      max-width: none;
      max-height: none;
      width: 1800px;
      cursor: zoom-out;
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

    <div class="header-controls">
      <div class="difficulty-tabs">
        <button class="diff-btn active" data-diff="쉬움">쉬움</button>
        <button class="diff-btn" data-diff="중간">중간</button>
        <button class="diff-btn" data-diff="어려움">어려움</button>
        <button class="diff-btn" data-diff="초고난이도">초고난이도 (KTX/GTX)</button>
      </div>
      <button class="official-map-btn" id="btn-open-official-map">
        🗺️ 공식 노선도 원본 전체 보기
      </button>
    </div>
  </header>

  <!-- Main Layout -->
  <div class="game-layout">
    <aside class="sidebar">
      <div class="stage-selector-bar">
        <button class="stage-nav-btn" id="btn-prev-stage" title="이전 스테이지">◀</button>
        <select class="stage-select" id="stage-select"></select>
        <button class="stage-nav-btn" id="btn-next-stage-nav" title="다음 스테이지">▶</button>
        <button class="stage-nav-btn" id="btn-random-stage" title="랜덤 문제">🎲</button>
      </div>

      <div class="sidebar-header">
        <span class="stage-badge" id="sidebar-diff-badge">쉬움 · 스테이지 1</span>
        <h2 class="stage-title" id="stage-title-text">홍대입구 ➔ 여의도</h2>
        <p class="stage-story" id="stage-story-text"></p>
      </div>

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

      <div class="clues-section">
        <div class="section-title">
          <span>제공된 최소 단서 (Minimal Clues)</span>
          <span style="font-size: 10px; color: var(--accent-cyan);">*단서 1개 제거 시 복수 해</span>
        </div>
        <div class="clue-list" id="clue-list-container"></div>
      </div>

      <div class="current-path-bar">
        <div class="stats-row">
          <span>현재 이동 경로</span>
          <span class="stat-badge" id="current-station-count">1역</span>
        </div>
        <div class="route-sequence-preview" id="route-preview-text">홍대입구</div>
        <div class="stats-row" style="margin-top: 2px;">
          <span style="color: var(--text-muted);">최소 환승: <span id="current-transfers-count" style="color: white; font-weight: 600;">0회</span></span>
          <span style="color: var(--text-muted);">한강 도하: <span id="current-river-count" style="color: white; font-weight: 600;">0회</span></span>
        </div>
      </div>

      <div class="actions-bar">
        <button class="btn" id="btn-undo">↩ 취소</button>
        <button class="btn" id="btn-reset">초기화</button>
        <button class="btn btn-primary" id="btn-check">정답 확인</button>
      </div>
    </aside>

    <!-- Map Container -->
    <main class="map-container" id="map-area">
      <div class="guide-banner">
        💡 전체 수도권 철도망이 표시됩니다 · 인접 역을 클릭해 연결하세요 (휠 줌/드래그 지원)
      </div>

      <!-- Collapsible Line Legend -->
      <div class="legend-panel">
        <div class="legend-header" id="legend-toggle">
          <span>🚇 전체 노선 범례 (21개 노선)</span>
          <span id="legend-arrow">▼</span>
        </div>
        <div class="legend-grid" id="legend-grid"></div>
      </div>

      <!-- Full Map ViewBox (1.5x Spread Layout) -->
      <svg id="metro-svg" viewBox="-30 100 2180 1420">
        <defs>
          <filter id="path-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <!-- Han River Ribbon across full map (1.5x scaled) -->
        <g id="han-river-group">
          <path d="M -80 705 Q 375 705, 660 750 T 1050 855 T 1425 840 T 2175 990 L 2175 1050 Q 1425 900, 1050 915 T 660 810 T -80 765 Z"
                fill="rgba(24, 53, 94, 0.4)" stroke="rgba(56, 189, 248, 0.15)" stroke-width="2" />
          <text x="870" y="840" fill="rgba(56, 189, 248, 0.28)" font-size="32" font-weight="700" letter-spacing="14">한  강 (HAN RIVER)</text>
        </g>

        <g id="tracks-layer"></g>
        <g id="user-path-layer"></g>
        <g id="stations-layer"></g>
      </svg>

      <div class="map-controls">
        <button class="control-btn" id="btn-zoom-in" title="확대">+</button>
        <button class="control-btn" id="btn-zoom-out" title="축소">−</button>
        <button class="control-btn" id="btn-zoom-reset" title="전체 지도 보기">⛶</button>
        <button class="control-btn" id="btn-hint" title="다음 역 힌트">💡</button>
      </div>

      <div id="station-tooltip"></div>
    </main>
  </div>

  <!-- Victory Modal -->
  <div class="modal-overlay" id="victory-modal">
    <div class="modal-box">
      <div style="font-size: 46px; margin-bottom: 10px;">🎉</div>
      <h3 class="modal-title">경로 복원 성공!</h3>
      <p class="modal-desc">
        제공된 최소 단서만을 이용하여<br>
        수학적 유일해(Unique Solution)를 완벽히 찾아냈습니다!
      </p>
      <div class="modal-route" id="modal-route-display"></div>
      <button class="btn btn-primary" id="btn-next-stage" style="width: 100%; padding: 12px; font-size: 14.5px;">다음 스테이지로 이동 ➔</button>
    </div>
  </div>

  <!-- Official Map Photo Modal -->
  <div class="modal-overlay" id="official-map-modal">
    <div class="official-map-modal">
      <div class="official-map-header">
        <span style="font-weight: 700; font-size: 15px;">🗺️ 서울 지하철 공식 노선도 원본 (클릭 시 확대/축소)</span>
        <button class="btn" id="btn-close-official-map" style="flex: 0; padding: 6px 14px;">✕ 닫기</button>
      </div>
      <div class="official-map-body">
        <img src="assets/seoul_metro_map.jpg" id="official-map-img" alt="서울 지하철 노선도 전체 원본">
      </div>
    </div>
  </div>

  <script>
    const GAME_DATA = {json_data_str};

    let currentDifficulty = "쉬움";
    let currentStageIndex = 0;
    let currentStage = null;
    let userPath = [];
    let clearedStages = new Set(JSON.parse(localStorage.getItem("seoul_metro_cleared") || "[]"));

    const defaultViewBox = {{ x: -30, y: 100, w: 2180, h: 1420 }};
    let viewBox = {{ ...defaultViewBox }};
    let isPanning = false;
    let panStart = {{ x: 0, y: 0 }};

    const svg = document.getElementById("metro-svg");
    const tracksLayer = document.getElementById("tracks-layer");
    const userPathLayer = document.getElementById("user-path-layer");
    const stationsLayer = document.getElementById("stations-layer");
    const stageSelect = document.getElementById("stage-select");
    const clueListContainer = document.getElementById("clue-list-container");
    const routePreviewText = document.getElementById("route-preview-text");
    const tooltip = document.getElementById("station-tooltip");

    // Sound FX
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 440, type = 'sine', duration = 0.08) {{
      try {{
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.07, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch(e) {{}}
    }}

    function playSuccessChime() {{
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {{
        setTimeout(() => playBeep(freq, 'triangle', 0.25), idx * 120);
      }});
    }}

    // Build Graph
    const adj = {{}};
    for (const stName of Object.keys(GAME_DATA.stations)) adj[stName] = [];
    for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
      for (let i = 0; i < seq.length - 1; i++) {{
        const u = seq[i], v = seq[i+1];
        if (adj[u] && adj[v]) {{
          adj[u].push({{ neighbor: v, line: lineName }});
          adj[v].push({{ neighbor: u, line: lineName }});
        }}
      }}
    }}

    // Build Legend
    const legendGrid = document.getElementById("legend-grid");
    for (const [lineName, color] of Object.entries(GAME_DATA.line_colors)) {{
      if (!GAME_DATA.lines[lineName]) continue;
      const item = document.createElement("div");
      item.className = "legend-item";
      const isSpecial = ["KTX", "ITX-청춘", "무궁화호", "GTX-A"].includes(lineName);
      item.innerHTML = `<span class="legend-swatch" style="background:${{color}}; ${{isSpecial ? 'border-bottom: 2px dashed white;' : ''}}"></span><span>${{lineName}}</span>`;
      legendGrid.appendChild(item);
    }}

    document.getElementById("legend-toggle").addEventListener("click", () => {{
      legendGrid.classList.toggle("collapsed");
      document.getElementById("legend-arrow").textContent = legendGrid.classList.contains("collapsed") ? "▶" : "▼";
    }});

    // Render Tracks
    function renderBaseTracks() {{
      tracksLayer.innerHTML = '';
      for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
        const color = GAME_DATA.line_colors[lineName] || "#999";
        const isSpecial = ["KTX", "ITX-청춘", "무궁화호", "GTX-A"].includes(lineName);
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
            lineEl.setAttribute("stroke-width", isSpecial ? "2.8" : "3.5");
            lineEl.setAttribute("stroke-linecap", "round");
            if (isSpecial) lineEl.setAttribute("stroke-dasharray", "6,5");
            lineEl.setAttribute("opacity", isSpecial ? "0.7" : "0.52");
            tracksLayer.appendChild(lineEl);
          }}
        }}
      }}
    }}

    // Render Stations with Non-Overlapping Computed Coordinates
    function renderStations() {{
      stationsLayer.innerHTML = '';
      for (const [stName, stData] of Object.entries(GAME_DATA.stations)) {{
        const isTransfer = stData.lines.length > 1;
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "station-node");
        g.setAttribute("id", `st-${{stName}}`);
        g.style.cursor = "pointer";

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", stData.x);
        circle.setAttribute("cy", stData.y);
        circle.setAttribute("r", isTransfer ? "6.5" : "4");
        circle.setAttribute("fill", "#ffffff");
        circle.setAttribute("stroke", isTransfer ? "#0f172a" : "#334155");
        circle.setAttribute("stroke-width", isTransfer ? "2.5" : "1.5");
        g.appendChild(circle);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", stData.lx !== undefined ? stData.lx : stData.x);
        text.setAttribute("y", stData.ly !== undefined ? stData.ly : stData.y - 10);
        text.setAttribute("text-anchor", stData.anchor || "middle");
        text.setAttribute("fill", isTransfer ? "#f8fafc" : "#cbd5e1");
        text.setAttribute("font-size", isTransfer ? "10.5" : "9");
        text.setAttribute("font-weight", isTransfer ? "700" : "500");
        text.setAttribute("font-family", "Pretendard, sans-serif");
        text.style.paintOrder = "stroke";
        text.style.stroke = "#070a11";
        text.style.strokeWidth = "3.5px";
        text.style.strokeLinejoin = "round";
        text.textContent = stName;
        g.appendChild(text);

        g.addEventListener("click", (e) => {{ e.stopPropagation(); handleStationClick(stName); }});
        g.addEventListener("mouseenter", (e) => showTooltip(e, stName, stData));
        g.addEventListener("mousemove", moveTooltip);
        g.addEventListener("mouseleave", hideTooltip);

        stationsLayer.appendChild(g);
      }}
    }}

    function showTooltip(e, name, data) {{
      tooltip.style.display = "block";
      tooltip.innerHTML = `<strong>${{name}}</strong><br><span style="color:#94a3b8; font-size:11px;">${{data.lines.join(" · ")}}</span>`;
      moveTooltip(e);
    }}

    function moveTooltip(e) {{
      tooltip.style.left = (e.clientX + 14) + "px";
      tooltip.style.top = (e.clientY + 14) + "px";
    }}

    function hideTooltip() {{
      tooltip.style.display = "none";
    }}

    // Load Stage
    function loadStage(diff, index) {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === diff);
      if (!stages[index]) return;

      currentDifficulty = diff;
      currentStageIndex = index;
      currentStage = stages[index];
      userPath = [currentStage.start];

      // Update Stage Select Dropdown
      stageSelect.innerHTML = '';
      let clearedInDiff = 0;
      stages.forEach((s, i) => {{
        const isCleared = clearedStages.has(s.id);
        if (isCleared) clearedInDiff++;
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = `${{isCleared ? '✓ ' : ''}}#${{i + 1}} ${{s.start}} ➔ ${{s.end}} (${{s.path_length}}역)`;
        if (i === index) opt.selected = true;
        stageSelect.appendChild(opt);
      }});

      const badge = document.getElementById("sidebar-diff-badge");
      badge.textContent = `${{currentStage.difficulty}} · 스테이지 ${{index + 1}} / ${{stages.length}} (클리어: ${{clearedInDiff}})`;
      badge.style.backgroundColor =
        diff === "쉬움" ? "rgba(16, 185, 129, 0.2)" :
        diff === "중간" ? "rgba(245, 158, 11, 0.2)" :
        diff === "어려움" ? "rgba(239, 68, 68, 0.2)" : "rgba(168, 85, 247, 0.25)";
      badge.style.color =
        diff === "쉬움" ? "#10b981" :
        diff === "중간" ? "#f59e0b" :
        diff === "어려움" ? "#ef4444" : "#c084fc";

      document.getElementById("stage-title-text").textContent = currentStage.title;
      document.getElementById("stage-story-text").textContent = currentStage.story;
      document.getElementById("od-start-name").textContent = currentStage.start;
      document.getElementById("od-end-name").textContent = currentStage.end;

      renderClues();
      updatePathUI();
      playBeep(587.33, 'sine', 0.08);
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

    function handleStationClick(stName) {{
      const lastStation = userPath[userPath.length - 1];

      if (stName === lastStation) {{
        if (userPath.length > 1) {{
          userPath.pop();
          playBeep(330, 'sine', 0.08);
          updatePathUI();
        }}
        return;
      }}

      const existingIdx = userPath.indexOf(stName);
      if (existingIdx !== -1) {{
        userPath = userPath.slice(0, existingIdx + 1);
        playBeep(370, 'sine', 0.08);
        updatePathUI();
        return;
      }}

      const isConnected = adj[lastStation].some(edge => edge.neighbor === stName);
      if (!isConnected) {{
        playBeep(180, 'sawtooth', 0.14);
        highlightInvalidStation(stName);
        return;
      }}

      userPath.push(stName);
      playBeep(659.25, 'sine', 0.08);
      updatePathUI();

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
          circle.setAttribute("stroke-width", GAME_DATA.stations[stName].lines.length > 1 ? "2.5" : "1.5");
        }}, 400);
      }}
    }}

    // Exact DP solver for minimum transfers and all valid line sequences (matches Python solver 1:1)
    function getValidLineSequences(path) {{
      if (path.length < 2) return [[]];
      const u0 = path[0], u1 = path[1];
      const initLines = [...new Set(adj[u0].filter(e => e.neighbor === u1).map(e => e.line))].sort();
      let dp = {{}};
      for (const l of initLines) dp[l] = [[l]];

      for (let i = 1; i < path.length - 1; i++) {{
        const u = path[i], v = path[i + 1];
        const validLines = [...new Set(adj[u].filter(e => e.neighbor === v).map(e => e.line))].sort();
        const nextDp = {{}};
        for (const lNext of validLines) {{
          let bestLen = 9999;
          let bestSeqs = [];
          for (const [lPrev, seqsPrev] of Object.entries(dp)) {{
            for (const seqPrev of seqsPrev) {{
              const cand = (lPrev === lNext) ? seqPrev : [...seqPrev, lNext];
              if (cand.length < bestLen) {{
                bestLen = cand.length;
                bestSeqs = [cand];
              }} else if (cand.length === bestLen) {{
                const key = JSON.stringify(cand);
                if (!bestSeqs.some(s => JSON.stringify(s) === key)) bestSeqs.push(cand);
              }}
            }}
          }}
          if (bestSeqs.length > 0) nextDp[lNext] = bestSeqs;
        }}
        dp = nextDp;
      }}

      let allMin = [];
      let minLen = 9999;
      for (const seqList of Object.values(dp)) {{
        for (const s of seqList) {{
          if (s.length < minLen) {{
            minLen = s.length;
            allMin = [s];
          }} else if (s.length === minLen) {{
            const key = JSON.stringify(s);
            if (!allMin.some(x => JSON.stringify(x) === key)) allMin.push(s);
          }}
        }}
      }}
      return allMin;
    }}

    function analyzeUserPath() {{
      if (userPath.length < 2) return {{ transfers: 0, river: 0, seqs: [[]] }};
      const riverPairs = new Set([
        "당산-합정", "합정-당산", "강변-잠실나루", "잠실나루-강변",
        "용산-노량진", "노량진-용산", "옥수-압구정", "압구정-옥수",
        "이촌-동작", "동작-이촌", "여의나루-마포", "마포-여의나루",
        "뚝섬유원지-청담", "청담-뚝섬유원지", "마곡나루-디지털미디어시티", "디지털미디어시티-마곡나루",
        "김포공항-대곡", "대곡-김포공항", "용산-영등포", "영등포-용산", "용산-광명", "광명-용산"
      ]);

      let river = 0;
      for (let i = 0; i < userPath.length - 1; i++) {{
        if (riverPairs.has(`${{userPath[i]}}-${{userPath[i+1]}}`)) river++;
      }}

      const seqs = getValidLineSequences(userPath);
      const minTransfers = seqs.length > 0 && seqs[0].length > 0 ? seqs[0].length - 1 : 0;
      return {{ transfers: minTransfers, river, seqs }};
    }}

    function updatePathUI() {{
      userPathLayer.innerHTML = '';
      const analysis = analyzeUserPath();

      for (let i = 0; i < userPath.length - 1; i++) {{
        const u = GAME_DATA.stations[userPath[i]];
        const v = GAME_DATA.stations[userPath[i+1]];
        if (u && v) {{
          const glow = document.createElementNS("http://www.w3.org/2000/svg", "line");
          glow.setAttribute("x1", u.x); glow.setAttribute("y1", u.y);
          glow.setAttribute("x2", v.x); glow.setAttribute("y2", v.y);
          glow.setAttribute("stroke", "#38bdf8");
          glow.setAttribute("stroke-width", "10");
          glow.setAttribute("stroke-linecap", "round");
          glow.setAttribute("opacity", "0.65");
          glow.setAttribute("filter", "url(#path-glow)");
          userPathLayer.appendChild(glow);

          const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
          line.setAttribute("x1", u.x); line.setAttribute("y1", u.y);
          line.setAttribute("x2", v.x); line.setAttribute("y2", v.y);
          line.setAttribute("stroke", "#ffffff");
          line.setAttribute("stroke-width", "4.5");
          line.setAttribute("stroke-linecap", "round");
          userPathLayer.appendChild(line);
        }}
      }}

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
          circle.setAttribute("stroke-width", isTransfer ? "2.5" : "1.5");
          circle.setAttribute("r", isTransfer ? "6.5" : "4");
        }}
      }}

      document.getElementById("current-station-count").textContent = `${{userPath.length}}역`;
      routePreviewText.textContent = userPath.join(" ➔ ");
      document.getElementById("current-transfers-count").textContent = `${{analysis.transfers}}회`;
      document.getElementById("current-river-count").textContent = `${{analysis.river}}회`;

      currentStage.clues.forEach((clue, idx) => {{
        const item = document.getElementById(`clue-item-${{idx}}`);
        const status = document.getElementById(`clue-status-${{idx}}`);
        let satisfied = false, violated = false, statusText = "진행 중";

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
            satisfied = true; statusText = `경유 완료 (${{clue.val}})`;
          }} else {{
            statusText = `미경유 (${{clue.val}})`;
          }}
        }} else if (clue.type === "avoid_station") {{
          if (userPath.includes(clue.val)) {{
            violated = true; statusText = `위반! (${{clue.val}})`;
          }} else {{
            satisfied = true; statusText = `안전 (${{clue.val}} 미포함)`;
          }}
        }} else if (clue.type === "uses_line") {{
          const used = analysis.seqs.some(s => s.includes(clue.val));
          if (used) {{
            satisfied = true; statusText = `탑승 확인 (${{clue.val}})`;
          }} else {{
            statusText = `미탑승 (${{clue.val}})`;
          }}
        }} else if (clue.type === "line_sequence") {{
          const matched = analysis.seqs.some(s => JSON.stringify(s) === JSON.stringify(clue.val));
          if (matched) {{
            satisfied = true; statusText = `노선 순서 일치`;
          }} else {{
            statusText = `목표: ${{clue.val.join("➔")}}`;
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

    function checkVictoryCondition(manual = true) {{
      const isAtEnd = userPath[userPath.length - 1] === currentStage.end;
      const matchesSolution = JSON.stringify(userPath) === JSON.stringify(currentStage.path);

      if (isAtEnd && matchesSolution) {{
        playSuccessChime();
        clearedStages.add(currentStage.id);
        localStorage.setItem("seoul_metro_cleared", JSON.stringify([...clearedStages]));
        document.getElementById("modal-route-display").textContent = userPath.join(" ➔ ");
        document.getElementById("victory-modal").classList.add("active");
      }} else if (manual) {{
        playBeep(220, 'sawtooth', 0.2);
        alert("아직 모든 최소 단서 조건을 만족하는 유일해가 아닙니다! 단서 판정 상태를 다시 확인해 주세요.");
      }}
    }}

    // Pan & Zoom
    function updateSvgViewBox() {{
      svg.setAttribute("viewBox", `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.w}} ${{viewBox.h}}`);
    }}

    const mapArea = document.getElementById("map-area");
    mapArea.addEventListener("mousedown", (e) => {{
      if (e.target.closest(".station-node") || e.target.closest(".legend-panel")) return;
      isPanning = true;
      panStart = {{ x: e.clientX, y: e.clientY }};
    }});

    window.addEventListener("mousemove", (e) => {{
      if (!isPanning) return;
      const dx = (e.clientX - panStart.x) * (viewBox.w / mapArea.clientWidth);
      const dy = (e.clientY - panStart.y) * (viewBox.h / mapArea.clientHeight);
      viewBox.x -= dx; viewBox.y -= dy;
      panStart = {{ x: e.clientX, y: e.clientY }};
      updateSvgViewBox();
    }});

    window.addEventListener("mouseup", () => isPanning = false);

    mapArea.addEventListener("wheel", (e) => {{
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 1.12 : 0.88;
      const newW = Math.max(400, Math.min(3000, viewBox.w * zoomFactor));
      const newH = Math.max(260, Math.min(1950, viewBox.h * zoomFactor));
      viewBox.x += (viewBox.w - newW) / 2;
      viewBox.y += (viewBox.h - newH) / 2;
      viewBox.w = newW; viewBox.h = newH;
      updateSvgViewBox();
    }}, {{ passive: false }});

    document.getElementById("btn-zoom-in").addEventListener("click", () => {{
      viewBox.x += viewBox.w * 0.1; viewBox.y += viewBox.h * 0.1;
      viewBox.w *= 0.8; viewBox.h *= 0.8;
      updateSvgViewBox();
    }});
    document.getElementById("btn-zoom-out").addEventListener("click", () => {{
      viewBox.x -= viewBox.w * 0.1; viewBox.y -= viewBox.h * 0.1;
      viewBox.w *= 1.2; viewBox.h *= 1.2;
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

    // Fixed Hint Bug: uses currentStage.path
    document.getElementById("btn-hint").addEventListener("click", () => {{
      const sol = currentStage.path;
      for (let i = 0; i < sol.length; i++) {{
        if (userPath[i] !== sol[i]) {{
          alert(`💡 힌트: [${{userPath[i-1] || currentStage.start}}] 다음으로 이동할 올바른 역은 [${{sol[i]}}]입니다!`);
          return;
        }}
      }}
      alert("현재까지의 경로가 완벽합니다!");
    }});

    document.getElementById("btn-next-stage").addEventListener("click", () => {{
      document.getElementById("victory-modal").classList.remove("active");
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      if (currentStageIndex + 1 < stages.length) {{
        loadStage(currentDifficulty, currentStageIndex + 1);
      }} else {{
        const order = ["쉬움", "중간", "어려움", "초고난이도"];
        const nextDiff = order[(order.indexOf(currentDifficulty) + 1) % order.length];
        document.querySelectorAll(".diff-btn").forEach(b => b.classList.toggle("active", b.dataset.diff === nextDiff));
        loadStage(nextDiff, 0);
      }}
    }});

    document.querySelectorAll(".diff-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".diff-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        loadStage(btn.dataset.diff, 0);
      }});
    }});

    // Stage Navigator Listeners
    stageSelect.addEventListener("change", (e) => {{
      loadStage(currentDifficulty, parseInt(e.target.value, 10));
    }});
    document.getElementById("btn-prev-stage").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      const prevIdx = (currentStageIndex - 1 + stages.length) % stages.length;
      loadStage(currentDifficulty, prevIdx);
    }});
    document.getElementById("btn-next-stage-nav").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      const nextIdx = (currentStageIndex + 1) % stages.length;
      loadStage(currentDifficulty, nextIdx);
    }});
    document.getElementById("btn-random-stage").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      const randIdx = Math.floor(Math.random() * stages.length);
      loadStage(currentDifficulty, randIdx);
    }});

    // Official Map Modal Logic
    const officialModal = document.getElementById("official-map-modal");
    const officialImg = document.getElementById("official-map-img");
    document.getElementById("btn-open-official-map").addEventListener("click", () => officialModal.classList.add("active"));
    document.getElementById("btn-close-official-map").addEventListener("click", () => officialModal.classList.remove("active"));
    officialImg.addEventListener("click", () => officialImg.classList.toggle("zoomed"));

    renderBaseTracks();
    renderStations();
    loadStage("쉬움", 0);
  </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("index.html built successfully with 39 stages and full map!")
