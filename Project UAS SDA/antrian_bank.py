from tkinter import *
from tkinter import ttk, messagebox
from collections import deque
import re
import math

# DATA ANTREAN
teller1 = deque()
teller2 = deque()
cs1 = deque()
cs2 = deque()

waktu_teller1 = 0
waktu_teller2 = 0
waktu_cs1 = 0
waktu_cs2 = 0

nomor_antrian = 1

# JENIS LAYANAN
layanan_teller = ["Penyetoran", "Penarikan", "Transfer", "Pembayaran Tagihan"]
layanan_cs = ["Konsultasi", "Buka Rekening Baru", "Kehilangan Kartu", "Reset PIN", "Update Data Nasabah"]

# HITUNG WAKTU
def hitung_waktu(layanan, jumlah=0):

    if layanan in ["Penyetoran", "Penarikan"]:

        blok = max(1, math.ceil(jumlah / 10000000))
        return blok * 5

    elif layanan == "Transfer":
        return 5

    elif layanan == "Pembayaran Tagihan":
        return 5

    elif layanan == "Konsultasi":
        return 10

    elif layanan == "Buka Rekening Baru":
        return 20

    elif layanan == "Kehilangan Kartu":
        return 20

    elif layanan == "Reset PIN":
        return 10

    elif layanan == "Update Data Nasabah":
        return 15

    return 5

# UPDATE LISTBOX
def tampilkan(queue, listbox):
    listbox.delete(0, END)
    total_tunggu = 0
    for data in queue:
        total_tunggu += data["estimasi"]
        listbox.insert(END, f"No {data['nomor']} | " f"{data['nama']} | " f"{data['layanan']} | " f"Estimasi Tunggu: {total_tunggu} menit")

def update_semua():
    tampilkan(teller1, list_t1)
    tampilkan(teller2, list_t2)
    tampilkan(cs1, list_cs1)
    tampilkan(cs2, list_cs2)

    lbl_t1.config(text=f"Total: {waktu_teller1} menit")
    lbl_t2.config(text=f"Total: {waktu_teller2} menit")
    lbl_cs1.config(text=f"Total: {waktu_cs1} menit")
    lbl_cs2.config(text=f"Total: {waktu_cs2} menit")

# TOGGLE INPUT JUMLAH
def toggle_jumlah(event=None):
    layanan = combo_layanan.get()
    if layanan in ["Penyetoran", "Penarikan"]:
        label_jumlah.grid(row=2, column=0, padx=10, pady=10)
        entry_jumlah.grid(row=2, column=1)
    else:
        label_jumlah.grid_remove()
        entry_jumlah.grid_remove()

# SIMPAN KE TXT
def simpan_ke_txt(nama, layanan, jumlah):
    with open("data_nasabah.txt", "a", encoding="utf-8") as file:
        if jumlah > 0:
            nominal = f"Rp {jumlah:,}".replace(",", ".")
        else:
            nominal = "-"
        file.write(f"\n{nama}|{layanan}|{nominal}")

# TAMBAH NASABAH
def tambah_nasabah():
    global nomor_antrian
    global waktu_teller1, waktu_teller2
    global waktu_cs1, waktu_cs2

    nama = entry_nama.get().upper()
    layanan = combo_layanan.get()

    if nama == "" or layanan == "":
        messagebox.showwarning("Peringatan", "Lengkapi data terlebih dahulu")
        return
    jumlah = 0

    if layanan in ["Penyetoran", "Penarikan"]:
        try:
            jumlah = int(entry_jumlah.get())
        except:
            messagebox.showwarning("Peringatan", "Masukkan jumlah transaksi")
            return
    estimasi = hitung_waktu(layanan, jumlah)
    data = {"nomor": nomor_antrian, "nama": nama, "layanan": layanan, "estimasi": estimasi}

    #TELLER
    if layanan in layanan_teller:
        if waktu_teller1 <= waktu_teller2:
            teller1.append(data)
            waktu_teller1 += estimasi
            tujuan = "Teller 1"
        else:
            teller2.append(data)
            waktu_teller2 += estimasi
            tujuan = "Teller 2"

    #CUSTOMER SERVICE
    else:
        if waktu_cs1 <= waktu_cs2:
            cs1.append(data)
            waktu_cs1 += estimasi
            tujuan = "Customer Service 1"
        else:
            cs2.append(data)
            waktu_cs2 += estimasi
            tujuan = "Customer Service 2"

    #SIMPAN KE TXT
    simpan_ke_txt(nama, layanan, jumlah)
    nomor_antrian += 1
    update_semua()
    messagebox.showinfo("Berhasil", f"Nasabah masuk ke {tujuan}")

    entry_nama.delete(0, END)
    entry_jumlah.delete(0, END)

