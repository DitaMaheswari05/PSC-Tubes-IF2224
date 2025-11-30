program TestFungsiRekursif;
variabel
  hasil: integer;

fungsi faktorial(n: integer) : integer;
mulai
  jika n <= 1 maka
    faktorial := 1
  selain-itu
    faktorial := n * faktorial(n - 1);
selesai;

mulai
  hasil := faktorial(5);
  writeln('Faktorial 5 = ', hasil);
selesai.

