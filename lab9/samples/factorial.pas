program factorial(input, output);
var n, result: integer;

function fact(n: integer): integer;
begin
    if n = 0 then fact := 1
    else fact := n * fact(n - 1)
end;

begin
    read(n);
    result := fact(n);
    write(result)
end