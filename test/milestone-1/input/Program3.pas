program larikprogram;
variabel
  i: integer;
  arr: larik[1..5] dari integer;
mulai
  untuk i := 1 ke 5 lakukan
    arr[i] := i * i;

  untuk i := 5 turun-ke 1 lakukan
    arr[i] := arr[i] + 1;

  jika arr[1] <= arr[2] maka
    arr[3] := arr[1] + arr[2];
selesai.