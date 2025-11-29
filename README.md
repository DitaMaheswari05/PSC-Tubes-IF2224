# PASCAL-S Compiler — Milestone 3: Semantic Analysis

## Deskripsi
Milestone ini merupakan bagian ketiga dari Tugas Besar IF2224 Teori Bahasa Formal dan Otomata (TBFO), dengan fokus pada **Semantic Analysis** untuk Pascal-S Compiler.  
Tahap ini memastikan bahwa program hasil parsing **valid secara semantik** dengan melakukan:

- Type Checking  
- Scope Checking  
- Validasi deklarasi variabel, konstanta, prosedur, dan fungsi  
- Validasi operasi aritmetika, logika, relasional, dan assignment  
- Validasi parameter prosedur/fungsi  
- Validasi akses array  
- Build **Decorated AST**  
- Build **Symbol Table** (`tab`, `btab`, `atab`)  

Semantic Analyzer menggunakan pendekatan **L-Attributed Grammar** dan **Visitor Pattern** untuk melakukan traversal parse tree secara top-down.

---

## Requirements

### Bahasa dan Tools
- Python
- Library bawaan Python (enum, typing, dataclasses, dll.)

### Input
- File pascal-S (.pas)

### Output
- Decorated AST (AST dengan anotasi tipe & symbol reference)
- Symbol Table lengkap
- Informasi kesalahan semantik
- Disimpan dalam path milestone-3/output

---

## Penjelasan Class

### `SemanticAnalyzer.py` -> Main
Entry point utama proses semantic analysis.  
Mengatur:
- inisialisasi symbol table  
- pemanggilan visitor  
- penggabungan hasil annotate AST  
- pengecekan error utama  

### **Decorated AST**
Folder `DecoratedAST/` berisi struktur node AST yang telah diberi anotasi:
- tipe data  
- referensi ke symbol table  
- scope level  
- informasi tambahan semantik lainnya  

### **Symbol Table**
Implementasi tiga tabel Pascal-S:
- `tab` — identifier (konstanta, variabel, prosedur, fungsi, tipe)
- `btab` — block table (informasi block, parameter, variabel lokal)
- `atab` — array table (batas, elemen, tipe indeks)

### **Visitor**
Folder `Visitor/` berisi visitor yang menangani tiap kategori grammar:
- `DeclarationVisitor`  
- `ExpressionVisitor`  
- `StatementVisitor`  
- `ArrayAccessVisitor`  
- `ProcFuncVisitor`  
- `SemanticAnalyzerBase` (abstract visitor)  
- `SemanticError` (exception khusus semantic error)

---

## Cara Instalasi & Penggunaan

### 1️. Clone Repository
```bash
git clone https://github.com/DitaMaheswari05/PSC-Tubes-IF2224.git
cd PSC-Tubes-IF2224/src
```

### 2️. Jalankan Program
```bash
python run.py -s <path_kode_pascal>
```
**Contoh:**
```bash
python run.py ../test/milestone-3/input/program1.pas
```

### 3️. Format Output
Output Decorated AST dan Symbol Table akan muncul di terminal
Kemudian akan tersimpan dalam bentuk `.txt` pada test/milestone-3/output


## Anggota Kelompok

| NIM | Nama |
|-----|------|
| 13523125 | **Dita Maheswari** |
| 13523127 | **Boye Mangaratua Ginting** |
| 13523138 | **Samantha Laqueenna Ginting** |
| 13523158 | **Lukas Raja Agripa** |

---
