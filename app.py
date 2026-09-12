import html
from datetime import date, timedelta
from textwrap import dedent

import streamlit as st
from supabase import create_client


st.set_page_config(
    page_title="Pengingat Tugas",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


if "session" not in st.session_state:
    st.session_state.session = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Beranda"

if "login_mode" not in st.session_state:
    st.session_state.login_mode = "Masuk"

if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False

if "message" not in st.session_state:
    st.session_state.message = None

if "message_type" not in st.session_state:
    st.session_state.message_type = "info"

if "task_filter" not in st.session_state:
    st.session_state.task_filter = "Semua"


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


def tanggal_indonesia(tanggal, tampilkan_hari=False):

    if isinstance(tanggal, str):
        tanggal = date.fromisoformat(tanggal[:10])

    hasil = (
        f"{tanggal.day} "
        f"{bulan[tanggal.month - 1]} "
        f"{tanggal.year}"
    )

    if tampilkan_hari:
        hasil = (
            f"{hari[tanggal.weekday()]}, "
            f"{hasil}"
        )

    return hasil


def set_message(message, message_type="info"):

    st.session_state.message = message
    st.session_state.message_type = message_type


def pasang_access_token():

    session = st.session_state.session

    if session is None:
        return

    try:
        supabase.postgrest.auth(session.access_token)
    except Exception:
        pass


def logout():

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.session = None
    st.session_state.user = None
    st.session_state.page = "Beranda"
    st.session_state.login_mode = "Masuk"
    st.session_state.show_add_task = False
    st.session_state.message = None

    st.rerun()


def get_subjects():

    try:

        response = (
            supabase
            .table("subjects")
            .select("id, name, created_at")
            .eq(
                "user_id",
                st.session_state.user.id
            )
            .order(
                "created_at",
                desc=False
            )
            .execute()
        )

        return response.data or []

    except Exception:

        return []


def get_tasks():

    try:

        response = (
            supabase
            .table("tasks")
            .select(
                "id, subject_id, name, deadline, done"
            )
            .eq(
                "user_id",
                st.session_state.user.id
            )
            .order(
                "deadline",
                desc=False
            )
            .execute()
        )

        return response.data or []

    except Exception:

        return []


def auth_error_text(error):

    text = str(error)
    lower = text.lower()

    if "already registered" in lower:
        return (
            "Email ini sudah terdaftar. "
            "Coba gunakan menu Masuk."
        )

    if "invalid login credentials" in lower:
        return "Email atau password salah."

    if "email not confirmed" in lower:
        return (
            "Email belum diverifikasi. "
            "Cek inbox email kamu."
        )

    return f"Supabase error: {text}"


if (
    st.session_state.session is None
    or st.session_state.user is None
):

    st.markdown(
        dedent("""
        <style>

        .stApp {
            background: #fff5f8;
        }

        .main .block-container {
            max-width: 520px;
            padding-top: 70px;
        }

        .login-title {
            text-align: center;
            color: #880E4F;
            font-family: "Times New Roman", serif;
            font-size: 46px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .login-subtitle {
            text-align: center;
            color: #666;
            font-family: Georgia, serif;
            font-size: 17px;
            margin-bottom: 28px;
        }

        div[data-testid="stForm"] {
            background: white;
            border: 1px solid #f0ccd9;
            border-radius: 20px;
            padding: 28px;
        }

        .stButton > button {
            border-radius: 12px;
            border: 1px solid #dca2b9;
            background: white;
            color: #880E4F;
            font-family: "Times New Roman", serif;
            font-size: 16px;
        }

        .stButton > button:hover {
            border-color: #880E4F;
            background: #fff0f5;
            color: #880E4F;
        }

        </style>
        """),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">PENGINGAT TUGAS</div>',
        unsafe_allow_html=True
    )

    if st.session_state.login_mode == "Masuk":

        st.markdown(
            dedent("""
            <div class="login-subtitle">
                Masuk untuk menyimpan tugasmu.
            </div>
            """),
            unsafe_allow_html=True
        )

        with st.form("form_login"):

            email = st.text_input(
                "Email",
                placeholder="contoh@gmail.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            masuk = st.form_submit_button(
                "Masuk",
                use_container_width=True
            )

        if masuk:

            email = email.strip()

            if not email:

                st.error("Email belum diisi.")

            elif not password:

                st.error("Password belum diisi.")

            else:

                try:

                    result = (
                        supabase
                        .auth
                        .sign_in_with_password(
                            {
                                "email": email,
                                "password": password
                            }
                        )
                    )

                    if result.user and result.session:

                        st.session_state.user = result.user
                        st.session_state.session = result.session

                        pasang_access_token()

                        st.session_state.page = "Beranda"

                        st.rerun()

                    else:

                        st.error(
                            "Login gagal. "
                            "Supabase tidak memberikan session."
                        )

                except Exception as error:

                    st.error(
                        auth_error_text(error)
                    )

        st.write("")

        if st.button(
            "Belum punya akun? Daftar",
            use_container_width=True
        ):

            st.session_state.login_mode = "Daftar"
            st.rerun()

    else:

        st.markdown(
            dedent("""
            <div class="login-subtitle">
                Buat akun baru untuk mulai mencatat tugas.
            </div>
            """),
            unsafe_allow_html=True
        )

        with st.form("form_register"):

            email = st.text_input(
                "Email",
                placeholder="contoh@gmail.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            password_confirmation = st.text_input(
                "Ulangi Password",
                type="password"
            )

            daftar = st.form_submit_button(
                "Daftar",
                use_container_width=True
            )

        if daftar:

            email = email.strip()

            if not email:

                st.error("Email belum diisi.")

            elif not password:

                st.error("Password belum diisi.")

            elif len(password) < 6:

                st.error(
                    "Password minimal 6 karakter."
                )

            elif password != password_confirmation:

                st.error("Password tidak sama.")

            else:

                try:

                    result = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": email,
                                "password": password
                            }
                        )
                    )

                    if result.user is None:

                        st.error(
                            "Supabase tidak membuat user."
                        )

                    elif result.session is not None:

                        st.session_state.user = result.user
                        st.session_state.session = result.session

                        pasang_access_token()

                        st.session_state.page = "Beranda"

                        st.rerun()

                    else:

                        st.session_state.login_mode = "Masuk"

                        set_message(
                            (
                                "Akun berhasil dibuat. "
                                "Silakan cek email untuk "
                                "verifikasi akun, kemudian login."
                            ),
                            "success"
                        )

                        st.rerun()

                except Exception as error:

                    st.error(
                        auth_error_text(error)
                    )

        st.write("")

        if st.button(
            "Sudah punya akun? Masuk",
            use_container_width=True
        ):

            st.session_state.login_mode = "Masuk"
            st.rerun()

    st.stop()


