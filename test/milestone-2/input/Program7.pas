program TestProcedure;
variabel
    x: integer;

prosedur printNumber(n: integer);
mulai
    writeln('Number is: ', n);
selesai;

mulai
    x := 42;
    printNumber(x);
selesai.