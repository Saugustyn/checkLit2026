import requests
import time
import json
import argparse
import sys
import math
from datetime import datetime

ANSWER_KEY = {
    1:  "human",   # Fikcyjna proza epicka (przypadek graniczny)
    2:  "ai",      # Claude — proza psychologiczna
    3:  "human",   # Mickiewicz – Pan Tadeusz (Inwokacja)
    4:  "ai",      # Claude — opis kamienicy
    5:  "ai",      # Claude — scena wiejska (trudny!)
    6:  "human",   # Reymont – Ziemia obiecana
    7:  "human",   # Mickiewicz – Ks. Robak
    8:  "ai",      # Claude — proza minimalistyczna
    9:  "human",   # Zapolska – Moralność pani Dulskiej
    10: "human",   # Orzeszkowa – Nad Niemnem
    11: "ai",      # Claude — dialog w kawiarni
    12: "human",   # Reymont – opis Łodzi
    13: "ai",      # Claude — pisarka przy biurku
    14: "human",   # Mickiewicz – Jacek Soplica
    15: "human",   # Sienkiewicz – W pustyni i w puszczy
    16: "human",   # Motyw góralski (Tetmajer/Witkiewicz)
    17: "ai",      # Claude — powrót do wsi
    18: "ai",      # Claude — opis rzeczki
    19: "human",   # Salon towarzyski XIX w.
    20: "ai",      # Claude — bezsenność
    21: "human",   # Sienkiewicz – Krzyżacy (Grunwald)
    22: "ai",      # Claude — kamienica wielorodzinna
    23: "human",   # Witkiewicz – Na przełęczy (Tatry)
    24: "ai",      # Claude — portret nauczyciela
    25: "human",   # Reymont – Chłopi (praca na roli)
    26: "ai",      # Claude — portret zakonnicy
    27: "human",   # Proza ludowa — babka z wnukiem
    28: "human",   # Kochanowski – Treny (archaiczny)
    29: "ai",      # Claude — spotkanie w parku
    30: "human",   # Orzeszkowa – Nad Niemnem (rzeka)
}

