program ControlLoops;
var
  x: integer;
begin
  x := 0;
  while x <= 10 do
  begin
    if x = 5 then
      x := x + 2
    else
      x := x + 1;
  end;
end.
