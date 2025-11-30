program ErrorVariabel;
konstanta
  PI = 3.14;
variabel
  r: real;

mulai
  r := 10.0;
  
  { ERROR 1: Variabel 'luas' tidak dideklarasikan }
  luas := PI * r * r;
  
  { ERROR 2: Konstanta tidak boleh diubah nilainya }
  PI := 3.14159;
selesai.


