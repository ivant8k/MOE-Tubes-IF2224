program TestDeclarations;
konstanta
  PI = 3.14;
  MAX = 100;
tipe
  TNumbers = larik [1..MAX] dari integer;
variabel
  a, b, c: integer;
  hasil: real;
  flags: boolean;
  data: TNumbers;

fungsi hitung(x: integer): real;
mulai
  hitung := (x * PI) + (x / 2)
selesai;

mulai
  a := 10;
  b := 20;
  c := (a * b) + (100 mod 3) * (5 bagi 2);
  hasil := hitung(c);
  flags := (a > b) atau (tidak (c = 0)) dan (b <> a);
  data[1] := a
selesai.