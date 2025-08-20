# payment.py
import streamlit as st

def get_pay_settings():
    s = st.secrets
    return {
        "PAYWALL_ENABLED": str(s.get("PAYWALL_ENABLED", "false")).lower() == "true",
        "ACCESS_MODE": str(s.get("ACCESS_MODE", "code")),  # keep "code"
        "ACCESS_CODE": s.get("ACCESS_CODE", ""),           # e.g. "MYVIP2025"
        "PAY_LINK": s.get("PAY_LINK", "https://your-pay-link"),
    }

def render_paywall_and_check():
    cfg = get_pay_settings()
    if not cfg["PAYWALL_ENABLED"]:
        return True  # no paywall -> allow download

    with st.sidebar:
        st.header("🔑 Download access")
        code = st.text_input("Access code", type="password")
        if st.button("Unlock"):
            if cfg["ACCESS_MODE"] == "code" and code == cfg["ACCESS_CODE"]:
                st.success("Download unlocked.")
                st.session_state["unlocked"] = True
            else:
                st.error("Invalid code. Please check your purchase email.")
        st.markdown(f"Don’t have a code? [Buy access]({cfg['PAY_LINK']})")

    return st.session_state.get("unlocked", False)
