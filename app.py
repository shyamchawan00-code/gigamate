import streamlit as st
import pandas as pd
from supabase import create_client, Client
from google import genai
from datetime import date

st.set_page_config(page_title="GIGMATE AI", page_icon="🤝", layout="wide")

def get_secrets():
    return st.secrets

def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

def get_gemini():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def init_auth(sb):
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        try:
            sb.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])
            return True
        except Exception:
            st.session_state.pop("access_token", None)
            st.session_state.pop("refresh_token", None)
    return False

def ai(prompt):
    try:
        client = get_gemini()
        response = client.models.generate_content(
            model=st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=prompt
        )
        return response.text or "Gemini returned an empty response."
    except Exception as e:
        return f"Gemini request failed: {e}"

def main_app(sb, user):
    st.title("🤝 GIGMATE AI")
    st.caption("Your AI-powered startup operations assistant · Hyderabad pilot")
    with st.sidebar:
        st.success(f"Signed in: {user.email}")
        if st.button("Sign out"):
            try:
                sb.auth.sign_out()
            finally:
                for key in ["access_token", "refresh_token", "user"]:
                    st.session_state.pop(key, None)
                st.rerun()
        st.divider()
        st.markdown("### Pilot targets")
        st.metric("Business partners", "0 / 10")
        st.metric("Students", "0 / 50")
        st.metric("Paid gigs", "0 / 10")

    tabs = st.tabs(["Dashboard", "Lead CRM", "AI Outreach", "AI Sales Coach"])

    with tabs[0]:
        res = sb.table("leads").select("*").order("created_at", desc=True).execute()
        leads = res.data or []
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total leads", len(leads))
        c2.metric("Interested", sum(x.get("status") == "Interested" for x in leads))
        c3.metric("Pilot agreed", sum(x.get("status") == "Pilot agreed" for x in leads))
        c4.metric("Active partners", sum(x.get("status") == "Active partner" for x in leads))
        st.subheader("Follow-ups due")
        due = [x for x in leads if x.get("next_followup") and x["next_followup"] <= date.today().isoformat()]
        if due:
            st.dataframe(pd.DataFrame(due)[["business","contact_person","phone","status","next_followup"]], use_container_width=True)
        else:
            st.info("No follow-ups due today. Add leads and set a next follow-up date.")

    with tabs[1]:
        st.subheader("Add a business lead")
        with st.form("add_lead", clear_on_submit=True):
            c1,c2 = st.columns(2)
            business = c1.text_input("Business name *")
            category = c2.selectbox("Category", ["Digital agency","Startup","Event company","Restaurant / retail","Real estate","E-commerce","Education","Other"])
            contact = c1.text_input("Contact person")
            phone = c2.text_input("Business phone")
            email = c1.text_input("Business email")
            area = c2.text_input("Hyderabad area")
            source = c1.selectbox("Source", ["Google Maps","LinkedIn","Instagram","Referral","Walk-in","Other"])
            budget = c2.text_input("Estimated budget")
            requirement = st.text_area("Potential requirement")
            priority = c1.selectbox("Priority", ["High","Medium","Low"], index=1)
            next_followup = c2.date_input("Next follow-up", value=date.today())
            notes = st.text_area("Notes")
            submit = st.form_submit_button("Save lead", type="primary")
            if submit:
                if not business.strip():
                    st.error("Business name is required.")
                else:
                    payload = {
                        "user_id": user.id, "business": business.strip(), "category": category,
                        "contact_person": contact, "phone": phone, "email": email, "area": area,
                        "source": source, "budget": budget, "requirement": requirement,
                        "priority": priority, "next_followup": next_followup.isoformat(), "notes": notes,
                        "status": "New"
                    }
                    try:
                        sb.table("leads").insert(payload).execute()
                        st.success("Lead saved to your cloud CRM.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not save lead: {e}")

        st.subheader("Your pipeline")
        data = sb.table("leads").select("*").order("created_at", desc=True).execute().data or []
        if data:
            for lead in data:
                with st.expander(f"#{lead['id']} · {lead['business']} · {lead['status']}"):
                    with st.form(f"update_{lead['id']}"):
                        status_options = ["New","Contacted","Interested","Meeting scheduled","Pilot agreed","Active partner","Not interested"]
                        current = lead.get("status") or "New"
                        status = st.selectbox("Status", status_options, index=status_options.index(current))
                        priority_options = ["High","Medium","Low"]
                        priority = st.selectbox("Priority", priority_options, index=priority_options.index(lead.get("priority") or "Medium"))
                        followup = st.text_input("Next follow-up (YYYY-MM-DD)", value=lead.get("next_followup") or "")
                        notes = st.text_area("Notes", value=lead.get("notes") or "")
                        if st.form_submit_button("Update lead"):
                            try:
                                sb.table("leads").update({"status":status,"priority":priority,"next_followup":followup or None,"notes":notes}).eq("id",lead["id"]).eq("user_id",user.id).execute()
                                st.success("Updated.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update failed: {e}")
        else:
            st.caption("No leads yet. Add your first Hyderabad prospect above.")

    with tabs[2]:
        st.subheader("AI outreach studio")
        data = sb.table("leads").select("*").order("business").execute().data or []
        if not data:
            st.info("Add a lead in CRM first.")
        else:
            selected_id = st.selectbox("Choose business", [x["id"] for x in data], format_func=lambda x: next((f'{r["business"]} (#{r["id"]})' for r in data if r["id"] == x), str(x)))
            lead = next(x for x in data if x["id"] == selected_id)
            channel = st.selectbox("Channel", ["WhatsApp","LinkedIn","Email","Cold-call script"])
            if st.button("Generate personalised draft", type="primary"):
                prompt = f"""You are GIGMATE AI, a practical sales assistant for a new Hyderabad student workforce marketplace.
Draft a concise, personalised {channel} message for this business.
Business: {lead.get('business')}
Category: {lead.get('category')}
Contact: {lead.get('contact_person')}
Area: {lead.get('area')}
Potential requirement: {lead.get('requirement')}
Offer: a small paid pilot matching the business with suitable adult students for a clearly scoped task.
Do not invent facts, claim prior contact, claim students are verified unless stated, or promise results.
Ask for a short discovery conversation. Make it natural and professional."""
                st.session_state["outreach_draft"] = ai(prompt)
            if "outreach_draft" in st.session_state:
                st.text_area("Review and edit before sending", value=st.session_state["outreach_draft"], height=220, key="edited_outreach")
                st.warning("This app only drafts messages. You must review and send them yourself.")

    with tabs[3]:
        st.subheader("Ask your AI sales coach")
        question = st.text_area("Your question", placeholder="A business says they already hire freelancers. How should I respond?")
        if st.button("Ask GIGMATE", type="primary", disabled=not question.strip()):
            prompt = f"""You are GIGMATE AI, a practical startup sales coach for a founder launching a student gig marketplace in Hyderabad.
Give specific, ethical, low-budget advice. Focus on acquiring business partners and running paid pilots.
Do not fabricate lead data or claim to have contacted anyone.
Founder question: {question}"""
            st.session_state["coach_reply"] = ai(prompt)
        if "coach_reply" in st.session_state:
            st.markdown(st.session_state["coach_reply"])

