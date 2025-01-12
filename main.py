# smtplib: Modul ini untuk melakukan operasi email seperti mengirim email menggunakan SMTP.
import smtplib
# os: Modul ini digunakan untuk berinteraksi dengan sistem operasi, seperti membaca atau menulis file.
import os
# pandas: Modul ini digunakan untuk analisis dan manipulasi data yang besar dan kompleks.
import pandas as pd
# colorama: Modul ini digunakan untuk memberikan warna pada output di terminal.
from colorama import Fore, Style, init
# dotenv: Modul ini digunakan untuk mengambil informasi dari file .env
from dotenv import load_dotenv
# MIMEText, MIMEMultipart, dan MIMEBase: digunakan untuk membuat pesan email dengan format MIME.
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
# encoders: Modul ini digunakan untuk encoding dan decoding MIME non-text seperti lampiran.
from email import encoders
# tqdm: Modul ini digunakan untuk membuat progress bar.
from tqdm import tqdm
# datetime: Modul ini digunakan untuk bekerja dengan objek tanggal dan waktu.
from datetime import datetime
# Template: Digunakan untuk substitusi string.
from string import Template


# ========================================================================================================
# Bagian diatas adalah import modul yang dibutuhkan. JANGAN DIUBAH! SUDAH ADA DESKRPSINYA JUGA KOK!
# Kode dibawah ini itu yang dijalanin.
# ========================================================================================================

