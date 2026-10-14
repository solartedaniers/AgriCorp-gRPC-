import streamlit as st


class ThemeInjector:
    STYLES = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Public+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap");
:root{--paper:#F3F5F1;--surface:#FFFFFF;--ink:#18261E;--muted:#5B6A61;--line:#D6DED6;--leaf:#2F6B4A;--leaf-soft:#E2EEE6;--cherry:#A8323A;--cherry-soft:#F6E3E4;--pergamino:#B8873A;--pergamino-soft:#F3EAD9;--cacao:#4B3427;}
html,body,[data-testid="stAppViewContainer"]{background:var(--paper);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stMainBlockContainer"]{max-width:1240px;padding-top:2.2rem;padding-bottom:4rem;}
#MainMenu,footer,[data-testid="stDecoration"]{display:none;}
h1,h2,h3{letter-spacing:-0.015em;}
.ag-masthead{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2rem;align-items:end;padding-bottom:1.6rem;margin-bottom:.4rem;border-bottom:1px solid var(--line);}
.ag-masthead h1{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:clamp(2.2rem,4.6vw,3.6rem);line-height:1;margin:0 0 .9rem 0;padding:0;color:var(--ink);}
.ag-masthead p{max-width:62ch;margin:0;color:var(--muted);font-size:1.02rem;line-height:1.55;}
.ag-stations{display:flex;flex-direction:column;gap:.5rem;min-width:260px;}
.ag-station{display:grid;grid-template-columns:12px 1fr auto;gap:.7rem;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:.65rem .9rem;}
.ag-station b{display:block;font-size:.92rem;color:var(--ink);font-weight:600;}
.ag-station small{color:var(--muted);font-size:.78rem;font-family:"JetBrains Mono",monospace;}
.ag-station span.state{font-size:.8rem;font-weight:600;}
.ag-dot{width:10px;height:10px;border-radius:50%;}
.ag-dot.on{background:var(--leaf);box-shadow:0 0 0 4px var(--leaf-soft);}
.ag-dot.off{background:var(--cherry);box-shadow:0 0 0 4px var(--cherry-soft);}
.state.on{color:var(--leaf);} .state.off{color:var(--cherry);}
.ag-section-caption{color:var(--muted);margin:-.4rem 0 1.1rem 0;font-size:.95rem;max-width:70ch;}
.ag-quote{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1.6rem 1.7rem 1.4rem;}
.ag-quote .name{font-family:"Bricolage Grotesque",sans-serif;font-size:1.35rem;font-weight:700;color:var(--ink);margin:0;}
.ag-quote .meta{color:var(--muted);font-size:.88rem;margin:.15rem 0 1.1rem;}
.ag-quote .price{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:clamp(2.4rem,5vw,3.4rem);line-height:1;color:var(--ink);font-variant-numeric:tabular-nums;}
.ag-quote .price small{font-family:"Public Sans",sans-serif;font-size:1rem;font-weight:500;color:var(--muted);margin-left:.4rem;}
.ag-change{display:inline-flex;gap:.35rem;align-items:center;margin-top:.8rem;padding:.25rem .65rem;border-radius:999px;font-weight:600;font-size:.88rem;font-variant-numeric:tabular-nums;}
.ag-change.up{background:var(--leaf-soft);color:var(--leaf);}
.ag-change.down{background:var(--cherry-soft);color:var(--cherry);}
.ag-change.stable{background:#ECEFEC;color:var(--muted);}
.ag-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1.3rem;padding-top:1.1rem;border-top:1px dashed var(--line);}
.ag-facts dt{color:var(--muted);font-size:.8rem;margin:0;}
.ag-facts dd{margin:.15rem 0 0;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums;}
.ag-wire{background:var(--ink);color:#E9EFEA;border-radius:14px;padding:1.4rem 1.6rem;margin-top:1rem;}
.ag-wire h4{font-family:"Bricolage Grotesque",sans-serif;font-size:1.05rem;font-weight:700;margin:0 0 .2rem;color:#FFFFFF;padding:0;}
.ag-wire .lead{display:flex;align-items:baseline;gap:.6rem;margin:.2rem 0 1.1rem;}
.ag-wire .lead strong{font-family:"Bricolage Grotesque",sans-serif;font-size:2.4rem;font-weight:800;color:#9FD3B2;line-height:1;font-variant-numeric:tabular-nums;}
.ag-wire .lead span{color:#B8C6BD;font-size:.92rem;}
.ag-wire .group{margin-top:.9rem;}
.ag-wire .group-label{font-size:.8rem;color:#B8C6BD;margin-bottom:.35rem;}
.ag-bar{display:grid;grid-template-columns:150px 1fr 96px;gap:.8rem;align-items:center;margin:.3rem 0;font-size:.84rem;}
.ag-bar .track{height:12px;background:rgba(255,255,255,.07);border-radius:6px;overflow:hidden;}
.ag-bar .fill{height:100%;border-radius:6px;}
.ag-bar .fill.pb{background:#9FD3B2;} .ag-bar .fill.js{background:#D9B36E;}
.ag-bar .value{text-align:right;font-family:"JetBrains Mono",monospace;font-size:.8rem;color:#FFFFFF;}
.ag-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden;}
.ag-stat{padding:1.1rem 1.3rem;border-right:1px solid var(--line);border-bottom:1px solid var(--line);}
.ag-stat:nth-child(3n){border-right:none;}
.ag-stat:nth-last-child(-n+3){border-bottom:none;}
.ag-stat dt{color:var(--muted);font-size:.82rem;margin:0;}
.ag-stat dd{margin:.25rem 0 0;font-family:"Bricolage Grotesque",sans-serif;font-size:1.65rem;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;line-height:1.1;}
.ag-stat dd small{display:block;font-family:"Public Sans",sans-serif;font-size:.78rem;font-weight:500;color:var(--muted);margin-top:.2rem;}
.ag-stat.alert dd{color:var(--cherry);}
.ag-empty{border:1.5px dashed var(--line);border-radius:14px;padding:2.4rem 1.8rem;color:var(--muted);background:rgba(255,255,255,.5);line-height:1.55;}
.ag-board{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.7rem;}
.ag-tile{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--pergamino);border-radius:8px;padding:.8rem 1rem;}
.ag-tile.up{border-left-color:var(--leaf);} .ag-tile.down{border-left-color:var(--cherry);}
.ag-tile b{display:block;font-size:.88rem;font-weight:600;color:var(--ink);}
.ag-tile .v{font-family:"Bricolage Grotesque",sans-serif;font-size:1.3rem;font-weight:700;font-variant-numeric:tabular-nums;color:var(--ink);}
.ag-tile small{color:var(--muted);font-size:.78rem;}
.ag-table-wrap{overflow-x:auto;margin-bottom:1.4rem;}
.ag-table{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:.9rem;}
.ag-table th{text-align:left;font-weight:600;color:var(--muted);background:#EEF2EE;padding:.7rem .9rem;border-bottom:1px solid var(--line);}
.ag-table td{padding:.7rem .9rem;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.45;color:var(--ink);}
.ag-table tr:last-child td{border-bottom:none;}
.ag-table td:first-child{font-weight:600;}
.stTabs [data-baseweb="tab-list"]{gap:1.6rem;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{padding:.9rem 0;font-weight:600;}
.stTabs [data-baseweb="tab"] p{font-size:1rem;}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--surface);}
.stButton button[kind="primary"]{font-weight:600;padding:.6rem 1rem;}
:focus-visible{outline:3px solid #8FC5A3 !important;outline-offset:2px;}
@media (max-width:820px){.ag-masthead{grid-template-columns:1fr;}.ag-stations{min-width:0;}.ag-stats{grid-template-columns:repeat(2,minmax(0,1fr));}.ag-stat{border-right:none;}.ag-facts{grid-template-columns:1fr 1fr;}.ag-bar{grid-template-columns:110px 1fr 80px;}}
@media (prefers-reduced-motion:reduce){*{transition:none !important;animation:none !important;}}
</style>
"""

    def apply(self) -> None:
        st.markdown(self.STYLES, unsafe_allow_html=True)
