"""
Build standalone sejong_bus.html for Sejong City Bus & BRT Logic Puzzle:
- 15 real Sejong City Bus & BRT lines (B0, B1, B2, B4, 201, 202, 203, 221, 222, 300, 601, 991, 1000, 1004, 1005)
- 51 stops across Happy City (1~6생활권), Jochiwon, Sojeong, Jeonui, Bugang, Osong, Banseok, Daejeon, Sintanjin
- Geumgang River (금강) crossing detection & schematic river ribbon
- Exact DP transfer calculation in JS matching Python solver 1:1
- 39 certified unique-solution stages across 4 difficulty tiers
- 3-stage progressive hint system, zoom/pan, focusOD, localStorage clear tracking
"""

import json
from sejong_bus_data import GEUMGANG_CROSSINGS, EXPRESS_DASHED_LINES, BRT_LINES

with open("scripts/sejong_bus/sejong_game_data.json", "r", encoding="utf-8") as f:
    game_data = json.load(f)

json_data_str = json.dumps(game_data, ensure_ascii=False)
river_pairs_list = [f"{u}-{v}" for (u, v) in sorted(GEUMGANG_CROSSINGS)]
river_pairs_js = json.dumps(river_pairs_list, ensure_ascii=False)
dashed_lines_js = json.dumps(sorted(EXPRESS_DASHED_LINES), ensure_ascii=False)
brt_lines_js = json.dumps(sorted(BRT_LINES), ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>세종 바로타: 마지막 버스 — 세종시 30개 버스노선 논리 퍼즐</title>
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
      --accent-rose: #e11d48;
      --font-main: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}

    body {{
      font-family: var(--font-main);
      background-color: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

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

    .logo-group {{ display: flex; align-items: center; gap: 10px; }}
    .logo-badge {{
      background: linear-gradient(135deg, #e11d48, #0284c7);
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
      background: linear-gradient(90deg, #fb7185, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .header-controls {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}

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
    .diff-btn:hover {{ color: var(--text-main); }}
    .diff-btn.active[data-diff="쉬움"] {{ background: #10b981; color: white; box-shadow: 0 0 12px rgba(16, 185, 129, 0.4); }}
    .diff-btn.active[data-diff="중간"] {{ background: #f59e0b; color: white; box-shadow: 0 0 12px rgba(245, 158, 11, 0.4); }}
    .diff-btn.active[data-diff="어려움"] {{ background: #ef4444; color: white; box-shadow: 0 0 12px rgba(239, 68, 68, 0.4); }}
    .diff-btn.active[data-diff="초고난이도"] {{ background: linear-gradient(135deg, #a855f7, #ec4899); color: white; box-shadow: 0 0 14px rgba(168, 85, 247, 0.5); }}

    .header-action-btn {{
      padding: 7px 12px;
      font-size: 12.5px;
      font-weight: 700;
      border-radius: 8px;
      border: 1px solid rgba(56, 189, 248, 0.45);
      background: rgba(14, 165, 233, 0.14);
      color: #38bdf8;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .header-action-btn:hover {{ background: rgba(14, 165, 233, 0.28); box-shadow: 0 0 12px rgba(56, 189, 248, 0.3); }}

    .game-layout {{ display: flex; flex: 1; height: calc(100vh - 58px); position: relative; overflow: hidden; }}

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
    .stage-nav-btn:hover {{ border-color: var(--accent-cyan); color: var(--accent-cyan); }}

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

    .sidebar-header {{ padding: 14px 20px; border-bottom: 1px solid var(--border-color); }}
    .stage-badge {{ display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; margin-bottom: 6px; }}
    .stage-title {{ font-size: 16px; font-weight: 700; margin-bottom: 5px; }}
    .stage-story {{ font-size: 12.5px; color: var(--text-muted); line-height: 1.45; }}

    .od-card {{
      margin: 10px 18px;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      justify-content: space-around;
      gap: 8px;
    }}
    .od-point {{ text-align: center; flex: 1; }}
    .od-label {{ font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 3px; }}
    .od-label.start {{ color: #10b981; }}
    .od-label.end {{ color: #ef4444; }}
    .od-station {{ font-size: 14px; font-weight: 700; word-break: keep-all; }}
    .od-arrow {{ font-size: 18px; color: var(--text-muted); }}

    .clues-section {{ flex: 1; padding: 12px 18px; overflow-y: auto; }}
    .section-title {{
      font-size: 11.5px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
      color: var(--text-muted); margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;
    }}
    .clue-list {{ display: flex; flex-direction: column; gap: 8px; }}
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
    .clue-item.satisfied {{ border-color: #10b981; background: rgba(16, 185, 129, 0.1); }}
    .clue-item.violated {{ border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }}
    .clue-top {{ display: flex; align-items: flex-start; gap: 8px; }}
    .clue-icon {{
      width: 18px; height: 18px; border-radius: 50%; background: rgba(148, 163, 184, 0.2);
      display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; margin-top: 1px;
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
      padding: 10px 14px;
      background: rgba(9, 13, 22, 0.98);
      border-top: 1px solid var(--border-color);
      display: flex;
      gap: 6px;
    }}

    .btn {{
      flex: 1;
      padding: 8px 6px;
      font-size: 12px;
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
    .btn-primary {{ background: linear-gradient(135deg, #e11d48, #0284c7); border: none; color: white; font-weight: 700; box-shadow: 0 0 14px rgba(225, 29, 72, 0.35); }}
    .btn-primary:hover {{ filter: brightness(1.12); box-shadow: 0 0 20px rgba(14, 165, 233, 0.5); }}

    .map-container {{
      flex: 1;
      position: relative;
      background: radial-gradient(circle at 50% 45%, #10192e 0%, #050811 100%);
      overflow: hidden;
      cursor: grab;
    }}
    .map-container:active {{ cursor: grabbing; }}
    svg#bus-svg {{ width: 100%; height: 100%; display: block; }}

    .map-controls {{ position: absolute; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 8px; z-index: 15; }}
    .control-btn {{
      width: 38px; height: 38px; background: var(--panel-bg); border: 1px solid var(--border-color);
      border-radius: 8px; color: var(--text-main); font-size: 17px; display: flex; align-items: center; justify-content: center;
      cursor: pointer; backdrop-filter: blur(8px); box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: all 0.2s;
    }}
    .control-btn:hover {{ border-color: var(--accent-cyan); color: var(--accent-cyan); }}

    .legend-panel {{
      position: absolute; top: 16px; right: 20px; background: var(--panel-bg);
      border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 14px;
      z-index: 15; max-width: 280px; backdrop-filter: blur(10px);
    }}
    .legend-header {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; font-weight: 700; cursor: pointer; color: var(--text-main); }}
    .legend-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5px 10px; margin-top: 8px; font-size: 11px; max-height: 360px; overflow-y: auto; padding-right: 4px; }}
    .legend-grid.collapsed {{ display: none; }}
    .legend-item {{ display: flex; align-items: center; gap: 5px; color: var(--text-muted); }}
    .legend-swatch {{ width: 14px; height: 4px; border-radius: 2px; flex-shrink: 0; }}

    .guide-banner {{
      position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.88); border: 1px solid var(--border-color);
      padding: 7px 16px; border-radius: 30px; font-size: 12.5px; font-weight: 600;
      backdrop-filter: blur(8px); color: var(--accent-cyan); box-shadow: 0 4px 16px rgba(0,0,0,0.4);
      pointer-events: none; z-index: 15; white-space: nowrap;
    }}

    #station-tooltip {{
      position: fixed; display: none; background: rgba(13, 19, 33, 0.96);
      border: 1px solid var(--accent-cyan); color: white; padding: 7px 12px;
      border-radius: 8px; font-size: 12px; pointer-events: none; z-index: 999;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6); line-height: 1.4;
    }}

    .modal-overlay {{
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(3, 7, 18, 0.82); backdrop-filter: blur(10px);
      display: flex; align-items: center; justify-content: center; z-index: 100;
      opacity: 0; pointer-events: none; transition: opacity 0.25s ease;
    }}
    .modal-overlay.active {{ opacity: 1; pointer-events: auto; }}

    .modal-box {{
      background: #111827; border: 1px solid rgba(16, 185, 129, 0.5); border-radius: 16px;
      padding: 32px; width: 460px; max-width: 92vw; text-align: center; box-shadow: 0 0 40px rgba(16, 185, 129, 0.25);
    }}
    .modal-title {{ font-size: 22px; font-weight: 800; color: #10b981; margin-bottom: 10px; }}
    .modal-desc {{ font-size: 13.5px; color: var(--text-muted); line-height: 1.6; margin-bottom: 20px; }}
    .modal-route {{ background: rgba(31, 41, 55, 0.7); border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: var(--accent-cyan); margin-bottom: 22px; word-break: keep-all; }}

    .guide-modal-box {{
      background: #0f172a; border: 1px solid var(--border-color); border-radius: 16px;
      padding: 26px 28px; width: 540px; max-width: 92vw; text-align: left;
      box-shadow: 0 12px 48px rgba(0,0,0,0.6);
    }}
    .guide-modal-box h3 {{ font-size: 18px; margin-bottom: 12px; color: #38bdf8; }}
    .guide-modal-box ul {{ margin-left: 18px; color: #cbd5e1; font-size: 13px; line-height: 1.75; margin-bottom: 18px; }}
  </style>
</head>
<body>

  <header>
    <div class="logo-group">
      <span class="logo-badge">SEJONG BUS 30</span>
      <h1 class="logo-title">세종 바로타: 마지막 버스 (전역 30개 노선 · 1생활권 정밀망)</h1>
    </div>

    <div class="header-controls">
      <div class="difficulty-tabs">
        <button class="diff-btn active" data-diff="쉬움">쉬움</button>
        <button class="diff-btn" data-diff="중간">중간</button>
        <button class="diff-btn" data-diff="어려움">어려움</button>
        <button class="diff-btn" data-diff="초고난이도">초고난이도</button>
      </div>
      <button class="header-action-btn" id="btn-open-guide">🚌 노선·규칙 안내</button>
      <a class="header-action-btn" href="index.html" title="서울 메트로 버전으로 이동">🚇 서울 지하철 버전</a>
    </div>
  </header>

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
        <h2 class="stage-title" id="stage-title-text">스테이지 제목</h2>
        <p class="stage-story" id="stage-story-text"></p>
      </div>

      <div class="od-card">
        <div class="od-point">
          <div class="od-label start">START · 출발</div>
          <div class="od-station" id="od-start-name">-</div>
        </div>
        <div class="od-arrow">➔</div>
        <div class="od-point">
          <div class="od-label end">DEST · 도착</div>
          <div class="od-station" id="od-end-name">-</div>
        </div>
      </div>
      <div style="padding: 0 18px;">
        <button class="btn" id="btn-focus-od" style="width: 100%; padding: 8px 10px; font-size: 12px; border-color: rgba(6, 182, 212, 0.45); color: #67e8f9;">🎯 출발·도착 정류장 한 화면에 보기</button>
      </div>

      <div class="clues-section">
        <div class="section-title">
          <span>제공된 최소 단서 (Minimal Clues)</span>
          <span style="font-size: 10px; color: var(--accent-cyan);">*유일해 보장</span>
        </div>
        <div class="clue-list" id="clue-list-container"></div>
      </div>

      <div class="current-path-bar">
        <div class="stats-row">
          <span>현재 이동 경로</span>
          <span class="stat-badge" id="current-station-count">1정류장</span>
        </div>
        <div class="route-sequence-preview" id="route-preview-text">-</div>
        <div class="stats-row" style="margin-top: 2px;">
          <span style="color: var(--text-muted);">최소 환승: <span id="current-transfers-count" style="color: white; font-weight: 600;">0회</span></span>
          <span style="color: var(--text-muted);">금강 횡단: <span id="current-river-count" style="color: white; font-weight: 600;">0회</span></span>
        </div>
      </div>

      <div class="actions-bar">
        <button class="btn" id="btn-undo">↩ 취소</button>
        <button class="btn" id="btn-reset">초기화</button>
        <button class="btn" id="btn-hint-side" style="border-color: rgba(56, 189, 248, 0.45); color: #7dd3fc;">💡 힌트</button>
        <button class="btn" id="btn-reveal" style="border-color: rgba(250, 204, 21, 0.45); color: #fde047;">👁️ 정답</button>
        <button class="btn btn-primary" id="btn-check">정답 확인</button>
      </div>
    </aside>

    <main class="map-container" id="map-area">
      <div class="guide-banner">
        🚌 세종시 30개 노선 · 81개 정류장 (BRT·M버스·200·27X·읍면·광역) · 인접 정류장을 클릭해 연결하세요
      </div>

      <div class="legend-panel">
        <div class="legend-header" id="legend-toggle">
          <span>🚌 세종 버스 범례 (30개 노선)</span>
          <span id="legend-arrow">▼</span>
        </div>
        <div class="legend-grid" id="legend-grid"></div>
      </div>

      <svg id="bus-svg" viewBox="40 20 3120 2560">
        <defs>
          <filter id="path-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <!-- Zone Watermarks -->
        <g id="zone-labels" fill="rgba(148, 163, 184, 0.11)" font-size="48" font-weight="800" letter-spacing="4">
          <text x="520" y="540">1생활권 (고운·아름·종촌)</text>
          <text x="1500" y="700">1생활권 (도담·어진)</text>
          <text x="2180" y="640">5·6생활권</text>
          <text x="1360" y="2180">3·4생활권</text>
        </g>

        <!-- Geumgang River (금강) Ribbon dividing North Bank and South Bank -->
        <g id="geumgang-river-group">
          <path d="M 40 1830 Q 820 1775 1600 1810 T 3160 1745 L 3160 1835 Q 1600 1895 820 1860 T 40 1915 Z"
                fill="rgba(14, 116, 144, 0.30)" stroke="rgba(56, 189, 248, 0.25)" stroke-width="3" />
          <text x="540" y="1858" fill="rgba(56, 189, 248, 0.38)" font-size="36" font-weight="700" letter-spacing="14">금  강 (GEUMGANG RIVER)</text>
        </g>

        <g id="tracks-layer"></g>
        <g id="user-path-layer"></g>
        <g id="stations-layer"></g>
      </svg>

      <div class="map-controls">
        <button class="control-btn" id="btn-zoom-in" title="확대">+</button>
        <button class="control-btn" id="btn-zoom-out" title="축소">−</button>
        <button class="control-btn" id="btn-focus-od-map" title="출발·도착 정류장 한 화면에 보기">🎯</button>
        <button class="control-btn" id="btn-zoom-reset" title="전체 노선도 보기">⛶</button>
        <button class="control-btn" id="btn-hint" title="단계별 힌트">💡</button>
      </div>

      <div id="station-tooltip"></div>
    </main>
  </div>

  <!-- Victory Modal -->
  <div class="modal-overlay" id="victory-modal">
    <div class="modal-box">
      <div style="font-size: 46px; margin-bottom: 10px;">🚌🎉</div>
      <h3 class="modal-title">버스 경로 복원 성공!</h3>
      <p class="modal-desc">
        제공된 최소 단서만을 이용하여<br>
        세종시 버스망의 수학적 유일해(Unique Solution)를 찾아냈습니다!
      </p>
      <div class="modal-route" id="modal-route-display"></div>
      <button class="btn btn-primary" id="btn-next-stage" style="width: 100%; padding: 12px; font-size: 14.5px;">다음 스테이지로 이동 ➔</button>
    </div>
  </div>

  <!-- Guide Modal -->
  <div class="modal-overlay" id="guide-modal">
    <div class="guide-modal-box">
      <h3>🚌 세종 30개 노선 버스 퍼즐 안내</h3>
      <ul>
        <li><strong>BRT·광역급행(7개):</strong> B0(내부순환), B1(오송~대전역), B2(오송~반석역), B4(동측~반석역), B5(보조BRT), B7(청주공항), M1(누리동~정부대전청사)</li>
        <li><strong>1·2·6생활권 지선(12개):</strong> 201~205, 221~222, 271~275번이 1생활권(고운·아름·종촌·도담·어진)과 공동캠퍼스를 촘촘히 잇습니다.</li>
        <li><strong>읍면·광역 간선(11개):</strong> 52, 300, 340, 430, 550, 601, 801, 991, 1000, 1004, 1005번이 조치원·전의·소정·부강·장군·공주·신탄진·반석을 연결합니다.</li>
        <li><strong>금강 횡단:</strong> 금강 이북과 이남(3·4생활권·금남·대전)을 다리로 건널 때마다 횡단 횟수가 1회 증가합니다.</li>
      </ul>
      <button class="btn btn-primary" id="btn-close-guide" style="width: 100%; padding: 10px;">확인</button>
    </div>
  </div>

  <script>
    const GAME_DATA = {json_data_str};
    const RIVER_PAIRS = new Set({river_pairs_js});
    const DASHED_LINES = new Set({dashed_lines_js});
    const BRT_LINES = new Set({brt_lines_js});

    let currentDifficulty = "쉬움";
    let currentStageIndex = 0;
    let currentStage = null;
    let userPath = [];
    let hintStep = 0;
    let clearedStages = new Set(JSON.parse(localStorage.getItem("sejong_full30_bus_cleared") || "[]"));

    const defaultViewBox = {{ x: 40, y: 20, w: 3120, h: 2560 }};
    let viewBox = {{ ...defaultViewBox }};
    let isPanning = false;
    let panStart = {{ x: 0, y: 0 }};

    const svg = document.getElementById("bus-svg");
    const tracksLayer = document.getElementById("tracks-layer");
    const userPathLayer = document.getElementById("user-path-layer");
    const stationsLayer = document.getElementById("stations-layer");
    const stageSelect = document.getElementById("stage-select");
    const clueListContainer = document.getElementById("clue-list-container");
    const routePreviewText = document.getElementById("route-preview-text");
    const tooltip = document.getElementById("station-tooltip");

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 440, type = 'sine', duration = 0.08) {{
      try {{
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
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

    const adj = {{}};
    for (const stName of Object.keys(GAME_DATA.stations)) adj[stName] = [];
    for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
      for (let i = 0; i < seq.length - 1; i++) {{
        const u = seq[i], v = seq[i + 1];
        if (adj[u] && adj[v]) {{
          adj[u].push({{ neighbor: v, line: lineName }});
          adj[v].push({{ neighbor: u, line: lineName }});
        }}
      }}
    }}

    const legendGrid = document.getElementById("legend-grid");
    for (const [lineName, color] of Object.entries(GAME_DATA.line_colors)) {{
      if (!GAME_DATA.lines[lineName]) continue;
      const item = document.createElement("div");
      item.className = "legend-item";
      const isDashed = DASHED_LINES.has(lineName);
      item.innerHTML = `<span class="legend-swatch" style="background:${{color}}; ${{isDashed ? 'border-bottom: 2px dashed white;' : ''}}"></span><span>${{lineName}}</span>`;
      legendGrid.appendChild(item);
    }}

    document.getElementById("legend-toggle").addEventListener("click", () => {{
      legendGrid.classList.toggle("collapsed");
      document.getElementById("legend-arrow").textContent = legendGrid.classList.contains("collapsed") ? "▶" : "▼";
    }});

    const edgePathCache = {{}};
    function getEdgePathD(uName, vName, isSpecial = false) {{
      const u = GAME_DATA.stations[uName];
      const v = GAME_DATA.stations[vName];
      if (!u || !v) return "";
      const [p1Name, p2Name] = uName < vName ? [uName, vName] : [vName, uName];
      const p1 = GAME_DATA.stations[p1Name];
      const p2 = GAME_DATA.stations[p2Name];
      const dx = p2.x - p1.x, dy = p2.y - p1.y;
      const dist = Math.hypot(dx, dy);
      if (isSpecial || dist > 260) {{
        const mx = (p1.x + p2.x) / 2;
        const my = (p1.y + p2.y) / 2;
        const offset = isSpecial ? Math.min(65, dist * 0.16) : Math.min(40, dist * 0.11);
        const nx = -dy / (dist || 1);
        const ny = dx / (dist || 1);
        const cx = mx + nx * offset;
        const cy = my + ny * offset;
        return `M ${{u.x}} ${{u.y}} Q ${{cx}} ${{cy}} ${{v.x}} ${{v.y}}`;
      }}
      return `M ${{u.x}} ${{u.y}} L ${{v.x}} ${{v.y}}`;
    }}

    function renderBaseTracks() {{
      tracksLayer.innerHTML = '';
      for (const [lineName, seq] of Object.entries(GAME_DATA.lines)) {{
        const color = GAME_DATA.line_colors[lineName] || "#999";
        const isDashed = DASHED_LINES.has(lineName);
        const isBrt = BRT_LINES.has(lineName);
        for (let i = 0; i < seq.length - 1; i++) {{
          const uName = seq[i], vName = seq[i + 1];
          const u = GAME_DATA.stations[uName];
          const v = GAME_DATA.stations[vName];
          if (u && v) {{
            const d = getEdgePathD(uName, vName, isDashed);
            const key1 = `${{uName}}|${{vName}}`;
            const key2 = `${{vName}}|${{uName}}`;
            if (!edgePathCache[key1] || !isDashed) {{
              edgePathCache[key1] = d;
              edgePathCache[key2] = getEdgePathD(vName, uName, isDashed);
            }}
            const pathEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pathEl.setAttribute("d", d);
            pathEl.setAttribute("fill", "none");
            pathEl.setAttribute("stroke", color);
            pathEl.setAttribute("stroke-width", isBrt ? "4.6" : "3.2");
            pathEl.setAttribute("stroke-linecap", "round");
            if (isDashed) pathEl.setAttribute("stroke-dasharray", "8,6");
            pathEl.setAttribute("opacity", isBrt ? "0.78" : "0.55");
            tracksLayer.appendChild(pathEl);
          }}
        }}
      }}
    }}

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
        circle.setAttribute("r", isTransfer ? "9" : "6");
        circle.setAttribute("fill", "#ffffff");
        circle.setAttribute("stroke", isTransfer ? "#0f172a" : "#334155");
        circle.setAttribute("stroke-width", isTransfer ? "3" : "2");
        g.appendChild(circle);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", stData.lx !== undefined ? stData.lx : stData.x);
        text.setAttribute("y", stData.ly !== undefined ? stData.ly : stData.y - 14);
        text.setAttribute("text-anchor", stData.anchor || "middle");
        text.setAttribute("fill", isTransfer ? "#f8fafc" : "#cbd5e1");
        text.setAttribute("font-size", isTransfer ? "14" : "12");
        text.setAttribute("font-weight", isTransfer ? "700" : "500");
        text.setAttribute("font-family", "Pretendard, sans-serif");
        text.style.paintOrder = "stroke";
        text.style.stroke = "#070a11";
        text.style.strokeWidth = "5px";
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
    function hideTooltip() {{ tooltip.style.display = "none"; }}

    function loadStage(diff, index) {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === diff);
      if (!stages[index]) return;

      currentDifficulty = diff;
      currentStageIndex = index;
      currentStage = stages[index];
      userPath = [currentStage.start];

      stageSelect.innerHTML = '';
      let clearedInDiff = 0;
      stages.forEach((s, i) => {{
        const isCleared = clearedStages.has(s.id);
        if (isCleared) clearedInDiff++;
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = `${{isCleared ? '✓ ' : ''}}#${{i + 1}} ${{s.start}} ➔ ${{s.end}} (${{s.path_length}}정류장)`;
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
      hintStep = 0;
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
          circle.setAttribute("stroke-width", GAME_DATA.stations[stName].lines.length > 1 ? "3" : "2");
        }}, 400);
      }}
    }}

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
      let river = 0;
      for (let i = 0; i < userPath.length - 1; i++) {{
        if (RIVER_PAIRS.has(`${{userPath[i]}}-${{userPath[i + 1]}}`)) river++;
      }}
      const seqs = getValidLineSequences(userPath);
      const minTransfers = seqs.length > 0 && seqs[0].length > 0 ? seqs[0].length - 1 : 0;
      return {{ transfers: minTransfers, river, seqs }};
    }}

    function updatePathUI() {{
      hintStep = 0;
      userPathLayer.innerHTML = '';
      const analysis = analyzeUserPath();

      for (let i = 0; i < userPath.length - 1; i++) {{
        const uName = userPath[i], vName = userPath[i + 1];
        const u = GAME_DATA.stations[uName], v = GAME_DATA.stations[vName];
        if (u && v) {{
          const d = edgePathCache[`${{uName}}|${{vName}}`] || getEdgePathD(uName, vName, false);
          const glow = document.createElementNS("http://www.w3.org/2000/svg", "path");
          glow.setAttribute("d", d);
          glow.setAttribute("fill", "none");
          glow.setAttribute("stroke", "#38bdf8");
          glow.setAttribute("stroke-width", "11");
          glow.setAttribute("stroke-linecap", "round");
          glow.setAttribute("opacity", "0.65");
          glow.setAttribute("filter", "url(#path-glow)");
          userPathLayer.appendChild(glow);

          const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
          line.setAttribute("d", d);
          line.setAttribute("fill", "none");
          line.setAttribute("stroke", "#ffffff");
          line.setAttribute("stroke-width", "4.8");
          line.setAttribute("stroke-linecap", "round");
          userPathLayer.appendChild(line);
        }}
      }}

      const viaStations = new Set(
        (currentStage.clues || []).filter(c => c.type === "via_station").map(c => c.val)
      );

      for (const [stName, stData] of Object.entries(GAME_DATA.stations)) {{
        const g = document.getElementById(`st-${{stName}}`);
        if (!g) continue;
        const circle = g.querySelector("circle");
        const text = g.querySelector("text");
        const isStart = stName === currentStage.start;
        const isEnd = stName === currentStage.end;
        const isVia = viaStations.has(stName);
        const inPath = userPath.includes(stName);

        if (isStart) {{
          circle.setAttribute("fill", "#10b981");
          circle.setAttribute("stroke", "#ffffff");
          circle.setAttribute("stroke-width", "4");
          circle.setAttribute("r", "14");
          if (text) text.setAttribute("fill", "#34d399");
        }} else if (isEnd) {{
          circle.setAttribute("fill", "#ef4444");
          circle.setAttribute("stroke", "#ffffff");
          circle.setAttribute("stroke-width", "4");
          circle.setAttribute("r", "14");
          if (text) text.setAttribute("fill", "#f87171");
        }} else if (isVia) {{
          circle.setAttribute("fill", inPath ? "#38bdf8" : "#facc15");
          circle.setAttribute("stroke", inPath ? "#facc15" : "#ffffff");
          circle.setAttribute("stroke-width", "4");
          circle.setAttribute("r", "12");
          if (text) text.setAttribute("fill", "#fde047");
        }} else if (inPath) {{
          circle.setAttribute("fill", "#38bdf8");
          circle.setAttribute("stroke", "#0f172a");
          circle.setAttribute("stroke-width", "3");
          circle.setAttribute("r", "10");
          if (text) text.setAttribute("fill", "#7dd3fc");
        }} else {{
          const isTransfer = stData.lines.length > 1;
          circle.setAttribute("fill", "#ffffff");
          circle.setAttribute("stroke", isTransfer ? "#0f172a" : "#334155");
          circle.setAttribute("stroke-width", isTransfer ? "3" : "2");
          circle.setAttribute("r", isTransfer ? "9" : "6");
          if (text) text.setAttribute("fill", isTransfer ? "#f8fafc" : "#cbd5e1");
        }}
      }}

      document.getElementById("current-station-count").textContent = `${{userPath.length}}정류장`;
      routePreviewText.textContent = userPath.join(" ➔ ");
      document.getElementById("current-transfers-count").textContent = `${{analysis.transfers}}회`;
      document.getElementById("current-river-count").textContent = `${{analysis.river}}회`;

      currentStage.clues.forEach((clue, idx) => {{
        const item = document.getElementById(`clue-item-${{idx}}`);
        const status = document.getElementById(`clue-status-${{idx}}`);
        let satisfied = false, violated = false, statusText = "진행 중";

        if (clue.type === "total_stations") {{
          statusText = `${{userPath.length}} / ${{clue.val}}정류장`;
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
      const matchesSolution = JSON.stringify(userPath) === JSON.stringify(currentStage.solution);

      if (isAtEnd && matchesSolution) {{
        playSuccessChime();
        clearedStages.add(currentStage.id);
        localStorage.setItem("sejong_full30_bus_cleared", JSON.stringify([...clearedStages]));
        document.getElementById("modal-route-display").textContent = userPath.join(" ➔ ");
        document.getElementById("victory-modal").classList.add("active");
      }} else if (manual) {{
        playBeep(220, 'sawtooth', 0.2);
        alert("아직 모든 최소 단서 조건을 만족하는 유일해가 아닙니다! 단서 판정 상태를 다시 확인해 주세요.");
      }}
    }}

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
      let delta = e.deltaY;
      if (e.deltaMode === 1) delta *= 30;
      else if (e.deltaMode === 2) delta *= 300;
      const clampedDelta = Math.max(-80, Math.min(80, delta));
      const zoomFactor = 1 + clampedDelta * 0.0012;

      const rect = svg.getBoundingClientRect();
      const relX = (e.clientX - rect.left) / rect.width;
      const relY = (e.clientY - rect.top) / rect.height;

      const newW = Math.max(240, Math.min(4200, viewBox.w * zoomFactor));
      const newH = newW * (defaultViewBox.h / defaultViewBox.w);
      viewBox.x += (viewBox.w - newW) * relX;
      viewBox.y += (viewBox.h - newH) * relY;
      viewBox.w = newW; viewBox.h = newH;
      updateSvgViewBox();
    }}, {{ passive: false }});

    document.getElementById("btn-zoom-in").addEventListener("click", () => {{
      const newW = Math.max(240, viewBox.w * 0.78);
      const newH = newW * (defaultViewBox.h / defaultViewBox.w);
      viewBox.x += (viewBox.w - newW) / 2; viewBox.y += (viewBox.h - newH) / 2;
      viewBox.w = newW; viewBox.h = newH;
      updateSvgViewBox();
    }});
    document.getElementById("btn-zoom-out").addEventListener("click", () => {{
      const newW = Math.min(4200, viewBox.w * 1.28);
      const newH = newW * (defaultViewBox.h / defaultViewBox.w);
      viewBox.x += (viewBox.w - newW) / 2; viewBox.y += (viewBox.h - newH) / 2;
      viewBox.w = newW; viewBox.h = newH;
      updateSvgViewBox();
    }});
    document.getElementById("btn-zoom-reset").addEventListener("click", () => {{
      viewBox = {{ ...defaultViewBox }};
      updateSvgViewBox();
    }});

    function focusODStations() {{
      if (!currentStage) return;
      const s = GAME_DATA.stations[currentStage.start];
      const e = GAME_DATA.stations[currentStage.end];
      if (!s || !e) return;
      const cx = (s.x + e.x) / 2;
      const cy = (s.y + e.y) / 2;
      const spanW = Math.min(2560, Math.max(520, Math.abs(s.x - e.x) * 1.65, Math.abs(s.y - e.y) * 1.65));
      const spanH = spanW * (defaultViewBox.h / defaultViewBox.w);
      viewBox = {{ x: cx - spanW / 2, y: cy - spanH / 2, w: spanW, h: spanH }};
      updateSvgViewBox();
    }}
    document.getElementById("btn-focus-od").addEventListener("click", focusODStations);
    document.getElementById("btn-focus-od-map").addEventListener("click", focusODStations);

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

    function showProgressiveHint() {{
      if (!currentStage) return;
      const sol = currentStage.solution;
      let mismatchIdx = -1;
      for (let i = 0; i < sol.length; i++) {{
        if (userPath[i] !== sol[i]) {{ mismatchIdx = i; break; }}
      }}
      if (mismatchIdx === -1) {{
        alert("현재까지의 경로가 완벽합니다! '정답 확인'을 눌러보세요.");
        return;
      }}

      const prevSt = sol[mismatchIdx - 1] || currentStage.start;
      const nextSt = sol[mismatchIdx];
      const nextLines = [...new Set(adj[prevSt].filter(e => e.neighbor === nextSt).map(e => e.line))];
      hintStep = Math.min(3, hintStep + 1);

      if (hintStep === 1) {{
        if (mismatchIdx < userPath.length) {{
          alert(`💡 1단계 힌트 (분기점): [${{prevSt}}] 다음 정류장(${{userPath[mismatchIdx]}})부터 정답 경로와 다릅니다.\n[${{prevSt}}]까지 되돌아가서 다시 선택해보세요. (다시 누르면 2단계 힌트)`);
        }} else {{
          alert(`💡 1단계 힌트 (다음 노선): [${{prevSt}}] 다음 구간은 [${{nextLines.join(" / ")}}] 버스를 타고 이동합니다. (다시 누르면 2단계 힌트)`);
        }}
      }} else if (hintStep === 2) {{
        const nextHub = sol.slice(mismatchIdx).find(st => GAME_DATA.stations[st].lines.length > 1 && st !== currentStage.end);
        const hubMsg = nextHub ? `앞으로 주요 환승 정류장 '${{nextHub}}'을(를) 지납니다.` : `이후 도착 정류장(${{currentStage.end}})까지 이어집니다.`;
        alert(`💡 2단계 힌트 (노선·거점): 전체 이용 노선 순서는 [${{currentStage.solution_lines.join(" ➔ ")}}]이며, ${{hubMsg}} (다시 누르면 3단계 힌트)`);
      }} else {{
        alert(`💡 3단계 힌트 (정답 정류장): [${{prevSt}}] 다음으로 이동할 올바른 정류장은 [${{nextSt}}]입니다!`);
      }}
    }}
    document.getElementById("btn-hint").addEventListener("click", showProgressiveHint);
    document.getElementById("btn-hint-side").addEventListener("click", showProgressiveHint);

    document.getElementById("btn-reveal").addEventListener("click", () => {{
      if (!currentStage) return;
      userPath = [...currentStage.solution];
      updatePathUI();
      alert(`🔓 정답 경로 (${{currentStage.solution.length}}정류장 · 최소 환승 ${{currentStage.min_transfers}}회)\n\n${{currentStage.solution.join(" ➔ ")}}\n\n[이용 노선: ${{currentStage.solution_lines.join(" ➔ ")}}]`);
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

    stageSelect.addEventListener("change", (e) => loadStage(currentDifficulty, parseInt(e.target.value, 10)));
    document.getElementById("btn-prev-stage").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      loadStage(currentDifficulty, (currentStageIndex - 1 + stages.length) % stages.length);
    }});
    document.getElementById("btn-next-stage-nav").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      loadStage(currentDifficulty, (currentStageIndex + 1) % stages.length);
    }});
    document.getElementById("btn-random-stage").addEventListener("click", () => {{
      const stages = GAME_DATA.stages.filter(s => s.difficulty === currentDifficulty);
      loadStage(currentDifficulty, Math.floor(Math.random() * stages.length));
    }});

    const guideModal = document.getElementById("guide-modal");
    document.getElementById("btn-open-guide").addEventListener("click", () => guideModal.classList.add("active"));
    document.getElementById("btn-close-guide").addEventListener("click", () => guideModal.classList.remove("active"));
    guideModal.addEventListener("click", (e) => {{ if (e.target === guideModal) guideModal.classList.remove("active"); }});

    renderBaseTracks();
    renderStations();
    loadStage("쉬움", 0);
  </script>
</body>
</html>
"""

with open("sejong_bus.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("sejong_bus.html built successfully with", len(game_data["stages"]), "stages!")