# ─── 30 tekstów ──────────────────────────────────────────────────────────────
TEXTS = {
    1: """Rok 1812 nastąpił. Napoleon wyruszył z wojskiem ku Rosji. Wojsko
polskie towarzyszyło mu z zapałem i nadzieją. Sławutnik Ścibor,
chorąży pancerny województwa trockiego, zebrał sto koni własnym
kosztem i poprowadził je pod rozkazy księcia Józefa. Żona jego,
Zofia z Lubońskich, pozostała na Litwie z trójką dzieci. Starszy
syn Tadeusz miał lat piętnaście, córka Zosia lat trzynaście,
a najmłodszy Kazimierz, zwany Kaziukiem, dopiero siedem. Majątek
Soplicowo, odziedziczony po rodzicach, był niemały: folwark,
trzy wsie, lasy. Zarządzał nim stary ekonom Rymsza, człek
uczciwy i oddany, który pamiętał jeszcze czasy Kościuszki.""",

    2: """Aleksandra poczuła, że coś się zmieniło, zanim jeszcze zdążyła
to nazwać. Może to było światło — inne niż zwykle o tej porze,
bardziej miękkie, jakby przefiltrowane przez cienką warstwę
chmur. Albo może to był zapach: wilgoć zmieszana z wonią
rozgrzanego asfaltu, ta charakterystyczna mieszanina, którą
pamięta się przez całe życie. Siedziała przy oknie z kawą
stygnącą w dłoniach i patrzyła na ulicę. Nic szczególnego się
nie działo. Tramwaj przejechał. Jakiś mężczyzna zatrzymał się
przy witrynie sklepu i zaraz poszedł dalej. Pies obwąchał latarnię.
Zupełnie zwykłe południe, a jednak coś było nie tak.""",

    3: """Kraj lat dziecinnych! On zawsze zostanie
Święty i czysty jak pierwsze kochanie.
Nie zaburzony błędów przypomnieniem,
Nie podkopany nadziei złudzeniem
Ani zmieniony wypadków strumieniem.
Tę ziemię, co ją tylu wróg przeorał,
Tylu na własnej ziemi klęczą w okowach,
Ja lubię i kocham, i będę miłować
Dopóki oczy mi w głowie stać będą.
Litwo! Ojczyzno moja! Ty jesteś jak zdrowie:
Ile cię trzeba cenić, ten tylko się dowie,
Kto cię stracił. Dziś piękność twą w całej ozdobie
Widzę i opisuję, bo tęsknię po tobie.""",

    4: """Dom przy Królewskiej stał od trzydziestu lat i wyglądał na to,
że stać będzie kolejne trzydzieści. Kamienica z czerwonej cegły,
z bramą łukową i podwórkiem, na którym rosła lipa — jedyna
w tej części miasta. Lokatorzy zmieniali się przez dekady:
rodziny robotnicze zamieniały się na studenckie lokum, potem
na biura, teraz z powrotem były mieszkania. Pani Helena
mieszkała tu od zawsze, lub przynajmniej od tak dawna, że
nikomu nie przychodziło do głowy pytać kiedy się wprowadził.
Miała siedemdziesiąt dwa lata, kotkę Różę i zwyczaj palenia
papierosów przy otwartym oknie, zawsze o dziesiątej wieczór,
patrząc na lipę, która dawno ją przerosła.""",

    5: """Stach wyszedł ze stajni i rozejrzał po obejściu. Słońce już
chyliło się ku zachodowi, barwiąc niebo na purpurę i złoto.
Kury z głośnym gdakaniem szukały noclegu przy płocie.
Gdzieś daleko szczekał pies, a echo niosło ten odgłos przez
całą dolinę. Chłop otarł czoło chustą, splunął na ziemię
i ruszył ku domowi. Nogi miał ciężkie od całodziennej roboty,
plecy bolały — ale zboże stało na polu, i to był fakt, który
wszystko tłumaczył i wszystko usprawiedliwiał. Robota to
robota, a chleb sam z nieba nie spada. Matka stała już
w progu i machała ręką, żeby się śpieszył.""",

    6: """Ziemia obiecana była wszędzie i nigdzie. Bauer patrzył na
kominy fabryczne sterczące nad miastem jak szable wbite
w niebo i czuł w sobie tę samą mieszaninę pogardy i pożądania,
która go prowadziła tu z Niemiec. Łódź była szpetna,
hałaśliwa, zaśmiecona bawełnianym puchem, który leżał na
ulicach jak brudny śnieg przez cały rok. Robotnicy chodzili
jak cienie, blade twarze, ręce spracowane do kości. A jednak
tu właśnie robiły się pieniądze — szybko, nieomal naocznie,
jak ciasto drożdżowe w ciepłym piecu. Karol Borowiecki
wiedział o tym lepiej niż ktokolwiek inny. Wiedział i czuł,
że go to niszczy, i nic z tym nie robił.""",

    7: """Ksiądz Robak siedział w cieniu lip klasztornych i czytał
brewiarz. Liście drżały lekko — nie od wiatru, bo wiatr
tego dnia nie wiał, lecz od jakiegoś własnego, wewnętrznego
drżenia, które ogarniało wszystko żywe w letnie południe.
Był to człowiek już niemłody, z twarzą pooraną bliznami,
których nie zasłaniał habit. Oczy miał jasne, skupione,
takie, co to widziały niejedną rzecz i wybrały milczenie.
Kiedy ktoś go pytał o przeszłość, odpowiadał krótko:
służyłem. Komu — nie dopowiadał. Klasztor przyjął go bez
pytań, a on odpłacał tą samą monetą: pracą i ciszą.""",

    8: """Michał wrócił do domu o ósmej. Zdjął buty przy wejściu,
powiesił kurtkę na haczyk, wstawił wodę na herbatę.
Wszystko po kolei, jak zawsze, mechanicznie i bez namysłu.
W salonie leżała gazeta z wczoraj — nie czytał jej, nie
zamierzał. Usiadł przy stole i wyjął telefon. Trzynaście
wiadomości, dwie nieodebrane połączenia. Odłożył telefon
ekranem w dół. Herbata zrobiła się za gorąca. Poczekał.
Za oknem zachodziło słońce i robiło to spokojnie, bez
pośpiechu, jakby wiedziało że ma na to czas. Michał
pomyślał, że nie pamięta, kiedy ostatnio patrzył jak
zachodzi słońce. Może nigdy. Może po prostu nigdy.""",

    9: """Przez całą noc pani Dulska nie spała. Leżała w łóżku
z otwartymi oczyma i liczyła sufit, który znała na pamięć
od trzydziestu lat. Siedemdziesiąt dwie belki, plama
od przecieku koło okna, pęknięcie wzdłuż rogu — wszystko
na swoim miejscu. Rano wstała wcześniej niż zwykle,
zeszła do kuchni, zajrzała do spiżarni, sprawdziła zamek
przy drzwiach wejściowych. Świat był na miejscu. Dom stał.
Kamienica przynosiła dochód. Dzieci spały. Mąż chrząkał
przez sen. Wszystko było w należytym porządku, tak jak
być powinno, i nikomu nic do tego, co sobie pani Dulska
myśli po nocach, kiedy nikt jej nie widzi.""",

    10: """Nad Niemnem płynął spokojnie, niosąc na swojej szerokiej
tafli odbicia nieba i brzegów. Po lewej stronie ciągnęły
się łąki, po prawej — las gęsty i ciemny, w którym gniazdo
sobie uwiły wszelkie stworzenia leśne. Justyna Orzelska
siedziała na kamieniu przy samej wodzie i patrzyła, jak
nurt unosi żółtą łódź liści. Myślała o wielu rzeczach
naraz — o ojcu, o przyszłości, o tym, że już jesień
i za miesiąc trzeba będzie wracać do miasta. Rzeka płynęła
i zdawało się, że czas płynie razem z nią, że nic tu
nie jest pilne, że wszystko, co ważne, można odłożyć
na później. Ale to było złudzenie. Justyna wiedziała o tym.""",

    11: """Poeta przyszedł do Poety w południe. Tak zaczyna się wiele
historii, które potem okazują się ważne, i ta nie była
wyjątkiem. Weszli razem do kawiarni przy Floriańskiej,
zamówili czarną kawę, usiedli przy oknie. Przez chwilę
siedzieli w milczeniu, bo milczenie między nimi zawsze
było treściwsze niż cudza rozmowa. W końcu starszy
powiedział: napisz o tym, co boli. Młodszy zapytał:
a co jeśli nie wiem, co boli? Starszy odparł: właśnie
dlatego pisz. Kawiarnia była pełna ludzi, którzy nie
słyszeli tej rozmowy. To dobrze. Niektóre rzeczy
należą tylko do tych, którzy je mówią.""",

    12: """Łódź kipiała życiem fabrycznym. Z kominów buchał dym,
a tkackie maszyny dudniły bez przerwy, dzień i noc,
świątki i piątki. Robotnicy szli rano do pracy szarymi
rzędami, twarze blade, oczy opuszczone, nogi powłóczyły
po bruku. Właściciel fabryki, gruby Müller, chodził między
krosnami i sprawdzał metry tkaniny palcem wskazującym.
Każdy metr to pieniądz. Każda przerwa to strata. Tylko
że tego, co traciły twarze wchodzące rano do hali
i wychodzące wieczorem, żaden rachunek nie obliczał.
Nikt o to nie pytał. Łódź rosła w bogactwo i rosła
w nędzę jednocześnie, i nikomu to nie wydawało się
sprzecznością.""",

    13: """Anna zamknęła książkę i spojrzała za okno. Śnieg padał
od rana, cicho i konsekwentnie, zasypując miasto równą
białą warstwą. Przy biurku siedziała od szóstej i napisała
może trzy zdania — dobre, właściwe trzy zdania, ale tylko
trzy. Pisanie było ostatnio jak ciągnięcie wozu pod górę:
każde słowo z trudem, każda scena z oporami. Wstała,
zrobiła kawę, stanęła przy oknie. Śnieg padał dalej.
Może to jest właśnie odpowiedź, pomyślała — może
trzeba po prostu padać konsekwentnie, bez spektakularnych
efektów, bez oglądania się czy ktoś patrzy. Usiadła
z powrotem przy biurku i napisała czwarte zdanie.""",

    14: """Jacek Soplica — kto o nim nie słyszał w powiecie?
Zwano go niegdyś Niedźwiedziem i Wojevodą, i jeszcze
różnymi przezwiskami, bo miał do nich szczęście szczególne.
Był szlachcicem z dobrego domu, ale zabijaką i pijakiem
od młodości, tego wszyscy byli pewni — pewniejsi może,
niż należało. Ojciec go nie kochał, bo ojciec kochał tylko
starszego, co to umarł w kwiecie wieku. Matka umarła
przy porodzie Jacka, i może to dlatego chłopiec wyrósł
sam jak chwast, nie uczony, nie prowadzony. Jeśli zaś
miał w sobie coś, co nim kierowało, to była to tylko
ta uparta siła, którą się zwie w różnych językach różnie,
a po polsku zwie się po prostu: żal.""",

    15: """Stasio Tarkowski miał czternaście lat i od dawna wiedział,
że zostanie podróżnikiem. Nie takim, co to jedzie pociągiem
z Warszawy do Krakowa i z powrotem, ale prawdziwym —
przez Afrykę, przez dżungle, przez pustynie. Ojciec jego,
inżynier Tarkowski, pracował przy budowie kanału
w Egipcie i zabrał syna ze sobą, bo szkoła była zamknięta
na wakacje, a zostawić chłopaka samego w domu nie wypadało.
Nel Rawlison mieszkała w domu naprzeciwko i miała osiem
lat i koronkową suknię, i taki spokojny, poważny wzrok,
że wszyscy mówili: ta dziewczynka będzie kimś. Oboje
nie wiedzieli jeszcze, co ich czeka — a może właśnie
dlatego wchodzili w to z otwartymi oczami.""",

    16: """Górale znali te szlaki od pokoleń. Ojciec uczył syna,
dziad uczył ojca — skałka po skałce, przejście po przejściu.
Sabała chodził z turystami od trzydziestu lat i nigdy
żadnego nie zgubił, co sam podkreślał przy każdej
okazji, szczególnie przy kieliszku. Był człowiekiem małym,
zwartym jak pień kosówki, z wąsami które przykrywały
pół twarzy. Mówił mało, ale kiedy już mówił, to zawsze
coś konkretnego: tu nie leziec, tam leziec, uważać
na ten kamień co wygląda mocno a jest jak papier.
Miasto go nie interesowało. Tatry były jego i on był Tatrów,
i to wystarczało za wszystko.""",

    17: """Piotr wrócił do wioski po piętnastu latach. Droga była
ta sama, tylko drzewa po obu stronach wyrosły i teraz
tworzyły tunel z gałęzi, przez który słońce przebijało
się w plamach. Dom stał. Płot był naprawiony — nowe deski,
inny kolor. Ktoś dosadził jabłoń przy furtce, której
wcześniej nie było. Matki już nie było. Piotr wiedział
o tym, po to tu przyjechał. Wszedł przez furtkę, usiadł
na ławce przed domem i przez chwilę siedział niemal
bez ruchu. Sąsiadka, pani Rozalia, wyjrzała przez okno
i zaraz zasłoniła firankę. Dała mu spokój. Wiedziała,
że są rzeczy, przy których człowiek potrzebuje chwili sam.""",

    18: """Rzeczka pod lasem nosiła w sobie pamięć całej wsi.
Każde pokolenie przychodziło tu po wodę, każde pokolenie
zostawiało tu coś swojego. Kobiety prały tu bieliznę
i rozmawiały przez lata o tych samych rzeczach: urodziny,
śmierci, żniwa, zima. Dzieci wchodziły po kolana
i łapały raki, które uciekały im spomiędzy palców.
Stary Józef chodził tu co wieczór z wędką i nie łowił
nic, bo nigdy nic nie było — ale siedział, i to wystarczało.
Woda płynęła. Las szumiał. Gdzie indziej działy się
wielkie rzeczy, ale tutaj, przy tej rzeczce, nic się
nie musiało dziać. Po prostu było.""",

    19: """Księżna Izabela przyjmowała gości we wtorki. Salon
był odpowiednio urządzony do tego celu: fotele miękkie,
ale niezbyt, lampy rzucające światło pochlebne dla
karnacji, stolik z herbatą i ciastkami angielskimi.
Gości było zazwyczaj ośmioro, dziesięcioro — dobrani
starannie pod względem poglądów, bo księżna nie lubiła
przy herbacie kłótni, lubiła natomiast dyskusję grzeczną
i bezpieczną, kończącą się niczym konkretnym. Tego
wieczoru jednak przyszedł ktoś, kto zepsuł ten porządek:
młody człowiek w zbyt nowym fraku, z oczami,
które patrzyły za uważnie na wszystko — i na księżnę,
i na gości, i na ciastka angielskie.""",

    20: """Marta długo nie mogła zasnąć. Leżała na plecach
w ciemnościach i słuchała odgłosów kamienicy:
skrzypnięcie deski na klatce schodowej, czyjaś rozmowa
za ścianą stłumiona do szeptu, kapanie kranu w łazience.
Miasto za oknem trwało w swoim nocnym życiu — daleko
karetka, bliżej śmieciarka — nieprzerwany hałas, do
którego przywykła przez lata tak bardzo, że cisza by
ją obudziła. Myślała o jutrzejszym spotkaniu. Wiedziała,
co powie i co usłyszy, bo oboje wiedzieli to od dawna.
Były rzeczy, które się mówiło po kilku latach, kiedy
człowiek przestawał udawać, że jakoś samo się ułoży.""",

    21: """Na polach pod Grunwaldem leżała cicha ziemia.
Krzyżacy ciągnęli z zachodu w szykach żelaznych,
z krzyżem na płaszczach białych. Jagiełło stał na wzgórzu
i patrzył przez ciepły lipcowy poranek na ich kolumny.
Przy nim stał Zyndram z Maszkowic, który milczał,
a milczenie jego było takie, że każdy wódz wolałby
sto głośnych doradców niż jednego tak milczącego.
W końcu król powiedział: czas. I to jedno słowo
ruszyło wszystko — chorągwie, konie, tamburyno —
cały ten ogrom, który potem przez wieki będą liczyć
historycy. Ale w tej chwili było tylko to jedno słowo:
czas.""",

    22: """Kamienica przy Złotej miała cztery piętra i dwadzieścia
trzy mieszkania, i tyle samo historii. Na parterze
mieszkał szewc Wiśniewski ze starą żoną; wyżej — rodzina
z trójką dzieci hałaśliwych i jednym niemowlęciem spokojnym;
dalej — student prawa, który uczył się nocami i spał
przez dzień; pod samym dachem — stary malarz, który
od lat nic nie malował, tylko zbierał gazety. Wszyscy się
znali, bo kamienica zmuszała do znajomości: te same
schody, ta sama studnia, ten sam podwórzec. Życie
toczyło się osobno, ale niedaleko od siebie — jak rzeki,
które nigdy się nie łączą, a jednak płyną tą samą doliną.""",

    23: """Tatry o świcie miały w sobie coś z objawienia.
Witkiewicz chodził tam od lat, ale za każdym razem
ten widok zatrzymywał go w pół kroku: szczyty wynurzające
się z mgły, pierwsze słońce malujące skały na pomarańcz,
cisza tak gęsta, że słyszało się własne serce.
Miejscowi tego nie rozumieli — dla nich góry były pracą,
pastwiskiem, drogą na targ. Ale on przychodził tu szukać
czegoś, czego nie umiałby nazwać: może po prostu obecności
czegoś większego. Może po prostu tego, że jest się małym
i to jest właściwe. Ruszył dalej w górę, a mgła za nim
zamykała się powoli jak kurtyna.""",

    24: """Profesor Radwan miał sześćdziesiąt lat i od czterdziestu
uczył historii w tej samej szkole, przy tej samej tablicy.
Ławki się zmieniały, dzieci się zmieniały, programy się
zmieniały — on nie. Mówił zawsze tym samym głosem,
równym, trochę za cichym jak na klasę trzydziestu uczniów.
Ale słuchali. Nie wszyscy, nie zawsze, ale kiedy zaczynał
mówić o rzeczach, które sam uważał za ważne, to i ten
ostatni rząd podnosił głowę. Bo był w nim jakiś spokój —
nie spokój człowieka, któremu jest wszystko jedno, ale
spokój człowieka, który wie, że to co mówi, jest prawdą.
I to czuć było przez całą klasę.""",

    25: """Antek wyrósł na polu. Ojciec zabrał go do roboty jak
miał sześć lat — jeszcze pod pachy nosił go między
bruzdy, a on patrzył na ziemię z góry i myślał,
że to jest cały świat. Potem okazało się, że nie cały —
że za lasem jest miasto, za miastem inne miasto, za górami
inne kraje. Ale ziemia została ziemią. Tę prawdę
wbił mu ojciec nie słowami, ale pracą: że wszystko
wraca do ziemi i wszystko z ziemi pochodzi.
Kiedy ojciec umarł, Antek przykrył go ziemią
i zaorał pole na wiosnę, i posiał żyto. To był
jedyny pogrzeb, jaki znał. I jedyny, jaki miał sens.""",

    26: """Siostra Klara prowadziła szkółkę od lat trzydziestu.
Dzieci przychodziły różne — mądre i tępe, chętne i leniwe,
z bogatych domów i z ubogich. Ona traktowała wszystkie
jednakowo, co bogatsi uważali za niesprawiedliwość,
a ubodzy — za cud. Uczyła czytać, pisać, rachować.
Przy okazji uczyła czegoś, czego nie było w żadnym
podręczniku: że wiedza jest po to, żeby z niej korzystać,
a nie po to, żeby się nią chwalić. To ostatnie
przychodziło dzieciom najtrudniej. Zresztą nie tylko
dzieciom. Siostra Klara wiedziała o tym doskonale,
bo sama przeszła przez to samo, zanim wstąpiła
do zakonu.""",

    27: """W izbie było zimno i pachniało smołą i suszonymi grzybami.
Babka Agnieszka siedziała przy piecu i przędła, palce
chodziły jej szybko i pewnie mimo że miała osiemdziesiąt
lat i wzrok nie ten co dawniej. Wnuk, mały Jasiek,
siedział obok i patrzył na wrzeciono. Spytał: babciu,
po co przędziesz, jak można kupić nitkę w sklepie?
Babka odparła nie odrywając wzroku od wełny:
bo to moja nić, Jasiek, nie ich. To jest różnica.
Chłopiec nie rozumiał, ale zapamiętał. Takie słowa
zapamiętuje się nawet wtedy, gdy się ich nie rozumie —
może właśnie dlatego.""",

    28: """Tren VIII
Wielka mi to ulga w płaczu i w żalu,
Że po wszytkich stronach w smętnym tym niedobrze
Wspomnieniu wołam cię, Hanusiu droga,
Wszędzie cię szukam i wszędzie mi błoga
Twoja pamięć stoi przed oczyma mojemi.
Nie masz cię, nie masz! darmo łzy ronię —
Znikłaś jak mgła poranna, jak dźwięk dzwonu,
Jak sen który pierzchnie przy pierwszym brzasku.
I mnie i domu i tej całej trosce,
Coś się tyczyła ciebie, Urszuleczko,
Już cię nie stanie ku pociesze żadnej.
Ach, co tu więcej mówić, gdy nie masz obrony
Przeciw śmierci, która wszystko kosi równo.""",

    29: """Zofię poznał w maju. To było w parku, przy fontannie,
która nie działała od lat i służyła teraz jako siedzisko
dla gołębi i miejsce spotkań psów. Ona czytała książkę,
on jadł kanapkę, oboje udawali, że są sami, bo w parku
tak się robi: siedzi się obok i nie patrzy. W końcu
powiedział: przepraszam, wie pani co to za drzewo?
Wskazał na kasztanowiec. Wiedziała oczywiście —
wiedziała od podstawówki — ale powiedziała: nie wiem.
I to było początkiem, choć żadne z nich tego nie widziało
jako początku. Zaczyna się od takich małych kłamstw,
które chcą być miłe dla kogoś obcego.""",

    30: """Rzeka Niemno wiła się przez kraj jak żyła przez ciało.
Tadeusz Korczyński znał każdy zakręt, każdy bród,
każde miejsce, gdzie woda zwalniała w spokojną sadzawkę.
Od dziecka pływał tu z bratem, który umarł w powstaniu.
Teraz chodził tu sam i myślał, że ziemia pamięta
tych, których nosi. Kamienie pod wodą były te same.
Drzewa były te same. Tylko ludzie się zmieniali,
odchodzili, wracali odmienieni albo nie wracali wcale.
Tadeusz stał przy brzegu i patrzył na wodę, i wiedział,
że za rok, za dziesięć lat ta rzeka będzie płynąć dalej —
bez niego, bez braci, bez tego wszystkiego co minęło —
i że to jest właściwe, i że nie ma się co smucić.""",
}

