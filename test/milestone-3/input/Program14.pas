program ErrorTipeData;
variabel
  angka: integer;
  status: boolean;

mulai
  status := true;
  
  { ERROR 1: Tidak bisa assign boolean ke integer }
  angka := status; 
  
  { ERROR 2: Kondisi JIKA harus boolean, tapi ini integer }
  jika angka maka 
    writeln('Ini salah');
selesai.

