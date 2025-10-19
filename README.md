# PASCAL-S Compiler — Milestone 1: Lexical Analysis

## Deskripsi
Proyek ini merupakan Milestone 1 dari Tugas Besar IF2224 Teori Bahasa Formal dan Otomata (TBFO), dengan fokus pada **Lexical Analysis** untuk *Pascal-S Compiler*.  
Tahap ini bertujuan untuk membangun **Lexical Analyzer (Lexer)** yang menggunakan **Deterministic Finite Automata (DFA)** untuk membaca kode sumber Pascal-S (.pas) dan mengubahnya menjadi **daftar token** yang bermakna seperti *keyword*, *identifier*, *operator*, *literal*, dan *delimiter*.

Lexer membaca source code karakter demi karakter dan mengenali pola menggunakan transisi DFA. Implementasi dilakukan menggunakan **Python**, dengan pembacaan file aturan DFA dalam format **JSON (`dfa.json`)**.

---

## Struktur Proyek

```
PSC-Tubes-IF2224/
│
├── src/
│   ├── main.py
│   ├── run.py
│   ├── model/
│   │   ├── Lexer.py
│   │   ├── Token.py
│   │   ├── DFA.py
│   │   ├── State.py
│   ├── repository/
│   │   ├── Parser.py
│   │   ├── JSONParser.py
│   │   ├── DFAParser.py
│   │   ├── TokenType.py
│   ├── view/
│   │   └── Services.py
│   └── dfa.json
│
├── doc/
│   ├── Laporan-1-PSC.pdf
│   ├── Diagram-1-PSC.pdf
│
├── test/
│   └── milestone-1/
│       ├── input/
│       └── output/
│
└── README.md
```

---

## Requirements

### Python dan Library
- **Python 3.10+**
- Library bawaan Python (`json`, `enum`, `os`, `typing`, dan sebagainya)

### File Input
- Source code Pascal-S (`.pas`)
- File DFA (`dfa.json`), yang berisi definisi state, transisi, start state, dan final state.

### File Output
- Daftar token hasil analisis leksikal, ditampilkan di terminal dan dapat disimpan di file `.txt`.

---

## Cara Instalasi & Penggunaan

### 1️⃣ Clone Repository
```bash
git clone https://github.com/DitaMaheswari05/PSC-Tubes-IF2224.git
cd PSC-Tubes-IF2224/src
```

### 2️⃣ Jalankan Program
```bash
python run.py <path_kode_pascal>
```
**Contoh:**
```bash
python run.py ../test/milestone-1/program1.pas
```

### 3️⃣ Format Output
Output token akan muncul di terminal, dengan format:
```
KEYWORD(program)
IDENTIFIER(Hello)
SEMICOLON(;)
NUMBER(10)
ARITHMETIC_OPERATOR(+)
...
```
Kemudian akan tersimpan dalam bentuk `.txt` pada test/milestone-1/output

---

## Fitur Utama

- **Implementasi DFA dari file eksternal (JSON)**  
  DFA digunakan untuk mengenali setiap token berdasarkan transisi antar state.
- **Mendukung tipe token lengkap** seperti:
  - `KEYWORD`, `IDENTIFIER`, `NUMBER`, `CHAR_LITERAL`, `STRING_LITERAL`
  - `ARITHMETIC_OPERATOR`, `RELATIONAL_OPERATOR`, `LOGICAL_OPERATOR`
  - `ASSIGN_OPERATOR`, `RANGE_OPERATOR`, `DELIMITER`
- **Menangani kasus khusus:**
  - Bilangan negatif → `NUMBER(-0.123E10)`
  - Keyword `true` dan `false`
  - Range `..` dan assignment `:=`
- **Mengabaikan komentar dan whitespace**

---

## Arsitektur Program

Program diimplementasikan secara **modular OOP** dengan komponen utama:

| Komponen | Deskripsi Singkat |
|-----------|------------------|
| `DFA` | Struktur automata dengan kumpulan state dan transisi |
| `State` | Menyimpan status, transisi, dan tipe token akhir |
| `Lexer` | Melakukan pembacaan file sumber dan menghasilkan token |
| `Token` | Representasi setiap unit token dengan tipe dan nilai |
| `Services` | Lapisan antarmuka yang memanggil lexer dan parser |
| `Parser` / `DFAParser` | Membaca dan memetakan struktur JSON DFA ke objek Python |

---


## Identitas & Pembagian Tugas

| NIM | Nama | Pekerjaan |
|-----|------|------------|
| 13523125 | **Dita Maheswari** | DFA rules, lexer (sedikit), laporan |
| 13523127 | **Boye Mangaratua Ginting** | Diagram DFA, laporan |
| 13523138 | **Samantha Laqueenna Ginting** | Diagram DFA, laporan |
| 13523158 | **Lukas Raja Agripa** | Lexer, laporan |

---
