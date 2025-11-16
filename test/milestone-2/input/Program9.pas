program TestRepeat;
variabel
    i, sum: integer;
mulai
    i := 1;
    sum := 0;
    ulangi
        sum := sum + i;
        i := i + 1;
    sampai i > 10;
    writeln('Sum = ', sum);
selesai.