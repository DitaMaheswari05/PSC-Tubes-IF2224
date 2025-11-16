program TestArray;
variabel
    numbers: larik[1..10] dari integer;
    i: integer;
mulai
    untuk i := 1 ke 10 lakukan
        numbers := i * 2;
    writeln('Done');
selesai.