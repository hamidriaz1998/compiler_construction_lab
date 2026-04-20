%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
%}

DIGIT      [0-9]
LETTER     [a-zA-Z]
ID         {LETTER}({LETTER}|{DIGIT})*
INT        {DIGIT}+
REAL       {DIGIT}+"."{DIGIT}+

%%

\n                 ;

"{"[^}]*"}"        ;

":="               { printf("ASSIGNOP\n"); }
".."               { printf("DOTDOT\n"); }
"<="               { printf("LE\n"); }
">="               { printf("GE\n"); }
"<>"               { printf("NE\n"); }

"+"                { printf("PLUS\n"); }
"-"                { printf("MINUS\n"); }
"*"                { printf("MULT\n"); }
"/"                { printf("DIV\n"); }
"="                { printf("EQ\n"); }
"<"                { printf("LT\n"); }
">"                { printf("GT\n"); }

";"                { printf("SEMICOLON\n"); }
","                { printf("COMMA\n"); }
":"                { printf("COLON\n"); }
"."                { printf("DOT\n"); }
"("                { printf("LPAREN\n"); }
")"                { printf("RPAREN\n"); }
"["                { printf("LBRACKET\n"); }
"]"                { printf("RBRACKET\n"); }

{REAL}             { printf("REAL(%s)\n", yytext); }
{INT}              { printf("INTEGER(%s)\n", yytext); }

{ID} {
    char temp[100];
    int i;
    for(i = 0; yytext[i]; i++)
        temp[i] = tolower(yytext[i]);
    temp[i] = '\0';

    if(strcmp(temp,"program")==0) printf("PROGRAM\n");
    else if(strcmp(temp,"var")==0) printf("VAR\n");
    else if(strcmp(temp,"array")==0) printf("ARRAY\n");
    else if(strcmp(temp,"of")==0) printf("OF\n");
    else if(strcmp(temp,"integer")==0) printf("INTEGER_TYPE\n");
    else if(strcmp(temp,"real")==0) printf("REAL_TYPE\n");
    else if(strcmp(temp,"begin")==0) printf("BEGIN\n");
    else if(strcmp(temp,"end")==0) printf("END\n");
    else if(strcmp(temp,"if")==0) printf("IF\n");
    else if(strcmp(temp,"then")==0) printf("THEN\n");
    else if(strcmp(temp,"else")==0) printf("ELSE\n");
    else if(strcmp(temp,"while")==0) printf("WHILE\n");
    else if(strcmp(temp,"do")==0) printf("DO\n");
    else if(strcmp(temp,"not")==0) printf("NOT\n");
    else printf("ID(%s)\n", yytext);
}

.                  { printf("UNKNOWN(%s)\n", yytext); }

%%

int main() {
    yylex();
    return 0;
}

int yywrap() {
    return 1;
}
