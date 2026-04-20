program power(input, output);
var base, exp, result: integer;

function pow(base, exp: integer): integer;
begin
    if exp = 0 then pow := 1
    else pow := base * pow(base, exp - 1)
end;

begin
    read(base, exp);
    result := pow(base, exp);
    write(result)
end