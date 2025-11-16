# Pascal-S Compiler

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pascal-00599C?style=for-the-badge&logo=pascal&logoColor=white" alt="Pascal" />
  <br/><br/>
  <a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Baloo&size=48&duration=3600&pause=600&color=FFB6C1&center=true&vCenter=true&width=600&lines=Moe+Moe+Kyun~" alt="Typing SVG" />
</div>

## Identitas Kelompok
* **Nama Kelompok:** MoeMoeKyun
* **Kode Kelompok:** MOE
* **Anggota:**
  1. Ivant Samuel Silaban - 13523129
  2. Rafa Abdussalam Danadyaksa - 13523133
  3. Muhamad Nazih Najmudin - 13523144
  4. Anas Ghazi Al Gifari - 13523159
  5. Muhammad Rizain Firdaus - 13523164

## Deskripsi Program

**Pascal-S Compiler** merupakan implementasi *compiler* untuk **subset bahasa Pascal** yang dirancang sebagai bagian dari tugas besar mata kuliah **IF2224 - Teori Bahasa Formal dan Otomata**.

Compiler ini dibangun melalui beberapa tahapan utama sebagai berikut:
### 1. **Lexical Analysis (Lexer)**
Tahap pertama dalam proses kompilasi adalah *lexical analysis*, yaitu proses mengubah *source code* menjadi sekumpulan token yang merepresentasikan elemen dasar bahasa seperti *keyword*, *identifier*, *operator*, *literal*, dan *delimiter*. Pada tahap ini, *lexer* membaca karakter demi karakter dari kode sumber dan mengelompokkannya berdasarkan pola tertentu yang telah ditentukan oleh aturan bahasa Pascal-S untuk memeriksa validitas karakter dan pola dasar dari kode sumber.
### 2. **Syntax Analysis (Parser)**
Setelah *lexer* menghasilkan sekumpulan token, tahap selanjutnya adalah *syntax analysis*, yaitu proses menyusun token-token tersebut menjadi *parse tree* yang merepresentasikan struktur program secara hierarkis berdasarkan aturan *grammar* Pascal-S. Pada tahap ini, *parser* menganalisis urutan token menggunakan *context-free grammar* untuk menentukan apakah bentuk program valid secara sintaks.
### 3. **Semantic Analysis**
### 4. **Intermediate Code Generation**
### 5. **Interpreter**

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, Linux, or macOS

### Python Dependencies
Tidak diperlukan dependensi eksternal. Program ini hanya menggunakan pustaka standar Python.

## Cara Instalasi Program

```bash
git clone https://github.com/ivant8k/MOE-Tubes-IF2224.git
cd MOE-Tubes-IF2224
```

## Cara Penggunaan Program

### Milestone 1 - Lexer

#### Output ke Terminal
```bash
cd src
python lexer.py <source_file.pas>
```

#### Output ke File
```bash
cd src
python lexer.py <source_file.pas> <output_file.txt>
```

#### Contoh Penggunaan
```bash
# Output ke terminal
python lexer.py ../test/milestone-1/input-1.pas

# Output ke file
python lexer.py ../test/milestone-1/input-1.pas ../test/milestone-1/output-1.txt
```

### Milestone 2 - Parser

#### Output ke Terminal
```bash
cd src
python syntax.py <source_file.pas>
```

#### Contoh Penggunaan
```bash
# Output ke terminal
python syntax.py ../test/milestone-2/test_hyphenated.pas
```

## Pembagian Tugas

| Nama Anggota | NIM | Tugas |
| :----------- | :-- | :---- |
| Ivant Samuel Silaban | 13523129 | Mengimplementasikan kelas Lexer pada lexer.py.<br>Membuat logika looping untuk simulasi DFA dan prinsip Longest Match.<br>Mengimplementasikan kelas LexicalError dan logika error handling.<br>Merancang grammar dan struktur parser.<br>Memperbaiki bug yang ditemukan selama development dan mengatasi error pada fungsi-fungsi parsing.<br>Membuat test case untuk parser.<br>Menulis Landasan Teori (BAB I) pada Milestone 2. |
| Rafa Abdussalam Danadyaksa | 13523133 | Merancang Keseluruhan Diagram DFA.<br>Mendefinisikan character classes, keywords, dan operator pada dfa.json.<br>Merancang grammar dan struktur parser.<br>Mengimplementasi Non terminal dan production rule.<br>Membuat test case untuk parser.<br>Melakukan pengujian dan dokumentasi Hasil Pengujian (BAB III) pada Milestone 1 dan 2. |
| Muhamad Nazih Najmudin | 13523144 | Merancang Keseluruhan Diagram DFA.<br>Mendefinisikan character classes, keywords, dan operator pada dfa.json.<br>Merancang grammar dan struktur parser.<br>Mengimplementasi Parse Tree dan fungsi-fungsi parsing.<br>Menentukan strategi error handling.<br>Menulis Perancangan dan Implementasi (BAB II) pada Milestone 1 dan 2. |
| Anas Ghazi Al Gifari | 13523159 | Mendefinisikan character classes, keywords, dan operator pada dfa.json.<br>Merancang grammar dan struktur parser.<br>Membuat test case untuk parser.<br>Menulis Landasan Teori (BAB I) dan Implementasi Algoritma pada Milestone 1.<br>Menulis Landasan Teori (BAB I), Lampiran, dan Referensi pada Milestone 2.<br>Menyusun kerangka konseptual laporan Milestone 2 secara menyeluruh. |
| Muhammad Rizain Firdaus | 13523164 | Mendefinisikan character classes, keywords, dan operator pada dfa.json.<br>Merancang grammar dan struktur parser.<br>Menulis Metodologi pengujian dan Analisis Hasil pada Milestone 1.<br>Menulis Kesimpulan dan Saran (BAB IV). pada Milestone 1 dan 2. |

## Tautan

* [Dokumen Terpusat](https://docs.google.com/document/d/1dzZKVdEjTrXSutzDch2dXB5dbkM6w2DJawScLp4VhYI/edit?tab=t.0#heading=h.gauvvmq6h9pp)
* [Milestone 1](https://docs.google.com/document/d/1w0GmHW5L0gKZQWbgmtJPFmOzlpSWBknNPdugucn4eII/edit?tab=t.0#heading=h.gauvvmq6h9pp)
* [Milestone 2](https://docs.google.com/document/d/1G_pC2dltQ5Q-iQ3xOpmLIl3XWLDcLfodN8jdiaJBA0Q/edit?tab=t.0#heading=h.gauvvmq6h9pp)
