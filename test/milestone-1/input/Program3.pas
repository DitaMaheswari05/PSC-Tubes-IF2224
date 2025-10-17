program arrays;
var
  i: integer;
  arr: array[1..5] of integer;
begin
  for i := 1 to 5 do
    arr[i] := i * i;

  for i := 5 downto 1 do
    arr[i] := arr[i] + 1;

  if arr[1] <= arr[2] then
    arr[3] := arr[1] + arr[2]; 
end.