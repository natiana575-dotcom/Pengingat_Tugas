import streamlit as st
from datetime import date, timedelta
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

if "task_filter" not in st.session_state:
    st.session_state.task_filter = "Semua"

if "message" not in st.session_state:
    st.session_state.message = None

if "message_type" not in st.session_state:
    st.session_state.message_type = "info"


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


def pasang_access_token():

    if st.session_state.session is None:
        return

    try:
        supabase.postgrest.auth(
            st.session_state.session.access_token
        )
    except Exception:
        pass


def set_message(text, message_type="info"):

    st.session_state.message = text
    st.session_state.message_type = message_type


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

        pasang_access_token()

        result = (
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

        return result.data or []

    except Exception:

        return []


def get_tasks():

    try:

        pasang_access_token()

        result = (
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

        return result.data or []

    except Exception:

        return []


def auth_error_text(error):

    text = str(error)
    lower = text.lower()

    if "invalid login credentials" in lower:
        return "Email atau password salah."

    if "email not confirmed" in lower:
        return (
            "Email belum diverifikasi. "
            "Silakan cek inbox email kamu."
        )

    if "already registered" in lower:
        return (
            "Email tersebut sudah terdaftar. "
            "Silakan masuk."
        )

    return f"Supabase error: {text}"


if (
    st.session_state.session is not None
    and st.session_state.user is not None
):

    pasang_access_token()


if (
    st.session_state.session is None
    or st.session_state.user is None
):

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #fff5f8;
        }

        .main .block-container {
            max-width: 520px;
            padding-top: 70px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("PENGINGAT TUGAS")

    st.caption(
        "Masuk untuk menyimpan tugasmu."
        if st.session_state.login_mode == "Masuk"
        else
        "Buat akun baru untuk mulai mencatat tugas."
    )


    if st.session_state.login_mode == "Masuk":

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="contoh@gmail.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submit = st.form_submit_button(
                "Masuk",
                use_container_width=True
            )

        if submit:

            if not email.strip():

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
                                "email": email.strip(),
                                "password": password
                            }
                        )
                    )

                    if result.session and result.user:

                        st.session_state.session = result.session
                        st.session_state.user = result.user

                        pasang_access_token()

                        st.session_state.page = "Beranda"

                        st.rerun()

                    else:

                        st.error(
                            "Login gagal. Session tidak ditemukan."
                        )

                except Exception as error:

                    st.error(
                        auth_error_text(error)
                    )


        if st.button(
            "Belum punya akun? Daftar",
            use_container_width=True
        ):

            st.session_state.login_mode = "Daftar"
            st.rerun()


    else:

        with st.form("register_form"):

            email = st.text_input(
                "Email",
                placeholder="contoh@gmail.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            password2 = st.text_input(
                "Ulangi Password",
                type="password"
            )

            submit = st.form_submit_button(
                "Daftar",
                use_container_width=True
            )

        if submit:

            if not email.strip():

                st.error("Email belum diisi.")

            elif not password:

                st.error("Password belum diisi.")

            elif len(password) < 6:

                st.error(
                    "Password minimal 6 karakter."
                )

            elif password != password2:

                st.error(
                    "Password tidak sama."
                )

            else:

                try:

                    result = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": email.strip(),
                                "password": password
                            }
                        )
                    )

                    if result.user is None:

                        st.error(
                            "User gagal dibuat."
                        )

                    elif result.session:

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
                                "verifikasi akun."
                            ),
                            "success"
                        )

                        st.rerun()

                except Exception as error:

                    st.error(
                        auth_error_text(error)
                    )


        if st.button(
            "Sudah punya akun? Masuk",
            use_container_width=True
        ):

            st.session_state.login_mode = "Masuk"
            st.rerun()


    st.stop()


