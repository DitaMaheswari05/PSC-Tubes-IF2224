program TestScope;
variabel
  x, y: integer;

prosedur cekLokal;
variabel
  x: boolean; { Shadowing: x lokal menutupi x global }
mulai
  x := true;
  jika x maka
    writeln('Ini x lokal (boolean)');
selesai;

mulai
  x := 10; { Ini akses x global }
  cekLokal();
  y := x + 5;
  writeln(y);
selesai.