try:
    try:
        # Penentuan lokasi file .env yang mengandung informasi penting dan sensitif
        env_path = os.path.join(os.path.dirname(__file__), '.env.development') # Ubah .env.development menjadi .env.production jika sudah fix jadi
        load_dotenv(env_path)

    except Exception as e:
        print(f'{Fore.RED}{Style.BRIGHT}File config .env tidak ditemukan!')
        print(f'{Fore.YELLOW}{Style.BRIGHT}Hubungi Ihsan atau Farrel untuk mendapatkan file .env')
        print('Kesalahan:', str(e))
        exit()

    # Inisialisasi colorama untuk memberikan warna pada output di terminal dan autoreset untuk mengembalikan warna terminal ke default
    init(autoreset=True)

    # Fungsi ini digunakan untuk mengirim email ke penerima dengan beberapa parameter yang diperlukan
    def send_email(sender_name, sender_email, sender_password, recipient_email, recipient_company, subject, html_message_template, attachment_path):
        smtp_server = os.getenv('smtp_server')
        smtp_port = int(os.getenv('smtp_port'))

        # Mengubah template pesan email dengan informasi perusahaan penerima
        html_message = Template(html_message_template).safe_substitute(nama_pt=recipient_company)

        # Inisialisasi email multipart untuk menampung teks dan lampiran
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_name
        message['To'] = recipient_email

        # Menambahkan html jadi badan email, tapi bentuk format teks sebagai pesan multipart
        message.attach(MIMEText(html_message, 'html'))

        try:
            # Membaca file lampiran dalam mode biner dan menambahkannya ke dalam pesan multipart
            with open(attachment_path, 'rb') as attachment:
                mime_attachment = MIMEBase('application', 'octet-stream')
                mime_attachment.set_payload(attachment.read())
                encoders.encode_base64(mime_attachment)
                mime_attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                message.attach(mime_attachment)

        except FileNotFoundError:
            print(f'{Fore.RED}{Style.BRIGHT}File attachment {attachment_path} tidak ditemukan!')
            print(f'{Fore.YELLOW}{Style.BRIGHT}Pastikan file attachment berada di folder yang sama dengan file python ini!')
            exit()

        except Exception as e:
            print(f'{Fore.RED}{Style.BRIGHT}Terjadi kesalahan saat membaca file attachment {attachment_path}!')
            print('Kesalahan:', str(e))
            exit()

        # Mengatur koneksi ke server SMTP dan mencoba mengirim email.
        # Jika ada kesalahan, fungsi akan menangkapnya dan mencetak pesan kesalahan
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f'\n{Fore.GREEN}{Style.BRIGHT}Email berhasil dikirim ke: {recipient_email}')
            return('Sukses')

        except Exception as e:
            print(f'\n{Fore.RED}{Style.BRIGHT}Terjadi kesalahan saat mengirim email ke: {recipient_email}')
            print('Kesalahan:', str(e))
            return('Gagal')

        finally:
            if 'server' in locals():
                server.quit()

    # Fungsi untuk membaca database email dari file Excel.
    # Fungsi ini mengembalikan sebuah DataFrame yang berisi informasi tentang penerima.
    def read_email_database(filename):
        dataframe = pd.read_excel(filename)
        return dataframe

    # Mengambil informasi pengirim dan password dari file .env
    sender_email = os.getenv('sender_email')
    sender_password = os.getenv('sender_password')

    # Mengatur informasi detail email melalui input dari pengguna
    sender_name = input(f'{Fore.WHITE}{Style.BRIGHT}Ketik nama pengirim atau tekan enter untuk default [OSIS SMK Telkom Sidoarjo]: ') or 'OSIS SMK Telkom Sidoarjo'
    subject = input(f'{Fore.WHITE}{Style.BRIGHT}Ketik subjek email untuk dikirm atau tekan enter untuk default [Pengajuan Kerja Sama Sponsorship OSIS SMK Telkom Sidoarjo]:{Fore.WHITE}{Style.BRIGHT} ') or 'Pengajuan Kerja Sama Sponsorship OSIS SMK Telkom Sidoarjo'
    html_file = input(f'{Fore.WHITE}{Style.BRIGHT}Ketik nama file template html atau tekan enter untuk default [email.html]: ') or 'email.html'
    attachment_path = input(f'{Fore.WHITE}{Style.BRIGHT}Ketik nama file attachment atau tekan enter untuk default [Proposal.pdf]: ') or 'Proposal.pdf'
    database_filename = input(f'{Fore.WHITE}{Style.BRIGHT}Ketik nama file Excel atau tekan enter untuk default [database_email.xlsx]: ') or 'database_email.xlsx'

    try:
        # Membaca database email dan memasukkannya ke dalam DataFrame
        dataframe_recipient_emails = read_email_database(database_filename)
        dataframe_update = pd.DataFrame(columns=['Status Pengiriman', 'Timestamp'])

    except FileNotFoundError:
        print(f'{Fore.RED}{Style.BRIGHT}File Excel {database_filename} tidak ditemukan!')
        print(f'{Fore.YELLOW}{Style.BRIGHT}Pastikan file Excel berada di dalam folder yang sama dengan file python ini!')
        exit()

    except PermissionError:
        print(f'{Fore.RED}{Style.BRIGHT}File Excel {database_filename} sedang digunakan oleh program lain!')
        exit()

    except Exception as e:
        print(f'{Fore.RED}{Style.BRIGHT}Terjadi kesalahan saat membaca file Excel {database_filename}!')
        print('Kesalahan:', str(e))
        exit()

    try:
        # Membaca template email dari file dan menyimpannya sebagai string
        with open(html_file, 'r') as f:
            html_message_template = f.read()

    except FileNotFoundError:
        print(f'{Fore.RED}{Style.BRIGHT}File HTML {html_file} tidak ditemukan!')
        print(f'{Fore.YELLOW}{Style.BRIGHT}Pastikan file template HTML untuk email berada di dalam folder yang sama dengan file python ini!')
        exit()

    except PermissionError:
        print(f'{Fore.RED}{Style.BRIGHT}File HTML {html_file} sedang digunakan oleh program lain!')
        exit()

    # Meminta konfirmasi dari pengguna sebelum mulai mengirim email
    execute_confirmation = input('\nApakah Anda yakin ingin mengirim email ke semua penerima? (y/n) ')
    if execute_confirmation == 'y':
        # Jumlah total email di database
        total_emails = dataframe_recipient_emails.shape[0]
        # Jumlah email baru (Status Pengiriman kosong)
        new_emails = dataframe_recipient_emails[dataframe_recipient_emails['Status Pengiriman'].isnull()].shape[0]
        # Jumlah email gagal sebelumnya, yang mau dicoba lagi (Status Pengiriman 'Gagal')
        failed_emails = dataframe_recipient_emails[(dataframe_recipient_emails['Status Pengiriman'] != 'Sukses') & (dataframe_recipient_emails['Status Pengiriman'].notnull())].shape[0]
        # Jumlah email yang akan dikirim (Status Pengiriman 'Gagal' + email baru)
        emails_to_send = new_emails + failed_emails

        # Menampilkan informasi email yang akan dikirim
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Email pengirim           : {Style.BRIGHT}{sender_email}')
        print(f'Nama pengirim            : {Style.BRIGHT}{sender_name}')
        print(f'Subjek                   : {Style.BRIGHT}{subject}\n')
        print(f'Total DB alamat email    : {total_emails}\n')
        print(f'{Fore.CYAN}{Style.BRIGHT}Mengirim email ke total  : {emails_to_send} alamat email')
        print(f'   - Email baru          : ' + str(new_emails))
        print(f'   - Retry yg gagal      : ' + str(failed_emails) + '\n')

        try:
            if emails_to_send > 0:
                # Loop untuk mengirim email ke setiap penerima yang ada dalam DataFrame
                for index, row in tqdm(dataframe_recipient_emails.iterrows(), total=dataframe_recipient_emails.shape[0], desc='Progress Pengiriman', unit='email'):
                    # Cek 'Status Pengiriman' untuk setiap penerima
                    # Hanya mengirim email jika 'Status Pengiriman' kosong atau 'Gagal'
                    if pd.isna(row['Status Pengiriman']) or row['Status Pengiriman'] != 'Sukses':
                        recipient_email = row['Alamat Email']
                        recipient_company = row['Nama PT']
                        status = send_email(sender_name, sender_email, sender_password, recipient_email, recipient_company, subject, html_message_template, attachment_path)
                        timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S') if status == 'Sukses' else ''
                        dataframe_recipient_emails.loc[index, 'Status Pengiriman'] = status
                        dataframe_recipient_emails.loc[index, 'Timestamp'] = timestamp

                    # Menyimpan DataFrame dengan informasi pengiriman ke file Excel
                    dataframe_recipient_emails.to_excel(database_filename, index=False)
            else:
                print(f'{Fore.YELLOW}Tidak ada email baru yang akan dikirim, kalau ini salah... coba cek database email.')
                print(f'{Fore.YELLOW}Kalau tidak ada masalah, berarti semua email sudah dikirim sebelumnya.')

        except KeyboardInterrupt:
            # Kalau ada ctrl+c, menyimpan DataFrame ke file Excel sebelum keluar
            dataframe_recipient_emails.to_excel(database_filename, index=False)
            print(f'\n{Fore.RED}{Style.BRIGHT}"CTRL+C" terdeteksi, menghentikan program...')
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}Progress pengiriman email berhasil disimpan ke file Excel sebelum keluar.')

        except Exception as e:
            print(f'\n{Fore.RED}{Style.BRIGHT}Terjadi kesalahan, baca pesan di bawah ini untuk info lebih lanjut.')
            print('Kesalahan:', str(e))

    else:
        print(f'{Fore.YELLOW}Pengiriman email dibatalkan\n')

