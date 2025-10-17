program comprehensiveTest;
var
myInt, loopCounter: integer;
myReal            : real;
isReady           : boolean;
myInitial         : char;
myArray           : array[1..10] of char;

begin
myInt := (100 mod 3) + (20 * 3) div 2 - 1;
myReal := 123.456 / 2.0E-1;
isReady := true;
myInitial := 'Z';
writeln('--- Starting Loop ---');
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
if loopCounter < 1 then
myArray[1] := 'A';

end.