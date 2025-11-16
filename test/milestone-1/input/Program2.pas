program logika;
variabel
  a, b, c: integer;
  ok: boolean;
mulai
  a := 10;
  b := 3;
  c := a bagi b + a mod b - (a - b) * 2;
  ok := (a >= b) dan (b <> 0) atau tidak (a < 0);
  jika ok maka
    c := c + 1
  selain-itu
    c := c - 1;
selesai.