pasang_access_token()


st.markdown(
    dedent("""
    <style>

    .stApp {
        background: #fff5f8;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 30px;
        padding-bottom: 100px;
    }

    .main-title {
        text-align: center;
        color: #880E4F;
        font-family: "Times New Roman", serif;
        font-size: 50px;
        font-weight: bold;
        margin-bottom: 25px;
    }

    .header-card {
        background: white;
        border: 1px solid #f2ccd9;
        border-radius: 24px;
        padding: 32px 40px;
        box-shadow: 0 8px 28px rgba(136,14,79,0.08);
        margin-bottom: 28px;
    }

    .current-date {
        color: #555;
        font-family: "Times New Roman", serif;
        font-size: 19px;
    }

    .greeting {
        color: #880E4F;
        font-family: "Times New Roman", serif;
        font-size: 40px;
        font-weight: bold;
        margin-top: 7px;
    }

    .description {
        color: #444;
        font-family: Georgia, serif;
        font-size: 17px;
        line-height: 1.6;
        margin-top: 8px;
    }

    .stats {
        display: flex;
        gap: 35px;
        margin-top: 20px;
        font-family: "Times New Roman", serif;
        font-size: 17px;
    }

    .completed-stat {
        color: #39764d;
    }

    .incomplete-stat {
        color: #880E4F;
    }

    .section-title {
        color: #880E4F;
        font-family: "Times New Roman", serif;
        font-size: 28px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .task-card {
        background: white;
        border: 1px solid #f1d5df;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 8px;
        box-shadow: 0 5px 18px rgba(136,14,79,0.07);
    }

    .subject-text {
        color: #666;
        font-family: "Times New Roman", serif;
        font-size: 16px;
    }

    .task-text {
        color: #222;
        font-family: "Times New Roman", serif;
        font-size: 22px;
        font-weight: bold;
        margin-top: 3px;
    }

    .deadline-text {
        color: #777;
        font-family: "Times New Roman", serif;
        font-size: 15px;
        margin-top: 6px;
    }

    .empty-box {
        background: white;
        border: 1px dashed #dfa7bc;
        border-radius: 20px;
        padding: 45px 20px;
        text-align: center;
        color: #777;
        font-family: "Times New Roman", serif;
        font-size: 18px;
    }

    .page-title {
        color: #880E4F;
        font-family: "Times New Roman", serif;
        font-size: 34px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .info-card {
        background: white;
        border: 1px solid #f1d0dc;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
    }

    .add-button button {
        background: #880E4F !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        font-size: 32px !important;
        box-shadow: 0 7px 22px rgba(136,14,79,0.30);
    }

    </style>
    """),
    unsafe_allow_html=True
)


