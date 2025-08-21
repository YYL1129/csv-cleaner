# payment.py
import streamlit as st

def get_pay_settings():
    s = st.secrets
    return {
        "PAYWALL_ENABLED": str(s.get("PAYWALL_ENABLED", "false")).lower() == "true",
        "ACCESS_MODE": str(s.get("ACCESS_MODE", "code")),
        "ACCESS_CODE": s.get("ACCESS_CODE", ""),
        "PAY_LINK": s.get("PAY_LINK", "#"),
        "SHOW_BUY_LINK": str(s.get("SHOW_BUY_LINK", "true")).lower() == "true",
    }

def _code_from_url() -> str:
    """Read ?code=... from URL; works with new and old Streamlit APIs."""
    # New API
    try:
        qp = st.query_params  # dict-like
        raw = qp.get("code", "")
        if isinstance(raw, (list, tuple)):
            return (raw[0] or "").strip()
        return (raw or "").strip()
    except Exception:
        pass
    # Fallback to old API (just in case)
    try:
        qp_old = st.experimental_get_query_params()
        return (qp_old.get("code", [""])[0] or "").strip()
    except Exception:
        return ""

def render_paywall_and_check():
    cfg = get_pay_settings()
    if not cfg["PAYWALL_ENABLED"]:
        return True  # Paywall disabled

    # ----- Prefill from URL & sync into session state -----
    prefill = _code_from_url()
    # Ensure the text_input uses a stable key
    key = "access_code_field"

    # If URL contains a code and session has a different/empty value, overwrite it
    if prefill and st.session_state.get(key, "") != prefill:
        st.session_state[key] = prefill

    with st.sidebar:
        st.header("🔑 Download access")
        code = st.text_input("Access code", type="password", key=key)

        auto = False
        # Auto-unlock if URL code matches
        if prefill and cfg["ACCESS_MODE"] == "code" and prefill == cfg["ACCESS_CODE"]:
            st.success("✅ Download unlocked (via purchase link).")
            st.session_state["unlocked"] = True
            auto = True

        if not auto and st.button("Unlock"):
            if cfg["ACCESS_MODE"] == "code" and code == cfg["ACCESS_CODE"]:
                st.success("✅ Download unlocked.")
                st.session_state["unlocked"] = True
            else:
                st.error("❌ Invalid code. Please check your purchase email.")

        if cfg["SHOW_BUY_LINK"]:
            st.markdown(f"Don’t have a code? 👉 [Buy access]({cfg['PAY_LINK']})")

    return st.session_state.get("unlocked", False)
