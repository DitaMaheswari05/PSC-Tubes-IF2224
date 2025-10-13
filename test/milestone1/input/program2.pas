program MathLogic;
var
  a, b, c: integer;
  ok: boolean;
begin
  a := 10;
  b := 3;
  c := a div b + a mod b - (a - b) * 2;
  ok := (a >= b) and (b <> 0) or not (a < 0);
  if ok then
    c := c + 1
  else
    c := c - 1;
end.
