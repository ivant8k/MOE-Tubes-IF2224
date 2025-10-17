program BooleanTest;
var
  flag1, flag2: boolean;
  result: boolean;
begin
  flag1 := true;
  flag2 := false;
  result := flag1 and flag2;
  if result then
    writeln('Result is true')
  else
    writeln('Result is false');
end.
