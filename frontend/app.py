import streamlit as st
import requests
import os
import time
import math
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Memora Graph Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling for dark mode/glassmorphism
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3 {
        color: #66fcf1 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1f2833;
        border-right: 1px solid rgba(102, 252, 241, 0.1);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
    }
    
    .status-badge {
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-left: 8px;
    }
    
    .badge-active {
        color: #00ff87;
        background: rgba(0, 255, 135, 0.1);
        border: 1px solid rgba(0, 255, 135, 0.2);
    }
    
    .badge-superseded {
        color: #8a8a8a;
        background: rgba(138, 138, 138, 0.1);
        border: 1px solid rgba(138, 138, 138, 0.2);
    }
    
    .badge-disputed {
        color: #ff3366;
        background: rgba(255, 51, 102, 0.15);
        border: 1px solid rgba(255, 51, 102, 0.3);
    }

    .badge-rejected {
        color: #ff99aa;
        background: rgba(255, 0, 0, 0.05);
        border: 1px solid rgba(255, 0, 0, 0.2);
    }
    
    .chat-bubble-user {
        background: linear-gradient(135deg, #1f2833 0%, #0b0c10 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px 15px 0px 15px;
        padding: 12px 18px;
        margin: 8px 0;
        color: #fff;
        max-width: 85%;
        margin-left: auto;
    }
    
    .chat-bubble-agent {
        background: linear-gradient(135deg, #0e1e24 0%, #1f2833 100%);
        border: 1px solid rgba(102, 252, 241, 0.15);
        border-radius: 15px 15px 15px 0px;
        padding: 12px 18px;
        margin: 8px 0;
        color: #e5e5e5;
        max-width: 85%;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #888;
        margin-top: 4px;
        display: block;
    }
    
    .preset-title {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 5px;
        color: #45f3ff;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = os.environ.get("BACKEND_URL", "http://localhost:8002")

# Setup Hybrid fallback imports
try:
    from app.db import SessionLocal
    from app.memory_agent import MemoryAgent
    from app.memory_db import MemoryDB
    from app.graph_store import GraphStore
    from app.reflection import reflection_engine
    from app.models import DB_Memory, DB_AuditEvent, DB_User, DB_Entity, DB_Relationship
    from app.auth import hash_password, verify_password
    DIRECT_MODE_AVAILABLE = True
except ImportError:
    DIRECT_MODE_AVAILABLE = False

# Initialize Session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username" not in st.session_state:
    st.session_state.username = None
if "token" not in st.session_state:
    st.session_state.token = None
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{int(time.time())}"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "consolidation_logs" not in st.session_state:
    st.session_state.consolidation_logs = []

# Header UI
col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.markdown("<h1 style='text-align: center; margin: 0;'>🧠</h1>", unsafe_allow_html=True)
with col_title:
    st.title("Memora Graph: Persistent Memory Graph & Reasoning Engine")
    st.caption("A multi-user Entity-Relationship Memory Graph with dense semantic vectors, LLM resolvers, and reflecting workers.")

st.markdown("<hr style='border-color: rgba(102, 252, 241, 0.1); margin-top: 5px; margin-bottom: 20px;'/>", unsafe_allow_html=True)

# -----------------
# CONNECTION HEALTH CHECK
# -----------------
is_backend_alive = False
try:
    res = requests.get(f"{API_URL}/health", timeout=1)
    if res.status_code == 200:
        is_backend_alive = True
except Exception:
    pass

actual_mode = "API Server" if is_backend_alive else "Direct DB Connection (Port Blocked Fallback)" if DIRECT_MODE_AVAILABLE else "Disconnected"

# ==========================================
# AUTHENTICATION SCREEN
# ==========================================
if not st.session_state.username:
    st.subheader("🔐 Access Control Verification")
    
    if actual_mode == "API Server":
        st.success("🟢 Connected to FastAPI Server")
    elif "Direct DB" in actual_mode:
        st.info("⚡ Direct DB connection active (API server port blocked)")
    else:
        st.error("🔴 Backend Disconnected")

    col_auth_left, col_auth_right = st.columns(2)
    
    with col_auth_left:
        st.markdown("#### User Registration")
        reg_username = st.text_input("New Username", key="reg_user")
        reg_password = st.text_input("New Password", type="password", key="reg_pass")
        
        if st.button("Create Account"):
            if not reg_username or not reg_password:
                st.warning("Fields cannot be empty")
            elif is_backend_alive:
                try:
                    payload = {"username": reg_username, "password": reg_password}
                    res = requests.post(f"{API_URL}/register", json=payload)
                    if res.status_code == 200:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error(res.json().get("detail", "Failed to register"))
                except Exception as e:
                    st.error(f"Network error: {e}")
            elif DIRECT_MODE_AVAILABLE:
                db = SessionLocal()
                try:
                    existing = db.query(DB_User).filter(DB_User.username == reg_username).first()
                    if existing:
                        st.error("Username already exists locally")
                    else:
                        new_u = DB_User(username=reg_username, hashed_password=hash_password(reg_password))
                        db.add(new_u)
                        db.commit()
                        st.success("Account created locally! Please login.")
                finally:
                    db.close()
            else:
                st.error("System disconnected.")
                
    with col_auth_right:
        st.markdown("#### User Sign In")
        login_username = st.text_input("Username", key="log_user")
        login_password = st.text_input("Password", type="password", key="log_pass")
        
        if st.button("Sign In"):
            if is_backend_alive:
                try:
                    payload = {"username": login_username, "password": login_password}
                    res = requests.post(f"{API_URL}/token", data=payload)
                    if res.status_code == 200:
                        token_data = res.json()
                        st.session_state.token = token_data["access_token"]
                        st.session_state.username = login_username
                        st.success(f"Authenticated as {login_username}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except Exception as e:
                    st.error(f"Network error: {e}")
            elif DIRECT_MODE_AVAILABLE:
                db = SessionLocal()
                try:
                    user = db.query(DB_User).filter(DB_User.username == login_username).first()
                    if user and verify_password(login_password, user.hashed_password):
                        st.session_state.username = login_username
                        st.success(f"Authenticated locally as {login_username}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                finally:
                    db.close()
            else:
                st.error("System disconnected.")
    st.stop()

# ==========================================
# MAIN APP (AUTHENTICATED)
# ==========================================

# Auth headers helper
auth_headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# Sidebar Controls
with st.sidebar:
    st.markdown(f"👤 Logged in as: **{st.session_state.username}**")
    if st.button("🚪 Sign Out"):
        st.session_state.username = None
        st.session_state.token = None
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### ⚙️ Configurations")
    openai_key = st.text_input("OpenAI Key (Optional)", value=st.session_state.api_key, type="password")
    if openai_key != st.session_state.api_key:
        st.session_state.api_key = openai_key
        os.environ["OPENAI_API_KEY"] = openai_key
        st.success("Key updated!")
        
    st.markdown("---")
    st.markdown("### 🧪 Quick Seed Scenarios")
    
    def send_preset(msg: str):
        st.session_state.preset_to_send = msg

    st.markdown("<div class='preset-title'>Scenario A: Relocation & Job Change</div>", unsafe_allow_html=True)
    if st.button("1. 'I work at Google in San Francisco'", key="btn_a1", use_container_width=True):
        send_preset("I work at Google in San Francisco")
    if st.button("2. 'I just moved to New York for my new job at Meta'", key="btn_a2", use_container_width=True):
        send_preset("I just moved to New York for my new job at Meta")
        
    st.markdown("<div class='preset-title'>Scenario B: Dog Name Stability</div>", unsafe_allow_html=True)
    if st.button("1. 'My dog's name is Max'", key="btn_b1", use_container_width=True):
        send_preset("My dog's name is Max")
    if st.button("2. 'What's my dog's name?'", key="btn_b2", use_container_width=True):
        send_preset("What's my dog's name?")

    st.markdown("<div class='preset-title'>Scenario C: Stable Fact Conflict</div>", unsafe_allow_html=True)
    if st.button("1. 'My birthday is July 15th'", key="btn_c1", use_container_width=True):
        send_preset("My birthday is July 15th")
    if st.button("2. 'My birthday is July 20th'", key="btn_c2", use_container_width=True):
        send_preset("My birthday is July 20th")

    st.markdown("<div class='preset-title'>Scenario D: Preference Reversal</div>", unsafe_allow_html=True)
    if st.button("1. 'I hate spicy food'", key="btn_d1", use_container_width=True):
        send_preset("I hate spicy food")
    if st.button("2. 'I love spicy food actually'", key="btn_d2", use_container_width=True):
        send_preset("I love spicy food actually")

    st.markdown("---")
    st.markdown("### 🔄 Reflection Engine")
    if st.button("⚡ Trigger Consolidation Cycle", use_container_width=True):
        if is_backend_alive:
            try:
                res = requests.post(f"{API_URL}/reflection/trigger", headers=auth_headers)
                if res.status_code == 200:
                    st.session_state.consolidation_logs = res.json().get("actions_performed", [])
                    st.success("Consolidation run finished!")
                else:
                    st.error("Consolidation trigger failed.")
            except Exception as e:
                st.error(f"Error: {e}")
        elif DIRECT_MODE_AVAILABLE:
            db = SessionLocal()
            try:
                actions = reflection_engine.reflect_and_consolidate(st.session_state.username, db)
                st.session_state.consolidation_logs = actions
                st.success("Consolidation run finished locally!")
            finally:
                db.close()

    if st.button("🗑️ Reset User Memory Graph", type="primary", use_container_width=True):
        if is_backend_alive:
            try:
                requests.post(f"{API_URL}/memories/clear", headers=auth_headers)
                st.session_state.messages = []
                st.success("Memory cleared!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        elif DIRECT_MODE_AVAILABLE:
            db = SessionLocal()
            try:
                memory_db = MemoryDB(db)
                memory_db.clear_user_memory(st.session_state.username)
                st.session_state.messages = []
                st.success("Memory cleared locally!")
                time.sleep(0.5)
                st.rerun()
            finally:
                db.close()

# -----------------
# DATA LOADER HELPERS
# -----------------
def fetch_graph_data():
    active_mems = []
    history_mems = []
    audit_events = []
    graph_snap = {"nodes": [], "edges": []}
    
    if is_backend_alive:
        try:
            res_act = requests.get(f"{API_URL}/memories", headers=auth_headers)
            if res_act.status_code == 200:
                active_mems = res_act.json()
            res_hist = requests.get(f"{API_URL}/memories/history", headers=auth_headers)
            if res_hist.status_code == 200:
                history_mems = res_hist.json()
            res_aud = requests.get(f"{API_URL}/memories/audit", headers=auth_headers)
            if res_aud.status_code == 200:
                audit_events = res_aud.json()
            res_graph = requests.get(f"{API_URL}/graph/snapshot", headers=auth_headers)
            if res_graph.status_code == 200:
                graph_snap = res_graph.json()
        except Exception:
            pass
    elif DIRECT_MODE_AVAILABLE:
        db = SessionLocal()
        try:
            memory_db = MemoryDB(db)
            graph_store = GraphStore(db)
            
            # Graph snapshot
            graph_snap = graph_store.get_graph_snapshot(st.session_state.username)
            
            # Active facts
            mems_act = memory_db.get_user_profile(st.session_state.username)
            active_mems = [{
                "canonical_property": m.canonical_property,
                "status": m.status,
                "value_canonical": m.value_canonical,
                "value_raw": m.value_raw,
                "confidence": m.confidence,
                "session_id": m.session_id
            } for m in mems_act]
            
            # All history
            mems_hist = db.query(DB_Memory).filter(DB_Memory.user_id == st.session_state.username).all()
            history_mems = [{
                "canonical_property": m.canonical_property,
                "status": m.status,
                "value_canonical": m.value_canonical,
                "value_raw": m.value_raw,
                "version": m.version,
                "created_at": m.created_at.isoformat(),
                "resolution_note": m.resolution_note
            } for m in mems_hist]
            
            # Audits
            auds = memory_db.get_audit_log(st.session_state.username)
            audit_events = [{
                "event_type": e.event_type,
                "previous_value": e.previous_value,
                "new_value": e.new_value,
                "reason": e.reason,
                "resolver_type": e.resolver_type,
                "created_at": e.created_at.isoformat()
            } for e in auds]
        finally:
            db.close()
            
    return active_mems, history_mems, audit_events, graph_snap

# -----------------
# WORKSPACE LAYOUT
# -----------------
col_left, col_right = st.columns([7, 5])

# Left: Chat
with col_left:
    st.subheader("💬 Dialog Interface")
    chat_container = st.container()
    
    # Preset triggers
    preset_msg = None
    if "preset_to_send" in st.session_state and st.session_state.preset_to_send:
        preset_msg = st.session_state.preset_to_send
        st.session_state.preset_to_send = None

    # Render previous
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-agent'>{msg['content']}</div>", unsafe_allow_html=True)

    # Inputs
    user_input = st.chat_input("Feed a graph statement...")
    input_to_process = preset_msg or user_input
    
    if input_to_process:
        st.session_state.messages.append({"role": "user", "content": input_to_process})
        st.markdown(f"<div class='chat-bubble-user'>{input_to_process}</div>", unsafe_allow_html=True)
        
        agent_res = ""
        with st.spinner("Processing Memory..."):
            if is_backend_alive:
                try:
                    payload = {"user_id": st.session_state.username, "message": input_to_process, "session_id": st.session_state.session_id}
                    res = requests.post(f"{API_URL}/chat", json=payload, headers=auth_headers, timeout=5)
                    if res.status_code == 200:
                        agent_res = res.json().get("response", "")
                    else:
                        agent_res = f"API Error: {res.text}"
                except Exception as e:
                    agent_res = f"Network Error: {e}"
            elif DIRECT_MODE_AVAILABLE:
                db = SessionLocal()
                try:
                    agent = MemoryAgent(db)
                    chat_res = agent.process_message(st.session_state.username, input_to_process, st.session_state.session_id)
                    agent_res = chat_res.response
                except Exception as e:
                    agent_res = f"Local processing error: {e}"
                finally:
                    db.close()
                    
        st.session_state.messages.append({"role": "agent", "content": agent_res})
        st.markdown(f"<div class='chat-bubble-agent'>{agent_res}</div>", unsafe_allow_html=True)
        st.rerun()

# Right: Graph Visualizations & Tabs
with col_right:
    active_mems, history_mems, audit_events, graph_snap = fetch_graph_data()
    
    st.subheader("📊 Graph Diagnostics")
    
    tab_graph, tab_active, tab_history, tab_audit = st.tabs([
        "🔮 Network Graph", "🟢 Active Nodes", "🕰️ Version Timeline", "🔍 Audit Log Console"
    ])
    
    with tab_graph:
        st.markdown("#### Entity-Relationship Graph Visual")
        nodes = graph_snap.get("nodes", [])
        edges = graph_snap.get("edges", [])
        
        if not nodes:
            st.info("No nodes in graph yet. Send statements to generate node linkages.")
        else:
            # Render a beautiful SVG-based node-edge visualization
            svg_width = 500
            svg_height = 300
            
            # Map type colors
            type_colors = {
                "self": "#66fcf1",
                "organization": "#a855f7",
                "location": "#f97316",
                "pet": "#eab308"
            }
            
            # Find User node
            user_node_id = None
            for n in nodes:
                if n["type"] == "self":
                    user_node_id = n["id"]
                    break
                    
            # Layout calculation: Central Star/Radial Topology
            coords = {}
            if user_node_id is not None:
                coords[user_node_id] = (svg_width / 2, svg_height / 2)
                
            leaf_nodes = [n for n in nodes if n["id"] != user_node_id]
            R = 110 # Radius
            
            for idx, ln in enumerate(leaf_nodes):
                angle = (idx * 2 * math.pi) / len(leaf_nodes) if leaf_nodes else 0
                cx = (svg_width / 2) + R * math.cos(angle)
                cy = (svg_height / 2) + R * math.sin(angle)
                coords[ln["id"]] = (cx, cy)
                
            # If user node doesn't exist but others do, arrange in a circle
            if user_node_id is None and nodes:
                for idx, n in enumerate(nodes):
                    angle = (idx * 2 * math.pi) / len(nodes)
                    cx = (svg_width / 2) + R * math.cos(angle)
                    cy = (svg_height / 2) + R * math.sin(angle)
                    coords[n["id"]] = (cx, cy)
                    
            # Generate SVG elements
            svg_elements = []
            
            # 1. Draw edge lines
            for e in edges:
                s_id = e["source"]
                t_id = e["target"]
                if s_id in coords and t_id in coords:
                    x1, y1 = coords[s_id]
                    x2, y2 = coords[t_id]
                    # Line
                    svg_elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgba(102, 252, 241, 0.3)" stroke-width="2" />')
                    # Edge label along line (midpoint)
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    svg_elements.append(f'<rect x="{mx-35}" y="{my-8}" width="70" height="15" rx="3" fill="#1f2833" stroke="rgba(102, 252, 241, 0.2)" stroke-width="1"/>')
                    svg_elements.append(f'<text x="{mx}" y="{my+3}" fill="#66fcf1" font-size="8" text-anchor="middle" font-family="sans-serif">{e["label"]}</text>')
                    
            # 2. Draw node circles
            for n in nodes:
                if n["id"] in coords:
                    cx, cy = coords[n["id"]]
                    color = type_colors.get(n["type"], "#9ca3af")
                    r_size = 22 if n["type"] == "self" else 18
                    
                    # Glowing shadow for user node
                    glow = f'<circle cx="{cx}" cy="{cy}" r="{r_size+5}" fill="none" stroke="{color}" stroke-dasharray="2" stroke-width="1" opacity="0.5"/>' if n["type"] == "self" else ""
                    
                    svg_elements.append(f"""
                    {glow}
                    <circle cx="{cx}" cy="{cy}" r="{r_size}" fill="#0b0c10" stroke="{color}" stroke-width="3" />
                    <text x="{cx}" y="{cy+4}" fill="#fff" font-size="8" font-weight="bold" font-family="sans-serif" text-anchor="middle">{n["name"][:7]}</text>
                    <text x="{cx}" y="{cy + r_size + 12}" fill="#9ca3af" font-size="8" font-family="sans-serif" text-anchor="middle">{n["type"].upper()}</text>
                    """)
                    
            svg_html = f"""
            <svg width="100%" height="{svg_height}" style="background-color:#121824; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
                {"".join(svg_elements)}
            </svg>
            """
            st.markdown(svg_html, unsafe_allow_html=True)
            
            # Show consolidation actions if run
            if st.session_state.consolidation_logs:
                st.markdown("##### ⚡ Reflection Optimization Log")
                for action in st.session_state.consolidation_logs:
                    st.caption(f"🔧 {action}")

    with tab_active:
        st.markdown("#### Current Active Profile Nodes")
        if not active_mems:
            st.info("No active memories. Start dialogs to extract facts.")
        else:
            for mem in active_mems:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color: #66fcf1; text-transform: capitalize;">{mem['canonical_property'].replace('_', ' ')}</strong>
                        <span class="status-badge badge-active">{mem['status']}</span>
                    </div>
                    <div style="font-size: 1.1rem; margin: 8px 0; color: #fff;">
                        {mem['value_canonical']}
                    </div>
                    <div style="font-size: 0.8rem; color: #888;">
                        Raw representation: <i>"{mem['value_raw']}"</i><br/>
                        Confidence: <b>{mem['confidence']:.2f}</b> | Session: {mem['session_id']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_history:
        st.markdown("#### Complete Graph Fact History")
        if not history_mems:
            st.info("No version history recorded yet.")
        else:
            properties_grouped = {}
            for m in history_mems:
                p = m["canonical_property"]
                if p not in properties_grouped:
                    properties_grouped[p] = []
                properties_grouped[p].append(m)
                
            for prop, items in properties_grouped.items():
                st.markdown(f"<h5 style='color: #45f3ff; margin-bottom:5px;'>Property: {prop.replace('_', ' ').capitalize()}</h5>", unsafe_allow_html=True)
                items.sort(key=lambda x: x["version"], reverse=True)
                
                for item in items:
                    badge_class = "badge-active"
                    if item["status"] == "superseded":
                        badge_class = "badge-superseded"
                    elif item["status"] == "disputed":
                        badge_class = "badge-disputed"
                    elif item["status"] == "rejected":
                        badge_class = "badge-rejected"
                        
                    note = f"<div style='font-size:0.75rem; color:#ffb3ba; margin-top:4px;'>⚠️ {item['resolution_note']}</div>" if item['resolution_note'] else ""
                    
                    st.markdown(f"""
                    <div style="border-left: 2px solid rgba(102, 252, 241, 0.4); padding-left: 12px; margin-bottom: 12px; margin-left: 8px;">
                        <div>
                            <b>v{item['version']}</b>: <span style="color:#fff;">{item['value_canonical']}</span>
                            <span class="status-badge {badge_class}">{item['status']}</span>
                        </div>
                        <span class="timestamp">
                            Raw: "{item['value_raw']}" | Effective: {item['created_at'][:19].replace('T', ' ')}
                        </span>
                        {note}
                    </div>
                    """, unsafe_allow_html=True)

    with tab_audit:
        st.markdown("#### Audit Event Logs")
        if not audit_events:
            st.info("No system operations registered yet.")
        else:
            for event in audit_events:
                ev_type = event["event_type"].upper()
                badge_style = "color:#00ff87;" if ev_type == "CREATED" else "color:#ff3366;" if ev_type == "DISPUTED" else "color:#8a8a8a;"
                
                prev_text = f"Previously: <del style='color:#ff8888;'>'{event['previous_value']}'</del> &rarr; " if event['previous_value'] else ""
                val_text = f"Value: <b style='color:#fff;'>'{event['new_value']}'</b>" if event['new_value'] else ""
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.04); border-radius:8px; padding:10px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
                        <span style="{badge_style} font-weight:bold;">[{ev_type}]</span>
                        <span style="color:#666;">{event['created_at'][:19].replace('T', ' ')}</span>
                    </div>
                    <div style="font-size:0.85rem; margin: 4px 0;">
                        {prev_text}{val_text}
                    </div>
                    <div style="font-size:0.8rem; color:#888;">
                        Reason: <i>{event['reason']}</i> (Resolver: {event['resolver_type'] or 'system'})
                    </div>
                </div>
                """, unsafe_allow_html=True)
