"""
app.py
Streamlit Face Recognition Attendance System.
Run with: streamlit run app.py
"""
# python -m streamlit run app.py
import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
from datetime import date
import io
import os

import database as db
import face_utils as fu

st.set_page_config(
    page_title="Face Attendance 😄",
    page_icon=":material/center_focus_strong:",
    layout="wide"
)
db.init_db()


# ---------------- Theme Presets Configuration ----------------

THEME_PRESETS = {
    "Style 1: Modern Indigo Light (Current)": """[theme]
base = "light"
primaryColor = "#4F46E5"
backgroundColor = "#F9FAFB"
secondaryBackgroundColor = "#FFFFFF"
codeBackgroundColor = "#F3F4F6"
textColor = "#111827"
linkColor = "#4F46E5"
borderColor = "#E5E7EB"
showWidgetBorder = true
showSidebarBorder = true
baseRadius = "10px"
buttonRadius = "8px"
font = "'Inter':https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
baseFontSize = 14

[theme.sidebar]
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#111827"
borderColor = "#E5E7EB"
primaryColor = "#4F46E5"
""",
    "Style 2: One Dark Pro (Sleek Dark)": """[theme]
base = "dark"
primaryColor = "#61AFEF"
backgroundColor = "#1E222A"
secondaryBackgroundColor = "#21252B"
codeBackgroundColor = "#1E222A"
textColor = "#ABB2BF"
linkColor = "#61AFEF"
borderColor = "#282C34"
showWidgetBorder = true
showSidebarBorder = true
baseRadius = "10px"
buttonRadius = "8px"
font = "'Inter':https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
baseFontSize = 14

[theme.sidebar]
backgroundColor = "#21252B"
secondaryBackgroundColor = "#282C34"
textColor = "#ABB2BF"
borderColor = "#282C34"
primaryColor = "#61AFEF"
""",
    "Style 3: Dracula Violet (Vibrant Dark)": """[theme]
base = "dark"
primaryColor = "#BD93F9"
backgroundColor = "#282A36"
secondaryBackgroundColor = "#44475A"
codeBackgroundColor = "#282A36"
textColor = "#F8F8F2"
linkColor = "#FF79C6"
borderColor = "#6272A4"
showWidgetBorder = true
showSidebarBorder = true
baseRadius = "10px"
buttonRadius = "8px"
font = "'Inter':https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
baseFontSize = 14

[theme.sidebar]
backgroundColor = "#44475A"
secondaryBackgroundColor = "#282A36"
textColor = "#F8F8F2"
borderColor = "#6272A4"
primaryColor = "#BD93F9"
"""
}


def apply_theme_preset(preset_name):
    if "current_theme_name" not in st.session_state:
        st.session_state.current_theme_name = "Style 1: Modern Indigo Light (Current)"
        
    if st.session_state.current_theme_name != preset_name:
        st.session_state.current_theme_name = preset_name
        config_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.toml")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(THEME_PRESETS[preset_name])
        st.rerun()


def image_to_np(uploaded_or_camera_file):
    img = Image.open(uploaded_or_camera_file).convert("RGB")
    return np.array(img)


def image_to_bytes(uploaded_or_camera_file):
    uploaded_or_camera_file.seek(0)
    return uploaded_or_camera_file.read()


@st.cache_data(ttl=60)
def get_cached_batches():
    return db.get_batches()


batches = get_cached_batches()
batch_names = [b[1] for b in batches]
batch_lookup = {b[1]: b[0] for b in batches}  # name -> id

# ---------------- Header Banner ----------------

header_col1, header_col2 = st.columns([3, 1], vertical_alignment="center")
with header_col1:
    st.title("Face Attendance 😄", text_alignment="left")
    st.caption("Batch-wise facial recognition & automated attendance register")
with header_col2:
    st.markdown(" :blue-badge[AI Facial Recognition] :green-badge[Local SQLite] ")

st.write("")

