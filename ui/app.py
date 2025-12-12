import streamlit as st
import requests #http requests to agents


# Load Custom CSS
with open("assets/custom.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="People Pleasing AI - Conflict Resolution", page_icon="💬", layout="centered")


# Center-aligned title
st.markdown("<h1 style='text-align:center;'>People Pleasing AI – Conflict Resolution</h1>", unsafe_allow_html=True)


with st.form(key="inputs"):
    col1, col2 = st.columns(2)
    with col1:
        user_A = st.text_area("User A says...", height=60, key='userA')
    with col2:
        user_B = st.text_area("User B says...", height=60, key='userB')
    submit = st.form_submit_button("✨ Generate AI Response")


if submit and user_A and user_B:
    payload = {"user_A_text": user_A, "user_B_text": user_B}
    with st.spinner('Analyzing and generating response...'):
        persp = requests.post("http://localhost:8001/extract", json=payload, timeout=45).json() #perspective requests
        sent = requests.post("http://localhost:8002/analyze", json=payload, timeout=45).json() #sentiment requests
        reconcile = {"perspectives": persp, "sentiments": sent}
        reply = requests.post("http://localhost:8003/reconcile", json=reconcile, timeout=60).json() #reconcile request
        final_reply = reply.get('reply', '')

        # ---- NEW: call safety agent on the final reply ----
        safety_result = {}
        if final_reply:
            safety_payload = {"reply_text": final_reply}
            safety_resp = requests.post("http://localhost:8004/safety", json=safety_payload, timeout=30)
            try:
                safety_result = safety_resp.json()
            except Exception:
                safety_result = {"approved": False, "reason": "Safety check failed", "scores": {}}
        # ---------------------------------------------------

    # Extract perspective and sentiment data
    ua_persp = persp["user_A_perspectives"][0]
    ub_persp = persp["user_B_perspectives"][0]
    ua = sent["user_A_sentiment"]
    ub = sent["user_B_sentiment"]
    
    # Display perspective and sentiment side by side
    st.markdown(f"""
    <div style="display:flex;gap:24px;margin:20px 0;">
        <div style="background:#f0f9ff;border-left:6px solid #2193b0;border-radius:12px;padding:18px;box-shadow:0 3px 18px rgba(33,147,176,.12);flex:1;">
            <h3 style="margin:0 0 12px 0;color:#134e5e;">User A</h3>
            <p style="margin:5px 0;color:#134e5e;"><b>Stance:</b> {ua_persp['stance']}</p>
            <p style="margin:5px 0;color:#134e5e;"><b>Intent:</b> {ua['intent']}</p>
            <p style="margin:5px 0;color:#134e5e;"><b>Valence:</b> {ua['valence']:.2f}</p>
            <p style="margin:5px 0;font-size:0.95em;color:#134e5e;"><b>Emotions:</b> <i>{', '.join(f"{k}: {v:.2f}" for k,v in ua['emotion_scores'].items())}</i></p>
        </div>
        <div style="background:#fff9f0;border-left:6px solid #f2994a;border-radius:12px;padding:18px;box-shadow:0 3px 18px rgba(242,153,74,.12);flex:1;">
            <h3 style="margin:0 0 12px 0;color:#134e5e;">User B</h3>
            <p style="margin:5px 0;color:#134e5e;"><b>Stance:</b> {ub_persp['stance']}</p>
            <p style="margin:5px 0;color:#134e5e;"><b>Intent:</b> {ub['intent']}</p>
            <p style="margin:5px 0;color:#134e5e;"><b>Valence:</b> {ub['valence']:.2f}</p>
            <p style="margin:5px 0;font-size:0.95em;color:#134e5e;"><b>Emotions:</b> <i>{', '.join(f"{k}: {v:.2f}" for k,v in ub['emotion_scores'].items())}</i></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Professional response tray
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px 40px;
        margin: 28px 0;
        box-shadow: 0 12px 42px rgba(102, 126, 234, 0.35);
        border: 2px solid rgba(255,255,255,0.18);
    ">
        <h3 style="color:#fff;text-align:center;margin:0 0 20px 0;font-size:1.5em;font-weight:700;">Generated Response</h3>
        <div style="
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 24px 28px;
            color: #2d3748;
            font-size: 1.12em;
            line-height: 1.7;
            text-align: left;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        ">{final_reply}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- NEW: show safety result ----
    if safety_result:
        if safety_result.get("approved", False):
            st.success("✅ Safety check passed: response is approved.")
        else:
            st.error("⚠️ Safety check flagged this response.")
            reason = safety_result.get("reason")
            if reason:
                st.write(reason)
            scores = safety_result.get("scores", {})
            if scores:
                st.write("Safety scores:")
                st.json(scores)
    # ---------------------------------


    # Professional feedback section
    st.markdown("<hr style='margin:36px 0 24px 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style='text-align:center;color:#2d3748;margin-bottom:20px;'>Feedback & Evaluation</h3>
    <p style='text-align:center;color:#4a5568;font-size:1.05em;margin-bottom:24px;'>Please rate the proposed resolution</p>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div style='text-align:center;font-weight:600;color:#134e5e;margin-bottom:10px;'>User A</div>", unsafe_allow_html=True)
        like_a = st.button("✓ Approve", key="likeA", use_container_width=True)
        dislike_a = st.button("✗ Reject", key="dislikeA", use_container_width=True)
    with c2:
        st.markdown("<div style='text-align:center;font-weight:600;color:#134e5e;margin-bottom:10px;'>User B</div>", unsafe_allow_html=True)
        like_b = st.button("✓ Approve", key="likeB", use_container_width=True)
        dislike_b = st.button("✗ Reject", key="dislikeB", use_container_width=True)

    feedback = []
    if like_a:
        feedback.append("User A: Approved")
    if dislike_a:
        feedback.append("User A: Rejected")
    if like_b:
        feedback.append("User B: Approved")
    if dislike_b:
        feedback.append("User B: Rejected")
    if feedback:
        st.info("📊 " + " | ".join(feedback))


st.markdown('<div style="text-align:center;color:#777;margin-top:2em;">Designed by Archit Gupta, Rounaq Moin, Gunda Rama Praneetha 💡</div>', unsafe_allow_html=True)
