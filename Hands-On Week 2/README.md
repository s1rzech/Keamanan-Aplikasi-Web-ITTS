# Laporan Praktikum Week 2 — OWASP Top 10, Risk Mapping & MiniMart Lab

**Mata Kuliah:** Keamanan Aplikasi Web (TI215 / MK15)  
**Institusi:** Institut Teknologi Tangerang Selatan (ITTS)  
**Dosen Pengampu:** Taufik Iqbal Ramdhani, S.Kom., M.Sc.  
**Kelompok / Tim:**
1. Hafiz Hablillah
2. Farel Eka Saputra

**Tanggal Praktik:** 14 Oktober 2026  
**Scope:** Pengujian dilakukan secara eksklusif pada target lokal `http://localhost:8080` (`server.py`). Tidak ada pengujian, pemindaian, atau pengiriman payload yang diarahkan ke sistem publik, jaringan luar, maupun server kampus ITTS.

---

## 1. Ringkasan Eksekutif
Praktikum ini bertujuan untuk mengidentifikasi, memetakan, dan menganalisis kerentanan pada aplikasi simulasi MiniMart berdasarkan taksonomi OWASP Top 10 (2021). Berdasarkan pengujian dinamis berbasis terminal (`curl -i`), ditemukan sejumlah kelemahan kritis yang meliputi ketiadaan kontrol otorisasi server-side pada endpoint administratif, kebocoran konfigurasi internal aplikasi, manajemen sesi dan cookie yang tidak aman, ketiadaan sanitasi input rendering yang membuka celah injeksi HTML/XSS, serta hilangnya HTTP Security Headers. Seluruh temuan telah diverifikasi secara empiris melalui respons server, dianalisis dampaknya terhadap aset bisnis, dipetakan prioritas risikonya, dan dirumuskan langkah remediasi teknis yang sesuai dengan akar permasalahan (*root cause*).

---

## 2. Inventaris Berkas Bukti Teknis (Evidence Artifacts)

| Kode Bukti | Endpoint Target | Perintah Pengujian | File Bukti | Kondisi Respons Kunci |
| :---: | :--- | :--- | :--- | :--- |
| **A** | `/` | `curl -i http://localhost:8080/` | `Evidence-01-HTTP_Basic.png` | `HTTP/1.0 200 OK`, `Server: Week2OWASPLab/1.0 Python/3.14.6`, ketiadaan seluruh HTTP security headers dasar. |
| **B** | `/login` | `curl -i "http://localhost:8080/login?user=alice"` | `Evidence-02-Sensitive_Data.png` | `HTTP/1.0 200 OK`, `Set-Cookie: username=alice; Path=/` tanpa atribut `HttpOnly`, `Secure`, maupun `SameSite`. |
| **C** | `/admin` | `curl -i http://localhost:8080/admin` | `Evidence-03-Broken_Access_Control.png` | `HTTP/1.0 200 OK`, panel admin dan daftar pengguna sensitif dapat dibaca langsung tanpa login/role checking. |
| **D** | `/debug` | `curl -i http://localhost:8080/debug` | `Evidence-04-Security_Misconfiguration.png` | `HTTP/1.0 200 OK`, ekspos JSON sensitif (`debug: true`, `fake_db_host: localhost`, error feature flag). |
| **E** | `/search` | `curl -i "http://localhost:8080/search?q=%3Cb%3Etest%3C/b%3E"` | `Evidence-05-Input_Injection.png` | `HTTP/1.0 200 OK`, parameter input pengguna dirender mentah ke dalam DOM HTML tanpa output encoding/escaping. |

---

## 3. Worksheet Pemetaan Kerentanan (OWASP Mapping)

