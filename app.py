import streamlit as st
from datetime import date
import html
from supabase import create_client

st.set_page_config(
    page_title="Pengingat Tugas",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Beranda"

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
    if isinstance(tanggal, str):
        tanggal = date.fromisoformat(tanggal)

    if dengan_hari:
        return f"{hari[tanggal.weekday()]}, {tanggal.day} {bulan[tanggal.month - 1]} {tanggal.year}"

    return f"{tanggal.day} {bulan[tanggal.month - 1]} {tanggal.year}"


def login_user(email, password):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        st.session_state.user = result.user
        st.session_state.page = "Beranda"
        st.session_state.show_form = False
        st.rerun()

    except Exception:
        st.error("Email atau password tidak benar.")


def register_user(email, password):
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if result.user:
            st.success("Akun berhasil dibuat. Silakan masuk.")
        else:
            st.error("Akun gagal dibuat.")

    except Exception:
        st.error(
            "Gagal membuat akun. Pastikan email dan password sudah benar."
        )


def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.page = "Beranda"
    st.session_state.show_form = False
    st.rerun()


def get_subjects():
    try:
        result = (
            supabase
            .table("subjects")
            .select("id, name")
            .eq("user_id", st.session_state.user.id)
            .order("name")
            .execute()
        )

        return result.data or []

    except Exception:
        return []


def get_tasks():
    try:
        result = (
            supabase
            .table("tasks")
            .select("id, subject_id, name, deadline, done")
            .eq("user_id", st.session_state.user.id)
            .order("deadline")
            .execute()
        )

        tasks = result.data or []

        subjects = get_subjects()

        subject_names = {
            subject["id"]: subject["name"]
            for subject in subjects
        }

        for task in tasks:
            task["subject"] = subject_names.get(
                task["subject_id"],
                "Mata pelajaran"
            )

        return tasks

    except Exception:
        return []


def add_subject(name):
    try:
        name = name.strip()

        if not name:
            st.warning("Nama mata pelajaran harus diisi.")
            return

        existing = (
            supabase
            .table("subjects")
            .select("id")
            .eq("user_id", st.session_state.user.id)
            .eq("name", name)
            .execute()
        )

        if existing.data:
            st.warning("Mata pelajaran tersebut sudah ada.")
            return

        supabase.table("subjects").insert({
            "user_id": st.session_state.user.id,
            "name": name
        }).execute()

        st.success("Mata pelajaran berhasil ditambahkan.")
        st.rerun()

    except Exception:
        st.error("Mata pelajaran gagal ditambahkan.")


def delete_subject(subject_id):
    try:
        tasks = (
            supabase
            .table("tasks")
            .select("id")
            .eq("user_id", st.session_state.user.id)
            .eq("subject_id", subject_id)
            .execute()
        )

        if tasks.data:
            st.warning(
                "Mata pelajaran ini masih digunakan oleh tugas. "
                "Hapus tugasnya terlebih dahulu."
            )
            return

        supabase.table("subjects").delete().eq(
            "id", subject_id
        ).eq(
            "user_id", st.session_state.user.id
        ).execute()

        st.success("Mata pelajaran berhasil dihapus.")
        st.rerun()

    except Exception:
        st.error("Gagal menghapus mata pelajaran.")


def add_task(subject_id, task_name, deadline):
    try:
        supabase.table("tasks").insert({
            "user_id": st.session_state.user.id,
            "subject_id": subject_id,
            "name": task_name.strip(),
            "deadline": str(deadline),
            "done": False
        }).execute()

        st.session_state.show_form = False
        st.rerun()

    except Exception:
        st.error("Tugas gagal ditambahkan.")


def update_task_status(task_id, done):
    try:
        supabase.table("tasks").update({
            "done": done
        }).eq(
            "id", task_id
        ).eq(
            "user_id", st.session_state.user.id
        ).execute()

        st.rerun()

    except Exception:
        st.error("Status tugas gagal diperbarui.")


def delete_task(task_id):
    try:
        supabase.table("tasks").delete().eq(
            "id", task_id
        ).eq(
            "user_id", st.session_state.user.id
        ).execute()

        st.rerun()

    except Exception:
        st.error("Tugas gagal dihapus.")


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
    background: #ffffff;
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
    background: #ffffff;
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
    background: #ffffff;
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

.page-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 34px;
    font-weight: bold;
    margin-bottom: 20px;
}

.login-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 44px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8px;
}

.login-subtitle {
    color: #666666;
    font-family: Georgia, serif;
    text-align: center;
    margin-bottom: 30px;
}

