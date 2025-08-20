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

def render_paywall_and_check():
    cfg = get_pay_settings()
    if not cfg["PAYWALL_ENABLED"]:
        return True  # Paywall disabled

    # Auto pre-fill from ?code=XXXX in URL
    qp = st.experimental_get_query_params()
    prefill = (qp.get("code", [""])[0] or "").strip()

    with st.sidebar:
        st.header("🔑 Download access")
        code = st.text_input("Access code", value=prefill, type="password")

        auto = False
        # Auto-unlock if ?code=XXXX matches
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