# ---------------- Sidebar Navigation & Theme Picker ----------------

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Go to",
        ["Manage Batches", "Register Student", "Take Attendance", "View Reports"],
        index=2 if batches else 0,
        format_func=lambda x: {
            "Manage Batches": "📁 Manage Batches",
            "Register Student": "👤 Register Student",
            "Take Attendance": "📸 Take Attendance",
            "View Reports": "📊 View Reports"
        }[x]
    )
    
    st.divider()
    st.markdown("### 🎨 Look Styles")
    current_preset = st.session_state.get("current_theme_name", "Style 1: Modern Indigo Light (Current)")
    selected_preset = st.selectbox(
        "Select Theme Style",
        list(THEME_PRESETS.keys()),
        index=list(THEME_PRESETS.keys()).index(current_preset) if current_preset in THEME_PRESETS else 0,
        help="Switch between 3 look styles for demo"
    )
    apply_theme_preset(selected_preset)

    st.divider()
    st.markdown("### System Quick Stats")
    stat_batches = len(batches)
    stat_students = len(db.get_all_students())
    
    mcol1, mcol2 = st.columns(2)
    with mcol1:
        st.metric("Batches", stat_batches)
    with mcol2:
        st.metric("Students", stat_students)


# ---------------- Page: Manage Batches ----------------

if page == "Manage Batches":
    st.header(":material/folder: Manage batches")

    col_list, col_actions = st.columns([1, 1], gap="medium")
    
    with col_list:
        with st.container(border=True):
            st.subheader(":material/list: Existing batches")
            if batches:
                df_batches = pd.DataFrame(batches, columns=["ID", "Batch Name"]).set_index("ID")
                st.dataframe(df_batches, width="stretch")
            else:
                st.info("No batches found. Create your first batch on the right.", icon=":material/info:")

    with col_actions:
        with st.container(border=True):
            st.subheader(":material/add_circle: Add a new batch")
            with st.form("add_batch_form", border=False):
                new_batch = st.text_input(
                    "Batch name",
                    placeholder="e.g. Data Science, Web Development, C++ Class"
                )
                submitted = st.form_submit_button("Add batch", icon=":material/add:", type="primary")
                if submitted:
                    if new_batch.strip():
                        ok, msg = db.add_batch(new_batch.strip())
                        if ok:
                            st.toast(msg, icon="✅")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(msg, icon=":material/error:")
                    else:
                        st.error("Please enter a valid batch name.", icon=":material/warning:")

        st.write("")
        if batches:
            with st.container(border=True):
                st.subheader(":material/delete: Remove a batch")
                batch_to_remove = st.selectbox(
                    "Select batch to delete",
                    batch_names,
                    key="remove_batch_select"
                )
                st.caption("⚠️ Deleting a batch will also remove all student profiles & attendance history for this batch.")
                if st.button("Remove batch", icon=":material/delete:", type="secondary", use_container_width=True):
                    b_id = batch_lookup[batch_to_remove]
                    ok, msg = db.delete_batch(b_id)
                    if ok:
                        st.toast(f"Batch '{batch_to_remove}' removed successfully!", icon="🗑️")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(msg, icon=":material/error:")


# ---------------- Page: Register Student ----------------

