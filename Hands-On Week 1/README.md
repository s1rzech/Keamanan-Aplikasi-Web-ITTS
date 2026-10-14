# Laporan Praktikum Week 1 — Security Mindset & Fondasi Web

**Mata Kuliah:** Keamanan Aplikasi Web (TI215 / MK15)  
**Institusi:** Institut Teknologi Tangerang Selatan (ITTS)  
**Dosen Pengampu:** Taufik Iqbal Ramdhani, S.Kom., M.Sc.  
**Kelompok / Tim:**
1. Hafiz Hablillah
2. Farel Eka Saputra

**Tanggal:** 14 Oktober 2026  
**Target Pengujian:** `http://localhost:8000` & `http://localhost:8001` (Lingkungan lokal terisolasi)

---

## 1. Tujuan Praktikum
Praktikum ini bertujuan untuk memahami arsitektur web client-server, mengamati lalu lintas HTTP secara langsung menggunakan DevTools dan `curl`, membuktikan batas isolasi data *Same-Origin Policy* (SOP) pada `localStorage`, serta membuktikan bahwa antarmuka pengguna (UI/DOM) di browser bukanlah batas keamanan (*security boundary*).

---

## 2. Environment Pengujian
* **Sistem Operasi:** Windows 11
* **Web Server:** Python HTTP Server (`py -m http.server`)
* **Port yang Digunakan:** Port 8000 (Origin A) dan Port 8001 (Origin B)
* **Klien Pengujian:** Google Chrome DevTools & Windows Terminal `curl`
* **Target Host:** `localhost` dan `127.0.0.1`

---

## 3. Ringkasan Langkah Praktikum
1. Menjalankan server HTTP lokal di port 8000 dan mengamati daur hidup request/response serta header HTTP via browser DevTools (Network tab).
2. Melakukan request langsung tanpa browser menggunakan `curl -i http://localhost:8000/` untuk membandingkan representasi data mentah.
3. Mengisi data pada `localStorage` di origin `http://localhost:8000`, lalu membuktikan kegagalan akses (menghasilkan `null`) saat diakses dari port berbeda (`:8001`) dan host berbeda (`127.0.0.1`).
4. Memanipulasi atribut elemen input form (`disabled = false` dan merubah nilai `role` menjadi `admin`) melalui Console JavaScript untuk melakukan *client-side authorization bypass*.

---

## 4. Hasil Pengujian & Artefak Bukti (Evidence)

| No | Komponen Uji | File Bukti | Deskripsi Hasil Pengamatan |
| :---: | :--- | :--- | :--- |
| **1** | Observasi HTTP DevTools | `01-network.png` | Teramati request method `GET`, HTTP status code `200 OK`, dan response header `Content-Type: text/html`. |
| **2** | Inspeksi Raw via `curl` | `02-curl.png` | Resource HTML berhasil ditarik langsung lewat terminal tanpa antarmuka browser, membuktikan request dapat dibentuk secara independen. |
| **3** | Isolasi Origin (SOP) | `03-origin.png` | Key `username` dan `role` bernilai valid di `localhost:8000`, namun bernilai `null` saat diakses via `127.0.0.1:8000` dan `localhost:8001`. |
| **4** | Manipulasi DOM & State | `04-dom.png` | Atribut `disabled` pada form berhasil dimatikan via Console dan nilai berhasil diubah menjadi `admin`, memicu pop-up alert `Role: admin`. |

---

## 5. Lembar Jawaban & Analisis Keamanan (Q1 – Q6)

### Q1. Mengapa origin B (localhost:8001) tidak dapat melihat localStorage origin A (localhost:8000)?
**Jawaban:**
Peramban (*browser*) menerapkan mekanisme keamanan **Same-Origin Policy (SOP)**. Sebuah origin didefinisikan secara mutlak oleh kombinasi tiga elemen: **`scheme` + `host` + `port`**. Meskipun *scheme* (`http`) dan *host* (`localhost`) bernilai sama, *port* keduanya berbeda (`8000` vs `8001`). Karena salah satu komponen penentu origin berbeda, browser mempartisi dan mengisolasi ruang penyimpanan `localStorage` ke dalam *sandbox* terpisah demi mencegah situs web lain mencuri data sesi atau kredensial lokal.

### Q2. Mengapa origin C (127.0.0.1:8000) juga dianggap berbeda dari localhost:8000?
**Jawaban:**
Meskipun secara jaringan `localhost` dan `127.0.0.1` merujuk ke mesin fisik (*loopback address*) yang sama, mekanisme evaluasi SOP pada browser bekerja berbasis **pencocokan string DNS/nama host secara literal (*string-based matching*)**, bukan berdasarkan resolusi IP jaringan. Karena string `'localhost'` secara tekstual tidak identik dengan string `'127.0.0.1'`, browser memperlakukan keduanya sebagai dua origin yang sepenuhnya berbeda dan saling terisolasi.

