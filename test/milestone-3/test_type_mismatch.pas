program TestTypeMismatch;

variabel
  x: integer;
  y: real;
  flag: boolean;

mulai
  x := 10;
  y := 3.14;
  flag := x;
  x := y;
selesai.