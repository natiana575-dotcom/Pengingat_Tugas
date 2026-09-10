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

if "message" not in st.session_state:
    st.session_state.message = ""

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
        st.session_state.message = ""
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

    except Exception as e:
        st.error("Gagal membuat akun. Pastikan email dan password sudah benar.")


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
            .select("id, subject_id, name, deadline")
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
            task["done"] = task.get("done", False)

        return tasks

    except Exception:
        return []


def add_subject(name):
    try:
        supabase.table("subjects").insert({
            "user_id": st.session_state.user.id,
            "name": name.strip()
        }).execute()

        st.success("Mata pelajaran berhasil ditambahkan.")
        st.rerun()

    except Exception:
        st.error("Mata pelajaran tersebut mungkin sudah ada.")


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
            "deadline": str(deadline)
        }).execute()

        st.session_state.show_form = False
        st.rerun()

    except Exception:
        st.error("Tugas gagal ditambahkan.")


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
    border: none
