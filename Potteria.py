import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel(r"C:\Users\NIV\Downloads\Data Dummy Potteria.xlsx")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Bulan"] = df["Tanggal"].dt.to_period("M")

    # Ubah Pengeluaran ke nilai absolut (positif)
    df["Pengeluaran (Rp)"] = df["Pengeluaran (Rp)"].abs()
    return df

df = load_data()

# Sidebar untuk navigasi
st.sidebar.title("Navigasi Halaman")
selected_page = st.sidebar.radio("Pilih Halaman:", ["Report Pengeluaran Bulanan per PT", "Report Pengeluaran PT MBA"])

if selected_page == "Report Pengeluaran Bulanan per PT":
    # Sidebar filters
    st.sidebar.header("Filter Data")

    # Pilih PT
    all_pts = sorted(df["PT"].dropna().unique())
    selected_pt = st.sidebar.selectbox("Pilih PT", ["All"] + all_pts)

    # Pilih bulan
    min_date = df["Tanggal"].min()
    max_date = df["Tanggal"].max()

    start_month = st.sidebar.date_input("Dari Tanggal", min_value=min_date, value=min_date)
    end_month = st.sidebar.date_input("Sampai Tanggal", max_value=max_date, value=max_date)

    # Convert ke datetime64[ns]
    start_month = pd.to_datetime(start_month)
    end_month = pd.to_datetime(end_month)

    # Filter berdasarkan input
    mask = (df["Tanggal"] >= start_month) & (df["Tanggal"] <= end_month)
    if selected_pt != "All":
        mask &= (df["PT"] == selected_pt)

    filtered_df = df[mask]

    # Hitung total pengeluaran per bulan untuk setiap PT
    data_summary = (
        filtered_df.groupby(["PT", df["Tanggal"].dt.to_period("M")])["Pengeluaran (Rp)"]
        .sum()
        .reset_index()
    )
    data_summary["Tanggal"] = data_summary["Tanggal"].astype(str)

    # Tombol agregasi total tanpa per bulan
    aggregate_total = st.sidebar.checkbox("Tampilkan total saja per PT (tanpa per bulan)")

    if aggregate_total:
        total_summary = (
            filtered_df.groupby("PT")["Pengeluaran (Rp)"].sum().reset_index()
        )
        st.header("Total Pengeluaran Selama Periode yang Dipilih per PT")
        fig = px.bar(
            total_summary,
            x="PT",
            y="Pengeluaran (Rp)",
            title="Total Pengeluaran Selama Periode Tertentu per PT",
            labels={"Pengeluaran (Rp)": "Total Pengeluaran"}
        )
        st.plotly_chart(fig)
    else:
        if selected_pt != "All":
            pt_summary = data_summary[data_summary["PT"] == selected_pt]
            st.header(f"Total Pengeluaran Bulanan - {selected_pt}")
            fig = px.bar(
                pt_summary,
                x="Tanggal",
                y="Pengeluaran (Rp)",
                title=f"Pengeluaran {selected_pt}",
                labels={"Tanggal": "Bulan", "Pengeluaran (Rp)": "Total Pengeluaran"}
            )
            st.plotly_chart(fig)
        else:
            st.header("Total Pengeluaran Bulanan - Semua PT")
            fig = px.bar(
                data_summary,
                x="Tanggal",
                y="Pengeluaran (Rp)",
                color="PT",
                barmode="group",
                title="Pengeluaran Semua PT",
                labels={"Tanggal": "Bulan", "Pengeluaran (Rp)": "Total Pengeluaran"}
            )
            st.plotly_chart(fig)

    # Tambahkan grafik berdasarkan Bank
    bank_summary = (
        filtered_df.groupby("Bank")["Pengeluaran (Rp)"].sum().reset_index()
    )
    bank_summary = bank_summary[bank_summary["Pengeluaran (Rp)"] > 0]

    if not bank_summary.empty:
        st.subheader("Total Pengeluaran per Bank")
        fig_bank = px.bar(
            bank_summary,
            x="Bank",
            y="Pengeluaran (Rp)",
            title="Total Pengeluaran berdasarkan Bank",
            labels={"Pengeluaran (Rp)": "Total Pengeluaran"}
        )
        st.plotly_chart(fig_bank)

elif selected_page == "Report Pengeluaran PT MBA":
    # Filter hanya untuk PT MBA
    pt_target = "MBA"
    df_mba = df[df["PT"].str.upper() == pt_target.upper()]

    # Sidebar - Filter tanggal
    st.sidebar.header("Filter Bulan")
    min_date = df_mba["Tanggal"].min()
    max_date = df_mba["Tanggal"].max()

    start_month = st.sidebar.date_input("Dari Bulan", min_value=min_date, value=min_date)
    end_month = st.sidebar.date_input("Sampai Bulan", max_value=max_date, value=max_date)

    # Konversi ke datetime untuk filtering
    start_month = pd.to_datetime(start_month)
    end_month = pd.to_datetime(end_month)

    mask = (df_mba["Tanggal"] >= start_month) & (df_mba["Tanggal"] <= end_month)
    df_filtered = df_mba[mask]

    st.title("Proporsi Pengeluaran PT MBA")

    if df_filtered.empty:
        st.warning("Tidak ada data pengeluaran untuk PT MBA di rentang tanggal yang dipilih.")
    else:
        # Hitung proporsi pengeluaran berdasarkan jenis transaksi
        summary = df_filtered.groupby("Jenis Transaksi")["Pengeluaran (Rp)"].sum().reset_index()
        summary = summary[summary["Pengeluaran (Rp)"] != 0]  # hanya yang punya pengeluaran

        # Doughnut Chart
        fig = px.pie(
            summary,
            names="Jenis Transaksi",
            values="Pengeluaran (Rp)",
            hole=0.4,
            title="Proporsi Pengeluaran per Jenis Transaksi (PT MBA)",
            labels={"Pengeluaran (Rp)": "Total Pengeluaran"},
        )
        st.plotly_chart(fig)