| No | Endpoint | Evidence Teknis | Kategori OWASP | Dampak | Mitigasi Spesifik |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `/admin` | Respons `HTTP/1.0 200 OK` menyajikan data JSON `{"adminPanel": true, "users": ["alice", "bob", "admin"]}` secara bebas kepada klien tanpa memerlukan header autentikasi maupun validasi cookie sesi. | **A01:2021 – Broken Access Control** | Penyerang atau pengguna anonim dapat mengakses fungsionalitas manajemen internal, membaca daftar seluruh pengguna aplikasi, dan berpotensi mengambil alih hak administratif sistem secara horizontal maupun vertikal. | 1. Terapkan prinsip *deny-by-default* pada seluruh endpoint administratif.<br>2. Pasang *middleware authorization* di sisi server untuk memvalidasi identitas sesi dan memastikan atribut `role == 'admin'` sebelum merender halaman. |
| **2** | `/search` | Parameter kueri `q=%3Cb%3Etest%3C/b%3E` dipantulkan secara harfiah ke dalam struktur body HTML respons: `<p>Hasil pencarian untuk: <b><b>test</b></b></p>` tanpa proses sanitasi maupun encoding karakter khusus. | **A03:2021 – Injection** (Konteks *Reflected XSS*) | Penyerang dapat menyusun tautan manipulatif berisi skrip JavaScript berbahaya. Saat diakses oleh korban, skrip akan dieksekusi oleh peramban korban untuk mencuri session cookie, manipulasi DOM, atau defacement. | 1. Terapkan fungsi *context-aware output encoding* (seperti `html.escape()` pada Python) pada semua variabel dinamis yang disisipkan ke dalam HTML.<br>2. Terapkan *Content Security Policy* (CSP) ketat (`default-src 'self'`). |
| **3** | `/login` | Respons mengembalikan header `Set-Cookie: username=alice; Path=/`. Nilai sesi bersifat prediktif (nama pengguna mentah) serta tidak menyertakan atribut pengaman `HttpOnly`, `Secure`, maupun `SameSite`. | **A07:2021 – Identification and Authentication Failures** *(serta A05: Security Misconfiguration)* | Sesi pengguna sangat mudah dipalsukan (*session spoofing/tampering*) hanya dengan menebak username. Cookie dapat diakses langsung oleh skrip berbahaya via `document.cookie` serta rentan serangan CSRF. | 1. Terbitkan *Session ID* acak berbasis kriptografi aman (*cryptographically secure pseudorandom number generator*) di sisi server.<br>2. Tambahkan atribut pengaman cookie: `HttpOnly; Secure; SameSite=Strict; Path=/`. |
| **4** | `/debug` | Endpoint merender payload JSON yang membeberkan informasi operasional internal: status `"debug": true`, nama dan versi server `"Week2OWASPLab/1.0"`, serta alamat infrastruktur `"fake_db_host": "localhost"`. | **A05:2021 – Security Misconfiguration** | Penyerang memperoleh informasi jejak arsitektur internal (*information disclosure*) untuk menyusun skenario serangan bertarget (*reconnaissance stage*), mempermudah eksploitasi celah komponen tertentu. | 1. Nonaktifkan mode debug pada lingkungan produksi (*production*).<br>2. Batasi akses rute diagnostik/debug hanya untuk IP localhost internal yang terotentikasi, atau hapus rute debug dari routing utama. |
| **5** | `/` | Respons server menampilkan header informasi detail `Server: Week2OWASPLab/1.0 Python/3.14.6` dan tidak memiliki satupun security headers modern (`CSP`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`). | **A05:2021 – Security Misconfiguration** | Aplikasi rentan terhadap serangan *Clickjacking* melalui `<iframe>`, serangan *MIME-type sniffing*, kebocoran data navigasi via header `Referer`, dan mempermudah pemetaan versi (*fingerprinting*). | 1. Samarkan atau hapus banner header `Server`.<br>2. Konfigurasikan header keamanan standar: `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, dan `Referrer-Policy: no-referrer`. |

---

## 4. Analisis Matriks Prioritas Risiko

Penentuan prioritas risiko dilakukan dengan mempertimbangkan tingkat keparahan dampak terhadap kerahasiaan (*confidentiality*), integritas (*integrity*), dan ketersediaan (*availability*) data, serta kemudahan celah tersebut untuk dieksploitasi oleh penyerang.

| Prioritas | Temuan Kerentanan | Alasan & Justifikasi Dampak terhadap Aset |
| :---: | :--- | :--- |
| **HIGH** | **Broken Access Control pada `/admin`** | Dampak eksploitasi bersifat destruktif dan masif. Celah ini dapat dieksploitasi seketika tanpa memerlukan hak akses awal (hanya memanggil URL), memungkinkan pihak luar mengakses data akun pengguna dan aset administratif inti tanpa halangan. |
| **HIGH** | **Reflected XSS / Injection pada `/search`** | Dampak tinggi dan mudah direproduksi. Karena cookie sesi pada aplikasi ini belum dilindungi atribut `HttpOnly`, celah eksekusi skrip melalui XSS dapat berujung langsung pada pembajakan akun pengguna (*account takeover*) secara penuh. |
| **MEDIUM** | **Insecure Session Cookie pada `/login`** | Nilai cookie berbasis *plain text* memudahkan manipulasi identitas (*privilege escalation* dari `user=bob` menjadi `user=admin`), namun membutuhkan pengetahuan awal mengenai struktur parameter akun korban. |
| **MEDIUM** | **Information Disclosure pada `/debug`** | Membocorkan data konfigurasi internal yang sensitif. Meski tidak secara langsung merusak data, informasi ini memangkas waktu pengintaian penyerang untuk merancang eksploitasi tahap berikutnya. |
| **LOW** | **Missing HTTP Security Headers & Banner Grabbing pada `/`** | Merupakan kelemahan konfigurasi dasar (*hardening issue*). Tidak memicu kompromi langsung yang berdiri sendiri, melainkan bertindak sebagai faktor pelipat ganda dampak jika celah lain (seperti XSS atau Clickjacking) dieksploitasi. |

---

## 5. Refleksi Praktikum
* **Hal Paling Sulit Saat Menghubungkan Bukti ke Kategori OWASP:**  
  Tantangan paling utama adalah membedakan batasan antara **A01 (Broken Access Control)**, **A05 (Security Misconfiguration)**, dan **A07 (Identification/Authentication Failures)** pada kasus-kasus batas (*edge cases*). Sebagai contoh, ketiadaan atribut pengaman pada header `Set-Cookie` secara teknis merupakan kesalahan konfigurasi header respons (A05), tetapi secara fungsi langsung merusak ketahanan mekanisme manajemen sesi dan identifikasi pengguna (A07). Pembuktian harus selalu dikembalikan kepada **akar penyebab utama (*root cause*)** dan mekanisme kontrol yang seharusnya menggagalkan serangan tersebut.

---

## 6. Exit Ticket & Diskusi Kelas

1. **Sebutkan satu kategori OWASP yang paling mudah diamati dari HTTP response header.**  
   * **Jawaban:** **A05: Security Misconfiguration**. Kategori ini dapat langsung diverifikasi melalui inspeksi pasif pada header HTTP (misalnya kebocoran versi pada header `Server`, ketiadaan `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, atau absennya flag `HttpOnly` dan `Secure` pada header `Set-Cookie`).
2. **Apa perbedaan evidence dan asumsi dalam laporan keamanan?**  
   * **Jawaban:** 
     * **Evidence (Bukti Teknis):** Fakta empiris yang dapat direproduksi (*reproducible*), diverifikasi, dan dicatat secara objektif dari respons sistem nyata (misalnya baris perintah `curl -i`, kode status HTTP `200 OK`, isi header mentah, atau payload yang terpantul pada DOM).
     * **Asumsi:** Dugaan, hipotesis, atau spekulasi penguji tanpa adanya bukti teknis yang menyertainya (misalnya menduga suatu form rentan SQL Injection hanya karena tampilannya sederhana, tanpa melakukan pengujian payload atau melihat pesan error dari backend).
3. **Untuk temuan cookie tanpa `HttpOnly`, dampak dan mitigasinya apa?**  
   * **Dampak:** Cookie dapat dibaca, disalin, dan dimanipulasi oleh skrip JavaScript di sisi klien melalui objek `document.cookie`. Jika aplikasi memiliki kerentanan XSS (*Cross-Site Scripting*), penyerang dapat mengekstrak cookie sesi pengguna dan melakukan pembajakan sesi (*session hijacking*).
   * **Mitigasi:** Tambahkan atribut `HttpOnly` secara eksplisit pada saat server menerbitkan header `Set-Cookie` (misalnya: `Set-Cookie: session_id=xyz; Secure; HttpOnly; SameSite=Strict; Path=/`). Atribut ini memerintahkan peramban untuk memblokir seluruh akses API JavaScript terhadap cookie tersebut.
