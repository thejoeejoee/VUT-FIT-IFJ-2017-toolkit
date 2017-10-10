# Automatické testy kompilátoru jazyka IFJ2017
Repozitář pro sbírku programů v jazyce IFJ17 a jejich předpokládaných výstupů včetně automatického spouštěče a aktuální distribuce intepretu.

## Instalace
Spouštěč je schopen provozu na architektuře **Linux nebo Windows**, požadována je **64-bit architektura** (interpret není zadávajícími dodávána jiná architektura). Jediná závislost je interpret jazyka **`Python` ve verzi `3.4` nebo vyšší**.

Spouštěč lze nainstalovat pomocí standardního nástroje `git`
```bash
$ git clone https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests.git
$ python3 --version
```

## Použití
Celá funkce se situována do jednoho skriptu v jazyce `Python`. Pro výchozí funkci je nutno předat cestu ke spustitelnému kompilátoru jazyka `IFJ17` do jazyka `IFJcode17`, tedy například takto:
```bash
$ cd VUT-FIT-IFJ-2017-tests
$ python3 test.py ./ifj2017
```
kde `./ifj2017` je cesta ke kompilátoru, tedy například `~/school/fit/ifj/ifj2017`.
Takto spuštěný skript automaticky projde implictině složku `tests` a provede následující sekvenci příkazů (viz struktura testů níže):
1. pomocí předaného kompilátoru spustí kompilaci testovaného kódu v jazyce `IFJ17` do jazyka `IFJcode17`
2. zkontroluje návratovou hodnotu
3. v případě, že je navrácená nebo očekávaná hodnota kompilátoru nenulová, je běh testu ukončen
4. spustí přibalený interpret jazyka `IFJcode17`, kterému volitelně předá na standardní vstup definovaný obsah
5. zkontroluje návratový kód interpretu vůči požadovanému
6. v případě, že je navrácená nebo očekávaná hodnota interpretu nenulová, je běh testu ukončen
7. zkontroluje obsah vypsaný na standardní výstup vůči požadovanému

Ve všech případech jsou očekávané hodnoty i jejich reálné protějšky zalogovány.