def navigation():

    menu = st.popover("☰")

    with menu:

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


navigation()


if st.session_state.message:

    if st.session_state.message_type == "success":
        st.success(st.session_state.message)

    elif st.session_state.message_type == "error":
        st.error(st.session_state.message)

    else:
        st.info(st.session_state.message)

    st.session_state.message = None


subjects = get_subjects()
tasks = get_tasks()


if st.session_state.page == "Beranda":

    st.markdown(
        '<div class="main-title">PENGINGAT TUGAS</div>',
        unsafe_allow_html=True
    )

    today = date.today()

    completed = [
        task
        for task in tasks
        if task.get("done") is True
    ]

    unfinished = [
        task
        for task in tasks
        if task.get("done") is not True
    ]

    st.markdown(
        dedent(f"""<div class="header-card"><div class="current-date">{tanggal_indonesia(today, True)}
            </div><div class="greeting">Satu - satu, selesai<div class="description">Catat yang perlu dikerjakan. Biar kepala lebih lega dan deadline terasa lebih dekat untuk ditaklukan.</div><div class="stats"><span class="completed-stat">Tugas selesai: {len(completed)}</span><span class="incomplete-stat">Tugas belum selesai: {len(unfinished)}</span></div></div>"""),
        unsafe_allow_html=True
    )

    if st.session_state.show_add_task:
        st.markdown('<div class="section-title">Tambah Tugas</div>',
            unsafe_allow_html=True
        )

        if not subjects:

            st.warning(
                "Belum ada mata pelajaran. "
                "Tambahkan mata pelajaran terlebih dahulu."
            )

        else:

            subject_names = {
                subject["name"]: subject["id"]
                for subject in subjects
            }

            with st.form(
                "task_form",
                clear_on_submit=True
            ):

                selected_subject = st.selectbox(
                    "Mata Pelajaran",
                    list(subject_names.keys())
                )

                task_name = st.text_input(
                    "Nama Tugas"
                )

                deadline = st.date_input(
                    "Deadline",
                    value=date.today()
                )

                save_task = st.form_submit_button(
                    "Simpan Tugas"
                )

            if save_task:

                if not task_name.strip():

                    st.error(
                        "Nama tugas harus diisi."
                    )

                else:

                    try:

                        (
                            supabase
                            .table("tasks")
                            .insert(
                                {
                                    "user_id":
                                        st.session_state.user.id,
                                    "subject_id":
                                        subject_names[selected_subject],
                                    "name":
                                        task_name.strip(),
                                    "deadline":
                                        deadline.isoformat(),
                                    "done":
                                        False
                                }
                            )
                            .execute()
                        )

                        st.session_state.show_add_task = False

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Gagal menyimpan tugas: {error}"
                        )

        if st.button("Batal"):

            st.session_state.show_add_task = False
            st.rerun()

    else:

        st.markdown(
            '<div class="add-button">',
            unsafe_allow_html=True
        )

        if st.button(
            "+",
            key="add_task_button"
        ):

            st.session_state.show_add_task = True
            st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">DAFTAR TUGAS</div>',
        unsafe_allow_html=True
    )

    filter_all, filter_unfinished, filter_done = st.columns(3)

    with filter_all:

        if st.button(
            f"Semua ({len(tasks)})",
            use_container_width=True
        ):

            st.session_state.task_filter = "Semua"
            st.rerun()

    with filter_unfinished:

        if st.button(
            f"Belum selesai ({len(unfinished)})",
            use_container_width=True
        ):

            st.session_state.task_filter = "Belum selesai"
            st.rerun()

    with filter_done:

        if st.button(
            f"Sudah selesai ({len(completed)})",
            use_container_width=True
        ):

            st.session_state.task_filter = "Sudah selesai"
            st.rerun()

    if st.session_state.task_filter == "Semua":

        visible_tasks = tasks

    elif st.session_state.task_filter == "Belum selesai":

        visible_tasks = unfinished

    else:

        visible_tasks = completed

    subject_map = {
        subject["id"]: subject["name"]
        for subject in subjects
    }

    if not visible_tasks:

        st.markdown(
            dedent("""
            <div class="empty-box">
                Belum ada tugas.
                <br>
                Tekan tombol + untuk menambahkan tugas.
            </div>
            """),
            unsafe_allow_html=True
        )

    else:

        columns = st.columns(2)

        for index, task in enumerate(visible_tasks):

            with columns[index % 2]:

                subject_name = html.escape(
                    str(subject_map.get(task["subject_id"],"Mata Pelajaran"))
                )

                task_name = html.escape(
                    str(task["name"])
                )

                st.markdown(
                    dedent(f"""<div class="task-card"><div class="subject-text">{subject_name}</div><div class="task-text">{task_name}</div><div class="deadline-text">Tenggat:{tanggal_indonesia(task["deadline"])}</div></div>"""),
                    unsafe_allow_html=True
                )

                current_done = task.get(
                    "done",
                    False
                )

                new_done = st.checkbox(
                    "Tandai selesai",
                    value=current_done,
                    key=f"done_{task['id']}"
                )

                if new_done != current_done:

                    try:

                        (
                            supabase
                            .table("tasks")
                            .update(
                                {
                                    "done": new_done
                                }
                            )
                            .eq(
                                "id",
                                task["id"]
                            )
                            .eq(
                                "user_id",
                                st.session_state.user.id
                            )
                            .execute()
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Gagal mengubah status: {error}"
                        )

                if st.button(
                    "Hapus tugas",
                    key=f"delete_{task['id']}"
                ):

                    try:

                        (
                            supabase
                            .table("tasks")
                            .delete()
                            .eq(
                                "id",
                                task["id"]
                            )
                            .eq(
                                "user_id",
                                st.session_state.user.id
                            )
                            .execute()
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Gagal menghapus tugas: {error}"
                        )


