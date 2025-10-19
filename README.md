# Pascal-S Compiler

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pascal-00599C?style=for-the-badge&logo=pascal&logoColor=white" alt="Pascal" />
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
1. **Lexical Analysis (Lexer)**
   Mengubah *source code* menjadi sekumpulan *token* yang merepresentasikan elemen dasar bahasa seperti *keyword*, *identifier*, *operator*, *literal*, dan *delimiter*. Tahap ini memeriksa validitas karakter dan pola dasar dari kode sumber.
2. **Syntax Analysis (Parser)**
3. **Semantic Analysis**
4. **Intermediate Code Generation**
5. **Interpreter**

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

## Pembagian Tugas

| Nama Anggota | NIM | Tugas |
| :----------- | :-- | :---- |
| Ivant Samuel Silaban | 13523129 | Mengimplementasikan kelas Lexer pada lexer.py.<br>Membuat logika looping untuk simulasi DFA dan prinsip Longest Match.<br>Mengimplementasikan kelas LexicalError dan logika error handling. |
| Rafa Abdussalam Danadyaksa | 13523133 | Merancang Keseluruhan Diagram DFA<br>Mendefinisikan character classes, keywords, dan operator pada dfa.json<br>Melakukan pengujian dan Laporan Hasil Pengujian |
| Muhamad Nazih Najmudin | 13523144 | Merancang Keseluruhan Diagram DFA<br>Mendefinisikan character classes, keywords, dan operator pada dfa.json<br>Menulis Laporan (BAB 2) |
| Anas Ghazi Al Gifari | 13523159 | Mendefinisikan character classes, keywords, dan operator pada dfa.json<br>Menulis Landasan Teori (BAB I)<br>Menulis laporan bagian implementasi algoritma |
| Muhammad Rizain Firdaus | 13523164 | Mendefinisikan character classes, keywords, dan operator pada dfa.json<br>Menulis laporan metodologi pengujian dan analisis hasil<br>Laporan Kesimpulan dan Saran |

## Tautan

Dokumen Terpusat: https://docs.google.com/document/d/1w0GmHW5L0gKZQWbgmtJPFmOzlpSWBknNPdugucn4eII/edit?tab=t.0#heading=h.gauvvmq6h9pp  
Milestone 1: https://docs.google.com/document/d/1w0GmHW5L0gKZQWbgmtJPFmOzlpSWBknNPdugucn4eII/edit?tab=t.0#heading=h.gauvvmq6h9pp