program TestTipeData;
variabel
  angka: integer;
  pecahan: real;
  hasil: real;

mulai
  angka := 5;
  pecahan := 2.5;
  
  { Valid: Assign Integer ke Real (Implicit Casting) }
  hasil := angka; 
  
  { Valid: Operasi Aritmatika Campuran (Int + Real = Real) }
  hasil := angka + pecahan;
  
  writeln('Hasil = ', hasil);
selesai.