import streamlit as st
from model import (
    analyze_text,
    analyze_claims,
    virality_risk,
    explain_score,
    confidence_band,
    recommended_action,
    fact_check_assist
)

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="VeriLens",
    layout="wide"
)

# ================== HEADER ==================
st.title("🛡️ VeriLens")
st.subheader("Explainable AI for Early Misinformation Risk Detection")

# ================== DECISION MODE ==================
st.markdown("### Decision Mode")
mode = st.radio(
    "Select analysis context:",
    ["Informational", "High-Stakes (Journalism / Policy)"],
    horizontal=True
)

# ================== INPUT ==================
text = st.text_area(
    "Paste a news article or social media post:",
    height=180
)

# ================== ANALYSIS ==================
if st.button("Analyze"):
    if text.strip() == "":
        st.warning("Please enter some text.")
    else:
        # ---- MODEL OUTPUTS ----
        risk, tone = analyze_text(text)
        claims = analyze_claims(text)
        viral = virality_risk(text)
        reasons = explain_score(text, risk)

        signals_count = len(reasons)
        confidence, uncertainty = confidence_band(risk, signals_count)
        actions = recommended_action(risk, mode)

        # ================== DASHBOARD TOP BAR ==================
        st.divider()
        st.markdown("## Analysis Overview")

        col1, col2, col3 = st.columns([1.3, 1, 1])

        with col1:
            st.metric("Misinformation Risk Score", f"{risk}/100")

        with col2:
            if risk > 70:
                st.error("High Risk")
            elif risk > 40:
                st.warning("Moderate Risk")
            else:
                st.success("Low Risk")

        with col3:
            st.markdown("**Context**")
            st.write(mode)

        # ================== CONFIDENCE ==================
        st.divider()
        st.markdown("## Confidence & Uncertainty")

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Confidence Level:** {confidence}")
        with c2:
            st.write(f"**Uncertainty Margin:** {uncertainty}")

        # ================== INTELLIGENCE SIGNALS ==================
        st.divider()
        st.markdown("## Intelligence Signals")

        left, right = st.columns(2)

        with left:
            st.markdown("### Explainability")
            if reasons:
                for r in reasons:
                    st.write("•", r)
            else:
                st.success("No significant linguistic risk signals detected.")

        with right:
            st.markdown("### Virality Risk")
            st.info(f"Expected Spread Potential: **{viral}**")

        # ================== RISK BREAKDOWN ==================
        st.divider()
        st.markdown("## Risk Breakdown")

        r1, r2 = st.columns(2)

        with r1:
            st.markdown("### Highest Risk Claim")
            if claims:
                st.warning(f"“{claims[0]['claim']}”")
                st.caption(f"Claim Risk Score: {claims[0]['risk']}/100")
            else:
                st.success("No dominant high-risk claim identified.")

        with r2:
            st.markdown("### Recommended Action")
            for act in actions:
                st.write("•", act)

        # ================== VERIFICATION SIGNALS ==================
        st.divider()
        st.markdown("##  Verification Signals")
        st.caption("Automated credibility cues — not automated fact determination")

        verify_claims, sources, status = fact_check_assist(text)

        if verify_claims:
            st.warning("Claims that may require independent verification:")
            for c in verify_claims:
                st.write("•", c)
        else:
            st.success("No obvious unverifiable claims detected.")

        st.markdown("**Suggested sources to consult:**")
        for s in sources:
            st.write("•", s)

        st.caption(f"Verification status: {status}")

        # ================== FOOTER ==================
        st.divider()
        st.markdown("### Language Tone")
        st.write(tone)

        st.markdown(
            "<center><small>"
            "VeriLens is an explainable, human-in-the-loop decision support system. "
            "It provides early misinformation risk signals and does not determine absolute truth."
            "</small></center>",
            unsafe_allow_html=True
        )