st.markdown(
    """
    <style>

    .stApp {
        background-color: #fff5f8;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 25px;
        padding-bottom: 100px;
    }

    h1 {
        color: #880E4F !important;
        font-family: "Times New Roman", serif !important;
    }

    h2 {
        color: #880E4F !important;
        font-family: "Times New Roman", serif !important;
    }

    .hero {
        background: white;
        border: 1px solid #f2ccd9;
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 7px 25px rgba(136, 14, 79, 0.08);
    }

    .date-text {
        color: #666666;
        font-family: "Times New Roman", serif;
        font-size: 18px;
    }

    .hero-title {
        color: #880E4F;
        font-family: "Times New Roman", serif;
        font-size: 40px;
        font-weight: bold;
        margin-top: 8px;
    }

    .hero-description {
        color: #444444;
        font-family: Georgia, serif;
        font-size: 17px;
        line-height: 1.6;
        margin-top: 8px;
    }

    .stat-box {
        background: #fff7fa;
        border: 1px solid #f2d4df;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }

    .task-box {
        background: white;
        border: 1px solid #f1d5df;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 8px;
        box-shadow: 0 5px 18px rgba(136,14,79,0.07);
    }

    .task-subject {
        color: #777777;
        font-family: "Times New Roman", serif;
        font-size: 16px;
    }

    .task-name {
        color: #222222;
        font-family: "Times New Roman", serif;
        font-size: 22px;
        font-weight: bold;
        margin-top: 4px;
    }

    .task-deadline {
        color: #777777;
        font-family: "Times New Roman", serif;
        font-size: 15px;
        margin-top: 6px;
    }

    .info-box {
        background: white;
        border: 1px solid #f1d0dc;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid #dca2b9;
        color: #880E4F;
        background: white;
    }

    .stButton > button:hover {
        border-color: #880E4F;
        color: #880E4F;
        background: #fff1f6;
    }

    </style>
    """,
    unsafe_allow_html=True
)


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


if st.session_state.message:

    if st.session_state.message_type == "success":

        st.success(
            st.session_state.message
        )

    elif st.session_state.message_type == "error":

        st.error(
            st.session_state.message
        )

    else:

        st.info(
            st.session_state.message
        )

    st.session_state.message = None


subjects = get_subjects()
tasks = get_tasks()