elif st.session_state.page == "Mata Pelajaran":

    st.markdown(
        '<div class="page-title">Mata Pelajaran</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        dedent("""
        <div class="info-card">
            Tambahkan mata pelajaran yang kamu gunakan.
            Mata pelajaran akan muncul saat menambahkan tugas.
        </div>
        """),
        unsafe_allow_html=True
    )

    with st.form(
        "subject_form",
        clear_on_submit=True
    ):

        subject_name_input = st.text_input(
            "Nama Mata Pelajaran"
        )

        add_subject = st.form_submit_button(
            "Tambah Mata Pelajaran"
        )

    if add_subject:

        subject_name_input = subject_name_input.strip()

        if not subject_name_input:

            st.error(
                "Nama mata pelajaran harus diisi."
            )

        elif any(
            subject["name"].lower()
            == subject_name_input.lower()
            for subject in subjects
        ):

            st.warning(
                "Mata pelajaran tersebut sudah ada."
            )

        else:

            try:

                (
                    supabase
                    .table("subjects")
                    .insert(
                        {
                            "user_id":
                                st.session_state.user.id,
                            "name":
                                subject_name_input
                        }
                    )
                    .execute()
                )

                st.success(
                    "Mata pelajaran berhasil ditambahkan."
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Gagal menambahkan mata pelajaran: {error}"
                )

    st.markdown(
        '<div class="section-title">Daftar Mata Pelajaran</div>',
        unsafe_allow_html=True
    )

    if not subjects:

        st.markdown(
            dedent("""
            <div class="empty-box">
                Belum ada mata pelajaran.
            </div>
            """),
            unsafe_allow_html=True
        )

    else:

        for subject in subjects:

            col1, col2 = st.columns([5, 1])

            with col1:

                subject_name_display = html.escape(
                    str(subject["name"])
                )

                st.markdown(
                    dedent(f"""<div class="info-card"><b>{subject_name_display}</b></div>"""),
                    unsafe_allow_html=True
                )

            with col2:

                if st.button(
                    "Hapus",
                    key=f"delete_subject_{subject['id']}"
                ):

                    used = any(
                        task["subject_id"]
                        == subject["id"]
                        for task in tasks
                    )

                    if used:

                        st.warning(
                            "Mata pelajaran ini masih "
                            "digunakan oleh tugas."
                        )

                    else:

                        try:

                            (
                                supabase
                                .table("subjects")
                                .delete()
                                .eq(
                                    "id",
                                    subject["id"]
                                )
                                .eq(
                                    "user_id",
                                    st.session_state.user.id
                                )
                                .execute()
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Gagal menghapus: {error}"
                            )

elif st.session_state.page == "Akun":

    st.markdown(
        '<div class="page-title">Akun</div>',
        unsafe_allow_html=True
    )

    user_email = html.escape(
        str(st.session_state.user.email or "")
    )

    st.markdown(
        dedent(f"""<div class="info-card"><div style="color:#666;font-family:Georgia,serif;font-size:16px;">Email</div><div style="color:#880E4F;font-family:'Times New Roman',serif;font-size:25px;font-weight:bold;margin-top:8px;">{user_email}</div></div>"""),
        unsafe_allow_html=True
    )

    st.markdown(
        dedent(f"""<div class="info-card"><div style="color:#666;font-family:Georgia,serif;font-size:16px;">Total Tugas</div><div style="color:#880E4F;font-family:'Times New Roman',serif;font-size:30px;font-weight:bold;margin-top:8px;">{len(tasks)}</div></div>"""),
        unsafe_allow_html=True
    )

    if st.button(
        "Keluar",
        use_container_width=True
    ):

        logout()


elif st.session_state.page == "Pengaturan":

    st.markdown(
        '<div class="page-title">Pengaturan</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        dedent("""
        <div class="info-card">
        <b>Tampilan</b>
        <br>
        Pengingat Tugas menggunakan tampilan
        terang dengan nuansa pink.
        </div>
        
        <div class="info-card">
            <b>Penyimpanan</b>
            <br>
            Tugas dan mata pelajaran tersimpan
            di Supabase berdasarkan akun pengguna.
        </div>
        """),
        unsafe_allow_html=True
    )

    if st.button(
        "Keluar dari akun",
        use_container_width=True
    ):

        logout()
