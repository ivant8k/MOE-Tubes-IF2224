program TestSubprograms;
variabel
  i: integer;

prosedur cetakAngka(angka: integer; batas: integer);
mulai
  selama angka < batas lakukan
  mulai
    angka := angka + 1;
    jika angka = 5 maka
      angka := 6
  selesai
selesai;

mulai
  i := 0;
  cetakAngka(i, 10);

  untuk i := 1 ke 5 lakukan
    i := i
selesai.