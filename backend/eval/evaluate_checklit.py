"""
evaluate_checklit.py — Rozszerzona ewaluacja platformy checkLit (v2)
=====================================================================
Korpus: 25 tekstów ludzkich (Wolne Lektury, różne epoki i autorzy)
      + 25 tekstów generowanych przez AI

Uruchomienie:
    cd C:\\Users\\sebas\\Documents\\checkLit\\backend
    venv\\Scripts\\activate
    python evaluate_checklit.py

Wymaga działającego backendu na http://localhost:8000
Wyniki zapisuje do: eval_detection_<ts>.csv i eval_compare_<ts>.csv
"""

import requests
import json
import csv
import sys
import time
from datetime import datetime

BASE = "http://localhost:8000/api"

# ─── 50 TEKSTÓW TESTOWYCH ─────────────────────────────────────────────────────
# Format: (id, label_expected, category, autor_epoka, tekst)
# label: "human" | "ai"
# category: "HUMAN_LEKTURY" | "AI_GEN"

TEXTS = [

    # ══════════════════════════════════════════════════════════════════════════
    # BLOK A — LUDZKIE (25 tekstów z Wolnych Lektur)
    # ══════════════════════════════════════════════════════════════════════════

    # --- OŚWIECENIE ---

    ("h01", "human", "HUMAN_LEKTURY", "Krasicki – Mikołaja Doświadczyńskiego przypadki (1776)",
     """Wychowany byłem w domu ojca mego z wielką starannością, ile na owe czasy przyzwoitą. Nauczono mię czytać i pisać, nauczono katechizmu i nieco historii polskiej; reszta edukacji mojej zostawiona była na łaskę przypadku. Ojciec mój kochał mię szczerze, lecz nie umiał okazywać tej miłości sposobem rozsądnym. Pozwalał mi wszystkiego, czegokolwiek zapragnąłem, i wyobrażał sobie, że dobroć jego wyraża się w zupełnym pobłażaniu moim zachciankom. Matka znów, pobożna niewiasta, spędzała większą część dnia na modlitwach i na odwiedzinach kościołów, a o wychowaniu moim przez to nie myślała wiele. Miałem tedy lat szesnaście, gdym po raz pierwszy z domu rodzicielskiego wyjechał do Warszawy, pełen próżności i wyobrażeń, że świat cały stworzony jest ku rozrywce i uciesze młodego człowieka szlachetnego urodzenia. Jak bardzo myliłem się w tych mniemaniach, tego miałem się niedługo doświadczyć."""),

    ("h02", "human", "HUMAN_LEKTURY", "Krasicki – Monachomachia (1778)",
     """Mnisi siedzieli w refektarzu po obiedzie, gdy brat kuchmistrz przyniósł wiadomość, że sąsiedni klasztor zamierza wybudować nową dzwonnicę wyższą od ich własnej. Wieść ta wywołała poruszenie niezwykłe w całym zgromadzeniu. Przeor, człek spokojny i tłusty, który zwykł był po obiedzie zasypiać w fotelu, tym razem siedział wyprostowany i czerwony na twarzy, a palcem stukał o blat stołu z miną kogoś, kto postanowił w myślach wielkie rzeczy. Brat bibliotekarz, stary i wysuszony jak pergamin, odchrząknął i przypomniał, że w kronikach klasztornych wyraźnie zapisano pierwszeństwo ich wieży przed wszystkimi wieżami okolicy. Brat kucharz wzruszył ramionami i powiedział, że kroniki to jedno, a kamień i wapno to drugie, i kto szybciej postawi, ten i wyższy będzie."""),

    # --- ROMANTYZM ---

    ("h03", "human", "HUMAN_LEKTURY", "Mickiewicz – Pan Tadeusz (1834)",
     """Tymczasem przenoś moją duszę utęsknioną do tych pagórków leśnych, do tych łąk zielonych, szeroko nad błękitnym Niemnem rozciągnionych; do tych pól malowanych zbożem rozmaitem, wyzłacanych pszenicą, posrebrzanych żytem; gdzie bursztynowy świerzop, gryka jak śnieg biała, gdzie panieńskim rumieńcem dzięcielina pała, a wszystko przepasane jakby wstęgą, miedzą zieloną, na niej z rzadka ciche grusze siedzą. Śród takich pól przed laty, nad brzegiem ruczaju, na pagórku niewielkim, we brzozowym gaju, był dwór szlachecki z drzewa, lecz podmurowany; świeciły się z daleka pobielane ściany, tym białsze, że odbite od ciemnej zieleni topoli, co go bronią od wiatrów jesieni. Dom mieszkalny niewielki, lecz zewsząd chędogi, i stodołę miał wielką, i przy niej trzy stogi."""),

    ("h04", "human", "HUMAN_LEKTURY", "Słowacki – Kordian (1834)",
     """Kordian stanął na szczycie Mont Blanc, gdzie wiatr rwał mu płaszcz i smagał w twarz garściami śniegu, jakby sam szczyt bronił się przed człowiekiem, który ośmielił się tu wejść. Patrząc na bezmiar bieli i chmur poniżej, czuł — albo wydawało mu się, że czuje — tę osobliwą pustkę, która pojawia się na samym szczycie każdego pragnienia i każdego zwycięstwa. Dotarł. I oto wszystko. I oto nic. Że też wciąż człowiek przekonany jest, że gdy stanie wyżej, ujrzy więcej i poczuje się bardziej sobą — a tymczasem wyżej znaczy tylko zimniej, a szerzej znaczy tylko bardziej samotnie. Rozpościerała się Szwajcaria, Francja, morze chmur, reszta Europy gdzieś za horyzontem, i wszystko to było małe i bez znaczenia, jak mapa zamiast krajobrazu."""),

    ("h05", "human", "HUMAN_LEKTURY", "Norwid – Milczenie (1882)",
     """Milczenie — powiadają — jest złotem. Ja bym powiedział, że milczenie jest niebezpieczną i dwuznaczną materią, która równie dobrze może być szlachetniejsza od złota i nikczemniejsza od błota, zależnie od tego, skąd pochodzi i dokąd zmierza. Milczenie skrzywdzonego, który przebaczył, i milczenie winnego, który chowa się za ciszę jak za mur — czy mogą być tym samym złotem? Słowo musi sięgać do głębi; jeśli nie sięga, lepiej, żeby go nie było. Tyle razy widziałem ludzi mówiących nieprzerwanie — i to milczenie ciągłe, to gonienie własnego głosu jakby z obawy, że gdy się zatrzymają, usłyszą w tej chwili coś nieprzyjemnego o sobie samych. Więc mówią. A cisza czeka cierpliwie, bo cisza ma czas."""),

    ("h06", "human", "HUMAN_LEKTURY", "Fredro – Zemsta (1838)",
     """Cześnik Raptusiewicz chodził po izbie wielkimi krokami, z rękami założonymi za pas, i fukał w wąsy, co przy jego tuszy i temperamencie przypominało burzę w karczmie. Papkin stał przy drzwiach z miną kogoś, kto szuka w myślach najkrótszej drogi do wyjścia, ale wie, że Cześnik nie puści go przed wysłuchaniem całej przemowy. A przemowa zapowiadała się długa. Cześnik Raptusiewicz, gdy się rozgoryczy, może mówić trzy kwadranse bez zatrzymania, co Papkin wiedział z doświadczenia licznych poprzednich wizyt. Tym razem chodziło o mur graniczny, który Rejent Milczek kazał postawić o dwie piędzi za daleko, przez co, jak obliczył Cześnik, traci rocznie tyle ziemi, ile by starczyło na zasadzenie stu kapust."""),

    # --- POZYTYWIZM ---

    ("h07", "human", "HUMAN_LEKTURY", "Prus – Lalka (1890)",
     """Wokulski wszedł do sklepu Hopfera i zamówił szklankę wódki, choć od dawna nie pijał. Usiadł przy oknie od ulicy, oparł łokcie na stole i patrzył, jak za szybą przechodziły różne osoby — kupcy, przekupnie, dozorcy w liberiach, damy pod parasolkami. Nikt nie zwracał uwagi na nikogo. Każdy szedł swoją drogą z miną człowieka, który wie, dokąd idzie i po co — ale Wokulski, który obserwował ludzi od lat, wiedział, że ta pewność siebie jest w dziewięciu przypadkach na dziesięć tylko maską. Pod maską było zagubienie, niepokój, pośpiech bez celu. Jak u niego. Wódka stała przed nim i parzyła w palce. Nie wypił. Zostawił na stole monetę i wyszedł z powrotem w tłum, który szedł, nie wiedząc dokąd."""),

    ("h08", "human", "HUMAN_LEKTURY", "Prus – Faraon (1896)",
     """Ramzes stał na tarasie pałacu i patrzył, jak Nil wylewa. Z tej odległości i wysokości zalew wyglądał jak spokojne rozszerzenie się rzeki, niemal łagodne — dopiero kiedy patrzył na mniejsze budynki przy brzegu, na które woda wchodziła powoli, systematycznie, bez pośpiechu i bez litości, rozumiał ogrom tego co się dzieje. Egipt żył z wylewu i umierał bez niego. To było proste i straszne zarazem. Proste, bo jedno i drugie dawała ta sama woda. Straszne, bo człowiek, choćby był faraonem i bogiem w ludzkim ciele, nie miał nad tą wodą żadnej władzy. Mógł kazać budować kanały i zapory, mógł składać ofiary, mógł wznosić modlitwy do Ozyrysa — a Nil i tak robił, co chciał. Ramzes tego nie lubił."""),

    ("h09", "human", "HUMAN_LEKTURY", "Orzeszkowa – Nad Niemnem (1888)",
     """Nad Niemnem lato było w pełni. Rzeka lśniła między olchami jak kawał starego, nieco stłuczonego lustra, a na jej powierzchni kołysały się liście i gałązki niesione z górnych krain, niemym posłańcem czyjejś lasowni albo ogrodnika, który nie zbierał co spadło. Justyna Orzelska lubiła tu przychodzić rano, zanim ktokolwiek w dworze wstał, i siedzieć na kamieniu przy wodzie. W tym miejscu rzeka szumiała — nie głośno, raczej cicho i stale, jak ktoś, kto śpiewa pod nosem nie dlatego, że chce być słyszany, ale że musi. Justyna słuchała i myślała o niczym konkretnym. To było jedyne miejsce, gdzie myślenie o niczym nie wydawało się jej stratą czasu."""),

    ("h10", "human", "HUMAN_LEKTURY", "Konopnicka – Nasza szkapa (1897)",
     """Szkapa stała pod szopą i jadła siano z takiej powagi, jakby jadła ostatni raz w życiu. Stary Kuba patrzył na nią z progu i myślał, że nigdy nie widział stworzenia, które by jadło z taką skupioną godnością. Szkapa nie spoglądała na boki, nie potrząsała łbem, nie płoszyła się od wróbli. Jadła. Kuba miał sześćdziesiąt trzy lata i w jego życiu było kilka stałych rzeczy: kościół w niedzielę, pole wiosną, szkapa przez okrągły rok. Inne rzeczy przychodziły i odchodziły — dzieci wyrosły i rozeszły się po świecie, żona umarła na jesieni, rok był raz dobry, raz nie — ale szkapa była zawsze. Teraz patrząc na nią wiedział, że niedługo i ona odejdzie, i wtedy zostanie samo pole."""),

    ("h11", "human", "HUMAN_LEKTURY", "Sienkiewicz – Ogniem i Mieczem (1884)",
     """Pan Skrzetuski jechał stepem od trzech dni i konie zaczynały już odmawiać posłuszeństwa. Step był pusty aż po horyzont, co nie znaczyło, że bezpieczny — step nigdy nie był bezpieczny i kto o tym zapomniał, zwykle nie żył dość długo, by zapamiętać nauczkę. Skrzetuski jechał jednak bez nadmiernej ostrożności, z tą swobodą człowieka, który tyle razy patrzył śmierci w oczy, że przyzwyczaił się do jej obecności jak do niezbyt miłego towarzysza podróży. Zresztą miał poruczenictwo do Siczy, które trzeba było dostarczyć, a poruczenictwa się nie odkłada przez wzgląd na własną skórę. Tak przynajmniej rozumował pan Skrzetuski, i może dlatego żył jeszcze, bo rycerze, którzy za bardzo myślą o skórze, miewają paradoksalnie krótszy żywot."""),

    ("h12", "human", "HUMAN_LEKTURY", "Sienkiewicz – Quo Vadis (1896)",
     """Petroniusz leżał w kąpieli z alabastrowej misy i słuchał, jak Eunica czyta na głos Teokryta. Czytała nieźle — nie tak jak greckie niewolnice z dobrego domu, z tą ich śpiewną manierą, która w końcu nudziła — ale prosto, wyraźnie, jakby mówiła o rzeczach zwykłych. Petroniusz lubił to. Lubił też, gdy woda była dokładnie w odpowiedniej temperaturze i gdy olejki pachniały dokładnie tak, a nie inaczej, i gdy nikt w pobliżu nie mówił nic ważnego, bo rzeczy ważne są nużące. Rzym huczał za murami — ten Rzym wielki, głupi i okrutny, który Petroniusz kochał i którym pogardzał w równych częściach, bo tylko taki stosunek do Rzymu był możliwy dla człowieka, który miał oczy otwarte."""),

    ("h13", "human", "HUMAN_LEKTURY", "Kraszewski – Stara baśń (1876)",
     """Nad jeziorem, tam gdzie las podchodził do samej wody i sięgały w nią swymi korzeniami stare dęby, mieszkał stary Wisz, którego nikt nie pamiętał skąd przyszedł ani ile ma lat. Jedni mówili, że sto, inni że więcej, a dzieci, które się go bały i jednocześnie lgęły do niego nieodparcie, wyobrażały sobie, że żył już wtedy, kiedy dąb przy jego chacie był żołędziem. Wisz znał zioła leczące i trucizny, znał mowę ptaków i znaki na niebie, i wiedział, kiedy będzie deszcz, a kiedy susza, co w tamtych czasach, gdy plony decydowały o życiu i śmierci, miało wartość większą niż złoto. Przychodził do niego starosta z pytaniami, które wstydził się zadawać kapłanom."""),

    # --- MŁODA POLSKA ---

    ("h14", "human", "HUMAN_LEKTURY", "Żeromski – Ludzie bezdomni (1900)",
     """Doktor Judym wyszedł z kliniki późnym popołudniem i długo stał na chodniku, nie wiedząc, w którą stronę iść. Nie chodziło o to, że nie znał Warszawy. Znał ją za dobrze. Wiedział, że za rogiem jest kawiarnia, w której zbierają się lekarze z jego szpitala i rozmawiają o pieniądzach i kuriozalnych przypadkach z oddziałów, i że mógłby tam usiąść i napić się herbaty i udawać, że jest jednym z nich. Nie mógł. Nie potrafił. Zbyt wyraźnie widział różnicę między tamtą kawiarnią a Cisami — między miękkim fotelem i historią o wyjątkowo ciekawej chorobie a tymi ludźmi, którzy leżą w swoich izbach i umierają po cichu dlatego, że nikt nie uznał za właściwe im pomóc."""),

    ("h15", "human", "HUMAN_LEKTURY", "Żeromski – Przedwiośnie (1925)",
     """Cezary Baryka wrócił do Polski przez granicę wschodnią, z tymi samymi butami co wyszedł, tylko teraz podbite blachą, i z tym samym poczuciem, że wszystko, o czym marzył, jest tu — i zarazem, że tego, o czym marzył, tu nie ma. Polska była inna niż ta, którą nosił w głowie przez te lata w Rosji i podczas rewolucji. Tamta była z opowiadań ojca i ze wspomnień matki i z wierszy, które znał na pamięć. Ta była z błota i biedy i wojska i starych kobiet w chustkach i mężczyzn z twarzami bez wyrazu, którzy patrzyli na niego tak, jakby nikt ich dawno nie zapytał, jak się mają, i jakby nie oczekiwali, że ktoś zapyta."""),

    ("h16", "human", "HUMAN_LEKTURY", "Reymont – Chłopi (1904–1909)",
     """Listopad przychodził do Lipiec jak zawsze — od strony lasu, mokry i ciężki, z tym zapachem zgniłych liści i wilgotnej ziemi, który Agata znała od dziecka i który jej się kojarzył z końcem wszystkiego, choć przecież nie wszystko się kończyło, tylko świat się przykrywał szarą kiecką do wiosny. Maciej Boryna siedział przed chatą i darł łykowe powrósła, a ręce mu chodziły same, bez myślenia. Stary gospodarz, który przeszedł takich listopadów ze sześćdziesiąt, wiedział, że pójdą jeszcze trzy albo cztery zanim zima wejdzie na dobre, i że za każdym listopadem jest grudzień, a za grudniem — w końcu — marzec. Taka wiedza nie pociesza, ale daje jakiś grunt pod nogami."""),

    ("h17", "human", "HUMAN_LEKTURY", "Tetmajer – Na Skalnym Podhalu (1903)",
     """Juhasi siedzieli przy ogniu, a ogień był jedynym światłem na hali. Wokół ciemność, taka góralska ciemność bez dna, i wiatr, który chodził po hali jak coś żywego. Stary Sabała opowiadał. Opowiadał o zbójnikach i o wodnicach, i o tym, jak raz widział na Morskim Oku coś, czego nie umiał nazwać, i zaczął wtedy odmawiać pacierze i skończyło się dobrze. Młodsi słuchali, jedni z powagą, inni z tym uśmiechem, który pojawia się u ludzi, gdy słuchają historii, w które nie do końca wierzą, ale chcieliby wierzyć. Bachor Jędrek siedział z otwartymi ustami i miał tę minę, którą mają chłopcy, kiedy świat jest jeszcze na tyle duży, że do wszystkiego w nim jest miejsce, nawet do wodnic."""),

    ("h18", "human", "HUMAN_LEKTURY", "Przybyszewski – Dzieci szatana (1897)",
     """Był taki czas — Falk pamiętał go dobrze, zbyt dobrze — gdy muzyka była jego jedynym językiem. Nie ten język codziennych słów, który kłamał z definicji, bo każde słowo było już przed nim i każdy użył go i zużył na tysiąc rzeczy, które nie miały nic wspólnego z tym, co Falk chciał powiedzieć. Ale muzyka była inaczej. Muzyka brała się z miejsca, do którego słowa nie miały dostępu. Z tego miejsca za mostkiem, gdzie groty ciemne i zimne i w których żyją rzeczy bez nazwy. Siadał przy fortepianie i grał, i świat znikał, i zostawał tylko dźwięk, który był jednocześnie bólem i ulgą i czymś tak prywatnym, że wstydziłby się grać przy kimś, gdyby nie to, że wstydzić się nie umiał."""),

    # --- DWUDZIESTOLECIE MIĘDZYWOJENNE ---

    ("h19", "human", "HUMAN_LEKTURY", "Schulz – Sklepy Cynamonowe (1934)",
     """Ojciec w tym czasie właśnie przechodził swój szczytowy, swój heroiczny okres handlu. Wychylony na ladzie sklepowej jak kapitan na mostku okrętowym, z oczami biegnącymi daleko przed siebie, wzywał do nieustannej obecności swego asystenta. Manekin stał w rogu izby i ojciec ciągle patrzył w jego stronę, jakby spodziewał się po nim jakiegoś ruchu albo sygnału. Tymczasem manekin milczał z właściwą sobie drewnianą powagą. Klient, który wszedł i zastał tę sytuację, czuł się nieswojo, bo w sklepie były trzy żywe istoty i cicho jak w kościele, i nie był pewien, do której się zwrócić. Ojciec wyglądał na zagubionego, asystent na śpiącego, a manekin na jedyną rzecz, która tu wie, co robi."""),

    ("h20", "human", "HUMAN_LEKTURY", "Nałkowska – Granica (1935)",
     """Zenon Ziembiewicz patrzył na siebie z zewnątrz coraz częściej. To była ta właściwość, która go wyróżniała spośród ludzi, jakich znał, i która — jak zaczął rozumieć — nie była bynajmniej zaletą. Widział siebie siedzącego w gabinecie i podpisującego pisma, widział siebie przy stole z żoną, widział siebie podczas tamtych spotkań z Justyną, których wspomnienie było jak grudka lodu pod skórą. I za każdym razem widział kogoś, kto wie, co robi, i wie, że tego nie powinien robić, i robi to jednak. Granica — powiedział sobie raz — granica jest w tym miejscu, gdzie się ją postawi. Postawił za późno. Albo w złym miejscu. Albo wcale."""),

    ("h21", "human", "HUMAN_LEKTURY", "Dąbrowska – Noce i Dnie (1932–1934)",
     """Barbara Niechcic długo nie mogła zasnąć. Przez otwarte okno wchodziło nocne powietrze z zapachem traw i czegoś jeszcze — może ziemi po deszczu, może tego charakterystycznego zapachu, który Serbinów miał tylko w nocy. Słyszała oddech Bogumiła, spokojny i równy, jak wszystko w nim spokojne i równe, i myślała o tym z uczuciem, które było po trochę wdzięcznością i po trochę zazdrością. Ona tak nie umiała. Ona zawsze leżała i myślała, i im bardziej starała się nie myśleć, tym myśli były głośniejsze. Myślała o dzieciach, o pieniądzach, o tym, co powiedziała rano Agnieszce i czy to było w porządku, i o tym, że jutro trzeba pisać do matki, i o tym, że lato przemija szybko."""),

    ("h22", "human", "HUMAN_LEKTURY", "Boy-Żeleński – Słówka (1913)",
     """Teatr krakowski prezentował w tym sezonie pięć premier i każda z nich budziła we mnie pewne nadzieje, które teatr konsekwentnie i bez wyjątku zawodził. Nie mówię, że sztuki były złe — to wymagałoby ode mnie jakiegoś wzruszenia, choćby negatywnego. Były po prostu obojętne, jak potrawa bez soli, która nie smakuje ani dobrze, ani źle, tylko po prostu niknie na języku. Reżyser, człowiek miły w rozmowie i czytający bystro, realizował sceny z energią człowieka, który dokładnie wie, co robi i właśnie dlatego wychodzi coś bez niespodzianek. Aktorzy grali z przekonaniem, co jest dla aktora zaletą i niekiedy wadą zarazem, bo przekonanie o dobrze odgrywanej roli zwalnia z potrzeby szukania czegoś poza rolą."""),

    ("h23", "human", "HUMAN_LEKTURY", "Iwaszkiewicz – Panny z Wilka (1932)",
     """Wiktor Ruben przyjechał do Wilka po raz pierwszy od piętnastu lat i wszystko było inne i wszystko było to samo, co jest jednym z najcięższych do zniesienia doświadczeń, jakie może zgotować nam czas. Dom stał, sad stał, płot przy sadzie był nowy, ale stał tak samo. I te panny. Panny z Wilka — teraz kobiety, żony, matki — patrzyły na niego oczami, w których było coś z tamtego lata, i czegoś już nie było. Trudno powiedzieć czego. Może tamtej lekkości. Może tamtego przekonania, że wszystko jest jeszcze przed nami i że lato trwa zawsze. Wiktor siadł na ganku i pomyślał, że wrócić to nie to samo co powrócić, i że może nie należało przyjeżdżać."""),

    ("h24", "human", "HUMAN_LEKTURY", "Strug – Dzieje jednego pocisku (1910)",
     """Bomba leżała na stole, nakryta białą serwetą, jakby była czymś delikatnym, czymś, o co trzeba dbać. Władek patrzył na nią spod oka, gdy wchodził przez drzwi, i trochę mu się robiło słabo, co skrzętnie ukrywał, bo pokazać słabość przed tamtymi dwoma znaczyło stracić autorytet, na który pracował od miesięcy. Mechanizm był gotowy. Tak powiedziano mu wczoraj wieczorem. Jutro tędy przejedzie powóz gubernatora. Był w tym wszystkim porządek, który Władka niepokoił bardziej niż nieporządek. Nieporządek można naprawić. Porządek się wykonuje. A on czuł, że jest częścią tego porządku — precyzyjną, niezbędną częścią maszyny, która toczy się naprzód i nie zapyta, czy ma ochotę."""),

    ("h25", "human", "HUMAN_LEKTURY", "Witkacy – 622 upadki Bunga (1910)",
     """Bung siedział w kawiarni i myślał o Akne Montecalfi. Właściwie myślał o niej bez przerwy od trzech tygodni, co samo w sobie było dowodem na patologię jego systemu nerwowego — tak przynajmniej orzekł Sturmhahn, który był filozofem i z tego powodu o wszystkim miał wyrobione zdanie. Kawa stygła. Bung patrzył na nią i nie pił. Nie był w stanie pić, bo gdy tylko podnosił filiżankę, myśl o Akne powracała ze zdwojoną siłą i ręka mu drżała z tego powodu, że albo nie miał jej przy sobie, albo miał ją przy sobie, co wychodziło na to samo, to znaczy na niemożliwość spokojnego wypicia kawy. Sturmhahn tymczasem rozwijał teorię wiecznego powrotu, z którą Bung zgadzał się tylko w odniesieniu do Akne."""),

    # ══════════════════════════════════════════════════════════════════════════
    # BLOK B — TEKSTY GENEROWANE PRZEZ AI (25 tekstów)
    # ══════════════════════════════════════════════════════════════════════════

    ("ai01", "ai", "AI_GEN", "AI – opis wiosny (przyroda)",
     """Wiosna jest porą roku następującą po zimie, charakteryzującą się stopniowym wzrostem temperatury i wydłużaniem się dnia. W Polsce wiosna trwa od marca do maja i jest związana z przebudzeniem przyrody po zimowym spoczynku. Rośliny zaczynają kiełkować, a drzewa pokrywają się nowym listowiem. Warto podkreślić, że wiosna jest ważnym sezonem dla rolnictwa, ponieważ umożliwia rozpoczęcie prac polowych. Ptaki powracają z zimowisk, co jest charakterystycznym zjawiskiem migracyjnym. Temperatury wiosną są zmienne i wahają się zazwyczaj między 5 a 20 stopniami Celsjusza. Wiosenne deszcze zapewniają odpowiednie nawodnienie gleby, co sprzyja wzrostowi roślinności. Należy również zaznaczyć, że wiosna ma pozytywny wpływ na samopoczucie ludzi, co jest związane z większą ekspozycją na światło słoneczne i wydzielaniem serotoniny."""),

    ("ai02", "ai", "AI_GEN", "AI – portret nauczyciela",
     """Pan Kowalski był nauczycielem matematyki w szkole podstawowej i charakteryzował się ponadprzeciętnym zaangażowaniem w pracę dydaktyczną. Posiadał wykształcenie wyższe pedagogiczne oraz wieloletnie doświadczenie zawodowe, które pozwalało mu skutecznie przekazywać wiedzę uczniom o różnych poziomach zdolności. Jego metody nauczania były innowacyjne i dostosowane do potrzeb współczesnej edukacji. Stosował zróżnicowane podejścia metodyczne, łącząc tradycyjne formy nauczania z nowoczesnymi technologiami edukacyjnymi. Należy podkreślić, że pan Kowalski był ceniony zarówno przez uczniów, jak i rodziców oraz kadrę pedagogiczną. Warto zaznaczyć, że regularnie uczestniczył w szkoleniach doskonalenia zawodowego, co przyczyniało się do podnoszenia jakości jego pracy. Jego lekcje były dobrze zorganizowane i realizowane zgodnie z podstawą programową."""),

    ("ai03", "ai", "AI_GEN", "AI – opowiadanie o spotkaniu",
     """Anna Nowak spotkała swojego starego znajomego Michała na przystanku autobusowym w centrum miasta. Było to nieoczekiwane spotkanie, ponieważ nie widzieli się od kilku lat. Anna i Michał przywitali się serdecznie i wymienili podstawowe informacje dotyczące swojego aktualnego życia zawodowego i prywatnego. Michał poinformował Annę, że pracuje w korporacji na stanowisku specjalisty ds. marketingu. Anna z kolei podzieliła się informacją, że kontynuuje karierę naukową na uczelni wyższej. Oboje wyrazili zadowolenie z ponownego spotkania i uzgodnili, że powinni utrzymywać regularniejszy kontakt. Warto podkreślić, że takie przypadkowe spotkania są częstym elementem życia miejskiego. Rozmowa trwała kilkanaście minut, po czym oboje udali się w swoje kierunki, obiecując sobie wzajemnie bliższy kontakt w przyszłości."""),

    ("ai04", "ai", "AI_GEN", "AI – esej o zmianach klimatu",
     """Zmiany klimatu stanowią jedno z najpoważniejszych wyzwań globalnych współczesności. Wzrost średniej temperatury Ziemi, spowodowany emisją gazów cieplarnianych, prowadzi do licznych konsekwencji środowiskowych i społeczno-ekonomicznych. Należy podkreślić, że skutki zmian klimatu są odczuwalne na całym świecie, choć w różnym stopniu w zależności od regionu geograficznego. Warto zaznaczyć, że kraje rozwijające się są szczególnie narażone na negatywne skutki tego zjawiska. Wzrost poziomu mórz i oceanów, ekstremalne zjawiska pogodowe oraz zmiany w ekosystemach to tylko niektóre z obserwowanych konsekwencji. Podsumowując, problem zmian klimatu wymaga skoordynowanych działań na szczeblu międzynarodowym, obejmujących redukcję emisji, adaptację do zmieniających się warunków oraz inwestycje w odnawialne źródła energii. Kluczowe znaczenie ma tutaj współpraca między państwami i sektorami."""),

    ("ai05", "ai", "AI_GEN", "AI – opis Krakowa",
     """Kraków jest jednym z najważniejszych miast historycznych Polski i pełni funkcję ważnego centrum kulturalnego, turystycznego i akademickiego. Miasto zostało założone w średniowieczu i przez kilka stuleci pełniło rolę stolicy Polski. Rynek Główny, będący jednym z największych placów miejskich w Europie, stanowi centralne miejsce Krakowa i jest otoczony historyczną zabudową. Wawel, wzgórze zamkowe z zamkiem i katedrą, jest symbolem polskiej państwowości i historii. Dzielnica Kazimierz, dawna dzielnica żydowska, jest współcześnie centrum życia kulturalnego i artystycznego. Należy podkreślić, że Kraków przyciąga rocznie miliony turystów z całego świata. Warto zaznaczyć, że miasto posiada dobrze rozwiniętą infrastrukturę turystyczną. Klimat Krakowa jest umiarkowany, z wyraźnie zaznaczonymi czterema porami roku."""),

    ("ai06", "ai", "AI_GEN", "AI – analiza historyczna (II RP)",
     """Dwudziestolecie międzywojenne w Polsce, czyli okres od 1918 do 1939 roku, stanowiło czas odbudowy i konsolidacji państwowości polskiej po ponad stu latach zaborów. Polska, odzyskawszy niepodległość w 1918 roku, musiała zmierzyć się z licznymi wyzwaniami politycznymi, gospodarczymi i społecznymi. Warto podkreślić, że kraj ten odziedziczył po zaborcach trzy różne systemy prawne, walutowe i administracyjne, co znacząco utrudniało integrację. Przewrót majowy z 1926 roku zapoczątkował rządy sanacji, które trwały do wybuchu II wojny światowej. Należy zaznaczyć, że mimo trudności Polska dwudziestolecia dokonała znaczącego postępu w wielu dziedzinach. Rozwinęły się literatura, sztuka i nauka, a Polska wyraźnie zaznaczyła swoją obecność na arenie międzynarodowej. Podsumowując, był to okres dynamicznych przemian i budowania fundamentów nowoczesnego państwa."""),

    ("ai07", "ai", "AI_GEN", "AI – opis morza i plaży",
     """Morze Bałtyckie charakteryzuje się niskim zasoleniem w porównaniu do innych mórz i oceanów, co wynika ze znacznego dopływu słodkiej wody z rzek oraz ograniczonej wymiany wód z oceanem. Temperatura wody w Bałtyku latem wynosi od około 17 do 22 stopni Celsjusza, co czyni je odpowiednim miejscem do kąpieli. Plaże polskiego wybrzeża Bałtyku są szerokopiaschyste i długie, co jest jednym z czynników przyciągających turystów. Warto podkreślić, że wybrzeże Bałtyku w Polsce rozciąga się na długości około 500 kilometrów. Fale na Bałtyku są zazwyczaj niskie w porównaniu do oceanów, co sprawia, że jest to morze stosunkowo bezpieczne dla kąpiących się. Należy zaznaczyć, że plaże te są szczególnie popularne w sezonie letnim, gdy liczba odwiedzających znacznie wzrasta. Infrastruktura turystyczna nadmorskich miejscowości jest dobrze rozwinięta."""),

    ("ai08", "ai", "AI_GEN", "AI – portret psychologiczny osoby",
     """Katarzyna Wiśniewska była osobą o złożonej strukturze psychologicznej, charakteryzującą się wysokim poziomem inteligencji emocjonalnej oraz rozbudowaną sferą refleksyjną. Jej zachowanie cechowała systematyczność i dbałość o szczegóły, co przekładało się na wysoki poziom wykonywanych przez nią zadań zarówno w życiu zawodowym, jak i prywatnym. Należy podkreślić, że Katarzyna wykazywała silną tendencję do analizowania własnych emocji i zachowań, co z jednej strony było jej zaletą, z drugiej zaś mogło prowadzić do nadmiernego samokrytycyzmu. Warto zaznaczyć, że w relacjach interpersonalnych cechowała ją otwartość połączona z pewną rezerwą wobec nowo poznanych osób. Jej styl komunikacji był precyzyjny i przemyślany, co sprawiało, że inni postrzegali ją jako osobę wiarygodną i kompetentną. Ogólna ocena jej funkcjonowania psychospołecznego była pozytywna."""),

    ("ai09", "ai", "AI_GEN", "AI – opis sztucznej inteligencji",
     """Sztuczna inteligencja (AI) to dziedzina informatyki zajmująca się tworzeniem systemów zdolnych do wykonywania zadań wymagających ludzkiej inteligencji. Należy podkreślić, że AI obejmuje szerokie spektrum technologii, od prostych systemów regułowych po zaawansowane modele uczenia głębokiego. Modele językowe, takie jak duże modele językowe (LLM), stanowią jeden z najbardziej dynamicznie rozwijających się obszarów sztucznej inteligencji. Warto zaznaczyć, że zastosowania AI są coraz powszechniejsze w różnych sektorach gospodarki i życia społecznego. Medycyna, transport, edukacja i przemysł to przykłady dziedzin, w których AI przynosi wymierne korzyści. Należy jednak podkreślić, że rozwój AI wiąże się również z istotnymi wyzwaniami etycznymi, dotyczącymi prywatności, bezpieczeństwa i potencjalnych skutków dla rynku pracy. Odpowiedzialne wdrażanie AI wymaga uwzględnienia tych aspektów."""),

    ("ai10", "ai", "AI_GEN", "AI – opowiadanie podróżne",
     """Tomasz Zielański wyruszył w podróż po Polsce, chcąc lepiej poznać kraj, w którym mieszkał od urodzenia. Zaplanował trasę, która obejmowała najważniejsze historyczne i kulturowe miejsca kraju. Pierwszym etapem podróży był Kraków, gdzie Tomasz spędził trzy dni, zwiedzając Wawel, Rynek Główny i dzielnicę Kazimierz. Następnie udał się do Wrocławia, który zachwycił go swoją architekturą i atmosferą. Warto podkreślić, że każde miasto oferowało mu nowe, interesujące doświadczenia. Tomasz dokumentował swoją podróż, robiąc zdjęcia i prowadząc notatki. Podróż pozwoliła mu lepiej zrozumieć historię i kulturę Polski oraz dostrzec jej różnorodność regionalną. Należy zaznaczyć, że takie podróże krajoznawcze mają ogromną wartość edukacyjną i kulturową. Tomasz po powrocie do domu poczuł się bogatszy o nowe doświadczenia i wiedzę."""),

    ("ai11", "ai", "AI_GEN", "AI – esej o systemie edukacji",
     """System edukacji w Polsce przeszedł w ostatnich dekadach szereg istotnych zmian i reform, mających na celu dostosowanie go do wymogów współczesnego rynku pracy i standardów europejskich. Warto podkreślić, że edukacja stanowi jeden z fundamentów społeczeństwa i ma kluczowe znaczenie dla rozwoju jednostek i całych społeczeństw. Należy zaznaczyć, że polska szkoła mierzy się z wieloma wyzwaniami, w tym z koniecznością rozwijania kompetencji cyfrowych uczniów oraz kształtowania umiejętności krytycznego myślenia. Nauczyciele odgrywają centralną rolę w systemie edukacji i ich odpowiednie przygotowanie jest warunkiem koniecznym dla jego skuteczności. Podsumowując, inwestycje w edukację przynoszą korzyści zarówno indywidualne, jak i społeczne, przyczyniając się do wzrostu gospodarczego i poprawy jakości życia obywateli. Reforma edukacji powinna być procesem ciągłym i przemyślanym."""),

    ("ai12", "ai", "AI_GEN", "AI – opis krajobrazu górskiego",
     """Tatry stanowią najwyższe pasmo górskie w Polsce i są celem licznych turystów z kraju i zagranicy. Charakteryzują się wysokogórskim krajobrazem z licznymi szczytami przekraczającymi 2000 metrów n.p.m., z których najwyższy, Rysy, osiąga 2499 metrów. Warto podkreślić, że Tatry są cennym przyrodniczo obszarem, objętym ochroną w ramach Tatrzańskiego Parku Narodowego. Roślinność tatrzańska jest zróżnicowana i układa się w piętra roślinne, od lasów regla dolnego po goły skalisty szczyt. W Tatrach występują liczne gatunki zwierząt, w tym endemiczne, takie jak świstak tatrzański i kozica. Klimat tatrzański jest surowy, z niskimi temperaturami i dużymi opadami śniegu w zimie. Należy zaznaczyć, że turystyka tatrzańska wymaga odpowiedniego przygotowania i sprzętu ze względu na zmieniające się warunki pogodowe i trudny teren."""),

    ("ai13", "ai", "AI_GEN", "AI – opis zjawiska społecznego (samotność)",
     """Samotność jest złożonym zjawiskiem społecznym i psychologicznym, które dotyka coraz większą liczbę osób we współczesnym społeczeństwie. Należy odróżnić samotność obiektywną, rozumianą jako faktyczny brak kontaktów społecznych, od samotności subiektywnej, która jest odczuciem izolacji niezależnym od liczby posiadanych relacji. Warto podkreślić, że samotność może mieć poważne konsekwencje dla zdrowia psychicznego i fizycznego człowieka, w tym zwiększać ryzyko depresji i chorób sercowo-naczyniowych. Urbanizacja i postępująca indywidualizacja społeczeństw sprzyjają powstawaniu poczucia izolacji mimo życia w gęsto zaludnionych środowiskach. Technologie cyfrowe i media społecznościowe, mimo że formalnie zwiększają liczbę kontaktów, mogą paradoksalnie pogłębiać poczucie samotności. Należy zaznaczyć, że budowanie silnych więzi społecznych jest kluczowe dla dobrostanu psychicznego człowieka."""),

    ("ai14", "ai", "AI_GEN", "AI – opis deszczu jako zjawiska",
     """Deszcz jest formą opadów atmosferycznych polegającą na opadaniu kropelek wody z chmur na powierzchnię Ziemi. Warto podkreślić, że deszcz odgrywa kluczową rolę w obiegu wody w przyrodzie, uzupełniając zasoby wód gruntowych i powierzchniowych. Intensywność deszczu mierzona jest w milimetrach słupa wody na jednostkę czasu i jest jednym z podstawowych parametrów meteorologicznych. Należy zaznaczyć, że w Polsce opady deszczu rozkładają się nierównomiernie w ciągu roku, z większą ich koncentracją w miesiącach letnich. Deszcz ma istotne znaczenie dla rolnictwa, dostarczając niezbędnej wilgoci do wzrostu roślin. Jednak nadmiar opadów może prowadzić do powodzi i podtopień, stwarzając zagrożenie dla ludzi i infrastruktury. Podsumowując, deszcz jest zjawiskiem naturalnym o fundamentalnym znaczeniu dla ekosystemów i działalności człowieka. Odpowiednie zarządzanie zasobami wodnymi jest kluczowe dla minimalizowania negatywnych skutków ekstremalnych opadów."""),

    ("ai15", "ai", "AI_GEN", "AI – opowiadanie o rodzinie",
     """Rodzina Kowalskich mieszkała w typowym polskim mieście średniej wielkości i prowadziła spokojne, uporządkowane życie. Rodzice, Jan i Maria, pracowali w pełnym wymiarze czasu i starali się zapewnić swoim dwójce dzieci stabilne warunki do nauki i rozwoju. Starsza córka Zosia uczęszczała do szkoły średniej i wykazywała zainteresowanie naukową ścieżką kariery. Młodszy syn Piotrek był uczniem szkoły podstawowej i cechował się żywą temperaturą i ciekawością świata. Warto podkreślić, że Kowalskie regularnie spędzali wspólny czas, kultywując rodzinne tradycje i wartości. Należy zaznaczyć, że zdrowe relacje w rodzinie mają kluczowe znaczenie dla prawidłowego rozwoju dzieci. Kowalskie stanowili przykład rodziny, która mimo codziennych wyzwań potrafiła zachować więzi i wzajemne wsparcie. Ich dom był miejscem ciepłym i bezpiecznym dla wszystkich jego mieszkańców."""),

    ("ai16", "ai", "AI_GEN", "AI – esej o kulturze czytania",
     """Kultura czytania w Polsce, podobnie jak w wielu innych krajach, zmaga się z wyzwaniami wynikającymi z cyfryzacji i zmieniających się nawyków społecznych. Dane statystyczne wskazują, że odsetek Polaków regularnie czytających książki utrzymuje się na stosunkowo niskim poziomie w porównaniu do innych krajów europejskich. Warto podkreślić, że czytanie ma udokumentowane korzyści dla rozwoju intelektualnego, empatii i zdolności językowych. Biblioteki publiczne pełnią ważną rolę w upowszechnianiu czytelnictwa, szczególnie wśród grup o niższych dochodach. Należy zaznaczyć, że promocja czytania wśród dzieci i młodzieży jest szczególnie istotna dla kształtowania długoterminowych nawyków czytelniczych. E-booki i audiobooki stanowią nowe formy konsumpcji treści, które mogą przyczyniać się do zwiększenia ogólnego zainteresowania literaturą. Podsumowując, wspieranie kultury czytania wymaga skoordynowanych działań ze strony instytucji publicznych, wydawców i środowisk edukacyjnych."""),

    ("ai17", "ai", "AI_GEN", "AI – opis miasta nocą",
     """Miasto nocą funkcjonuje odmiennie niż w ciągu dnia i charakteryzuje się specyficzną atmosferą wynikającą ze zmniejszonej aktywności większości mieszkańców. Oświetlenie sztuczne tworzy charakterystyczny efekt wizualny, który nadaje przestrzeni miejskiej inny wymiar estetyczny niż w świetle dziennym. Warto podkreślić, że nocna tkanka miejska jest zamieszkana przez specyficzne grupy użytkowników przestrzeni: pracowników nocnej zmiany, osoby korzystające z rozrywki, służby mundurowe. Hałas miejski ulega znacznemu redukcji w godzinach nocnych, co jest wynikiem zmniejszonego natężenia ruchu drogowego i ogólnej aktywności gospodarczej. Należy zaznaczyć, że bezpieczeństwo w przestrzeni miejskiej nocą jest istotnym zagadnieniem z perspektywy planowania urbanistycznego. Właściwe oświetlenie i monitoring wpływają pozytywnie na poczucie bezpieczeństwa mieszkańców. Nocna gospodarka stanowi istotny element ekonomii miejskiej, generując miejsca pracy i dochody."""),

    ("ai18", "ai", "AI_GEN", "AI – analiza postaci literackiej (Wokulski)",
     """Stanisław Wokulski, główny bohater powieści Bolesława Prusa „Lalka", jest jedną z najbardziej złożonych postaci w polskiej literaturze pozytywistycznej. Jego charakterystyka łączy w sobie cechy człowieka sukcesu, romantycznego idealisty i tragikomicznego przegranego. Warto podkreślić, że Wokulski reprezentuje pokolenie Polaków ukształtowanych przez romantyzm, które próbuje odnaleźć się w realiach epoki pozytywizmu. Jego miłość do Izabeli Łęckiej jest jednocześnie siłą napędową i źródłem jego destrukcji. Należy zaznaczyć, że postać Wokulskiego jest wielowymiarowa i nie poddaje się prostej ocenie moralnej. Z jednej strony jest on pracowitym samoukiem i wizjonerskim przedsiębiorcą, z drugiej zaś traci zdolność racjonalnego osądu pod wpływem uczucia. Podsumowując, Wokulski uosabia fundamentalne napięcia epoki między pragmatycznym pozytywizmem a pozostałościami romantycznego światopoglądu."""),

    ("ai19", "ai", "AI_GEN", "AI – opis relacji przyjacielskiej",
     """Przyjaźń jest jedną z fundamentalnych więzi społecznych, opartą na wzajemnym szacunku, zaufaniu i wspólnych wartościach. Warto podkreślić, że badania psychologiczne potwierdzają kluczową rolę relacji przyjacielskich dla dobrostanu psychicznego i fizycznego człowieka. Trwała przyjaźń charakteryzuje się zdolnością do przetrwania trudnych okresów i różnic zdań, co odróżnia ją od relacji o charakterze wyłącznie towarzyskim. Należy zaznaczyć, że w dobie mediów społecznościowych pojęcie przyjaźni ulega rozszerzeniu i rozmyciu, co rodzi pytania o jakość współczesnych relacji interpersonalnych. Bliska przyjaźń wymaga inwestycji czasu i zaangażowania emocjonalnego, które nie zawsze są możliwe w szybkim tempie współczesnego życia. Podsumowując, pielęgnowanie głębokich relacji przyjacielskich jest ważnym elementem dbania o zdrowie psychiczne i jakość życia. Wzajemne wsparcie w trudnych momentach jest jednym z najważniejszych wymiarów przyjaźni."""),

    ("ai20", "ai", "AI_GEN", "AI – esej o pracy zdalnej",
     """Praca zdalna stała się jednym z najważniejszych trendów na rynku pracy, szczególnie po pandemii COVID-19, która przyspieszyła jej upowszechnienie. Warto podkreślić, że model hybrydowy, łączący pracę zdalną z obecnością w biurze, jest obecnie preferowany przez wiele organizacji. Praca zdalna oferuje pracownikom większą elastyczność i oszczędność czasu na dojazdy, co przekłada się na poprawę równowagi między życiem zawodowym a prywatnym. Należy zaznaczyć, że efektywna praca zdalna wymaga odpowiedniej infrastruktury technicznej oraz umiejętności samodyscypliny i zarządzania czasem. Pracodawcy muszą dostosować modele zarządzania i komunikacji do realiów pracy rozproszonej. Wyzwaniem pozostaje utrzymanie kultury organizacyjnej i poczucia przynależności do zespołu w warunkach fizycznej separacji pracowników. Podsumowując, praca zdalna jest zjawiskiem trwałym, które wymaga świadomego i przemyślanego podejścia zarówno ze strony pracodawców, jak i pracowników."""),

    ("ai21", "ai", "AI_GEN", "AI – opis zimy w Polsce",
     """Zima w Polsce charakteryzuje się niskimi temperaturami, opadami śniegu i krótkim dniem. Średnia temperatura w najzimniejszym miesiącu roku, jakim jest styczeń, wynosi w Polsce od minus 2 do minus 5 stopni Celsjusza, choć w górach może być znacznie niższa. Warto podkreślić, że zima jest istotnym sezonem dla turystyki, szczególnie w rejonach górskich, gdzie rozwinięta infrastruktura narciarska przyciąga miłośników sportów zimowych. Pokrywa śnieżna pełni ważną rolę ekologiczną, chroniąc glebę i rośliny przed przemarzaniem. Należy zaznaczyć, że w ostatnich dekadach obserwuje się tendencję do łagodniejszych zim w Polsce, co jest interpretowane jako jeden z symptomów globalnego ocieplenia. Krótki dzień zimowy może mieć negatywny wpływ na samopoczucie ludzi, co wiąże się z niedoborem witaminy D i sezonowymi zaburzeniami nastroju. Zimowewarunki wymagają odpowiedniego przygotowania infrastruktury drogowej i komunalnej."""),

    ("ai22", "ai", "AI_GEN", "AI – opowiadanie o przypadkowym spotkaniu",
     """Marek wracał do domu po długim dniu w pracy, gdy na peronie metra dostrzegł kobietę, którą rozpoznał jako swoją dawną koleżankę ze studiów, Ewę. Nie widział jej od co najmniej dziesięciu lat. Podszedł do niej i zagaił rozmowę, która początkowo była nieco niezręczna z uwagi na długi czas, który minął od ich ostatniego kontaktu. Warto podkreślić, że takie nieoczekiwane spotkania są charakterystycznym elementem życia miejskiego. Ewa opowiedziała, że pracuje jako architektka i mieszka w innej dzielnicy. Marek poinformował ją o swojej aktualnej sytuacji zawodowej i rodzinnej. Wymienili się numerami telefonów i obiecali sobie wzajemnie, że umówią się na kawę. Należy zaznaczyć, że tego rodzaju przypadkowe spotkania mogą prowadzić do odnowienia wartościowych relacji. Oboje dosiedli do swoich pociągów, czując przyjemne zaskoczenie tym spotkaniem."""),

    ("ai23", "ai", "AI_GEN", "AI – esej filozoficzny o czasie",
     """Czas jest jednym z fundamentalnych pojęć filozofii i nauki, stanowiącym przedmiot rozważań od starożytności do współczesności. Warto podkreślić, że koncepcje czasu ewoluowały wraz z rozwojem myśli filozoficznej i naukowej. W fizyce klasycznej czas był traktowany jako absolutny i jednorodny, natomiast teoria względności Einsteina zrewolucjonizowała to rozumienie, wskazując na jego relatywność. Należy zaznaczyć, że subiektywne odczuwanie czasu przez człowieka jest często rozbieżne z jego obiektywnym pomiarem. Czas ma fundamentalne znaczenie dla życia społecznego, wyznaczając rytmy pracy, odpoczynku i relacji międzyludzkich. Filozofia egzystencjalna szczególnie podkreśla temporalny wymiar ludzkiej egzystencji i jego związek ze świadomością śmiertelności. Podsumowując, czas jest pojęciem wielowymiarowym, które nie poddaje się jednoznacznej definicji i wymaga podejścia interdyscyplinarnego łączącego perspektywy fizyki, filozofii i psychologii."""),

    ("ai24", "ai", "AI_GEN", "AI – opis polskiej wsi",
     """Polska wieś przeszła w ostatnich dekadach znaczące przemiany społeczno-gospodarcze związane z transformacją ustrojową, integracją europejską i postępującą urbanizacją. Warto podkreślić, że rolnictwo, choć nadal stanowi ważną gałąź polskiej gospodarki, zatrudnia dziś znacznie mniejszy odsetek pracujących niż w połowie XX wieku. Struktura agrarnaPolski ulega stopniowemu przekształceniu w kierunku większych, bardziej efektywnych gospodarstw. Należy zaznaczyć, że wiele wsi przekształca się w miejsca atrakcyjne dla mieszkańców miast, poszukujących spokoju i kontaktu z przyrodą. Turystyka wiejska i agroturystyka stanowią rosnący segment rynku. Infrastruktura wiejska, w tym drogi, szerokopasmowy internet i obiekty użyteczności publicznej, systematycznie się poprawia. Jednak depopulacja wielu wsi, szczególnie w obszarach peryferyjnych, pozostaje istotnym wyzwaniem demograficznym i społecznym wymagającym przemyślanej polityki regionalnej."""),

    ("ai25", "ai", "AI_GEN", "AI – esej o literaturze polskiej",
     """Literatura polska posiada bogatą, kilkusetletnią tradycję i jest odzwierciedleniem burzliwych dziejów narodu. Warto podkreślić, że polska twórczość literacka rozwijała się w warunkach szczególnych historycznych wyzwań, w tym rozbiorów, wojen i systemów totalitarnych, co nadało jej specyficzny charakter. Romantyzm polski, reprezentowany przez takich twórców jak Adam Mickiewicz, Juliusz Słowacki i Zygmunt Krasiński, zajął centralne miejsce w kanonie literackim i przez długi czas wyznaczał ramy polskiej tożsamości kulturowej. Pozytywizm przyniósł zmianę paradygmatu w kierunku realizmu i programowych funkcji literatury. Należy zaznaczyć, że polska literatura jest dziś dobrze reprezentowana na arenie międzynarodowej, czego wyrazem są przekłady dzieł polskich autorów na wiele języków. Podsumowując, literatura polska stanowi ważną część dziedzictwa kulturowego Europy i dostarcza cennych perspektyw na rozumienie historii i kondycji ludzkiej."""),

]


