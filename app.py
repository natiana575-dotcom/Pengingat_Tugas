import streamlit as st
from datetime import date
import html

st.set_page_config(
    page_title="Pengingat Tugas",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "filter" not in st.session_state:
    st.session_state.filter = "Semua"

hari = [
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
    "Minggu"
]

bulan = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember"
]

def format_tanggal(tanggal, dengan_hari=False):
    if dengan_hari:
        return f"{hari[tanggal.weekday()]}, {tanggal.day} {bulan[tanggal.month - 1]} {tanggal.year}"
    return f"{tanggal.day} {bulan[tanggal.month - 1]} {tanggal.year}"

st.markdown("""
<style>
.stApp {
    background: #fff5f8;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 35px;
    padding-bottom: 100px;
}

.main-title {
    font-family: "Times New Roman", serif !important;
    font-size: 50px;
    font-weight: bold;
    color: #880E4F !important;
    text-align: center;
    margin-bottom: 8px;
}

.header-card {
    background: rgba(255,255,255,0.97);
    border: 1px solid #f3c8d8;
    border-radius: 24px;
    padding: 32px 42px;
    box-shadow: 0 8px 28px rgba(136,14,79,0.10);
    margin-bottom: 30px;
}

.current-date {
    color: #555555;
    font-family: "Times New Roman", Times, serif;
    font-size: 20px;
    margin-bottom: 8px;
}

.greeting {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif !important;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 10px;
}

.description {
    color: #444444;
    font-family: Georgia, serif;
    font-size: 18px;
    line-height: 1.5;
}

.stats {
    display: flex;
    gap: 40px;
    margin-top: 22px;
    font-family: "Times New Roman", Times, serif;
    font-size: 18px;
}

.completed-stat {
    color: #39764d;
}

.incomplete-stat {
    color: #880E4F;
}

.filter-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 27px;
    font-weight: bold;
    margin-top: 25px;
    margin-bottom: 12px;
}

.task-card {
    background: rgba(255,255,255,0.98);
    border: 1px solid #f1d5df;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 8px;
    box-shadow: 0 5px 18px rgba(136,14,79,0.08);
}

.book-icon {
    width: 58px;
    height: 58px;
    border-radius: 14px;
    background: #fde4ed;
    display: flex;
    align-items: center;
    justify-content: center;
}

.book-icon svg {
    width: 38px;
    height: 38px;
}

.subject {
    color: #555555;
    font-family: "Times New Roman", Times, serif;
    font-size: 17px;
    margin-bottom: 4px;
}

.task-name {
    color: #222222;
    font-family: "Times New Roman", Times, serif;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 7px;
}

.deadline {
    color: #777777;
    font-family: "Times New Roman", Times, serif;
    font-size: 15px;
}

.empty-box {
    background: rgba(255,255,255,0.9);
    border: 1px dashed #e4a9bd;
    border-radius: 20px;
    padding: 45px 20px;
    text-align: center;
    color: #777777;
    font-family: "Times New Roman", Times, serif;
    font-size: 19px;
    margin-top: 15px;
}

.add-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 15px;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #dca2b9;
    background: white;
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 16px;
}

.stButton > button:hover {
    border-color: #880E4F;
    color: #880E4F;
    background: #fff1f6;
}

.add-button {
    position: fixed;
    right: 35px;
    bottom: 30px;
    z-index: 999999;
}

.add-button button {
    background: #880E4F !important;
    color: white !important;
    border: none !important;
    border-radius: 50% !important;
    width: 65px !important;
    height: 65px !important;
    min-width: 65px !important;
    font-size: 34px !important;
    font-family: Arial, sans-serif !important;
    box-shadow: 0 7px 22px rgba(136,14,79,0.35);
}

.add-button button:hover {
    background: #6d0b3e !important;
    color: white !important;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.97);
    border: 1px solid #f1d0dc;
    border-radius: 20px;
    padding: 25px;
}

@media (max-width: 800px) {
    .main .block-container {
        padding: 20px 15px 100px 15px;
    }

    .main-title {
        font-size: 40px;
    }

    .header-card {
        padding: 24px;
    }

    .greeting {
        font-size: 31px;
    }

    .description {
        font-size: 16px;
    }

    .stats {
        gap: 20px;
        flex-wrap: wrap;
    }

    .task-name {
        font-size: 20px;
    }

    .add-button {
        right: 20px;
        bottom: 20px;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<h1 class="main-title">PENGINGAT TUGAS</h1>',
    unsafe_allow_html=True
)

today = date.today()

completed_count = sum(
    1 for task in st.session_state.tasks if task["done"]
)

incomplete_count = len(st.session_state.tasks) - completed_count

st.markdown(
    f'<div class="header-card"><div class="current-date">{format_tanggal(today, True)}</div><div class="greeting">Satu - satu, selesai</div><div class="description">Catat yang perlu dikerjakan. Biar kepala lebih lega dan deadline terasa lebih dekat untuk ditaklukan.</div><div class="stats"><span class="completed-stat">Tugas selesai: {completed_count}</span><span class="incomplete-stat">Tugas belum selesai: {incomplete_count}</span></div></div>',
    unsafe_allow_html=True
)

if not st.session_state.show_form:
    st.markdown('<div class="add-button">', unsafe_allow_html=True)

    if st.button("+", key="open_add"):
        st.session_state.show_form = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_form:

    st.markdown(
        '<div class="add-title">Tambah Tugas</div>',
        unsafe_allow_html=True
    )

    with st.form("add_task_form", clear_on_submit=True):

        subject = st.text_input("Mata pelajaran")
        task_name = st.text_input("Nama tugas")
        deadline = st.date_input("Deadline", value=date.today())

        submitted = st.form_submit_button("Tambahkan Tugas")

        if submitted:

            if subject.strip() and task_name.strip():

                st.session_state.tasks.append({
                    "subject": subject.strip(),
                    "name": task_name.strip(),
                    "deadline": deadline,
                    "done": False
                })

                st.session_state.show_form = False
                st.rerun()

            else:
                st.warning(
                    "Mata pelajaran dan nama tugas harus diisi."
                )

    if st.button("Batal", key="cancel_add"):
        st.session_state.show_form = False
        st.rerun()

st.markdown(
    '<div class="filter-title">DAFTAR TUGAS</div>',
    unsafe_allow_html=True
)

filter1, filter2, filter3 = st.columns(3)

with filter1:
    if st.button(
        f"Semua ({len(st.session_state.tasks)})",
        key="filter_all",
        use_container_width=True
    ):
        st.session_state.filter = "Semua"
        st.rerun()

with filter2:
    if st.button(
        f"Belum selesai ({incomplete_count})",
        key="filter_incomplete",
        use_container_width=True
    ):
        st.session_state.filter = "Belum selesai"
        st.rerun()

with filter3:
    if st.button(
        f"Sudah selesai ({completed_count})",
        key="filter_complete",
        use_container_width=True
    ):
        st.session_state.filter = "Sudah selesai"
        st.rerun()

if st.session_state.filter == "Semua":

    visible_tasks = st.session_state.tasks

elif st.session_state.filter == "Belum selesai":

    visible_tasks = [
        task for task in st.session_state.tasks
        if not task["done"]
    ]

else:

    visible_tasks = [
        task for task in st.session_state.tasks
        if task["done"]
    ]

if not visible_tasks:

    if st.session_state.filter == "Semua":
        message = "Belum ada tugas.<br>Tekan tombol + untuk menambahkan tugas baru."

    elif st.session_state.filter == "Belum selesai":
        message = "Tidak ada tugas yang belum selesai. ✨"

    else:
        message = "Belum ada tugas yang selesai."

    st.markdown(
        f'<div class="empty-box">{message}</div>',
        unsafe_allow_html=True
    )

else:

    columns = st.columns(2)

    for position, task in enumerate(visible_tasks):

        real_index = st.session_state.tasks.index(task)

        with columns[position % 2]:

            subject_safe = html.escape(str(task["subject"]))
            name_safe = html.escape(str(task["name"]))
            deadline_text = format_tanggal(task["deadline"])

            st.markdown(
                f'<div class="task-card"><div style="display:flex; gap:16px; align-items:center;"><div class="book-icon"><svg viewBox="0 0 64 64"><path d="M9 12 C20 9 30 13 32 18 L32 55 C28 50 18 48 9 51 Z" fill="#c2185b"/><path d="M55 12 C44 9 34 13 32 18 L32 55 C36 50 46 48 55 51 Z" fill="#ad1457"/><path d="M32 18 L32 55" stroke="#f8bbd0" stroke-width="3"/><path d="M15 20 C21 19 26 21 29 23" stroke="white" stroke-width="2" fill="none"/><path d="M49 20 C43 19 38 21 35 23" stroke="white" stroke-width="2" fill="none"/></svg></div><div style="flex:1;"><div class="subject">{subject_safe}</div><div class="task-name">{name_safe}</div><div class="deadline">Tenggat: {deadline_text}</div></div></div></div>',
                unsafe_allow_html=True
            )

            checked = st.checkbox(
                "Tandai selesai",
                value=task["done"],
                key=f"check_{real_index}"
            )

            if checked != task["done"]:
                st.session_state.tasks[real_index]["done"] = checked
                st.rerun()

            if st.button(
                "Hapus tugas",
                key=f"delete_{real_index}"
            ):
                st.session_state.tasks.pop(real_index)
                st.rerun()