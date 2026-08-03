// ==UserScript==
// @name         Autoreporter Tool Made by METAVPH
// @namespace    http://tampermonkey.net/
// @match        https://www.facebook.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    console.log('%c🛡️ Autoreporter Tool Made by METAVPH LOADED', 'color: #00d4ff; font-size: 18px; font-weight: bold; text-shadow: 0 0 15px #00d4ff;');

    const reportActions = [
        { step: 1, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 2, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 3, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 4, name: "Fake profile", xpath: "//span[contains(text(),'Fake profile')]" },
        { step: 5, name: "Me", xpath: "//span[text()='Me']" },
        { step: 6, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 7, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 8, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 9, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 10, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 11, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 12, name: "Problem involving someone under 18", xpath: "//span[contains(text(),'Problem involving someone under 18')]" },
        { step: 13, name: "Physical abuse", xpath: "//span[contains(text(),'Physical abuse')]" },
        { step: 14, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 15, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 16, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 17, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 18, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 19, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 20, name: "Violent, hateful content", xpath: "//span[contains(text(),'Violent, hateful or disturbing content')]" },
        { step: 21, name: "Credible threat to safety", xpath: "//span[contains(text(),'Credible threat to safety')]" },
        { step: 22, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 23, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 24, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 25, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 26, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 27, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 28, name: "Scam, fraud", xpath: "//span[contains(text(),'Scam, fraud or false information')]" },
        { step: 29, name: "Fraud or scam", xpath: "//span[contains(text(),'Fraud or scam')]" },
        { step: 30, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 31, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 32, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 33, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 34, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 35, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 36, name: "Something else", xpath: "//span[contains(text(),'Something else')]" },
        { step: 37, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 38, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 39, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 40, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 41, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 42, name: "Drugs", xpath: "//span[contains(text(),'Drugs')]" },
        { step: 43, name: "Highly addictive drugs (cocaine, heroin, fentanyl)", xpath: "//span[contains(text(),'Highly addictive drugs') or contains(text(),'cocaine') or contains(text(),'heroin') or contains(text(),'fentanyl')]" },
        { step: 44, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 45, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 46, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 47, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 48, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 49, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 50, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 51, name: "Weapons", xpath: "//span[contains(text(),'Weapons')]" },
        { step: 52, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 53, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 54, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 55, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 56, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 57, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 58, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 59, name: "Alcohol", xpath: "//span[contains(text(),'Alcohol')]" },
        { step: 60, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 61, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 62, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 63, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 64, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 65, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 66, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 67, name: "Tobacco", xpath: "//span[contains(text(),'Tobacco')]" },
        { step: 68, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 69, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 70, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 71, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 72, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 73, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 74, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 75, name: "Gambling", xpath: "//span[contains(text(),'Gambling')]" },
        { step: 76, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 77, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 78, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 79, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 80, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 81, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 82, name: "Selling or promoting restricted items", xpath: "//span[contains(text(),'Selling or promoting restricted items') or contains(text(),'Sale of regulated goods') or contains(text(),'restricted items')]" },
        { step: 83, name: "Animals", xpath: "//span[contains(text(),'Animals')]" },
        { step: 84, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 85, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 86, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 87, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 88, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 89, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 90, name: "Problem involving someone under 18", xpath: "//span[contains(text(),'Problem involving someone under 18')]" },
        { step: 91, name: "Threatening to share my nude images", xpath: "//span[contains(text(),'Threatening to share my nude images')]" },
        { step: 92, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 93, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 94, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 95, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 96, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 97, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 98, name: "Problem involving someone under 18", xpath: "//span[contains(text(),'Problem involving someone under 18')]" },
        { step: 99, name: "Sharing someone's nude images", xpath: "//span[contains(text(),'Sharing someone's nude images')]" },
        { step: 100, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 101, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 102, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 103, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 104, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 105, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 106, name: "Problem involving someone under 18", xpath: "//span[contains(text(),'Problem involving someone under 18')]" },
        { step: 107, name: "Seems like sexual exploitation", xpath: "//span[contains(text(),'Seems like sexual exploitation')]" },
        { step: 108, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 109, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 110, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" },

        { step: 111, name: "Menu (3 dots)", xpath: "//*[@aria-label='Profile settings see more options']" },
        { step: 112, name: "Report profile", xpath: "//span[contains(text(),'Report profile')]" },
        { step: 113, name: "Something about this profile", xpath: "//span[contains(text(),'Something about this profile')]" },
        { step: 114, name: "Bullying or harassment or abuse", xpath: "//span[contains(text(),'Bullying or harassment or abuse')]" },
        { step: 115, name: "Submit", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Submit') or contains(text(),'Gửi')]" },
        { step: 116, name: "Next", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Next') or contains(text(),'Tiếp')]" },
        { step: 117, name: "Done", xpath: "//div[contains(@class,'xdj266r')]//span[contains(text(),'Done') or contains(text(),'Xong') or contains(text(),'Hoàn tất')]" }
    ];

    const TG_BOT_TOKEN = "8884720634:AAGwGYDbKmn-90Pmz2N9uh0DyMq9XxlU4YE";
    const DEFAULT_CHAT_IDS = ["-5326047233", "-1003891622126"];
    const BASE_DELAY = 2500;

    let isRunning = false;
    let stopRequested = false;
    let loopCount = 0;
    let reportCount = 0;

    const initUI = () => {
        if (document.getElementById('metavph-panel')) return;

        const style = document.createElement('style');
        style.id = 'metavph-style';
        style.innerText = `
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
            :root {
                --primary: #00d4ff;
                --primary-dark: #0099cc;
                --secondary: #7b2ffc;
                --accent: #ff00aa;
                --bg-panel: rgba(12, 12, 24, 0.94);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text-primary: #e8e8ff;
                --text-secondary: #8888aa;
                --shadow-glow: 0 8px 40px rgba(0, 0, 0, 0.7);
                --radius-lg: 20px;
                --radius-sm: 10px;
            }
            * { box-sizing: border-box; }
            @keyframes borderFlow {
                0% { border-color: var(--primary); box-shadow: 0 0 30px rgba(0,212,255,0.15); }
                33% { border-color: var(--secondary); box-shadow: 0 0 30px rgba(123,47,252,0.15); }
                66% { border-color: var(--accent); box-shadow: 0 0 30px rgba(255,0,170,0.15); }
                100% { border-color: var(--primary); box-shadow: 0 0 30px rgba(0,212,255,0.15); }
            }
            @keyframes shimmer {
                0% { background-position: -200% center; }
                100% { background-position: 200% center; }
            }
            @keyframes pulseRing {
                0% { box-shadow: 0 0 0 0 rgba(0,212,255,0.4); }
                70% { box-shadow: 0 0 0 12px rgba(0,212,255,0); }
                100% { box-shadow: 0 0 0 0 rgba(0,212,255,0); }
            }
            #metavph-panel {
                position: fixed;
                top: 24px;
                right: 24px;
                width: 380px;
                max-height: calc(100vh - 48px);
                overflow-y: auto;
                background: var(--bg-panel);
                backdrop-filter: blur(24px);
                -webkit-backdrop-filter: blur(24px);
                color: var(--text-primary);
                padding: 0;
                border-radius: var(--radius-lg);
                z-index: 999998;
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                border: 1.5px solid var(--primary);
                animation: borderFlow 6s infinite ease-in-out;
                box-shadow: var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.05);
                transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
                scrollbar-width: thin;
                scrollbar-color: rgba(255,255,255,0.1) transparent;
            }
            #metavph-panel::-webkit-scrollbar { width: 4px; }
            #metavph-panel::-webkit-scrollbar-track { background: transparent; }
            #metavph-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
            .panel-header {
                padding: 18px 22px 14px 22px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: move;
                border-bottom: 1px solid var(--glass-border);
                background: linear-gradient(180deg, rgba(0,212,255,0.04) 0%, transparent 100%);
            }
            .panel-title-group { flex: 1; min-width: 0; }
            .panel-title {
                margin: 0;
                font-size: 20px;
                font-weight: 900;
                letter-spacing: -0.3px;
                background: linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
                background-size: 200% 200%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: shimmer 4s ease-in-out infinite;
                line-height: 1.2;
            }
            .panel-sub {
                font-size: 11px;
                color: var(--text-secondary);
                margin-top: 2px;
                letter-spacing: 0.3px;
            }
            .panel-controls { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
            .minimize-btn {
                color: var(--text-secondary);
                font-size: 20px;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 8px;
                transition: all 0.2s;
                line-height: 1;
                background: none;
                border: none;
                font-family: inherit;
            }
            .minimize-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
            .panel-body { padding: 18px 22px 22px 22px; }
            .section-box {
                background: rgba(255,255,255,0.03);
                padding: 14px 16px;
                border-radius: 14px;
                margin-bottom: 14px;
                border: 1px solid var(--glass-border);
                transition: all 0.25s ease;
            }
            .section-box:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
            .section-label {
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: var(--primary);
                font-weight: 700;
                margin-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .section-label .badge {
                font-size: 8px;
                background: rgba(0,212,255,0.15);
                padding: 1px 8px;
                border-radius: 12px;
                color: var(--primary);
                letter-spacing: 0.5px;
            }
            .license-status {
                font-size: 14px;
                font-weight: 700;
                color: #00ff88;
                text-shadow: 0 0 20px rgba(0,255,136,0.2);
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .license-status .dot {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #00ff88;
                animation: pulseRing 2s infinite;
            }
            .data-grid {
                display: flex;
                gap: 12px;
                margin-top: 4px;
            }
            .data-tile {
                flex: 1;
                background: rgba(0,0,0,0.35);
                border-radius: 10px;
                padding: 12px 8px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.04);
                transition: all 0.25s ease;
            }
            .data-tile:hover { border-color: rgba(0,212,255,0.15); }
            .tile-label {
                font-size: 9px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.6px;
                font-weight: 600;
            }
            .tile-value {
                font-size: 28px;
                font-weight: 900;
                color: var(--primary);
                text-shadow: 0 0 30px rgba(0,212,255,0.15);
                line-height: 1.3;
                font-variant-numeric: tabular-nums;
            }
            .status-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin: 6px 0 8px 0;
                padding: 0 2px;
            }
            .status-text {
                font-weight: 600;
                font-size: 12px;
                color: var(--text-secondary);
            }
            .status-text .status-value {
                color: var(--primary);
                font-weight: 700;
            }
            .status-text .status-value.running { color: #00ff88; }
            .status-text .status-value.paused { color: #ffbb33; }
            .status-text .status-value.stopped { color: #ff4466; }
            .progress-track {
                background: rgba(255,255,255,0.06);
                height: 5px;
                border-radius: 6px;
                overflow: hidden;
                margin: 0 0 4px 0;
            }
            .progress-fill {
                width: 0%;
                height: 100%;
                background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
                background-size: 200% 100%;
                animation: shimmer 3s ease-in-out infinite;
                border-radius: 6px;
                transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
            }
            .action-row {
                display: flex;
                gap: 10px;
                margin: 16px 0 14px 0;
            }
            .action-btn {
                flex: 1;
                padding: 13px 0;
                text-align: center;
                border-radius: 10px;
                font-weight: 700;
                font-size: 13px;
                cursor: pointer;
                border: none;
                transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
                font-family: inherit;
                letter-spacing: 0.3px;
            }
            .action-btn.primary {
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                color: #fff;
                box-shadow: 0 4px 20px rgba(0,212,255,0.25);
            }
            .action-btn.primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 30px rgba(0,212,255,0.35);
            }
            .action-btn.primary.running-state {
                background: linear-gradient(135deg, #ff8800, #ff5500);
                box-shadow: 0 4px 20px rgba(255,136,0,0.3);
            }
            .action-btn.primary.running-state:hover {
                box-shadow: 0 6px 30px rgba(255,136,0,0.4);
            }
            .action-btn.danger {
                background: transparent;
                color: #ff4d6d;
                border: 1.5px solid #ff4d6d;
            }
            .action-btn.danger:hover {
                background: #ff4d6d;
                color: #fff;
                box-shadow: 0 4px 20px rgba(255,77,109,0.25);
            }
            .log-area {
                background: rgba(0,0,0,0.5);
                padding: 12px 14px;
                border-radius: 10px;
                max-height: 110px;
                overflow-y: auto;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 10.5px;
                border: 1px solid rgba(255,255,255,0.04);
                margin-bottom: 12px;
                scrollbar-width: thin;
                scrollbar-color: rgba(255,255,255,0.08) transparent;
                line-height: 1.6;
            }
            .log-area::-webkit-scrollbar { width: 3px; }
            .log-area::-webkit-scrollbar-track { background: transparent; }
            .log-area::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
            .log-entry { margin-bottom: 2px; display: flex; gap: 8px; align-items: baseline; }
            .log-time { color: #555; flex-shrink: 0; font-size: 9.5px; }
            .log-green { color: #00ff88; }
            .log-red { color: #ff4466; }
            .log-yellow { color: #ffbb33; }
            .log-blue { color: #00d4ff; }
            .log-white { color: #c8c8dd; }
            .footer-text {
                font-size: 10px;
                color: #555;
                text-align: center;
                padding-top: 10px;
                border-top: 1px solid var(--glass-border);
                letter-spacing: 0.2px;
            }
            .footer-text strong { color: var(--primary); font-weight: 700; }
            #minimized-icon-metavph {
                display: none;
                position: fixed;
                top: 24px;
                right: 24px;
                width: 52px;
                height: 52px;
                background: var(--bg-panel);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 50%;
                border: 2px solid var(--primary);
                box-shadow: 0 0 40px rgba(0,212,255,0.2);
                z-index: 999999;
                cursor: pointer;
                text-align: center;
                line-height: 50px;
                font-size: 22px;
                color: var(--primary);
                animation: borderFlow 4s infinite alternate;
                transition: all 0.3s ease;
                font-weight: 900;
            }
            #minimized-icon-metavph:hover {
                transform: scale(1.05);
                box-shadow: 0 0 60px rgba(0,212,255,0.35);
            }
            @media (max-width: 480px) {
                #metavph-panel { width: calc(100vw - 32px); right: 16px; top: 16px; max-height: calc(100vh - 32px); }
                .panel-header { padding: 14px 16px 10px 16px; flex-wrap: wrap; }
                .panel-body { padding: 14px 16px 18px 16px; }
                .panel-title { font-size: 17px; }
                .data-grid { flex-direction: row; }
                .tile-value { font-size: 22px; }
            }
        `;
        document.head.appendChild(style);

        const panel = document.createElement('div');
        panel.id = 'metavph-panel';
        panel.innerHTML = `
            <div class="panel-header">
                <div class="panel-title-group">
                    <div class="panel-title">Autoreporter Tool</div>
                    <div class="panel-sub">Made by METAVPH</div>
                </div>
                <div class="panel-controls">
                    <button class="minimize-btn" id="minimize-toggle" title="Minimize">−</button>
                </div>
            </div>
            <div class="panel-body">
                <div class="section-box">
                    <div class="section-label">🔑 License <span class="badge">VIP</span></div>
                    <div class="license-status"><span class="dot"></span> Activated — METAVPH</div>
                </div>
                <div class="data-grid">
                    <div class="data-tile"><div class="tile-label">Reports</div><div class="tile-value" id="metavph-reports">0</div></div>
                    <div class="data-tile"><div class="tile-label">Loops</div><div class="tile-value" id="metavph-loops">0</div></div>
                </div>
                <div class="status-row">
                    <span class="status-text">Status: <span class="status-value" id="metavph-status">Idle</span></span>
                    <span style="font-size:10px; color:#555;" id="metavph-step-info">Ready</span>
                </div>
                <div class="progress-track"><div class="progress-fill" id="metavph-progress"></div></div>
                <div class="action-row">
                    <button class="action-btn primary" id="metavph-start">▶ START</button>
                    <button class="action-btn danger" id="metavph-stop">⏹ STOP</button>
                </div>
                <div class="log-area" id="metavph-log"></div>
                <div class="footer-text">Developed by <strong>METAVPH</strong> — All rights reserved</div>
            </div>
        `;
        document.body.appendChild(panel);

        const mini = document.createElement('div');
        mini.id = 'minimized-icon-metavph';
        mini.textContent = 'M';
        mini.title = 'Expand Autoreporter Tool';
        document.body.appendChild(mini);

        bindEvents();
        loadSaved();
    };

    const bindEvents = () => {
        const panel = document.getElementById('metavph-panel');
        const mini = document.getElementById('minimized-icon-metavph');
        const minimizeBtn = document.getElementById('minimize-toggle');
        const startBtn = document.getElementById('metavph-start');
        const stopBtn = document.getElementById('metavph-stop');

        minimizeBtn.onclick = () => {
            panel.style.display = 'none';
            mini.style.display = 'block';
        };
        mini.onclick = () => {
            mini.style.display = 'none';
            panel.style.display = 'block';
        };
        startBtn.onclick = () => {
            if (isRunning) { pauseTool(); } else { startTool(); }
        };
        stopBtn.onclick = stopTool;

        const header = panel.querySelector('.panel-header');
        let dragging = false, startX, startY, origX, origY;
        header.onmousedown = (e) => {
            if (e.target.closest('.panel-controls')) return;
            dragging = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = panel.getBoundingClientRect();
            origX = rect.left;
            origY = rect.top;
            document.onmousemove = (ev) => {
                if (!dragging) return;
                panel.style.left = (origX + ev.clientX - startX) + 'px';
                panel.style.top = (origY + ev.clientY - startY) + 'px';
                panel.style.right = 'auto';
            };
            document.onmouseup = () => {
                dragging = false;
                document.onmousemove = null;
            };
            e.preventDefault();
        };
    };

    const loadSaved = () => {};

    const addLog = (text, type = "white") => {
        const logArea = document.getElementById('metavph-log');
        if (!logArea) return;
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        const cls = `log-${type}`;
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `<span class="log-time">[${time}]</span> <span class="${cls}">${text}</span>`;
        logArea.appendChild(entry);
        logArea.scrollTop = logArea.scrollHeight;
    };

    const sendTelegram = async (msg) => {
        const recipients = [...DEFAULT_CHAT_IDS];
        for (const chatId of recipients) {
            if (!chatId) continue;
            const url = `https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage?chat_id=${encodeURIComponent(chatId)}&text=${encodeURIComponent(msg)}`;
            try { await fetch(url); } catch (e) { console.error(e); }
        }
    };

    const checkIsDie = () => {
        const title = document.title;
        const indicators = [
            "Content isn't available",
            "Không tìm thấy nội dung",
            "Trang này không khả dụng",
            "This page isn't available",
            "Page Not Found"
        ];
        return indicators.some(ind => title.includes(ind));
    };

    const findElement = (xpath, timeout = 5000) => {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const check = () => {
                try {
                    const el = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (el) { resolve(el); return; }
                } catch (e) {}
                if (Date.now() - startTime < timeout) {
                    setTimeout(check, 200);
                } else {
                    resolve(null);
                }
            };
            check();
        });
    };

    const simulateClick = (el) => {
        try {
            if (!el) return false;
            const hidden = el.closest('[aria-hidden="true"]');
            if (hidden) hidden.removeAttribute('aria-hidden');
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            ['mousedown', 'mouseup', 'click'].forEach(ev => {
                el.dispatchEvent(new MouseEvent(ev, { bubbles: true, cancelable: true, view: window }));
            });
            return true;
        } catch (e) {
            return false;
        }
    };

    const isPageLoading = () => {
        const selectors = ['[role="progressbar"]', 'img[src*="loading"]', 'i[class*="loading"]'];
        return selectors.some(sel => {
            const el = document.querySelector(sel);
            return el && el.offsetParent !== null;
        });
    };

    const sleep = ms => new Promise(r => setTimeout(r, ms));

    const updateProgress = (pct) => {
        const fill = document.getElementById('metavph-progress');
        if (fill) fill.style.width = Math.min(100, Math.max(0, pct)) + '%';
    };

    const updateStatus = (text, type = 'idle') => {
        const el = document.getElementById('metavph-status');
        if (!el) return;
        el.textContent = text;
        el.className = 'status-value';
        if (type === 'running') el.classList.add('running');
        else if (type === 'paused') el.classList.add('paused');
        else if (type === 'stopped') el.classList.add('stopped');
    };

    const startTool = async () => {
        if (isRunning) return;
        isRunning = true;
        stopRequested = false;
        const btn = document.getElementById('metavph-start');
        btn.textContent = '⏸ PAUSE';
        btn.className = 'action-btn primary running-state';
        updateStatus('Running...', 'running');
        document.getElementById('metavph-step-info').textContent = 'Initializing...';
        addLog("🚀 Started automation", "green");
        await sendTelegram(`🚀 Autoreporter Tool started on ${window.location.href}`);

        while (isRunning && !stopRequested) {
            loopCount++;
            document.getElementById('metavph-loops').textContent = loopCount;
            if (checkIsDie()) {
                addLog("🎉 Account is dead! Stopping.", "green");
                await sendTelegram(`🎉 Account died after ${loopCount} loops`);
                stopTool();
                break;
            }
            addLog(`🔄 Loop #${loopCount}`, "blue");

            for (let i = 0; i < reportActions.length; i++) {
                if (!isRunning || stopRequested) break;
                const action = reportActions[i];
                document.getElementById('metavph-step-info').textContent = `Step ${action.step}: ${action.name}`;
                updateProgress(((i + 1) / reportActions.length) * 100);

                let success = false;
                let retries = 0;
                const maxRetries = 30;

                while (!success && retries < maxRetries && isRunning && !stopRequested) {
                    retries++;
                    try {
                        if (action.xpath) {
                            let el = await findElement(action.xpath, 5000);
                            if (!el && action.name === "Selling or promoting restricted items") {
                                const altXpaths = [
                                    "//span[contains(text(),'Selling or promoting')]",
                                    "//span[contains(text(),'restricted items')]",
                                    "//span[contains(text(),'Sale of regulated goods')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Me") {
                                const altXpaths = [
                                    "//span[text()='Me']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Me')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Scam, fraud") {
                                const altXpaths = [
                                    "//span[contains(text(),'Scam, fraud')]/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Scam')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Problem involving someone under 18") {
                                const altXpaths = [
                                    "//span[contains(text(),'Problem involving someone under 18')]/ancestor::div[@role='button']",
                                    "//span[contains(text(),'under 18')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Sharing someone's nude images") {
                                const altXpaths = [
                                    "//span[contains(text(),'Sharing someone's nude images')]/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Sharing') and contains(text(),'nude')]",
                                    "//span[contains(text(),'nude images')]",
                                    "//span[contains(text(),'sharing') and contains(text(),'nude')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Threatening to share my nude images") {
                                const altXpaths = [
                                    "//span[contains(text(),'Threatening to share my nude images')]/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Threatening') and contains(text(),'nude')]",
                                    "//span[contains(text(),'threatening')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Seems like sexual exploitation") {
                                const altXpaths = [
                                    "//span[contains(text(),'Seems like sexual exploitation')]/ancestor::div[@role='button']",
                                    "//span[contains(text(),'sexual exploitation')]",
                                    "//span[contains(text(),'exploitation')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Highly addictive drugs (cocaine, heroin, fentanyl)") {
                                const altXpaths = [
                                    "//span[contains(text(),'Highly addictive drugs')]",
                                    "//span[contains(text(),'cocaine')]",
                                    "//span[contains(text(),'heroin')]",
                                    "//span[contains(text(),'fentanyl')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Next") {
                                const altXpaths = [
                                    "//span[text()='Next']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Next')]",
                                    "//span[text()='Tiếp']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Tiếp')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Done") {
                                const altXpaths = [
                                    "//span[text()='Done']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Done')]",
                                    "//span[text()='Xong']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Xong')]",
                                    "//span[text()='Hoàn tất']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Hoàn tất')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (!el && action.name === "Submit") {
                                const altXpaths = [
                                    "//span[text()='Submit']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Submit')]",
                                    "//span[text()='Gửi']/ancestor::div[@role='button']",
                                    "//span[contains(text(),'Gửi')]"
                                ];
                                for (const alt of altXpaths) {
                                    el = await findElement(alt, 2000);
                                    if (el) break;
                                }
                            }
                            if (el) {
                                success = simulateClick(el);
                            }
                        }
                    } catch (e) {
                        console.warn(`Retry ${retries} for step ${action.step}:`, e);
                    }
                    if (!success && retries < maxRetries) {
                        await sleep(800 + Math.random() * 700);
                    }
                }

                if (success) {
                    addLog(`[${action.step}] ${action.name} ✓`, "green");
                } else {
                    addLog(`[${action.step}] ${action.name} ✗ (skipped)`, "yellow");
                }

                let loadCount = 0;
                while (isPageLoading() && loadCount < 10) {
                    await sleep(1000 + Math.random() * 500);
                    loadCount++;
                }
                const jitter = BASE_DELAY * (0.8 + Math.random() * 0.4);
                await sleep(jitter);
            }

            reportCount++;
            document.getElementById('metavph-reports').textContent = reportCount;
            addLog(`✅ Round #${loopCount} completed`, "green");
            await sendTelegram(`✅ Completed round ${loopCount} for ${window.location.href}`);

            if (checkIsDie()) {
                addLog("🎉 Account died after round.", "green");
                await sendTelegram(`🎉 Account died after ${loopCount} rounds`);
                stopTool();
                break;
            }
            const restTime = 3000 + Math.random() * 3000;
            addLog(`⏳ Resting ${Math.round(restTime/1000)}s before next round`, "yellow");
            await sleep(restTime);
        }
    };

    const pauseTool = () => {
        isRunning = false;
        const btn = document.getElementById('metavph-start');
        btn.textContent = '▶ RESUME';
        btn.className = 'action-btn primary';
        updateStatus('Paused', 'paused');
        document.getElementById('metavph-step-info').textContent = 'Paused';
        addLog("⏸ Paused", "yellow");
    };

    const stopTool = () => {
        isRunning = false;
        stopRequested = true;
        const btn = document.getElementById('metavph-start');
        btn.textContent = '▶ START';
        btn.className = 'action-btn primary';
        updateStatus('Stopped', 'stopped');
        document.getElementById('metavph-step-info').textContent = 'Stopped';
        updateProgress(0);
        addLog("⏹ Stopped", "red");
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUI);
    } else {
        initUI();
    }
})();