Výsledek spuštění tedy poté může vypadat nějak takto:
![screenshot](https://ctrlv.cz/shots/2017/10/10/zmdz.png)

## Struktura testů
Testy jsou rozděleny do sekcí dle složkového rozdělení v hlavní složce testů - sekce oddělují jednotlivé obsahy a náročnosti testů:
```
tests
    ├── 001_basic
    └── 002_flow_controls
```
Každý test obsahuje následující data:
* kód v jazyce `IFJ17`
* název _volitelně_
* popis _volitelně_
* očekávaný návratový kód kompilátoru _volitelně_, výchozí `0`
* očekávaný návratový kód interpretu _volitelně_, výchozí `0`
* očekávaný standardní výstup z běhu _volitelně_, výchozí prázdný

## Definice testů
Testové jednotky lze definovat dvěma způsoby.
### Definice pro souborech
Jedná se o definici, při které jsou jednotlivé položky testovací jednotky uloženy jako soubory se shodným názvem:
```
tests/001_basic/
├── 01.code # kód ke zpracování
├── 01.cexitcode # očekávaný návratový kód kompilátoru
├── 01.iexitcode # očekávaný návratový kód interpretu
├── 01.stdin # standardní vstup předaný pro běh programu
├── 01.stdout # očekávaný standardní výstup běhu programu
|
└── 02_foo.code # další testová jednotka
```
Název testu je získán z názvu souboru, v tomto případě se jedná o `01`, popis může být udán jako jednořádkový komentář na začátku souboru `01.code`, resp. souboru definující test. Tento způsob slouží především pro složitější a komplexnější testy s předem očekávaným neprázdným výstupem.
### Definice pomocí JSON
Každá testovací sekce může také obsahovat soubor s pevným názvem `tests.json`. Ten definuje testové jednotky velmi obdobným systémem, avšak agregovaně:
```json
{
  "tests": [
    {
      "info": "empty scope",
      "code": "scope \n end scope",
      "stdout": ""
    },
    {
      "name": "syntax error",
      "code": "scope \n end scoppe",
      "stdin": "foobar",
      "compiler_exit_code": 2
    },
    {
      "info": "syntax error as scoppe",
      "code": "scope \n dim a as string \n dim a as integer \n end scope",
      "interpreter_exit_code": 3
    }
  ]
}
```
Z vlastností testů je opět povinný pouze `code`, tedy definice kódu pro zpracování. Klíče `info`, `name`, `compiler_exit_code`, `interpreter_exit_code`, `stdin` a `stdout` opět nejsou povinné a jsou doplněný dle výchozích hodnot definovaných ve struktuře testů. Pomocí JSON nejčastěji definujeme testy, které ověřují správné návratové kódy kompilátoru, ale jednoduché konstrukce, např. `PRINT` lze testovat s přehledem také.

### Logování
Pro každý test spouštěč zaloguje soubor do logovací složku (výchozí `log`) výsledky z testu. Tento soubor obsahuje veškeré dostupné informace o běhu kompilátoru, jeho výstup v jazyce `IFJcode17` i veškeré informace z běhu interpretu. Soubor logu jako takový je validní zdrojový kód jazyka `IFJcode17`, lze jej tedy přidat interpretu přímo (při standardní běhu je interpretu předáno pouze to, co reálně vypíše kompilátor). Struktura zalogovaných informací je následující, myslíme, že ji není třeba dodatečně popisovat: 
```
# TEST: 01
# INFO: Basic test for scope without any statements.
# INTERPRETER STDIN: 
# 
# 
# COMPILER STDERR:
# 
# INTERPRETER STDERR:
# Executing instruction: IJUMP at line: 2 with following arguments:
# Executing instruction: ILABEL at line: 3 with following arguments:
# 
#
# EXPECTED INTERPRETER STDOUT:
# 
# CURRENT INTERPRETER STDOUT:
# 
#
# EXPECTED COMPILER EXIT CODE: 0
# CURRENT COMPILER EXIT CODE: 0
# EXPECTED INTERPRETER EXIT CODE: 0
# CURRENT INTERPRETER EXIT CODE: 0
# 
# ' Basic test for scope without any statements.
# SCOPE
# END SCOPE

# # # # # # # # # # # # # # # # # # # # 

.IFJcode17
CALL scope  
LABEL scope  
```

### Konfigurace spouštění
Spouštěč testů lze dále také konfigurovat pomocí příkazové řádky, viz nápověda po zadání argumentu `-h`:
```bash
./test.py -h 
usage: test.py [-h] [-i INTERPRETER] [-d TESTS_DIR] [-l LOG_DIR]
               [--command-timeout COMMAND_TIMEOUT]
               compiler

Automatic test cases runner for IFJ17 compiler.

positional arguments:
  compiler              path to IFJ17 compiler binary

optional arguments:
  -h, --help            show this help message and exit
  -i INTERPRETER, --interpreter INTERPRETER
                        path to IFJ17 interpreter binary
  -d TESTS_DIR, --tests-dir TESTS_DIR
                        path to folder with tests to run
  -l LOG_DIR, --log-dir LOG_DIR
                        path to folder with logs
  --command-timeout COMMAND_TIMEOUT
                        maximal timeout for compiler and interpreter

Authors: Josef Kolář (xkolar71, @thejoeejoee), Son Hai Nguyen (xnguye16,
@SonyPony), GNU GPL v3, 2017
```


## Spolupráce
Tímto chceme všechny uživatele tototo repozitáře poprosit o **spolupráci s definicí testů**. Myslíme si, že čím více testovacích jednotek vytvoříme, tím **více** budeme mít **pokrytých stavů kompilátoru** a tím méně nás překvapí hodnocení. 
**Všem zájemcům doporučujeme poslat pull request** ([Jak poslat Pull Request](https://blog.tomasfejfar.cz/jak-udelat-pullrequest/)), je pro nás nejsnažší na integraci do repozitáře, ale nebudeme se zlobit, když nám definice hodíte na Facebook, vytvoříte issue nebo pošlete e-mail. **Děkujeme!**

_Také oceníme, když nám nalezené chyby zareportujete do Github issues, kam nám jistě můžete zapsat i vylepšení, co vás napadla nebo by se vám hodila - určitě se nějak domluvíme._

![Pomožte!](https://ctrlv.cz/shots/2017/10/10/KP3O.png)

## Autoři
- Josef Kolář, xkolar71, @thejoeejoee - idea, spouštěč, dokumentace
- Son Hai Nguyen, xnguye16, @SonyPony - JSON definice, konzultace
