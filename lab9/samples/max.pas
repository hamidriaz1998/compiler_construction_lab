program max(input, output);
var a, b, m: integer;

function maximum(a, b: integer): integer;
begin
    if a > b then maximum := a
    else maximum := b
end;

begin
    read(a, b);
    m := maximum(a, b);
    write(m)
end