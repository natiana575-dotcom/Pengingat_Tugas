import streamlit as st
from datetime import date, datetime
import html
from supabase import create_client, Client


st.set_page_config(
    page_title="Pengingat Tugas",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception:
        st.error("Supabase belum terhubung. Periksa SUPABASE_URL dan SUPABASE_KEY di Secrets.")
        st.stop()


supabase: Client = st.session_state.supabase


if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Beranda"

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "filter" not in st.session_state:
    st.session_state.filter = "Semua"

if "subjects" not in st.session_state:
    st.session_state.subjects = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []


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


def get_user():
    try:
        response = supabase.auth.get_user()

        if response and response.user:
            return response.user

    except Exception:
        pass

    return st.session_state.user


def load_data():
    user = get_user()

    if not user:
        return

    st.session_state.user = user

    try:
        subject_response = (
            supabase
            .table("subjects")
            .select("*")
            .eq("user_id", user.id)
            .order("name")
            .execute()
        )

        task_response = (
            supabase
            .table("task")
            .select("*")
            .eq("user_id", user.id)
            .order("deadline")
            .execute()
        )

        st.session_state.subjects = subject_response.data or []
        st.session_state.tasks = task_response.data or []

    except Exception as e:
        st.error("Data belum dapat dimuat dari Supabase.")
        st.caption(str(e))


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.subjects = []
    st.session_state.tasks = []
    st.session_state.page = "Beranda"
    st.session_state.show_form = False
    st.rerun()


def login_page():
    st.markdown("""
    <style>
    .login-box {
        max-width: 500px;
        margin: 70px auto;
        background: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #f3c8d8;
        box-shadow: 0 8px 28px rgba(136,14,79,0.10);
    }

    .login-title {
        font-family: "Times New Roman", serif;
        color: #880E4F;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .login-subtitle {
        text-align: center;
        color: #777777;
        font-family: Georgia, serif;
        font-size: 17px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-box"><div class="login-title">PENGINGAT TUGAS</div><div class="login-subtitle">Masuk untuk menyimpan tugasmu.</div></div>',
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(["Masuk", "Daftar akun"])

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
            if not email.strip() or not password:
                st.warning("Email dan password harus diisi.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password
                    })

                    if response.user:
                        st.session_state.user = response.user
                        st.session_state.page = "Beranda"
                        load_data()
                        st.success("Berhasil masuk.")
                        st.rerun()

                except Exception as e:
                    st.error("Email atau password salah.")
                    st.caption(str(e))

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

        register_password_confirm = st.text_input(
            "Ulangi password",
            type="password",
            key="register_password_confirm"
        )

        if st.button(
            "Daftar akun",
            key="register_button",
            use_container_width=True
        ):
            if not register_email.strip() or not register_password:
                st.warning("Email dan password harus diisi.")

            elif len(register_password) < 6:
                st.warning("Password minimal 6 karakter.")

            elif register_password != register_password_confirm:
                st.warning("Password tidak sama.")

            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": register_email.strip(),
                        "password": register_password
                    })

                    if response.user:
                        if response.session:
                            st.session_state.user = response.user
                            st.session_state.page = "Beranda"
                            load_data()
                            st.success("Akun berhasil dibuat.")
                            st.rerun()
                        else:
                            st.success(
                                "Akun berhasil dibuat. Silakan cek email untuk konfirmasi akun, lalu masuk."
                            )

                except Exception as e:
                    st.error("Akun gagal dibuat.")
                    st.caption(str(e))

    st.stop()


user = get_user()

if not user:
    login_page()


st.session_state.user = user

if not st.session_state.subjects and not st.session_state.tasks:
    load_data()


st.markdown("""
<style>
.stApp {
    background: #fff5f8;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 25px;
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

.page-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 35px;
    font-weight: bold;
    margin-bottom: 20px;
}

.info-card {
    background: rgba(255,255,255,0.97);
    border: 1px solid #f3c8d8;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 15px;
    box-shadow: 0 5px 18px rgba(136,14,79,0.07);
}

.info-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 8px;
}

.info-text {
    color: #555555;
    font-family: Georgia, serif;
    font-size: 17px;
}

.notification-card {
    background: white;
    border: 1px solid #f1d5df;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
    box-shadow: 0 5px 18px rgba(136,14,79,0.08);
}

.subject-item {
    background: white;
    border: 1px solid #f1d5df;
    border-radius: 15px;
    padding: 16px 20px;
    margin-bottom: 10px;
    color: #333333;
    font-family: "Times New Roman", Times, serif;
    font-size: 20px;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.97);
    border: 1px solid #f1d0dc;
    border-radius: 20px;
    padding: 25px;
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

.nav-button > button {
    border-radius: 14px;
    min-height: 42px;
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


nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:
    if st.button("🏠 Beranda", use_container_width=True):
        st.session_state.page = "Beranda"
        st.session_state.show_form = False
        st.rerun()

with nav2:
    if st.button("📚 Mata Pelajaran", use_container_width=True):
        st.session_state.page = "Mata Pelajaran"
        st.session_state.show_form = False
        st.rerun()

with nav3:
    if st.button("🔔 Notifikasi", use_container_width=True):
        st.session_state.page = "Notifikasi"
        st.session_state.show_form = False
        st.rerun()

with nav4:
    if st.button("👤 Akun", use_container_width=True):
        st.session_state.page = "Akun"
        st.session_state.show_form = False
        st.rerun()

with nav5:
    if st.button("⚙️ Pengaturan", use_container_width=True):
        st.session_state.page = "Pengaturan"
        st.session_state.show_form = False
        st.rerun()


if st.session_state.page == "Beranda":

    st.markdown(
        '<h1 class="main-title">PENGINGAT TUGAS</h1>',
        unsafe_allow_html=True
    )

    today = date.today()

    completed_count = sum(
        1 for task in st.session_state.tasks
        if task.get("done", False)
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

        if not st.session_state.subjects:
            st.warning(
                "Belum ada mata pelajaran. Tambahkan mata pelajaran terlebih dahulu."
            )

            if st.button(
                "Buka Mata Pelajaran",
                key="go_subjects"
            ):
                st.session_state.page = "Mata Pelajaran"
                st.session_state.show_form = False
                st.rerun()

        else:
            subject_options = {
                str(subject["id"]): subject["name"]
                for subject in st.session_state.subjects
            }

            with st.form("add_task_form", clear_on_submit=True):

                selected_subject_id = st.selectbox(
                    "Mata pelajaran",
                    options=list(subject_options.keys()),
                    format_func=lambda x: subject_options[x]
                )

                task_name = st.text_input("Nama tugas")

                deadline = st.date_input(
                    "Deadline",
                    value=date.today()
                )

                submitted = st.form_submit_button(
                    "Tambahkan Tugas"
                )

                if submitted:

                    if task_name.strip():

                        try:
                            supabase.table("task").insert({
                                "user_id": user.id,
                                "subject_id": selected_subject_id,
                                "name": task_name.strip(),
                                "deadline": deadline.isoformat(),
                                "done": False
                            }).execute()

                            st.session_state.show_form = False
                            load_data()
                            st.success("Tugas berhasil ditambahkan.")
                            st.rerun()

                        except Exception as e:
                            st.error("Tugas gagal ditambahkan.")
                            st.caption(str(e))

                    else:
                        st.warning(
                            "Nama tugas harus diisi."
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
            if not task.get("done", False)
        ]

    else:

        visible_tasks = [
            task for task in st.session_state.tasks
            if task.get("done", False)
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

        subject_lookup = {
            str(subject["id"]): subject["name"]
            for subject in st.session_state.subjects
        }

        for position, task in enumerate(visible_tasks):

            real_index = st.session_state.tasks.index(task)

            with columns[position % 2]:

                subject_name = subject_lookup.get(
                    str(task["subject_id"]),
                    "Mata pelajaran tidak ditemukan"
                )

                subject_safe = html.escape(str(subject_name))
                name_safe = html.escape(str(task["name"]))

                deadline_text = format_tanggal(
                    task["deadline"]
                )

                st.markdown(
                    f'<div class="task-card"><div style="display:flex; gap:16px; align-items:center;"><div class="book-icon"><svg viewBox="0 0 64 64"><path d="M9 12 C20 9 30 13 32 18 L32 55 C28 50 18 48 9 51 Z" fill="#c2185b"/><path d="M55 12 C44 9 34 13 32 18 L32 55 C36 50 46 48 55 51 Z" fill="#ad1457"/><path d="M32 18 L32 55" stroke="#f8bbd0" stroke-width="3"/><path d="M15 20 C21 19 26 21 29 23" stroke="white" stroke-width="2" fill="none"/><path d="M49 20 C43 19 38 21 35 23"