elif page == "Register Student":
    st.header(":material/person_add: Register a student")

    if not batch_names:
        st.warning("Please create a batch first under 'Manage Batches'.", icon=":material/warning:")
        st.stop()

    col_form, col_manage = st.columns([3, 2], gap="large")

    with col_form:
        with st.container(border=True):
            st.subheader(":material/badge: Student details")
            
            selected_batch = st.selectbox("Batch", batch_names)
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full name", placeholder="John Doe")
            with c2:
                roll_no = st.text_input("Roll number / ID", placeholder="DS-101")

            st.write("Photo source")
            capture_mode = st.segmented_control(
                "Source",
                ["Camera", "Upload"],
                default="Camera",
                label_visibility="collapsed"
            )

            photo_file = None
            if capture_mode == "Camera":
                photo_file = st.camera_input("Take a photo")
            else:
                photo_file = st.file_uploader("Upload a clear front-facing photo", type=["jpg", "jpeg", "png"])

            if st.button("Register student", icon=":material/check_circle:", type="primary", use_container_width=True):
                if not name.strip() or not roll_no.strip():
                    st.error("Please enter both name and roll number.", icon=":material/error:")
                elif photo_file is None:
                    st.error("Please provide a photo.", icon=":material/error:")
                else:
                    with st.spinner("Analyzing face features..."):
                        img_np = image_to_np(photo_file)
                        encoding, err = fu.get_single_face_encoding(img_np)
                    if err:
                        st.error(err, icon=":material/error:")
                    else:
                        ok, msg = db.add_student(
                            name.strip(),
                            roll_no.strip(),
                            batch_lookup[selected_batch],
                            encoding,
                            image_to_bytes(photo_file),
                        )
                        if ok:
                            st.toast(f"Registered {name} successfully!", icon="🎉")
                            st.image(photo_file, caption=f"Registered: {name} ({roll_no})", width=220)
                        else:
                            st.error(msg, icon=":material/error:")

    with col_manage:
        with st.container(border=True):
            st.subheader(":material/groups: Registered students")
            curr_batch_id = batch_lookup[selected_batch]
            existing = db.get_students_by_batch(curr_batch_id)
            
            if existing:
                st.caption(f"{len(existing)} student(s) in {selected_batch}")
                df_existing = pd.DataFrame(existing)[["roll_no", "name"]].rename(
                    columns={"roll_no": "Roll No", "name": "Name"}
                )
                st.dataframe(df_existing, width="stretch", height=240)
                
                st.divider()
                st.write("Remove a student")
                names_map = {f"{s['name']} ({s['roll_no']})": s["id"] for s in existing}
                to_remove = st.selectbox("Select student to remove", list(names_map.keys()), label_visibility="collapsed")
                if st.button("Remove student", icon=":material/delete:", type="secondary"):
                    db.delete_student(names_map[to_remove])
                    st.toast(f"Removed student", icon="🗑️")
                    st.rerun()
            else:
                st.info(f"No students registered in {selected_batch} yet.", icon=":material/info:")


# ---------------- Page: Take Attendance ----------------

elif page == "Take Attendance":
    st.header(":material/fact_check: Take attendance")

    if not batch_names:
        st.warning("Please create a batch first under 'Manage Batches'.", icon=":material/warning:")
        st.stop()

    top_c1, top_c2 = st.columns(2)
    with top_c1:
        selected_batch = st.selectbox("Batch", batch_names)
    with top_c2:
        selected_date = st.date_input("Lecture date", value=date.today())
        
    batch_id = batch_lookup[selected_batch]
    known_students = db.get_students_by_batch(batch_id)
    
    if not known_students:
        st.warning(f"No students registered in '{selected_batch}' batch yet. Please register students first.", icon=":material/warning:")
        st.stop()

    st.write("")

    with st.container(border=True):
        sc1, sc2 = st.columns([2, 1], vertical_alignment="center")
        with sc1:
            st.markdown(f"**{len(known_students)} student(s)** registered in **{selected_batch}**")
        with sc2:
            tolerance = st.slider(
                "Match strictness", min_value=0.3, max_value=0.7, value=0.5, step=0.05,
                help="Lower = stricter matching (fewer false positives); Higher = lenient"
            )

        st.divider()
        st.write("Class photo source")
        capture_mode = st.segmented_control(
            "Source Mode",
            ["Camera", "Upload"],
            default="Upload",
            label_visibility="collapsed",
            key="att_mode_seg"
        )

        photo_file = None
        if capture_mode == "Camera":
            photo_file = st.camera_input("Take class photo")
        else:
            photo_file = st.file_uploader("Upload class photo (one or many faces)", type=["jpg", "jpeg", "png"], key="att_upload")

        if photo_file is not None:
            st.image(photo_file, caption="Class Photo", width=400)
            
            if st.button("Process attendance", icon=":material/center_focus_strong:", type="primary", use_container_width=True):
                with st.spinner("Detecting faces and computing encodings..."):
                    img_np = image_to_np(photo_file)
                    faces = fu.get_all_faces(img_np)

                if not faces:
                    st.error("No faces detected in the photo. Please check lighting or photo clarity.", icon=":material/face_off:")
                else:
                    present_ids = set()
                    for location, encoding in faces:
                        match = fu.match_face(encoding, known_students, tolerance=tolerance)
                        if match:
                            present_ids.add(match["id"])

                    date_str = selected_date.isoformat()
                    for s in known_students:
                        status = "Present" if s["id"] in present_ids else "Absent"
                        db.mark_attendance(s["id"], batch_id, date_str, status)

                    num_present = len(present_ids)
                    num_absent = len(known_students) - num_present
                    
                    st.toast(f"Attendance recorded for {selected_batch} ({date_str})", icon="✅")
                    
                    st.write("")
                    st.subheader(":material/verified: Attendance results")
                    
                    res_m1, res_m2, res_m3 = st.columns(3)
                    with res_m1:
                        st.metric("Total Students", len(known_students))
                    with res_m2:
                        st.metric("Present", num_present, delta=f"{num_present} detected", delta_color="normal")
                    with res_m3:
                        st.metric("Absent", num_absent, delta=f"-{num_absent}" if num_absent > 0 else "None", delta_color="inverse")

                    result_rows = [
                        {
                            "Name": s["name"],
                            "Roll No": s["roll_no"],
                            "Status": "🟢 Present" if s["id"] in present_ids else "🔴 Absent"
                        }
                        for s in known_students
                    ]
                    st.dataframe(pd.DataFrame(result_rows), width="stretch")