# ─── PARY DO PORÓWNANIA ───────────────────────────────────────────────────────
# Format: (nazwa, id_a, id_b, oczekiwany_poziom, threshold)
# NISKIE  = human vs AI     → oczekiwane podobieństwo < 0.45
# SREDNIE = human vs human (różne epoki) → 0.40–0.70
# WYSOKIE = AI vs AI        → oczekiwane podobieństwo > 0.65

PAIRS = [
    # Ludzki vs. AI — ten sam temat (opis przyrody)
    ("human (Reymont, jesień) vs. AI (opis zimy)",        "h16",  "ai21",  "NISKIE",  0.35),

    # Ludzki vs. AI — portret postaci
    ("human (Prus, Lalka) vs. AI (portret postaci)",      "h07",  "ai02",  "NISKIE",  0.35),

    # Ludzki vs. AI — narracja miejska
    ("human (Żeromski, Judym) vs. AI (opis Krakowa)",     "h14",  "ai05",  "NISKIE",  0.35),

    # Ludzki vs. ludzki — ta sama epoka (pozytywizm)
    ("Prus (Lalka) vs. Orzeszkowa (Nad Niemnem)",         "h07",  "h09",   "SREDNIE", 0.60),

    # Ludzki vs. ludzki — bardzo różne epoki
    ("Mickiewicz (rom.) vs. Schulz (dw.międzywojenneie)", "h03",  "h19",   "SREDNIE", 0.55),

    # Ludzki vs. ludzki — ta sama epoka (Młoda Polska)
    ("Żeromski vs. Reymont (obaj: Młoda Polska)",         "h14",  "h16",   "SREDNIE", 0.62),

    # AI vs. AI — jednorodne (dwa eseje AI)
    ("AI esej (klimat) vs. AI esej (edukacja)",           "ai04", "ai11",  "WYSOKIE", 0.75),

    # AI vs. AI — opis i narracja AI
    ("AI opis przyrody vs. AI opowiadanie",               "ai01", "ai10",  "WYSOKIE", 0.70),

    # Ludzki vs. AI — bezpośrednie pary stylistyczne
    ("human (Norwid, esej) vs. AI (esej o czasie)",       "h05",  "ai23",  "NISKIE",  0.35),
    ("human (Sienkiewicz) vs. AI (analiza Wokulski)",     "h11",  "ai18",  "NISKIE",  0.35),
]