.menu-box {
    background: #ffffff;
    border: 1px solid #f1d5df;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 25px;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #dca2b9;
    background: #ffffff;
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
    background: #ffffff;
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

if st.session_state.user is None:

    st.markdown(
        '<div class="login-title">PENGINGAT TUGAS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Catat tugasmu. Selesaikan satu per satu.</div>',
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(["Masuk", "Daftar"])

    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Masuk",
            key="login_button",
            use_container_width=True
        ):
            if email.strip() and password:
                login_user(
                    email.strip(),
                    password
                )
            else:
                st.warning(
                    "Email dan password harus diisi."
                )

    with register_tab:

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        register_password2 = st.text_input(
            "Ulangi password",
            type="password",
            key="register_password2"
        )

        if st.button(
            "Daftar",
            key="register_button",
            use_container_width=True
        ):

            if not register_email.strip() or not register_password:
                st.warning(
                    "Email dan password harus diisi."
                )

            elif register_password != register_password2:
                st.warning(
                    "Password tidak sama."
                )

            elif len(register_password) < 6:
                st.warning(
                    "Password minimal 6 karakter."
                )

            else:
                register_user(
                    register_email.strip(),
                    register_password
                )

    st.stop()


tasks = get_tasks()
subjects = get_subjects()

completed_count = sum(
    1 for task in tasks
    if task.get("done", False)
)

incomplete_count = len(tasks) - completed_count

today = date.today()

menu_col1, menu_col2 = st.columns([8, 1])

with menu_col2:

    with st.popover("☰"):

        if st.button(
            "Beranda",
            use_container_width=True
        ):
            st.session_state.page = "Beranda"
            st.rerun()

        if st.button(
            "Mata Pelajaran",
            use_container_width=True
        ):
            st.session_state.page = "Mata Pelajaran"
            st.rerun()

        if st.button(
            "Notifikasi",
            use_container_width=True
        ):
            st.session_state.page = "Notifikasi"
            st.rerun()

        if st.button(
            "Akun",
            use_container_width=True
        ):
            st.session_state.page = "Akun"
            st.rerun()

        if st.button(
            "Pengaturan",
            use_container_width=True
        ):
            st.session_state.page = "Pengaturan"
            st.rerun()

        st.divider()

        if st.button(
            "Keluar",
            use_container_width=True
        ):
            logout_user()


if st.session_state.page == "Beranda":

    st.markdown(
        '<h1 class="main-title">PENGINGAT TUGAS</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="header-card">'
        f'<div class="current-date">'
        f'{format_tanggal(today, True)}'
        f'</div>'
        f'<div class="greeting">'
        f'Satu - satu, selesai'
        f'</div>'
        f'<div class="description">'
        f'Catat yang perlu dikerjakan. Biar kepala lebih lega dan deadline terasa lebih dekat untuk ditaklukan.'
        f'</div>'
        f'<div class="stats">'
        f'<span class="completed-stat">'
        f'Tugas selesai: {completed_count}'
        f'</span>'
        f'<span class="incomplete-stat">'
        f'Tugas belum selesai: {incomplete_count}'
        f'</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.show_form:

        st.markdown(
            '<div class="add-button">',
            unsafe_allow_html=True
        )

        if st.button(
            "+",
            key="open_add"
        ):
            st.session_state.show_form = True
            st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    if st.session_state.show_form:

        st.markdown(
            '<div class="add-title">Tambah Tugas</div>',
            unsafe_allow_html=True
        )

        if not subjects:

            st.warning(
                "Belum ada mata pelajaran. "
                "Tambahkan mata pelajaran terlebih dahulu melalui menu."
            )

            if st.button(
                "Buka Mata Pelajaran"
            ):
                st.session_state.page = "Mata Pelajaran"
                st.session_state.show_form = False
                st.rerun()

        else:

            with st.form(
                "add_task_form",
                clear_on_submit=True
            ):

                subject_options = {
                    subject["name"]: subject["id"]
                    for subject in subjects
                }

                selected_subject = st.selectbox(
                    "Mata pelajaran",
                    list(subject_options.keys())
                )

                task_name = st.text_input(
                    "Nama tugas"
                )

                deadline = st.date_input(
                    "Deadline",
                    value=date.today()
                )

                submitted = st.form_submit_button(
                    "Tambahkan Tugas"
                )

                if submitted:

                    if not task_name.strip():

                        st.warning(
                            "Nama tugas harus diisi."
                        )

                    else:

                        add_task(
                            subject_options[selected_subject],
                            task_name,
                            deadline
                        )

            if st.button(
                "Batal",
                key="cancel_add"
            ):
                st.session_state.show_form = False
                st.rerun()

    st.markdown(
        '<div class="filter-title">DAFTAR TUGAS</div>',
        unsafe_allow_html=True
    )

    filter1, filter2, filter3 = st.columns(3)

    with filter1:

        if st.button(
            f"Semua ({len(tasks)})",
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

        visible_tasks = tasks

    elif st.session_state.filter == "Belum selesai":

        visible_tasks = [
            task for task in tasks
            if not task.get("done", False)
        ]

    else:

        visible_tasks = [
            task for task in tasks
            if task.get("done", False)
        ]

    if not visible_tasks:

        if st.session_state.filter == "Semua":

            message = (
                "Belum ada tugas.<br>"
                "Tekan tombol + untuk menambahkan tugas baru."
            )

        elif st.session_state.filter == "Belum selesai":

            message = (
                "Tidak ada tugas yang belum selesai. ✨"
            )

        else:

            message = (
                "Belum ada tugas yang selesai."
            )

        st.markdown(
            f'<div class="empty-box">{message}</div>',
            unsafe_allow_html=True
        )

    else:

        columns = st.columns(2)

        for position, task in enumerate(visible_tasks):

            with columns[position % 2]:

                subject_safe = html.escape(
                    str(task["subject"])
                )

                name_safe = html.escape(
                    str(task["name"])
                )

                deadline_text = format_tanggal(
                    task["deadline"]
                )

                st.markdown(
                    f'<div class="task-card">'
                    f'<div style="display:flex; gap:16px; align-items:center;">'
                    f'<div class="book-icon">'
                    f'<svg viewBox="0 0 64 64">'
                    f'<path d="M9 12 C20 9 30 13 32 18 L32 55 C28 50 18 48 9 51 Z" fill="#c2185b"/>'
                    f'<path d="M55 12 C44 9 34 13 32 18 L32 55 C36 50 46 48 55 51 Z" fill="#ad1457"/>'
                    f'<path d="M32 18 L32 55" st