# BACA FILE TXT
def baca_file_txt():
    global nomor_antrian
    global waktu_teller1, waktu_teller2
    global waktu_cs1, waktu_cs2

    try:
        with open("data_nasabah.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            bagian = line.split("|")

            # format harus 3 kolom
            if len(bagian) != 3:
                continue
            nama = bagian[0].strip()
            layanan = bagian[1].strip()
            nominal = bagian[2].strip()
            jumlah = 0

    # AMBIL NOMINAL
            angka = re.sub(r"[^0-9]", "", nominal)

            if angka != "":
                jumlah = int(angka)

            estimasi = hitung_waktu(layanan, jumlah)
            data = {"nomor": nomor_antrian, "nama": nama, "layanan": layanan, "estimasi": estimasi}

    # TELLER
            if layanan in layanan_teller:

                if waktu_teller1 <= waktu_teller2:

                    teller1.append(data)
                    waktu_teller1 += estimasi
                else:

                    teller2.append(data)
                    waktu_teller2 += estimasi

    # CUSTOMER SERVICE
            elif layanan in layanan_cs:
                if waktu_cs1 <= waktu_cs2:
                    cs1.append(data)
                    waktu_cs1 += estimasi
                else:
                    cs2.append(data)
                    waktu_cs2 += estimasi
            nomor_antrian += 1
        update_semua()
    except Exception as e:
        print("ERROR:", e)

#LAYANI NASABAH
def layani(queue, nama_counter):
    global waktu_teller1, waktu_teller2
    global waktu_cs1, waktu_cs2

    if len(queue) == 0:
        messagebox.showinfo("Info", f"Antrean {nama_counter} kosong")
        return

    data = queue.popleft()
    hapus_dari_txt(data["nama"], data["layanan"])

    if nama_counter == "Teller 1":
        waktu_teller1 -= data["estimasi"]

    elif nama_counter == "Teller 2":
        waktu_teller2 -= data["estimasi"]

    elif nama_counter == "CS 1":
        waktu_cs1 -= data["estimasi"]

    elif nama_counter == "CS 2":
        waktu_cs2 -= data["estimasi"]

    update_semua()
    messagebox.showinfo("Melayani", f"{nama_counter} sedang melayani:\n\n" f"{data['nama']}")

# HAPUS DATA DARI TXT
def hapus_dari_txt(nama, layanan):
    try:
        with open("data_nasabah.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open("data_nasabah.txt", "w", encoding="utf-8") as file:
            sudah_dihapus = False

            for line in lines:
                bagian = line.strip().split("|")

                if len(bagian) >= 2:
                    nama_file = bagian[0].strip()
                    layanan_file = bagian[1].strip()

                    # hapus hanya satu data yang cocok
                    if nama_file == nama and layanan_file == layanan and not sudah_dihapus:
                        sudah_dihapus = True
                        continue

                file.write(line)

    except Exception as e:
        print("ERROR HAPUS TXT:", e)

# GUI
root = Tk()

root.title("Sistem Antrean Bank")
root.geometry("1200x800")
root.configure(bg="#EAF4FF")

# JUDUL
Label(root, text="SISTEM ANTREAN BANK", font=("Arial", 24, "bold"), bg="#EAF4FF", fg="#003366").pack(pady=10)

# TAB
tab = ttk.Notebook(root)
tab.pack(fill=BOTH, expand=True, padx=15, pady=(0, 10))

hal_input = Frame(tab, bg="#EAF4FF")
hal_monitor = Frame(tab, bg="#EAF4FF")

tab.add(hal_input, text="Input Nasabah")
tab.add(hal_monitor, text="Monitoring")

# TAB INPUT NASABAH
box = Frame(hal_input, bg="white", bd=2, relief=RIDGE)
box.place(relx=0.5, rely=0.45, anchor="center", width=500, height=320)

box.grid_columnconfigure(0, weight=1)
box.grid_columnconfigure(1, weight=1)

# INPUT NAMA

Label(box, text="Nama Nasabah", bg="white", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=10, pady=15)
entry_nama = Entry(box, width=35, font=("Arial", 12))
entry_nama.grid(row=0, column=1)

# INPUT LAYANAN
Label(box, text="Jenis Layanan", bg="white", font=("Arial", 13, "bold")).grid(row=1, column=0, padx=10, pady=15)
combo_layanan = ttk.Combobox(box, width=32, font=("Arial", 12), values=layanan_teller + layanan_cs)
combo_layanan.grid(row=1, column=1)
combo_layanan.bind("<<ComboboxSelected>>", toggle_jumlah)

# INPUT JUMLAH
label_jumlah = Label(box, text="Jumlah Uang", bg="white", font=("Arial", 13, "bold"))
entry_jumlah = Entry(box, width=35, font=("Arial", 12))

# BUTTON TAMBAH
Button(box, text="Tambah Nasabah", bg="#007BFF", fg="white", font=("Arial", 15, "bold"), width=18, height=2, command=tambah_nasabah).grid(row=4, column=0, columnspan=2, pady=50)

# TAB MONITORING
container = Frame(hal_monitor, bg="#EAF4FF")
container.pack(fill=BOTH, expand=True, padx=10, pady=10)

#FUNGSI KOTAK
def buat_kotak(parent, judul, row, col):
    frame = Frame(parent, bg="white", bd=2, relief=RIDGE)
    frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    Label(frame, text=judul, bg="white", fg="#003366", font=("Arial", 18, "bold")).pack(pady=10)
    lbl = Label(frame, text="Total: 0 menit", bg="white", font=("Arial", 12, "bold"))

    lbl.pack()

    area = Frame(frame, bg="white")
    area.pack(pady=5)

    scrollbar = Scrollbar(area)
    scrollbar.pack(side=RIGHT, fill=Y)

    lb = Listbox(area, width=55, height=10, font=("Arial", 10), yscrollcommand=scrollbar.set)

    lb.pack(side=LEFT)

    scrollbar.config(command=lb.yview)

    return frame, lbl, lb

# GRID
container.rowconfigure((0, 1), weight=1)
container.columnconfigure((0, 1), weight=1)

# BUAT KOTAK
f1, lbl_t1, list_t1 = buat_kotak(container, "TELLER 1", 0, 0)
f2, lbl_t2, list_t2 = buat_kotak(container, "TELLER 2", 0, 1)
f3, lbl_cs1, list_cs1 = buat_kotak(container, "CUSTOMER SERVICE 1", 1, 0)
f4, lbl_cs2, list_cs2 = buat_kotak(container, "CUSTOMER SERVICE 2", 1, 1)

# BUTTON LAYANI
Button(f1, text="Layani", bg="#28A745", fg="white", font=("Arial", 11, "bold"), width=12, height=1, command=lambda: layani(teller1, "Teller 1")).pack(pady=5)
Button(f2, text="Layani", bg="#28A745", fg="white", font=("Arial", 11, "bold"), width=12, height=1, command=lambda: layani(teller2, "Teller 2")).pack(pady=5)
Button(f3, text="Layani", bg="#DC3545", fg="white",font=("Arial", 11, "bold"), width=12, height=1, command=lambda: layani(cs1, "CS 1")).pack(pady=5)
Button(f4, text="Layani", bg="#DC3545", fg="white", font=("Arial", 11, "bold"), width=12, height=1, command=lambda: layani(cs2, "CS 2")).pack(pady=5)

root.after(100, baca_file_txt)
root.mainloop()