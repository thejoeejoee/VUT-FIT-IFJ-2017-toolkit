# Automatické testy kompilátoru jazyka IFJ2017
Repozitář pro sbírku programů v jazyce IFJ17 a jejich předpokládaných výstupů včetně automatického spouštěče a aktuální distribuce intepretu.

## Instalace
Repozitář lze naklonovat standardně pomocí GIT:
```bash
$ git clone https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests.git
```

## Použití
Celá funkce se situována do jednoho skriptu v jazyce `Python`. Pro výchozí funkci je nutno předat cestu ke spustitelnému kompilátoru jazyka `IFJ17` do jazyka `IFJcode17`, tedy například takto:
```bash
$ cd VUT-FIT-IFJ-2017-tests
$ ./test.py ./ifj2017
```
kde `./ifj2017` je cesta ke kompilátoru, tedy například `~/school/fit/ifj/ifj2017`.
Takto spuštěný skript automaticky projde implictině složku `tests` a provede následující sekvenci příkazů (viz struktura testů níže):
1. pomocí předaného kompilátoru spustí kompilaci testovaného kódu v jazyce `IFJ17` do jazyka `IFJcode17`
2. zkontroluje návratovou hodnotu
3. spustí přibalený interpret jazyka `IFJcode17`, kterému volitelně předá na standardní vstup definovaný obsah
4. zkontroluje návratový kód interpretu vůči požadovanému
5. zkontroluje obsah vypsaný na standardní výstup vůči požadovanému
6. výsledky jsou zalogovány

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
Název testu je získán z názvu souboru, v tomto případě se jedná o `01`, popis může být udán jako jednořádkový komentář na začátku souboru `01.code`, resp. souboru definující test.
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
Z vlastností testů je opět povinný pouze `code`, tedy definice kódu pro zpracování. Klíče `info`, `name`, `compiler_exit_code`, `interpreter_exit_code`, `stdin` a `stdout` opět nejsou povinné a jsou doplněný dle výchozích hodnot definovaných ve struktuře testů.

### Logování
Pro každý test spouštěč zaloguje soubor do logovací složku (výchozí `log`) výsledky z testu. Tento soubor obsahuje veškeré dostupné informace o běhu kompilátoru, jeho výstup v jazyce `IFJcode17` i veškeré informace z běhu interpretu.

## Spolupráce
Tímto chceme všechny uživatele tototo repozitáře poprosit o **spolupráci s definicí testů**. Myslíme si, že čím více testovacích jednotek vytvoříme, tím **více** budeme mít **pokrytých stavů kompilátoru** a tím méně nás překvapí hodnocení. 
**Všem zájemcům doporučujeme poslat pull request** ([Jak poslat Pull Request](https://blog.tomasfejfar.cz/jak-udelat-pullrequest/)), je pro nás nejsnažší na integraci do repozitáře, ale nebudeme se zlobit, když nám definice hodíte na Facebook, vytvoříte issue nebo pošlete e-mail. **Děkujeme!**

_Také oceníme, když nám nalezené chyby zareportujete do Github issues, kam nám jistě můžete zapsat i vylepšení, co vás napadla nebo by se vám hodila - určitě se nějak domluvíme._

## Autoři
- Josef Kolář, xkolar71, @thejoeejoee - idea, spouštěč, dokumentace
- Son Hai Nguyen, xnguye16, @SonyPony - JSON definice, konzultace
