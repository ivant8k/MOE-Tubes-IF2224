program TestConstModification;

konstanta
  PI = 3.14;
  MAX = 100;

variabel
  a, b, c: integer;

mulai
  a := 10;
  b := 20;
  MAX := 200;
  c := (a * b) + (PI * MAX);
  writeln(c);
selesai.