# Sada nástrojů pro `IFJ17` a `IFJcode17`

[![PyPI version](https://badge.fury.io/py/IFJcode17-toolkit.svg)](https://badge.fury.io/py/IFJcode17-toolkit)
[![GitHub issues](https://img.shields.io/github/issues/thejoeejoee/VUT-FIT-IFJ-2017-toolkit.svg)](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/issues)
[![GitHub stars](https://img.shields.io/github/stars/thejoeejoee/VUT-FIT-IFJ-2017-toolkit.svg)](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/stargazers)
[![GitHub license](https://img.shields.io/github/license/thejoeejoee/VUT-FIT-IFJ-2017-toolkit.svg)](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/thejoeejoee/VUT-FIT-IFJ-2017-toolkit.svg)](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/releases)
[![Join the chat at https://gitter.im/VUT-FIT-IFJ-2017-toolkit/Lobby](https://badges.gitter.im/VUT-FIT-IFJ-2017-toolkit/Lobby.svg)](https://gitter.im/VUT-FIT-IFJ-2017-toolkit/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Wiki](https://img.shields.io/badge/Wiki-here-blue.svg)](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/wiki)

Repozitář obsahuje nástroje k projektu kompilátoru do předmětu **IFJ** na FIT VUT v Brně v _akademickém roce 2017/2018_. Mezi nástroje patří **sada testů** včetně automatické spouštěče testových jednotek, **vývojové prostředí včetně debuggeru** jazyka `IFJcode17` a **vlastní interpret** tohoto jazyka.
Instalace těchto balíků je podrobně popsána ve Wiki, obecně je lze **nainstalovat** následovně:

```bash
$ pip install IFJcode17-toolkit
```
**Dokumentaci k nástrojům naleznete na [Github Wiki](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests/wiki).**

**Pro řešení chyb, definice testů či komunikaci mezi týmy můžete využít [Gitter místnost](https://gitter.im/VUT-FIT-IFJ-2017-toolkit/Lobby).**

## IDE
Spouštění vývojového prostředí provedete po nainstalování pomocí příkazu `ifjcode17-ide`, níže náhled jeho rozhraní při spuštěném debuggeru. Více informací o jeho funkci naleznete ve [wiki](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/wiki/V%C3%BDvojov%C3%A9-prost%C5%99ed%C3%AD-pro-IFJcode17).

[![náhled IDE](https://ctrlv.cz/shots/2017/11/16/axPA.png)](https://ctrlv.cz/shots/2017/11/16/axPA.png)

## Automatické testy
Toolkit obsahu sadu více než 200 testovacích jednotek předkládaných vašemu kompilátoru. Jejich automatické spuštění provedete pomocí příkazu `ifjcode17-tests <cesta k vašemu kompilátoru>`. Veškeré další informace naleznete ve [wiki](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/wiki/Automatick%C3%A9-testy).

[![náhled do testů](https://ctrlv.cz/shots/2017/11/16/yVIi.png)](https://ctrlv.cz/shots/2017/11/16/yVIi.png)

## Spolupráce
Tímto chceme všechny uživatele tototo repozitáře poprosit o **spolupráci s definicí testů** či jinou, jak uvážíte. Myslíme si, že čím více testovacích jednotek vytvoříme, tím **více** budeme mít **pokrytých stavů kompilátoru** a tím méně nás překvapí hodnocení. 
**Všem zájemcům doporučujeme poslat pull request** ([Jak poslat Pull Request](https://blog.tomasfejfar.cz/jak-udelat-pullrequest/)), je pro nás nejsnažší na integraci do repozitáře, ale nebudeme se zlobit, když nám definice hodíte na Facebook, vytvoříte issue nebo pošlete e-mail. **Děkujeme!**

_Také oceníme, když nám nalezené chyby zareportujete do Github issues, kam nám jistě můžete zapsat i vylepšení, co vás napadla nebo by se vám hodila - určitě se nějak domluvíme._

![Buď jako Iva!](https://ctrlv.cz/shots/2017/11/16/HfU0.png)

![Nebuď jako rohlík!](https://ctrlv.cz/shots/2017/11/16/cNpu.png)

![Pomožte!](https://ctrlv.cz/shots/2017/10/10/KP3O.png)

## Changelog
* 20-11-2017 - changelog nyní veden standardně v [releases na GitHub](https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit/releases)
* 16-11-2017 - publikace `1.1` oprava chyb v IDE a přidání značek do scrollbaru IDE
* 15-11-2017 - publikace `1.0` na PyPi pod názvem `IFJcode17-toolkit`
* 09-11-2017 - uživatelské testování a ladění IFJcode17 IDE, příprava release
* 08-11-2017 - kompletní testy pro `UNARY, SCOPE, BOOLOP, BASE`, testy na chyby zmíněné na přednáškách/democviku, celkem asi 180 testů
* 31-10-2017 - další várka testů, ~140 testů včetně testů některých rozšíření
* 26-10-2017 - možnost spouštění testů dle implementovaných rozšíření
* 24-10-2017 - drobné úpravy v logování, celkové agregace úspěšnosti
* 22-10-2017 - přidána další sada testů, ~90 testů
* 18-10-2017 - zveřejněno, průběžně základní sada ~60 testů

## Autoři
- [Josef Kolář](https://www.facebook.com/kolar.joe), xkolar71, [@thejoeejoee](https://github.com/thejoeejoee) - automatické testy, interpret
- [Son Hai Nguyen](https://www.facebook.com/sony.nguyen.98), xnguye16, [@SonyPony](https://github.com/SonyPony) - vývojové prostředí, debugger
- [Martin Kobelka](https://www.facebook.com/martin.kobelka), xkobel02, [@martinkobelka](https://github.com/martinkobelka) - definice testů
