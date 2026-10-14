# Keamanan Aplikasi Web — ITTS

Repositori ini memuat dokumentasi teknis, lembar kerja evaluasi, analisis kode, serta pengujian keamanan aplikasi web berbasis standar industri (**OWASP Top 10**, **DAST**, **SAST**, dan **SCA**). Seluruh modul disusun untuk memenuhi capaian pembelajaran mata kuliah **Keamanan Aplikasi Web (TI215)**, Program Studi Teknologi Informasi, Institut Teknologi Tangerang Selatan.

---

## Informasi Kelompok & Akademik

* **Institusi:** Institut Teknologi Tangerang Selatan (ITTS)
* **Program Studi:** S1 Teknologi Informasi
* **Mata Kuliah:** Keamanan Aplikasi Web (TI215)
* **Dosen Pengampu:** Taufik Iqbal Ramdhani, S.Kom., M.Sc.
* **Anggota Tim / Kelompok:**
  1. Hafiz Hablillah
  2. Farel Eka Saputra

---

## Modul Hands-On

Repositori ini dibagi menjadi direktori utama berdasarkan perkembangan topik praktikum:

| Direktori | Cakupan Topik Utama | Fokus Analisis & Kontrol |
| :--- | :--- | :--- |
| **`Hands-On Week 1`** | **Web Security Fundamentals** | Same-Origin Policy (SOP), isolasi konteks origin (`scheme + host + port`), inspeksi penyimpanan sisi klien (*Client-side Storage*), dan manipulasi DOM. |
| **`Hands-On Week 2`** | **OWASP Top 10 & Risk Mapping** | Pemetaan risiko aplikasi (A01 s.d. A05), observasi header respons HTTP dasar, evaluasi *Broken Access Control*, dan sanitasi *Input Rendering Context*. |
| **`Hands-On Week 3`** | **Framework Security & Hardening** | Implementasi *HTTP Security Headers* (CSP, nosniff, DENY, no-referrer), mitigasi *Reflected XSS* via *context-aware output escaping*, audit kode statis (*SAST manual review*), serta *Dependency Advisory Triage* (*SCA*). |

---

## Metodologi Pengujian Keamanan

Setiap modul praktikum menerapkan pendekatan pengujian keamanan komprehensif:

1. **Dynamic Application Security Testing (DAST):** Melakukan inspeksi terhadap *traffic* HTTP nyata, analisis respons header menggunakan `curl` dan script verifikasi otomatis, serta validasi payload injeksi dinamis.
2. **Static Application Security Testing (SAST):** Melakukan audit manual pada kode sumber untuk mengidentifikasi aliran data dari *Source* (input pengguna) menuju *Sink* (titik eksekusi) serta mengevaluasi kontrol keamanan yang hilang.
3. **Software Composition Analysis (SCA):** Memeriksa dependensi pihak ketiga terhadap database celah kerentanan resmi (*CVE / GitHub Security Advisories*), mengevaluasi *reachability*, serta merencanakan remediasi versi pustaka.
4. **Remediation & Defense-in-Depth:** Menerapkan perbaikan di level aplikasi (*output encoding*) dan konfigurasi lingkungan (*security headers*) untuk membangun proteksi berlapis.

---

## Batasan Etika & Kebijakan Lab

Seluruh pengujian, eksploitasi simulasi, dan observasi kerentanan yang ada pada repositori ini dilakukan secara bertanggung jawab dengan ketentuan:

* **Lingkungan Terisolasi:** Pengujian hanya dijalankan pada server lokal (*localhost / private testbed*).
* **Scope Akademik:** Tidak ada serangan atau pemindaian yang diarahkan ke sistem produksi, domain publik, maupun infrastruktur kampus tanpa otorisasi tertulis.
* **Responsible Defense:** Analisis dilakukan semata-mata untuk tujuan identifikasi risiko dan implementasi pertahanan kode yang aman.
