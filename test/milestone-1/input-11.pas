program comprehensiveTest;
{ Comprehensive Test Case for All PASCAL-S Tokens }
var
myInt, loopCounter: integer;
myReal            : real;
isReady           : boolean;
myInitial         : char;
myArray           : array[1..10] of char;

begin
(* Assignment dan semua operator aritmatika *)
myInt := (100 mod 3) + (20 * 3) div 2 - 1;
myReal := 123.456 / 2.0E-1;
isReady := true;
myInitial := 'Z';

(* Contoh string literal dan pemanggilan identifier 'writeln' *)
writeln('--- Starting Loop ---');

(* Loop dengan operator relasional dan logika lengkap *)
if (isReady = true) and (myInt >= 0) then
begin
loopCounter := 10;
while (loopCounter > 0) or (not isReady) do
begin
if (loopCounter <= 5) and (loopCounter <> 3) then
writeln('Looping...')
else
writeln('Still looping...');
loopCounter := loopCounter - 1;
end;
end;

(* Cek kondisi akhir, < digunakan di sini *)
if loopCounter < 1 then
myArray[1] := 'A';

end.