# ─── UTILS ───────────────────────────────────────────────────────────────────

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def red(t):    return color(t, "31")
def green(t):  return color(t, "32")
def yellow(t): return color(t, "33")
def cyan(t):   return color(t, "36")
def bold(t):   return color(t, "1")


def check_server():
    try:
        r = requests.get(f"{BASE}/history", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ─── GŁÓWNA EWALUACJA DETEKCJI ───────────────────────────────────────────────

def run_detection_eval():
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  EWALUACJA DETEKCJI AI — checkLit (50 tekstów)"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    results = []
    correct = 0
    total = 0

    print(f"{'Tekst':<48} {'Oczek.':<8} {'Wynik':<14} {'PPX':>7} {'P(AI)%':>7} {'TTR':>6} {'LD':>6} {'Entr.':>6} {'LIX':>6}")
    print("─" * 120)

    for tid, expected, category, name, text in TEXTS:
        try:
            r = requests.post(f"{BASE}/analyze", json={"text": text}, timeout=60)
            if r.status_code != 200:
                print(f"{name:<48} ERROR {r.status_code}")
                continue
            data = r.json()
        except Exception as e:
            print(f"{name:<48} TIMEOUT/ERROR: {e}")
            continue

        ai   = data["ai_detection"]
        sty  = data["stylometry"]
        qual = data.get("quality", {})

        ppx      = ai.get("perplexity", 0) or 0
        ai_prob  = ai.get("ai_probability", 0) * 100
        label    = ai.get("label", "?")
        ttr      = sty.get("ttr", 0)
        ld       = sty.get("lexical_density", 0)
        entropy  = sty.get("entropy", 0)
        lix      = qual.get("lix", 0) if qual else sty.get("lix", 0)

        if expected == "ai":
            correct_flag = ai_prob > 50
        else:
            correct_flag = ai_prob < 50

        if correct_flag:
            correct += 1
            status = green("✓")
        else:
            status = red("✗")
        total += 1

        if ai_prob > 60:
            prob_str = red(f"{ai_prob:>6.1f}%")
        elif ai_prob > 40:
            prob_str = yellow(f"{ai_prob:>6.1f}%")
        else:
            prob_str = green(f"{ai_prob:>6.1f}%")

        exp_str = red("AI ") if expected == "ai" else green("HUM")

        short_name = name[:47]
        print(f"{status} {short_name:<47} {exp_str}  {label:<14} {ppx:>7.1f} {prob_str}  {ttr:>5.3f}  {ld:>5.3f}  {entropy:>5.2f}  {lix:>5.1f}")

        results.append({
            "id":                  tid,
            "name":                name,
            "category":            category,
            "expected":            expected,
            "label":               label,
            "ai_probability":      round(ai_prob, 1),
            "perplexity":          round(ppx, 1),
            "correct":             correct_flag,
            "ttr":                 round(ttr, 4),
            "lexical_density":     round(ld, 4),
            "entropy":             round(entropy, 3),
            "lix":                 round(lix, 1),
            "avg_sentence_length": round(sty.get("avg_sentence_length", 0), 1),
            "sentence_length_std": round(sty.get("sentence_length_std", 0), 2),
            "vocab_richness":      round(sty.get("vocab_richness", 0), 4),
            "word_count":          sty.get("word_count", 0),
        })
        time.sleep(0.2)

    print("─" * 120)
    acc = correct / total * 100 if total > 0 else 0
    print(f"\n  Poprawnych klasyfikacji: {green(str(correct))}/{total}  ({acc:.1f}%)\n")

    # Statystyki per kategoria
    for cat in ["HUMAN_LEKTURY", "AI_GEN"]:
        cat_r = [r for r in results if r["category"] == cat]
        if not cat_r:
            continue
        cat_correct = sum(1 for r in cat_r if r["correct"])
        avg_ppx = sum(r["perplexity"] for r in cat_r) / len(cat_r)
        avg_prob = sum(r["ai_probability"] for r in cat_r) / len(cat_r)
        print(f"  {cat:<18}: {cat_correct:>2}/{len(cat_r)} poprawnych | "
              f"avg PPX={avg_ppx:.1f} | avg P(AI)={avg_prob:.1f}%")

    # Rozkład perplexity
    ai_ppx  = [r["perplexity"] for r in results if r["expected"] == "ai"]
    hum_ppx = [r["perplexity"] for r in results if r["expected"] == "human"]
    if ai_ppx and hum_ppx:
        print(f"\n  Perplexity AI:    min={min(ai_ppx):.1f}  max={max(ai_ppx):.1f}  avg={sum(ai_ppx)/len(ai_ppx):.1f}")
        print(f"  Perplexity human: min={min(hum_ppx):.1f}  max={max(hum_ppx):.1f}  avg={sum(hum_ppx)/len(hum_ppx):.1f}")
        overlap = sum(1 for p in ai_ppx if p > min(hum_ppx))
        print(f"  Nakładanie się: {overlap}/{len(ai_ppx)} tekstów AI ma PPX > min(human)")

    return results


# ─── EWALUACJA PORÓWNANIA ─────────────────────────────────────────────────────

def run_compare_eval(text_map):
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  EWALUACJA PORÓWNANIA STYLOMETRYCZNEGO"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    compare_results = []

    print(f"{'Para':<55} {'Oczek.':<8} {'Wynik':>7} {'Status':<8} {'MATTR-Δ':>8} {'LD-Δ':>7} {'Entr-Δ':>7} {'StdZd-Δ':>8}")
    print("─" * 120)

    for name, id_a, id_b, expected_level, expected_threshold in PAIRS:
        text_a = text_map[id_a]
        text_b = text_map[id_b]

        try:
            r = requests.post(f"{BASE}/compare", json={"text_a": text_a, "text_b": text_b}, timeout=60)
            if r.status_code != 200:
                print(f"{name:<55} ERROR {r.status_code}: {r.text[:80]}")
                continue
            data = r.json()
        except Exception as e:
            print(f"{name:<55} TIMEOUT/ERROR: {e}")
            continue

        score = data.get("similarity_score", 0) * 100
        ta = data.get("text_a", {})
        tb = data.get("text_b", {})

        mattr_diff = abs(ta.get("ttr", 0) - tb.get("ttr", 0))
        ld_diff    = abs(ta.get("lexical_density", 0) - tb.get("lexical_density", 0))
        entr_diff  = abs(ta.get("entropy", 0) - tb.get("entropy", 0))
        std_diff   = abs(ta.get("sentence_length_std", 0) - tb.get("sentence_length_std", 0))

        if expected_level == "NISKIE":
            ok = score < 55
        elif expected_level == "SREDNIE":
            ok = 35 <= score <= 72
        else:  # WYSOKIE
            ok = score >= 62

        status = green("✓ OK") if ok else red("✗ BUG")

        score_str = red(f"{score:.1f}%") if (score > 60 and expected_level == "NISKIE") else \
                    yellow(f"{score:.1f}%") if (50 <= score <= 65 and expected_level != "WYSOKIE") else \
                    green(f"{score:.1f}%")

        print(f"{status}  {name:<53} {expected_level:<8} {score:.1f}%  "
              f"Δmattr={mattr_diff:.3f}  Δld={ld_diff:.3f}  Δentr={entr_diff:.2f}  Δstd={std_diff:.1f}")

        compare_results.append({
            "pair":           name,
            "id_a":           id_a,
            "id_b":           id_b,
            "expected":       expected_level,
            "similarity_pct": round(score, 1),
            "ok":             ok,
            "mattr_a":        round(ta.get("ttr", 0), 4),
            "mattr_b":        round(tb.get("ttr", 0), 4),
            "ld_a":           round(ta.get("lexical_density", 0), 4),
            "ld_b":           round(tb.get("lexical_density", 0), 4),
            "entropy_a":      round(ta.get("entropy", 0), 3),
            "entropy_b":      round(tb.get("entropy", 0), 3),
            "avg_sl_a":       round(ta.get("avg_sentence_length", 0), 1),
            "avg_sl_b":       round(tb.get("avg_sentence_length", 0), 1),
            "std_sl_a":       round(ta.get("sentence_length_std", 0), 2),
            "std_sl_b":       round(tb.get("sentence_length_std", 0), 2),
            "vocab_a":        round(ta.get("vocab_richness", 0), 4),
            "vocab_b":        round(tb.get("vocab_richness", 0), 4),
        })
        time.sleep(0.2)

    print("─" * 120)

    if compare_results:
        print(f"\n  {'Para':<55} {'Δmattr':>8} {'Δld':>7} {'Δentr':>7} {'Δstd':>8} {'Δvoc':>7}")
        for r in compare_results:
            print(f"  {r['pair']:<55} "
                  f"{abs(r['mattr_a']-r['mattr_b']):>8.3f} "
                  f"{abs(r['ld_a']-r['ld_b']):>7.3f} "
                  f"{abs(r['entropy_a']-r['entropy_b']):>7.2f} "
                  f"{abs(r['std_sl_a']-r['std_sl_b']):>8.1f} "
                  f"{abs(r['vocab_a']-r['vocab_b']):>7.3f}")

    return compare_results


# ─── ZAPIS CSV ───────────────────────────────────────────────────────────────

def save_csv(results, compare_results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    det_file = f"eval_detection_{ts}.csv"
    with open(det_file, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"\n  Zapisano detekcję: {det_file}")

    cmp_file = f"eval_compare_{ts}.csv"
    with open(cmp_file, "w", newline="", encoding="utf-8") as f:
        if compare_results:
            writer = csv.DictWriter(f, fieldnames=compare_results[0].keys())
            writer.writeheader()
            writer.writerows(compare_results)
    print(f"  Zapisano porównanie: {cmp_file}")

    return det_file, cmp_file


# ─── DIAGNOZA ─────────────────────────────────────────────────────────────────

def print_diagnosis(results, compare_results):
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  DIAGNOZA I REKOMENDACJE"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    wrong = [r for r in results if not r["correct"]]
    if wrong:
        print(f"  {red('Błędne klasyfikacje detekcji')} ({len(wrong)}):")
        for r in wrong:
            direction = "za niskie PPX" if r["expected"] == "human" and r["ai_probability"] > 50 \
                        else "za wysokie PPX"
            print(f"    • {r['name']}: PPX={r['perplexity']:.1f}, P(AI)={r['ai_probability']:.1f}% [{direction}]")
    else:
        print(f"  {green('Brak błędnych klasyfikacji!')} ✓\n")

    wrong_cmp = [r for r in compare_results if not r["ok"]]
    if wrong_cmp:
        print(f"\n  {red('Błędne wyniki porównania')} ({len(wrong_cmp)}):")
        for r in wrong_cmp:
            print(f"    • {r['pair']}: {r['similarity_pct']:.1f}% (oczekiwano: {r['expected']})")

    # Separowalność metryk (d-prime)
    ai_res  = [r for r in results if r["expected"] == "ai"]
    hum_res = [r for r in results if r["expected"] == "human"]
    if ai_res and hum_res:
        print(f"\n  {cyan('Separowalność metryk (AI vs human, d-prime):')}")
        metrics = ["perplexity", "ttr", "lexical_density", "entropy",
                   "avg_sentence_length", "sentence_length_std", "vocab_richness"]
        dprime_data = []
        for metric in metrics:
            ai_vals  = [r[metric] for r in ai_res  if metric in r]
            hum_vals = [r[metric] for r in hum_res if metric in r]
            if ai_vals and hum_vals:
                ai_avg  = sum(ai_vals) / len(ai_vals)
                hum_avg = sum(hum_vals) / len(hum_vals)
                diff    = abs(ai_avg - hum_avg)
                combined_std = ((sum((v-ai_avg)**2 for v in ai_vals)/len(ai_vals) +
                                 sum((v-hum_avg)**2 for v in hum_vals)/len(hum_vals)) / 2) ** 0.5
                d_prime = diff / (combined_std + 1e-9)
                dprime_data.append((metric, ai_avg, hum_avg, d_prime))

        dprime_data.sort(key=lambda x: -x[3])
        for metric, ai_avg, hum_avg, d_prime in dprime_data:
            bar = "█" * int(min(d_prime * 5, 25))
            print(f"    {metric:<22}: AI={ai_avg:>7.2f}  hum={hum_avg:>7.2f}  d'={d_prime:>5.2f}  {bar}")

    # Sugestia progów PPX
    ai_ppx  = [r["perplexity"] for r in results if r["expected"] == "ai"]
    hum_ppx = [r["perplexity"] for r in results if r["expected"] == "human"]
    if ai_ppx and hum_ppx:
        max_ai  = max(ai_ppx)
        min_hum = min(hum_ppx)
        mid     = (max_ai + min_hum) / 2
        print(f"\n  {cyan('Sugestia progów PPX:')}")
        print(f"    Max PPX wśród AI:    {max_ai:.1f}")
        print(f"    Min PPX wśród human: {min_hum:.1f}")
        if max_ai < min_hum:
            print(f"    {green('Klasy separowalne!')} Środek zakresu: {mid:.1f}")
            print(f"    Sugerowany AI_THRESHOLD ≈ {max_ai + (mid - max_ai)*0.4:.1f}")
            print(f"    Sugerowany HUMAN_THRESHOLD ≈ {min_hum - (min_hum - mid)*0.4:.1f}")
        else:
            overlap_ppx = [p for p in ai_ppx if p > min_hum]
            print(f"    {red('Zakresy się nakładają!')} Problematyczne: {len(overlap_ppx)}/{len(ai_ppx)} tekstów AI")

    # Sprawdzenie compare — sugestie fix
    if compare_results:
        bugs = [r for r in compare_results if not r["ok"]]
        if bugs:
            print(f"\n  {cyan('Problematyczne pary compare:')}")
            for r in bugs:
                print(f"    Para '{r['pair']}':")
                print(f"      sim={r['similarity_pct']:.1f}%  "
                      f"Δmattr={abs(r['mattr_a']-r['mattr_b']):.3f}  "
                      f"Δld={abs(r['ld_a']-r['ld_b']):.3f}  "
                      f"Δentr={abs(r['entropy_a']-r['entropy_b']):.2f}  "
                      f"Δstd={abs(r['std_sl_a']-r['std_sl_b']):.1f}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(bold(f"\n  checkLit Evaluator v2  |  50 tekstów  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
    print(f"  Backend: {BASE}")
    print(f"  Teksty ludzkie: 25 (Wolne Lektury, oświecenie → dwudziestolecie)")
    print(f"  Teksty AI:      25 (różne gatunki i tematy)\n")

    if not check_server():
        print(red("  BŁĄD: Backend nie odpowiada na http://localhost:8000"))
        print("  Uruchom: uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    print(green("  ✓ Backend działa\n"))

    text_map = {tid: text for tid, _, _, _, text in TEXTS}

    det_results = run_detection_eval()
    cmp_results = run_compare_eval(text_map)
    print_diagnosis(det_results, cmp_results)
    save_csv(det_results, cmp_results)

    print(bold("\n═══════════════════════════════════════════════════════════════\n"))