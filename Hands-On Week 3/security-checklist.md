# Week 3 Framework Security Checklist

## Header evidence
- Baseline command: `curl -i http://localhost:3000/` dan `node tools/header_check.js http://localhost:3000/`
- Baseline missing headers: `content-security-policy`, `x-frame-options`, `x-content-type-options`, `referrer-policy` (Risiko kesalahan konfigurasi / Security Misconfiguration)
- Secure command: `curl -i http://localhost:3000/` dan `node tools/header_check.js http://localhost:3000/`
- Secure headers present: `Content-Security-Policy` (`default-src 'self'; base-uri 'none'; frame-ancestors 'none'; object-src 'none'; form-action 'self'`), `X-Frame-Options` (`DENY`), `X-Content-Type-Options` (`nosniff`), `Referrer-Policy` (`no-referrer`), dan `Permissions-Policy` (`geolocation=(), microphone=(), camera=()`)

## Rendering / escaping evidence
- Payload used: `http://localhost:3000/?q=<script>alert(1)</script>`
- Baseline result:Input parameter `q` dirender mentah ke dalam HTML tanpa proses escaping (`<p>Search: <script>alert(1)</script></p>`), sehingga browser mengeksekusi tag `<script>` sebagai kode JavaScript aktif (rentan Reflected XSS).
- Secure result: Karakter khusus HTML berhasil di-escape menjadi entitas HTML (`&lt;script&gt;alert(1)&lt;/script&gt;`), sehingga payload hanya ditampilkan sebagai teks biasa di halaman web (`Search: <script>alert(1)</script>`) dan tidak dieksekusi oleh browser.

## SAST manual review
| File | Source | Sink | Control found | Control missing | Recommendation |
|---|---|---|---|---|---|
| app-baseline.js | `url.searchParams.get('q')` (baris 24, rute `/`) dan `url.searchParams.get('name')` (baris 34, rute `/profile`) | `res.end(page('Baseline App', ...))` (baris 29) dan `res.end(page('Profile', ...))` (baris 36) | Header standar `Content-Type: text/html; charset=utf-8` | Tidak ada fungsi output escaping (`escapeHtml`) dan tidak ada HTTP security headers (`CSP`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`) | Terapkan fungsi `escapeHtml()` pada seluruh input user sebelum masuk ke sink `res.end()`, gunakan template auto-escaping, serta tambahkan HTTP security headers dan validasi ulang dengan `header_check.js` serta uji payload XSS. |
| app-secure.js | `url.searchParams.get('q')` (rute `/`) dan `url.searchParams.get('name')` (rute `/profile`) | `res.end(page('Secure App', ...))` dan `res.end(page('Profile', ...))` | Fungsi `escapeHtml()` pada variabel output serta pemasangan HTTP security headers lengkap (`CSP`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Permissions-Policy`) | Penggunaan middleware terpusat (seperti `helmet`) dan template engine dengan auto-escaping bawaan untuk mencegah kelalaian manual saat kode berkembang | Pertahankan fungsi `escapeHtml()` dan secure headers yang sudah aktif, serta adopsi framework middleware resmi dan template engine otomatis untuk skala produksi. |

## Dependency advisory triage
| Package | Installed version | Severity | Impact | Fix | Priority | Evidence/source |
|---|---|---|---|---|---|---|
| lodash | 4.17.11 | Critical | Command Injection (`GHSA-35jh-r3h4-6jhm`), Code Injection via `_.template` (`GHSA-r5fr-rjxr-66jc`), Prototype Pollution pada `_.unset` & `_.omit` (`GHSA-jf85-cpcp-j695`, `GHSA-p6mc-m468-83gw`, `GHSA-f23m-r3pf-42rh`, `GHSA-xxjr-mmjv-4gpg`), serta ReDoS (`GHSA-29mw-wpgm-hmr9`) | Upgrade ke `lodash@4.18.1` (via update `package.json` atau `npm audit fix --force`) | High (Severity berstatus Critical dan patch `4.18.1` sudah tersedia; meski fungsi `lodash` belum dipanggil/reachable langsung di rute kode saat ini, tetap wajib di-upgrade, diuji potensi breaking change karena di luar dependency range awal, lalu divalidasi ulang dengan `npm audit`) | Output `npm install` dan `npm audit --audit-level=high` (`package.json` & GitHub Advisory) |

## Reflection
1. What did the framework/middleware help automate?
   - Framework dan middleware membantu mengotomatisasi penerapan kontrol keamanan standar secara konsisten di seluruh endpoint, seperti penyematan HTTP security headers (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`), template auto-escaping untuk mencegah XSS, proteksi CSRF token, serta parameterized query pada ORM.
2. What still needs developer judgment?
   - Keputusan kontekstual tetap membutuhkan analisis developer, meliputi perancangan logika otorisasi/kontrol akses bisnis, kedisiplinan untuk tidak mem-bypass proteksi bawaan (menghindari raw HTML sink), penyusunan aturan CSP yang tepat agar tidak merusak fitur sah, serta penentuan prioritas update dependency berdasarkan reachability, ketersediaan patch, dan potensi breaking changes saat versi perbaikan berada di luar rentang deklarasi awal (`outside stated dependency range`).
3. Which control would you implement first in a real production app, and why?
   - Context-aware Output Escaping pada seluruh data input pengguna yang dirender ke halaman web, dikombinasikan dengan pemasangan Secure Headers (khususnya `Content-Security-Policy` dan `X-Content-Type-Options`). Alasannya, output escaping secara langsung menutup akar celah injeksi (Reflected/Stored XSS) pada titik sink kode, sedangkan secure headers memberikan lapis pertahanan tambahan (defense-in-depth) terhadap XSS, Clickjacking, dan MIME sniffing dengan usaha implementasi yang cepat dan berdampak luas.