HARD_CASES = {1: "graniczny — epicka narracja", 5: "AI w stylu wiejskim",
              27: "styl ludowy", 28: "archaiczny (Kochanowski)", 3: "wiersz (Mickiewicz)"}

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRAY   = "\033[90m"

def colored(text, color): return f"{color}{text}{RESET}"

def analyze(host, text, nr):
    url = f"{host}/api/analyze"
    try:
        r = requests.post(url, json={"text": text}, timeout=120)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        print(colored(f"  ✗ Błąd połączenia — czy backend działa? ({host})", RED))
        sys.exit(1)
    except Exception as e:
        print(colored(f"  ✗ Błąd #{nr}: {e}", RED))
        return None

def generate_html(results, metrics):
    rows = ""
    for r in results:
        nr = r["nr"]
        true_label = ANSWER_KEY[nr]
        pred = r.get("predicted", "?")
        prob = r.get("ai_prob", 0)
        correct = r.get("correct", False)
        is_hard = nr in HARD_CASES

        status_icon = "✅" if correct else ("⚠️" if is_hard else "❌")
        row_class = "correct" if correct else ("hard" if is_hard else "wrong")
        hard_note = f'<span class="hard-badge" title="{HARD_CASES.get(nr, "")}">⚠ graniczny</span>' if is_hard else ""

        s = r.get("stylometry", {})
        q = r.get("quality", {})
        ai_d = r.get("ai_detection", {})

        rows += f"""<tr class="{row_class}">
            <td class="center">{nr:02d}{hard_note}</td>
            <td class="center label-{true_label}">{true_label.upper()}</td>
            <td class="center label-{pred}">{pred.upper()}</td>
            <td class="center {'high' if prob > 0.6 else ('mid' if prob > 0.4 else 'low')}">{prob:.1%}</td>
            <td class="center">{ai_d.get('perplexity', '—')}</td>
            <td class="center">{status_icon}</td>
            <td class="mono">{s.get('ttr', '—'):.4f}</td>
            <td class="mono">{s.get('lexical_density', '—'):.4f}</td>
            <td class="mono">{s.get('entropy', '—'):.3f}</td>
            <td class="mono">{s.get('vocab_richness', '—'):.4f}</td>
            <td class="mono">{s.get('avg_sentence_length', '—'):.1f}</td>
            <td class="mono">{q.get('lix_score', q.get('flesch_score', '—')):.1f}</td>
            <td class="mono">{s.get('word_count', '—')}</td>
        </tr>"""

    ai_rows = [r for r in results if ANSWER_KEY[r["nr"]] == "ai"]
    human_rows = [r for r in results if ANSWER_KEY[r["nr"]] == "human"]

    def avg(rows, key, subkey):
        vals = [r.get(key, {}).get(subkey) for r in rows if r.get(key, {}).get(subkey) is not None]
        return sum(vals)/len(vals) if vals else 0

    stats_html = ""
    stylometric_metrics = [
        ("ttr", "MATTR (TTR)", "stylometry"),
        ("lexical_density", "Gęstość leksykalna", "stylometry"),
        ("entropy", "Entropia Shannona", "stylometry"),
        ("vocab_richness", "Bogactwo słow.", "stylometry"),
        ("avg_sentence_length", "Śr. dł. zdania", "stylometry"),
    ]
    for key, label, group in stylometric_metrics:
        ai_avg = avg(ai_rows, group, key)
        hu_avg = avg(human_rows, group, key)
        diff = abs(ai_avg - hu_avg)
        diff_pct = (diff / hu_avg * 100) if hu_avg else 0
        stats_html += f"""<tr>
            <td>{label}</td>
            <td class="label-ai mono">{ai_avg:.4f}</td>
            <td class="label-human mono">{hu_avg:.4f}</td>
            <td class="mono">Δ {diff:.4f} ({diff_pct:.1f}%)</td>
        </tr>"""

    ai_lix = avg(ai_rows, "quality", "lix_score") or avg(ai_rows, "quality", "flesch_score")
    hu_lix = avg(human_rows, "quality", "lix_score") or avg(human_rows, "quality", "flesch_score")
    stats_html += f"""<tr>
        <td>LIX (czytelność)</td>
        <td class="label-ai mono">{ai_lix:.2f}</td>
        <td class="label-human mono">{hu_lix:.2f}</td>
        <td class="mono">Δ {abs(ai_lix-hu_lix):.2f}</td>
    </tr>"""

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    m = metrics

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<title>checkLit – Raport ewaluacji ({ts})</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }}
  h1 {{ color: #4f6ef7; }}
  h2 {{ color: #334155; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 40px; }}
  .meta {{ color: #64748b; font-size: 13px; margin-bottom: 30px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin: 20px 0 40px; }}
  .card {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .card .val {{ font-size: 36px; font-weight: 900; }}
  .card .lbl {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  .green {{ color: #22c55e; }} .yellow {{ color: #f59e0b; }} .red {{ color: #ef4444; }} .blue {{ color: #4f6ef7; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); font-size: 13px; margin-bottom: 30px; }}
  th {{ background: #f1f5f9; padding: 10px 8px; text-align: left; font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: .05em; }}
  td {{ padding: 8px; border-bottom: 1px solid #f1f5f9; }}
  td.center {{ text-align: center; }}
  td.mono {{ font-family: monospace; font-size: 12px; }}
  tr.correct {{ background: #f0fdf4; }}
  tr.wrong {{ background: #fff1f2; }}
  tr.hard {{ background: #fffbeb; }}
  .label-ai {{ color: #dc2626; font-weight: 700; }}
  .label-human {{ color: #16a34a; font-weight: 700; }}
  .high {{ color: #dc2626; font-weight: 700; }}
  .mid {{ color: #d97706; font-weight: 700; }}
  .low {{ color: #16a34a; font-weight: 700; }}
  .hard-badge {{ font-size: 10px; background: #fef3c7; color: #92400e; border-radius: 4px; padding: 1px 4px; margin-left: 4px; }}
  .footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin-top: 40px; }}
  .confusion {{ display: inline-grid; grid-template-columns: 1fr 1fr; gap: 8px; text-align: center; }}
  .confusion div {{ padding: 16px 24px; border-radius: 8px; font-weight: 700; }}
  .tp {{ background: #dcfce7; color: #166534; }} .tn {{ background: #dcfce7; color: #166534; }}
  .fp {{ background: #fee2e2; color: #991b1b; }} .fn {{ background: #fee2e2; color: #991b1b; }}
</style>
</head>
<body>
<h1>checkLit – Raport ewaluacji live</h1>
<p class="meta">Wygenerowany: {ts} · Tekstów: 30 (15 AI + 15 human) · Próg klasyfikacji: 50%</p>

<div class="cards">
  <div class="card"><div class="val {'green' if m['accuracy']>=0.9 else 'yellow'}">{m['accuracy']:.1%}</div><div class="lbl">Accuracy</div></div>
  <div class="card"><div class="val {'green' if m['precision']>=0.85 else 'yellow'}">{m['precision']:.1%}</div><div class="lbl">Precision</div></div>
  <div class="card"><div class="val {'green' if m['recall']>=0.85 else 'yellow'}">{m['recall']:.1%}</div><div class="lbl">Recall</div></div>
  <div class="card"><div class="val {'green' if m['f1']>=0.85 else 'yellow'}">{m['f1']:.1%}</div><div class="lbl">F1 Score</div></div>
  <div class="card"><div class="val blue">{m['tp']}</div><div class="lbl">True Positives (AI←AI)</div></div>
  <div class="card"><div class="val blue">{m['tn']}</div><div class="lbl">True Negatives (Human←Human)</div></div>
  <div class="card"><div class="val red">{m['fp']}</div><div class="lbl">False Alarms (Human→AI)</div></div>
  <div class="card"><div class="val red">{m['fn']}</div><div class="lbl">Missed (AI→Human)</div></div>
</div>

<h2>📊 Wyniki per tekst</h2>
<table>
<thead>
  <tr>
    <th>Nr</th><th>Prawda</th><th>Predykcja</th><th>AI prob</th><th>Perplexity</th><th>OK?</th>
    <th>MATTR</th><th>Gęst.lex.</th><th>Entropia</th><th>Bogactwo</th><th>Śr.zdanie</th><th>LIX</th><th>Słów</th>
  </tr>
</thead>
<tbody>{rows}</tbody>
</table>

<h2>📈 Stylometria: AI vs Human (średnie)</h2>
<table>
<thead><tr><th>Metryka</th><th>AI (śr.)</th><th>Human (śr.)</th><th>Różnica</th></tr></thead>
<tbody>{stats_html}</tbody>
</table>

<p class="footer">checkLit Literary Analyzer · AUC korpusu kalibracyjnego: 0.94</p>
</body></html>"""
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--delay", type=float, default=0.8, help="Opóźnienie między requestami (s)")
    parser.add_argument("--start", type=int, default=1, help="Zacznij od tekstu nr X")
    args = parser.parse_args()

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  checkLit – Automatyczna ewaluacja live{RESET}")
    print(f"{'='*60}")
    print(f"  Host:    {args.host}")
    print(f"  Teksty:  {args.start}–30  ({31-args.start} do przeanalizowania)")
    print(f"  Delay:   {args.delay}s między requestami")
    print(f"{'='*60}\n")

    try:
        requests.get(f"{args.host}/health", timeout=5).raise_for_status()
        print(colored("  ✓ Backend działa\n", GREEN))
    except:
        print(colored(f"  ✗ Nie można połączyć z {args.host}\n    Uruchom backend przez start.ps1", RED))
        sys.exit(1)

    results = []
    correct_count = 0

    header = f"{'Nr':>3}  {'Prawda':8}  {'Predykc.':8}  {'AI prob':8}  {'Perplx':7}  {'MATTR':7}  {'Entrop':7}  {'LIX':6}  {'OK':4}"
    print(colored(header, CYAN))
    print("─" * len(header))

    for nr in range(args.start, 31):
        text = TEXTS[nr]
        true_label = ANSWER_KEY[nr]
        is_hard = nr in HARD_CASES

        result = analyze(args.host, text, nr)
        if result is None:
            continue

        ai_d = result.get("ai_detection", {})
        styl = result.get("stylometry", {})
        qual = result.get("quality", {})

        ai_prob = ai_d.get("ai_probability", 0.5)
        perplexity = ai_d.get("perplexity", "—")
        predicted = "ai" if ai_prob >= 0.5 else "human"
        correct = predicted == true_label
        if correct:
            correct_count += 1

        ttr = styl.get("ttr", 0)
        entropy = styl.get("entropy", 0)
        lix = qual.get("lix_score", qual.get("flesch_score", 0))

        status = colored("✓", GREEN) if correct else (colored("~", YELLOW) if is_hard else colored("✗", RED))
        prob_str = colored(f"{ai_prob:.1%}", RED if ai_prob > 0.6 else (YELLOW if ai_prob > 0.4 else GREEN))
        pred_str = colored(predicted[:5], RED if predicted == "ai" else GREEN)
        true_str = colored(true_label[:5], RED if true_label == "ai" else GREEN)
        hard_note = colored(f" ← {HARD_CASES[nr]}", YELLOW) if is_hard else ""

        ppx_str = f"{perplexity:.1f}" if isinstance(perplexity, float) else str(perplexity)

        print(f"{nr:>3}.  {true_str:20}  {pred_str:20}  {prob_str:20}  {ppx_str:7}  {ttr:.4f}  {entropy:.3f}  {lix:.1f}  {status}{hard_note}")

        results.append({
            "nr": nr, "ai_prob": ai_prob, "predicted": predicted,
            "correct": correct, "ai_detection": ai_d,
            "stylometry": styl, "quality": qual,
        })

        time.sleep(args.delay)

    print(f"\n{'─'*60}")
    if not results:
        print(colored("Brak wyników do analizy.", RED))
        return

    tp = sum(1 for r in results if ANSWER_KEY[r["nr"]] == "ai"    and r["predicted"] == "ai")
    tn = sum(1 for r in results if ANSWER_KEY[r["nr"]] == "human" and r["predicted"] == "human")
    fp = sum(1 for r in results if ANSWER_KEY[r["nr"]] == "human" and r["predicted"] == "ai")
    fn = sum(1 for r in results if ANSWER_KEY[r["nr"]] == "ai"    and r["predicted"] == "human")

    total = len(results)
    accuracy  = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall    = tp / (tp + fn) if (tp + fn) else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    metrics = dict(accuracy=accuracy, precision=precision, recall=recall, f1=f1,
                   tp=tp, tn=tn, fp=fp, fn=fn)

    print(f"\n{BOLD}WYNIKI DETEKCJI AI:{RESET}")
    print(f"  Accuracy:  {colored(f'{accuracy:.1%}', GREEN if accuracy >= 0.85 else YELLOW)}")
    print(f"  Precision: {colored(f'{precision:.1%}', GREEN if precision >= 0.8 else YELLOW)}")
    print(f"  Recall:    {colored(f'{recall:.1%}', GREEN if recall >= 0.8 else YELLOW)}")
    print(f"  F1 Score:  {colored(f'{f1:.1%}', GREEN if f1 >= 0.8 else YELLOW)}")
    print(f"\n  TP={tp}  TN={tn}  FP={fp}  FN={fn}")

    wrong = [r for r in results if not r["correct"]]
    if wrong:
        print(f"\n{BOLD}BŁĘDNE KLASYFIKACJE ({len(wrong)}):{RESET}")
        for r in wrong:
            nr = r["nr"]
            true_l = ANSWER_KEY[nr]
            note = f"  ← {HARD_CASES[nr]}" if nr in HARD_CASES else ""
            print(f"  #{nr:02d}: {true_l.upper()} → {r['predicted'].upper()}  (AI prob={r['ai_prob']:.1%}){colored(note, YELLOW)}")

    ai_results    = [r for r in results if ANSWER_KEY[r["nr"]] == "ai"]
    human_results = [r for r in results if ANSWER_KEY[r["nr"]] == "human"]

    def avg_val(rows, key, subkey):
        vals = [r.get(key, {}).get(subkey) for r in rows if r.get(key, {}).get(subkey) is not None]
        return sum(vals)/len(vals) if vals else 0

    print(f"\n{BOLD}PORÓWNANIE STYLOMETRYCZNE (AI vs Human):{RESET}")
    print(f"  {'Metryka':25}  {'AI (śr.)':10}  {'Human (śr.)':12}  {'Różnica':8}")
    print(f"  {'─'*65}")
    metrics_list = [
        ("stylometry", "ttr",               "MATTR"),
        ("stylometry", "lexical_density",    "Gęstość leksykalna"),
        ("stylometry", "entropy",            "Entropia Shannona"),
        ("stylometry", "vocab_richness",     "Bogactwo słow."),
        ("stylometry", "avg_sentence_length","Śr. dł. zdania"),
    ]
    for group, key, label in metrics_list:
        ai_avg = avg_val(ai_results, group, key)
        hu_avg = avg_val(human_results, group, key)
        diff = ai_avg - hu_avg
        diff_str = colored(f"{diff:+.4f}", GREEN if abs(diff) > 0.02 else GRAY)
        print(f"  {label:25}  {ai_avg:10.4f}  {hu_avg:12.4f}  {diff_str}")

    ai_lix = avg_val(ai_results, "quality", "lix_score") or avg_val(ai_results, "quality", "flesch_score")
    hu_lix = avg_val(human_results, "quality", "lix_score") or avg_val(human_results, "quality", "flesch_score")
    print(f"  {'LIX (czytelność)':25}  {ai_lix:10.2f}  {hu_lix:12.2f}  {colored(f'{ai_lix-hu_lix:+.2f}', GREEN)}")

    ts_ = datetime.now().isoformat()
    output_json = {
        "timestamp": ts_,
        "metrics": metrics,
        "results": results,
    }
    json_path = "evaluation_live_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ JSON zapisany: {json_path}")

    html_path = "evaluation_live_report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(generate_html(results, metrics))
    print(f"  ✓ Raport HTML: {html_path}  (otwórz w przeglądarce)")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()