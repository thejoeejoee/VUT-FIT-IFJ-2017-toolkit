# Toolkit k `IFJ2017` a `IFJcode17`
Repozitář nástrojů k projektu kompilátoru do předmětu **IFJ** na FIT VUT v Brně. Mezi nástroje patří **sada testů** včetně autmatického spouštěče jednotek, **vývojové prostředí včetně debuggeru** jazyka `IFJcode17` a **vlastní interpret** tohoto jazyka.
Instalace těchto balíků je podrobně popsána ve Wiki, obecně je lze **nainstalovat** následovně:

```bash
pip3 install IFJcode17-toolkit
```

**[Dokumentaci k nástrojům naleznete zde.](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/wiki)**

[![screenshot](https://ctrlv.cz/shots/2017/10/15/A6RL.png)](https://ctrlv.cz/shots/2017/10/15/A6RL.png)

## Spolupráce
Tímto chceme všechny uživatele tototo repozitáře poprosit o **spolupráci s definicí testů** či jinou, jak uvážíte. Myslíme si, že čím více testovacích jednotek vytvoříme, tím **více** budeme mít **pokrytých stavů kompilátoru** a tím méně nás překvapí hodnocení. 
**Všem zájemcům doporučujeme poslat pull request** ([Jak poslat Pull Request](https://blog.tomasfejfar.cz/jak-udelat-pullrequest/)), je pro nás nejsnažší na integraci do repozitáře, ale nebudeme se zlobit, když nám definice hodíte na Facebook, vytvoříte issue nebo pošlete e-mail. **Děkujeme!**

_Také oceníme, když nám nalezené chyby zareportujete do Github issues, kam nám jistě můžete zapsat i vylepšení, co vás napadla nebo by se vám hodila - určitě se nějak domluvíme._

![Pomožte!](https://ctrlv.cz/shots/2017/10/10/KP3O.png)

## Changelog
* 15-11-2017 - publikace `1.0` na PyPi pod názvem `IFJcode17-toolkit`
* 09-11-2017 - uživatelské testování a ladění IFJcode17 IDE, příprava release
* 08-11-2017 - kompletní testy pro `UNARY, SCOPE, BOOLOP, BASE`, testy na chyby zmíněné na přednáškách/democviku, celkem asi 180 testů
* 31-10-2017 - další várka testů, ~140 testů včetně testů některých rozšíření
* 26-10-2017 - možnost spouštění testů dle implementovaných rozšíření
* 24-10-2017 - drobné úpravy v logování, celkové agregace úspěšnosti
* 22-10-2017 - přidána další sada testů, ~90 testů
* 18-10-2017 - zveřejněno, průběžně základní sada ~60 testů

## Autoři
- [Josef Kolář](https://www.facebook.com/kolar.joe), xkolar71, [@thejoeejoee](https://github.com/thejoeejoee) - idea, spouštěč, hodnotící interpret, Wiki
- [Son Hai Nguyen](https://www.facebook.com/sony.nguyen.98), xnguye16, [@SonyPony](https://github.com/SonyPony) - JSON definice, konzultace
- [Martin Kobelka](https://www.facebook.com/martin.kobelka), xkobel02, [@martinkobelka](https://github.com/martinkobelka) - definice testů
