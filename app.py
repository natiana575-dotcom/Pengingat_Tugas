```python
import streamlit as st
from datetime import date, timedelta
import html
from supabase import create_client

st.set_page_config(
    page_title="Pengingat Tugas",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "session" not in st.session_state:
    st.session_state.session = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Beranda"

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "filter" not in st.session_state:
    st.session_state.filter = "Semua"

if "login_mode" not in st.session_state:
    st.session_state.login_mode = "Masuk"

if "auth_message" not in st.session_state:
    st.session_state.auth_message = None

if "auth_message_type" not in st.session_state:
    st.session_state.auth_message_type = "info"

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
        tanggal = date.fromisoformat(tanggal[:10])

    if dengan_hari:
        return (
            f"{hari[tanggal.weekday()]}, "
            f"{tanggal.day} "
            f"{bulan[tanggal.month - 1]} "
            f"{tanggal.year}"
        )

    return (
        f"{tanggal.day} "
        f"{bulan[tanggal.month - 1]} "
        f"{tanggal.year}"
    )


def get_subjects():

    response = (
        supabase
        .table("subjects")
        .select("id, name, created_at")
        .eq("user_id", st.session_state.user.id)
        .order("created_at")
        .execute()
    )

    return response.data or []


def get_tasks():

    response = (
        supabase
        .table("tasks")
        .select("id, subject_id, name, deadline, done")
        .eq("user_id", st.session_state.user.id)
        .order("deadline")
        .execute()
    )

    return response.data or []


def logout():

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.session = None
    st.session_state.user = None
    st.session_state.page = "Beranda"
    st.session_state.show_form = False
    st.session_state.login_mode = "Masuk"

    st.rerun()


def show_auth_error(error):

    message = str(error)

    lower_message = message.lower()

    if (
        "already registered" in lower_message
        or "user already registered" in lower_message
        or "already exists" in lower_message
    ):
        return (
            "Email ini sudah terdaftar di Supabase. "
            "Kalau kamu merasa belum pernah membuat akun, "
            "cek halaman Authentication → Users di Supabase."
        )

    if "invalid login credentials" in lower_message:
        return (
            "Email atau password salah."
        )

    if "password" in lower_message:
        return (
            f"Password ditolak oleh Supabase: {message}"
        )

    if "email" in lower_message:
        return (
            f"Email ditolak oleh Supabase: {message}"
        )

    return (
        f"Supabase mengembalikan error: {message}"
    )


if not st.session_state.session or not st.session_state.user:

    st.markdown("""
    <style>
    .stApp {
        background: #fff5f8;
    }

    .main .block-container {
        max-width: 550px;
        padding-top: 80px;
    }

    .login-title {
        font-family: "Times New Roman", serif !important;
        font-size: 46px;
        font-weight: bold;
        color: #880E4F !important;
        text-align: center;
        margin-bottom: 8px;
    }

    .login-subtitle {
        text-align: center;
        color: #666666;
        font-family: Georgia, serif;
        font-size: 17px;
        margin-bottom: 28px;
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.97);
        border: 1px solid #f1d0dc;
        border-radius: 20px;
        padding: 28px;
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

    .auth-note {
        background: #fff0f5;
        border: 1px solid #f0bfd0;
        border-radius: 14px;
        padding: 14px 16px;
        color: #6d2144;
        font-family: Georgia, serif;
        line-height: 1.5;
        margin-bottom: 18px;
    }

    @media (max-width: 800px) {
        .main .block-container {
            padding: 35px 15px;
        }

        .login-title {
            font-size: 38px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-title">PENGINGAT TUGAS</div>',
        unsafe_allow_html=True
    )

    if st.session_state.auth_message:

        if st.session_state.auth_message_type == "success":
            st.success(st.session_state.auth_message)

        elif st.session_state.auth_message_type == "error":
            st.error(st.session_state.auth_message)

        else:
            st.info(st.session_state.auth_message)

        st.session_state.auth_message = None

    if st.session_state.login_mode == "Masuk":

        st.markdown(
            '<div class="login-subtitle">'
            'Masuk ke akun Pengingat Tugas kamu.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="contoh@email.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Masuk",
                use_container_width=True
            )

        if submitted:

            email = email.strip()

            if not email or not password:

                st.error(
                    "Email dan password harus diisi."
                )

            else:

                try:

                    result = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    if result.session and result.user:

                        st.session_state.session = result.session
                        st.session_state.user = result.user
                        st.session_state.page = "Beranda"

                        st.rerun()

                    else:

                        st.error(
                            "Login gagal karena session tidak dibuat."
                        )

                except Exception as e:

                    st.error(
                        show_auth_error(e)
                    )

        if st.button(
            "Belum punya akun? Daftar",
            use_container_width=True
        ):

            st.session_state.login_mode = "Daftar"
            st.session_state.auth_message = None

            st.rerun()

    else:

        st.markdown(
            '<div class="login-subtitle">'
            'Buat akun baru untuk menyimpan tugasmu.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.form("register_form"):

            email = st.text_input(
                "Email",
                placeholder="contoh@email.com"
            )

            password = st.text_input(
                "Password",
                type="password",
                help="Minimal 6 karakter."
            )

            password2 = st.text_input(
                "Ulangi password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Daftar",
                use_container_width=True
            )

        if submitted:

            email = email.strip()

            if not email or not password or not password2:

                st.error(
                    "Semua bagian harus diisi."
                )

            elif password != password2:

                st.error(
                    "Password tidak sama."
                )

            elif len(password) < 6:

                st.error(
                    "Password minimal 6 karakter."
                )

            else:

                try:

                    result = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })

                    if result.user is None:

                        st.error(
                            "Supabase tidak membuat akun. "
                            "Coba lagi."
                        )

                    elif result.session:

                        st.session_state.session = result.session
                        st.session_state.user = result.user
                        st.session_state.page = "Beranda"

                        st.success(
                            "Akun berhasil dibuat."
                        )

                        st.rerun()

                    else:

                        st.session_state.login_mode = "Masuk"
                        st.session_state.auth_message_type = "success"
                        st.session_state.auth_message = (
                            "Akun berhasil dibuat. "
                            "Supabase meminta verifikasi email. "
                            "Cek inbox email kamu, lalu kembali ke sini "
                            "dan pilih Masuk."
                        )

                        st.rerun()

                except Exception as e:

                    st.error(
                        show_auth_error(e)
                    )

        if st.button(
            "Sudah punya akun? Masuk",
            use_container_width=True
        ):

            st.session_state.login_mode = "Masuk"
            st.session_state.auth_message = None

            st.rerun()

    st.stop()


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

.page-title {
    color: #880E4F;
    font-family: "Times New Roman", Times, serif;
    font-size: 32px;
    font-weight: bold;
    margin-top: 15px;
    margin-bottom: 20px;
}

.info-card {
    background: rgba(255,255,255,0.97);
    border: 1px solid #f1d0dc;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 18px;
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


def menu():

    selected = st.popover("☰")

    with selected:

        menu_items = [
            "Beranda",
            "Mata Pelajaran",
            "Notifikasi",
            "Akun",
            "Pengaturan"
        ]

        for item in menu_items:

            if st.button(
                item,
                key=f"menu_{item}",
                use_container_width=True
            ):

                st.session_state.page = item
                st.session_state.show_form = False

                st.rerun()


menu()

subjects = get_subjects()
tasks = get_tasks()


if st.session_state.page == "Beranda":

    st.markdown(
        '<h1 class="main-title">PENGINGAT TUGAS</h1>',
        unsafe_allow_html=True
    )

    today = date.today()

    completed_count = sum(
        1
        for task in tasks
        if task.get("done", False)
    )

    incomplete_count = len(tasks) - completed_count

    st.markdown(
        f'''
        <div class="header-card">
            <div class="current-date">
                {format_tanggal(today, True)}
            </div>

            <div class="greeting">
                Satu - satu, selesai
            </div>

            <div class="description">
                Catat yang perlu dikerjakan.
                Biar kepala lebih lega dan deadline terasa
                lebih dekat untuk ditaklukan.
            </div>

            <div class="stats">
                <span class="completed-stat">
                    Tugas selesai: {completed_count}
                </span>

                <span class="incomplete-stat">
                    Tugas belum selesai: {incomplete_count}
                </span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    if not st.session_state.show_form:

        st.markdown(
            '<div class="add-button">',
            unsafe_allow_html=True
        )

        if st.button("+", key="open_add"):

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

            st.info(
                "Tambahkan mata pelajaran terlebih dahulu "
                "melalui menu Mata Pelajaran."
            )

        else:

            subject_options = {
                subject["name"]: subject["id"]
                for subject in subjects
            }

            with st.form(
                "add_task_form",
                clear_on_submit=True
            ):

                subject_name = st.selectbox(
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

                        try:

                            supabase.table("tasks").insert({
                                "user_id": st.session_state.user.id,
                                "subject_id": subject_options[subject_name],
                                "name": task_name.strip(),
                                "deadline": deadline.isoformat(),
                                "done": False
                            }).execute()

                            st.session_state.show_form = False

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Tugas gagal ditambahkan: {e}"
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
            task
            for task in tasks
            if not task.get("done", False)
        ]

    else:

        visible_tasks = [
            task
            for task in tasks
            if task.get("done", False)
        ]

    subject_map = {
        subject["id"]: subject["name"]
        for subject in subjects
    }

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

                subject_text = html.escape(
                    str(
                        subject_map.get(
                            task["subject_id"],
                            "Mata pelajaran"
                        )
                    )
                )

                task_text = html.escape(
                    str(task["name"])
                )

                deadline_text = format_tanggal(
                    task["deadline"]
                )

                st.markdown(
                    f'''
                    <div class="task-card">
                        <div style="display:flex;gap:16px;align-items:center;">

                            <div class="book-icon">

                                <svg viewBox="0 0 64 64">

                                    <path
                                        d="M9 12 C20 9 30 13 32 18 L32 55 C28 50 18 48 9 51 Z"
                                        fill="#c2185b"
                                    />

                                    <path
                                        d="M55 12 C44 9 34 13 32 18 L32 55 C36 50 46 48 55 51 Z"
                                        fill="#ad1457"
                                    />

                                    <path
                                        d="M32 18 L32 55"
                                        stroke="#f8bbd0"
                                        stroke-width="3"
                                    />

                                </svg>

                            </div>

                            <div style="flex:1;">

                                <div class="subject">
                                    {subject_text}
                                </div>

                                <div class="task-name">
                                    {task_text}
                                </div>

                                <div class="deadline">
                                    Tenggat: {deadline_text}
                                </div>

                            </div>

                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                checked = st.checkbox(
                    "Tandai selesai",
                    value=task.get("done", False),
                    key=f"check_{task['id']}"
                )

                if checked != task.get("done", False):

                    try:

                        supabase.table("tasks").update({
                            "done": checked
                        }).eq(
                            "id",
                            task["id"]
                        ).eq(
                            "user_id",
                            st.session_state.user.id
                        ).execute()

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Status gagal diperbarui: {e}"
                        )

                if st.button(
                    "Hapus tugas",
                    key=f"delete_{task['id']}"
                ):

                    try:

                        supabase.table("tasks").delete().eq(
                            "id",
                            task["id"]
                        ).eq(
                            "user_id",
                            st.session_state.user.id
                        ).execute()

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Tugas gagal dihapus: {e}"
                        )


elif st.session_state.page == "Mata Pelajaran":

    st.markdown(
        '<div class="page-title">Mata Pelajaran</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="info-card">
            Tambahkan mata pelajaran yang kamu gunakan.
            Mata pelajaran ini hanya terlihat di akunmu sendiri.
        </div>
        ''',
        unsafe_allow_html=True
    )

    with st.form(
        "add_subject_form",
        clear_on_submit=True
    ):

        subject_name = st.text_input(
            "Nama mata pelajaran"
        )

        submitted = st.form_submit_button(
            "Tambahkan Mata Pelajaran"
        )

        if submitted:

            name = subject_name.strip()

            if not name:

                st.warning(
                    "Nama mata pelajaran harus diisi."
                )

            elif any(
                subject["name"].lower() == name.lower()
                for subject in subjects
            ):

                st.warning(
                    "Mata pelajaran tersebut sudah ada."
                )

            else:

                try:

                    supabase.table("subjects").insert({
                        "user_id": st.session_state.user.id,
                        "name": name
                    }).execute()

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Mata pelajaran gagal ditambahkan: {e}"
                    )

    st.markdown(
        '<div class="filter-title">Daftar Mata Pelajaran</div>',
        unsafe_allow_html=True
    )

    if not subjects:

        st.markdown(
            '''
            <div class="empty-box">
                Belum ada mata pelajaran.<br>
                Tambahkan mata pelajaran di atas.
            </div>
            ''',
            unsafe_allow_html=True
        )

    else:

        for subject in subjects:

            col1, col2 = st.columns([5, 1])

            with col1:

                subject_safe = html.escape(
                    str(subject["name"])
                )

                st.markdown(
                    f'''
                    <div class="info-card">
                        <b>{subject_safe}</b>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            with col2:

                if st.button(
                    "Hapus",
                    key=f"subject_delete_{subject['id']}"
                ):

                    used = any(
                        task["subject_id"] == subject["id"]
                        for task in tasks
                    )

                    if used:

                        st.warning(
                            "Mata pelajaran ini masih digunakan oleh tugas."
                        )

                    else:

                        try:

                            supabase.table("subjects").delete().eq(
                                "id",
                                subject["id"]
                            ).eq(
                                "user_id",
                                st.session_state.user.id
                            ).execute()

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Mata pelajaran gagal dihapus: {e}"
                            )


elif st.session_state.page == "Notifikasi":

    st.markdown(
        '<div class="page-title">Notifikasi</div>',
        unsafe_allow_html=True
    )

    today = date.today()

    unfinished = [
        task
        for task in tasks
        if not task.get("done", False)
    ]

    overdue = [
        task
        for task in unfinished
        if date.fromisoformat(task["deadline"][:10]) < today
    ]

    soon = [
        task
        for task in unfinished
        if today <= date.fromisoformat(task["deadline"][:10])
        <= today + timedelta(days=2)
    ]

    subject_map = {
        subject["id"]: subject["name"]
        for subject in subjects
    }

    if overdue:

        st.markdown(
            '<div class="filter-title">Tugas Terlewat</div>',
            unsafe_allow_html=True
        )

        for task in overdue:

            subject_text = html.escape(
                str(
                    subject_map.get(
                        task["subject_id"],
                        "Mata pelajaran"
                    )
                )
            )

            task_text = html.escape(
                str(task["name"])
            )

            deadline_text = format_tanggal(
                task["deadline"]
            )

            st.markdown(
                f'''
                <div class="info-card">
                    <b>{task_text}</b><br>
                    {subject_text}<br>
                    Deadline: {deadline_text}
                </div>
                ''',
                unsafe_allow_html=True
            )

    if soon:

        st.markdown(
            '<div class="filter-title">Deadline Terdekat</div>',
            unsafe_allow_html=True
        )

        for task in soon:

            subject_text = html.escape(
                str(
                    subject_map.get(
                        task["subject_id"],
                        "Mata pelajaran"
                    )
                )
            )

            task_text = html.escape(
                str(task["name"])
            )

            deadline_text = format_tanggal(
                task["deadline"]
            )

            st.markdown(
                f'''
                <div class="info-card">
                    <b>{task_text}</b><br>
                    {subject_text}<br>
                    Deadline: {deadline_text}
                </div>
                ''',
                unsafe_allow_html=True
            )

    if not overdue and not soon:

        st.markdown(
            '''
            <div class="empty-box">
                Tidak ada tugas yang perlu diperhatikan saat ini. ✨
            </div>
            ''',
            unsafe_allow_html=True
        )


elif st.session_state.page == "Akun":

    st.markdown(
        '<div class="page-title">Akun</div>',
        unsafe_allow_html=True
    )

    email = html.escape(
        str(st.session_state.user.email or "")
    )

    st.markdown(
        f'''
        <div class="info-card">
            <div style="
                font-family:Times New Roman,serif;
                font-size:18px;
                color:#555;
            ">
                Email
            </div>

            <div style="
                font-family:Times New Roman,serif;
                font-size:24px;
                font-weight:bold;
                color:#880E4F;
                margin-top:8px;
            ">
                {email}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="info-card">
            <div style="
                font-family:Times New Roman,serif;
                font-size:18px;
                color:#555;
            ">
                Jumlah tugas
            </div>

            <div style="
                font-family:Times New Roman,serif;
                font-size:28px;
                font-weight:bold;
                color:#880E4F;
                margin-top:8px;
            ">
                {len(tasks)}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    if st.button(
        "Keluar dari akun",
        use_container_width=True
    ):

        logout()


elif st.session_state.page == "Pengaturan":

    st.markdown(
        '<div class="page-title">Pengaturan</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="info-card">
            <b>Tampilan</b><br>
            Aplikasi menggunakan tampilan terang
            dengan desain pink.
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="info-card">
            <b>Penyimpanan</b><br>
            Data tugas dan mata pelajaran tersimpan
            berdasarkan akun yang sedang digunakan.
        </div>
        ''',
        unsafe_allow_html=True
    )

    if st.button(
        "Keluar dari akun",
        use_container_width=True
    ):

        logout()