# ---------------- Page: View Reports ----------------

elif page == "View Reports":
    st.header(":material/analytics: Attendance reports")

    if not batch_names:
        st.warning("Please create a batch first under 'Manage Batches'.", icon=":material/warning:")
        st.stop()

    rep_col1, rep_col2 = st.columns([1, 1])
    with rep_col1:
        selected_batch = st.selectbox("Batch", batch_names, key="rep_batch")
    with rep_col2:
        st.write("Report view")
        report_type = st.segmented_control(
            "Report type",
            ["Date-wise", "Student-wise", "Batch Summary"],
            default="Date-wise",
            label_visibility="collapsed"
        )
        
    batch_id = batch_lookup[selected_batch]

    with st.container(border=True):
        if report_type == "Date-wise":
            selected_date = st.date_input("Select date", value=date.today())
            rows = db.get_attendance_by_date(batch_id, selected_date.isoformat())
            if rows:
                df = pd.DataFrame(rows, columns=["Name", "Roll No", "Status", "Time Marked"])
                
                # Metrics header
                p_cnt = (df["Status"] == "Present").sum()
                a_cnt = (df["Status"] == "Absent").sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Recorded Students", len(df))
                m2.metric("Present", p_cnt)
                m3.metric("Absent", a_cnt)
                
                st.dataframe(df, width="stretch")
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download date register CSV",
                    csv,
                    f"attendance_{selected_batch}_{selected_date}.csv",
                    icon=":material/download:",
                    type="primary"
                )
            else:
                st.info(f"No attendance recorded for {selected_batch} on {selected_date} yet.", icon=":material/info:")

        elif report_type == "Student-wise":
            students = db.get_students_by_batch(batch_id)
            if not students:
                st.info(f"No students in '{selected_batch}' batch.", icon=":material/info:")
            else:
                names = {f"{s['name']} ({s['roll_no']})": s["id"] for s in students}
                selected_name = st.selectbox("Select student", list(names.keys()))
                rows = db.get_attendance_by_student(names[selected_name])
                if rows:
                    df = pd.DataFrame(rows, columns=["Date", "Status", "Time Marked"])
                    present = (df["Status"] == "Present").sum()
                    pct = (present / len(df) * 100) if len(df) > 0 else 0
                    
                    sm1, sm2 = st.columns(2)
                    sm1.metric("Total Lectures", len(df))
                    sm2.metric("Attendance %", f"{pct:.1f}%", delta="Good" if pct >= 75 else "Low", delta_color="normal" if pct >= 75 else "inverse")
                    
                    st.dataframe(df, width="stretch")
                else:
                    st.info("No attendance history for this student yet.", icon=":material/info:")

        else:  # Batch Summary
            rows = db.get_attendance_summary(batch_id)
            if rows:
                df = pd.DataFrame(rows, columns=["Name", "Roll No", "Present Lectures", "Total Lectures"])
                df["Attendance %"] = (df["Present Lectures"] / df["Total Lectures"].replace(0, 1) * 100).round(1)
                
                avg_pct = df["Attendance %"].mean()
                st.metric("Batch Average Attendance", f"{avg_pct:.1f}%")
                
                st.dataframe(df, width="stretch")
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download batch summary CSV",
                    csv,
                    f"summary_{selected_batch}.csv",
                    icon=":material/download:",
                    type="primary"
                )
            else:
                st.info(f"No summary data available for '{selected_batch}' yet.", icon=":material/info:")
