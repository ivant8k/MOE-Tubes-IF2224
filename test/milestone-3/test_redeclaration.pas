program TestRedeclaration;

variabel
  x: integer;
  x: real;
  y: integer;

mulai
  x := 67;
  y := x + 2;
  writeln(y);
selesai.