### Q3. Apa bukti dari praktikum bahwa UI browser tidak boleh dijadikan security boundary?
**Jawaban:**
Buktinya ditunjukkan pada Step 6 (Evidence #4). Elemen `<input id="role">` awalnya dikunci dengan atribut `disabled` agar pengguna tidak bisa mengubah nilai `student`. Namun, melalui Console DevTools di browser, pengguna dapat dengan mudah menjalankan skrip JavaScript untuk mengubah properti DOM (`role.disabled = false; role.value = 'admin'`). Hal ini membuktikan bahwa kontrol antarmuka di peramban berada di bawah kendali penuh pengguna (*attacker-controlled environment*) dan hanya berfungsi untuk kenyamanan visual (*usability/UX*), bukan mekanisme penegakan keamanan (*security boundary*).

### Q4. Sebutkan minimal 5 bagian request/data yang dapat dikontrol client.
**Jawaban:**
1. **HTTP Request Headers:** Klien bebas menambah, memodifikasi, atau menghapus header (misal: `User-Agent`, `Referer`, `Cookie`, atau custom header seperti `X-Role: admin`).
2. **Query Parameters / URL:** Seluruh teks parameter URL yang dikirim via metode GET (misal: `?role=admin&debug=true`).
3. **Request Body / Form Data:** Isi payload yang dikirim via metode POST, PUT, atau PATCH, baik berupa format *form-urlencoded*, *multipart*, maupun *raw JSON*.
4. **HTTP Request Method:** Klien dapat memilih sembarang verb HTTP (seperti `GET`, `POST`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`, `TRACE`).
5. **State Penyimpanan Sisi Klien (*Client-Side Storage*):** Seluruh data yang disimpan pada `localStorage`, `sessionStorage`, `IndexedDB`, serta nilai *cookie* yang tidak dilindungi atribut `HttpOnly`.

### Q5. Jika aplikasi menyimpan role pengguna di localStorage, kontrol apa yang tetap harus dilakukan server?
**Jawaban:**
Server **tidak boleh mempercayai klaim role** yang dikirimkan oleh browser/klien. Kontrol yang wajib ditegakkan di sisi server mencakup:
* **Autentikasi Terverifikasi Kriptografis:** Menggunakan sesi di sisi server (*server-side session store*) atau token yang ditandatangani secara kriptografis (*signed JWT*) dengan kunci rahasia yang hanya diketahui oleh server.
* **Otorisasi Independen di Setiap Endpoint:** Setiap kali request masuk, server wajib memeriksa ulang database/hak akses akun pengguna berdasarkan identitas sesi yang valid sebelum mengeksekusi aksi sensitif, bukan berdasarkan parameter role yang dikirimkan klien.
* **Prinsip Least Privilege:** Akses ditolak secara default (*deny-by-default*) kecuali telah terbukti memiliki hak otorisasi yang sah di sisi backend.

### Q6. Apa perbedaan validation untuk usability dan validation untuk security?
**Jawaban:**
* **Validation for Usability (Client-Side):**
  * *Tujuan:* Meningkatkan kenyamanan pengguna (*User Experience*), seperti memberi tahu format email salah secara instan, mencegah salah ketik, atau mencegah form dikirim kosong sebelum memakan kuota bandwidth.
  * *Karakteristik:* Dijalankan di browser menggunakan HTML5 validation atau JavaScript. Sangat mudah dilewati (*bypass*) oleh penyerang dengan mematikan JS, mengubah DOM, atau menembak request langsung menggunakan `curl`/Postman.
* **Validation for Security (Server-Side):**
  * *Tujuan:* Melindungi integritas data, logika bisnis, dan keamanan infrastruktur dari serangan berbahaya (seperti SQL Injection, Command Injection, atau Parameter Tampering).
  * *Karakteristik:* Dijalankan secara independen di sisi server/backend. Validasi ini bersifat mutlak (*mandatory*) karena server harus mengasumsikan seluruh data yang datang dari klien berpotensi membahayakan dan tidak tepercaya (*untrusted input*).

---

## 6. Kesimpulan
1. **Client is Not Trusted:** Antarmuka browser dan kode JavaScript di sisi klien berada di bawah kendali penuh pengguna. Kontrol keamanan tidak boleh diserahkan ke sisi browser.
2. **Isolasi Same-Origin Policy (SOP):** Browser melindungi data lokal (`localStorage`) dengan mengisolasinya berdasarkan kombinasi presisi `scheme + host + port`.
3. **HTTP Client Observability:** Klien dapat mengirimkan request secara terprogram melalui terminal (`curl`) tanpa melewati logika UI browser.
4. **Backend as the True Security Boundary:** Seluruh proses autentikasi, validasi data, dan penegakan hak akses otorisasi wajib dilakukan dan divalidasi ulang secara independen di sisi server.

---

## 7. Troubleshooting & Solusi
* **Kendala 1:** Perintah `python -m http.server 8000` gagal berjalan dan memunculkan notifikasi Microsoft Store.
  * *Solusi:* Menggunakan perintah launcher bawaan Windows `py -m http.server 8000` (atau alternatif `npx serve -l 8000`).
* **Kendala 2:** DevTools Network menampilkan status HTTP `304 Not Modified` akibat mekanisme caching lokal.
  * *Solusi:* Mencentang opsi *Disable cache* pada panel Network DevTools dan menjalankan *hard reload* (`Ctrl + F5`) untuk mendapatkan status `200 OK`.