def auth_screen(sb):
    st.title("🤝 GIGMATE AI")
    st.caption("Create your private founder workspace")
    mode = st.radio("Choose", ["Sign in","Create account"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button(mode, type="primary"):
        try:
            if mode == "Create account":
                result = sb.auth.sign_up({"email":email,"password":password})
                if result.session:
                    st.session_state["access_token"] = result.session.access_token
                    st.session_state["refresh_token"] = result.session.refresh_token
                    st.rerun()
                st.success("Account created. Check your email to confirm, then sign in.")
            else:
                result = sb.auth.sign_in_with_password({"email":email,"password":password})
                st.session_state["access_token"] = result.session.access_token
                st.session_state["refresh_token"] = result.session.refresh_token
                st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")

try:
    sb = get_supabase()
    authenticated = init_auth(sb)
    if authenticated and "user" not in st.session_state:
        st.session_state["user"] = sb.auth.get_user().user
    if authenticated and st.session_state.get("user"):
        main_app(sb, st.session_state["user"])
    else:
        auth_screen(sb)
except Exception as e:
    st.error("Cloud configuration is incomplete.")
    st.markdown("Add `SUPABASE_URL`, `SUPABASE_ANON_KEY` and `GEMINI_API_KEY` in Streamlit app secrets.")
    st.code(str(e))