except KeyboardInterrupt:
    # Kalau ada ctrl+c, menyimpan DataFrame ke file Excel sebelum keluar
    print(f'\n{Fore.RED}{Style.BRIGHT}"CTRL+C" terdeteksi, menghentikan program...')
# ====================================================================================================================
# INI RANGKUMAN ALUR KERJA PROGRAM, BUAT REFERENSI UNTUK SISWA UMUM
# ====================================================================================================================
# Program ini dibuat untuk mengirimkan email ke beberapa penerima secara otomatis dengan lampiran dan pesan yang telah
# ditentukan. Prosesnya adalah sebagai berikut:
#
# 1. Pertama, semua modul yang dibutuhkan diimpor, termasuk modul untuk mengirim email, memanipulasi data, dan berinteraksi
#    dengan sistem operasi.
#
# 2. Kemudian, informasi penting seperti alamat server SMTP dan port SMTP diambil dari file .env menggunakan modul dotenv.
#
# 3. Fungsi send_email() dibuat untuk mengirim email kepada penerima. Dalam fungsi ini, pesan email dibuat dengan
#    menggabungkan teks dan lampiran, dan kemudian email tersebut dikirim melalui server SMTP. Jika terjadi kesalahan
#    saat mengirim email, fungsi akan mencetak pesan kesalahan dan mengembalikan status 'Gagal'. Jika berhasil,
#    fungsi akan mencetak pesan sukses dan mengembalikan status 'Sukses'.
#
# 4. Fungsi read_email_database() digunakan untuk membaca database email dari file Excel dan mengembalikan DataFrame pandas.
#
# 5. Program kemudian mengambil data pengirim dan password dari file .env. Pengguna diminta untuk memasukkan informasi
#    lain seperti nama pengirim, subjek email, template email, file lampiran, dan nama file database. Jika pengguna tidak
#    memasukkan apa pun dan hanya menekan enter, program akan menggunakan nilai default.
#
# 6. Setelah itu, program membaca database email dan membuat DataFrame baru untuk menyimpan status pengiriman dan timestamp.
#
# 7. Pengguna kemudian diminta untuk memastikan apakah mereka ingin melanjutkan pengiriman email. Jika mereka menjawab
#    'y', program akan mengirim email ke setiap alamat dalam database. Untuk setiap email yang dikirim, program mencatat
#    status pengiriman dan timestamp (jika sukses) ke DataFrame.
#
# 8. Setelah semua email telah dikirim, program menyimpan DataFrame yang telah diperbarui ke file Excel. Jika pengguna
#    menjawab 'n' ketika diminta konfirmasi, pengiriman email akan dibatalkan.
#
#
# File Excel HARUS di-format sebagai berikut:
#
# | Alamat Email | Nama PT | Status Pengiriman | Timestamp |
# | ------------ | ------- | ----------------- | --------- |
# | email1       | PT1     |                   |           |
# | email2       | PT2     |                   |           |
# | ...          | ...     |                   |           |
#
# Dengan format tersebut, baru dapat membaca dan memproses database email dengan benar serta memperbarui
# status pengiriman dan timestamp.
# ====================================================================================================================