if st.session_state.page == "Beranda":

    st.title("PENGINGAT TUGAS")

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
        '<div class="hero">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<p class="date-text">{tanggal_indonesia(today, True)}</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### Satu - satu, selesai"
    )

    st.write(
        "Catat yang perlu dikerjakan. "
        "Biar kepala lebih lega dan deadline terasa "
        "lebih dekat untuk ditaklukan."
    )

    stat1, stat2 = st.columns(2)

    with stat1:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.write("Tugas selesai")

        st.subheader(
            str(len(completed))
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with stat2:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.write("Tugas belum selesai")

        st.subheader(
            str(len(unfinished))
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    if st.session_state.show_add_task:

        st.subheader("Tambah Tugas")

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
                "task_form",
                clear_on_submit=True
            ):

                selected_subject = st.selectbox(
                    "Mata Pelajaran",
                    list(subject_options.keys())
                )

                task_name = st.text_input(
                    "Nama Tugas"
                )

                deadline = st.date_input(
                    "Deadline",
                    value=date.today()
                )

                save = st.form_submit_button(
                    "Simpan Tugas",
                    use_container_width=True
                )

            if save:

                if not task_name.strip():

                    st.error(
                        "Nama tugas harus diisi."
                    )

                else:

                    try:

                        pasang_access_token()

                        (
                            supabase
                            .table("tasks")
                            .insert(
                                {
                                    "user_id":
                                        st.session_state.user.id,

                                    "subject_id":
                                        subject_options[
                                            selected_subject
                                        ],

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

        if st.button(
            "＋ Tambah Tugas",
            key="add_task"
        ):

            st.session_state.show_add_task = True
            st.rerun()


    st.subheader("DAFTAR TUGAS")


    col_all, col_unfinished, col_done = st.columns(3)


    with col_all:

        if st.button(
            f"Semua ({len(tasks)})",
            use_container_width=True
        ):

            st.session_state.task_filter = "Semua"
            st.rerun()


    with col_unfinished:

        if st.button(
            f"Belum selesai ({len(unfinished)})",
            use_container_width=True
        ):

            st.session_state.task_filter = "Belum selesai"
            st.rerun()


    with col_done:

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

        st.info(
            "Belum ada tugas. "
            "Tekan tombol Tambah Tugas untuk membuat tugas."
        )

    else:

        columns = st.columns(2)

        for index, task in enumerate(visible_tasks):

            with columns[index % 2]:

                st.markdown(
                    '<div class="task-box">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="task-subject">{subject_map.get(task["subject_id"], "Mata Pelajaran")}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="task-name">{task["name"]}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="task-deadline">Tenggat: {tanggal_indonesia(task["deadline"])}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


                old_done = task.get(
                    "done",
                    False
                )

                new_done = st.checkbox(
                    "Tandai selesai",
                    value=old_done,
                    key=f"done_{task['id']}"
                )


                if new_done != old_done:

                    try:

                        pasang_access_token()

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
                    key=f"delete_task_{task['id']}"
                ):

                    try:

                        pasang_access_token()

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

    st.title("Mata Pelajaran")

    st.info(
        "Tambahkan mata pelajaran yang ingin kamu gunakan "
        "saat membuat tugas."
    )


    with st.form(
        "subject_form",
        clear_on_submit=True
    ):

        subject_name = st.text_input(
            "Nama Mata Pelajaran"
        )

        add_subject = st.form_submit_button(
            "Tambah Mata Pelajaran",
            use_container_width=True
        )


    if add_subject:

        subject_name = subject_name.strip()

        if not subject_name:

            st.error(
                "Nama mata pelajaran harus diisi."
            )

        elif any(
            subject["name"].lower()
            == subject_name.lower()
            for subject in subjects
        ):

            st.warning(
                "Mata pelajaran tersebut sudah ada."
            )

        else:

            try:

                pasang_access_token()

                (
                    supabase
                    .table("subjects")
                    .insert(
                        {
                            "user_id":
                                st.session_state.user.id,

                            "name":
                                subject_name
                        }
                    )
                    .execute()
                )

                set_message(
                    "Mata pelajaran berhasil ditambahkan.",
                    "success"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Gagal menambahkan mata pelajaran: {error}"
                )


    st.subheader(
        "Daftar Mata Pelajaran"
    )


    if not subjects:

        st.info(
            "Belum ada mata pelajaran."
        )

    else:

        for subject in subjects:

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                st.markdown(
                    f'<div class="info-box"><b>{subject["name"]}</b></div>',
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

                            pasang_access_token()

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


elif st.session_state.page == "Notifikasi":

    st.title("Notifikasi")

    today = date.today()

    unfinished = [
        task
        for task in tasks
        if task.get("done") is not True
    ]

    overdue = [
        task
        for task in unfinished
        if date.fromisoformat(
            task["deadline"][:10]
        ) < today
    ]

    upcoming = [
        task
        for task in unfinished
        if today
        <= date.fromisoformat(
            task["deadline"][:10]
        )
        <= today + timedelta(days=2)
    ]


    if overdue:

        st.subheader("Tugas Terlewat")

        for task in overdue:

            st.warning(
                f"{task['name']} — deadline "
                f"{tanggal_indonesia(task['deadline'])}"
            )


    if upcoming:

        st.subheader("Deadline Terdekat")

        for task in upcoming:

            st.info(
                f"{task['name']} — deadline "
                f"{tanggal_indonesia(task['deadline'])}"
            )


    if not overdue and not upcoming:

        st.success(
            "Tidak ada notifikasi saat ini. ✨"
        )


elif st.session_state.page == "Akun":

    st.title("Akun")

    st.subheader("Informasi Akun")

    st.write("Email")

    st.info(
        st.session_state.user.email
    )

    st.write("Total Tugas")

    st.metric(
        label="Jumlah tugas",
        value=len(tasks)
    )

    st.write("")

    if st.button(
        "Keluar",
        use_container_width=True
    ):

        logout()


elif st.session_state.page == "Pengaturan":

    st.title("Pengaturan")

    st.subheader("Tampilan")

    st.write(
        "Pengingat Tugas menggunakan tampilan "
        "terang dengan nuansa pink."
    )

    st.divider()

    st.subheader("Penyimpanan")

    st.write(
        "Tugas dan mata pelajaran tersimpan "
        "di Supabase berdasarkan akun pengguna."
    )

    st.divider()

    if st.button(
        "Keluar dari akun",
        use_container_width=True
    ):

        logout()
