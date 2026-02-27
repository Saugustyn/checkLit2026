"""
evaluate_checklit.py — Kompleksowa ewaluacja platformy checkLit
===============================================================
Uruchomienie:
    cd C:\\Users\\sebas\\Documents\\checkLit\\backend
    venv\\Scripts\\activate
    python evaluate_checklit.py

Wymaga działającego backendu na http://localhost:8000
Wyniki zapisuje do: evaluation_results.csv i compare_results.csv
"""

import requests
import json
import csv
import sys
import time
from datetime import datetime

BASE = "http://localhost:8000/api"

# ─── 12 TEKSTÓW TESTOWYCH ────────────────────────────────────────────────────

TEXTS = [
    # (id, label_expected, category, name, text)

    # Para 1
    ("p1a", "human", "PARA",    "Para1A – opis przyrody (ludzki)",
     """Lipiec przyszedł nagle, bez zapowiedzi, jakby ktoś obrócił klocek kalendarza i zatrzasnął za sobą czerwiec. Nad łąką za wsią unosiła się mgła — nie taka zimna, grudniowa mgła, co osiadała na płaszczach i wchodziła za kołnierz, lecz ciepła, mleczna, prawie słodka w smaku. Stary Maciej Krawczyk, który wstał o czwartej rano, żeby obejść rowy przed żniwami, nie spieszył się. Szedł wąską miedzą między pszenicą a rzepakiem, lewą ręką trącając co jakiś czas kłosy, jakby liczył je przez dotyk. Wiedział, że do żniw zostały może dwa tygodnie, może trzy. Pszenica była jeszcze za zielona od spodu.

Zatrzymał się przy starym wiązie, który stał tu od niepamiętnych czasów, gruby w pasie na tyle, że nie objąłby go sam. Drzewo miało w sobie coś z pomnika i coś z żywego stworzenia jednocześnie. Korona sięgała wysoko, a cień pod nią był gęsty i ciemny jak piwnica. Maciej wyciągnął z kieszeni kawałek chleba zawiniętego w szmatkę i usiadł na korzeniu. Nie myślał o niczym szczególnym. Myślenie w taki ranek wymagało wysiłku, na który nie miał ochoty. Wystarczyło patrzeć — na mgłę, na kłosy, na jaskółki, które ścinały powietrze przy samej trawie.

Kiedy słońce wzeszło wyżej i zaczęło gryźć w kark, wstał, otrzepał okruchy i ruszył z powrotem. Droga do domu zajęła mu dobre dwadzieścia minut, bo przy strumieniu zatrzymał się jeszcze, żeby sprawdzić poziom wody. Strumień był niski — za niski jak na lipiec — i to trochę niepokoiło. Sąsiad Witek mówił, że od trzech lat takie same suche lata. Maciej nie wiedział, czy Witek ma rację, ale patrzył na wodę i coś w środku mu mówiło, że tamten się nie myli."""),

    ("p1b", "ai",    "PARA",    "Para1B – opis przyrody (AI)",
     """Lipiec charakteryzuje się najwyższymi temperaturami w roku na półkuli północnej, co jest bezpośrednim wynikiem maksymalnego nachylenia osi Ziemi względem Słońca. W Polsce jest to miesiąc o największym nasłonecznieniu, z temperaturami sięgającymi od 20 do 35 stopni Celsjusza w zależności od regionu i konkretnego roku. Zjawiska pogodowe w lipcu obejmują zarówno okresy suszy, jak i intensywne burze, co sprawia, że jest to miesiąc o dużej zmienności warunków atmosferycznych.

Łąki i pola w tym okresie osiągają pełnię wegetacji. Pszenica ozima, stanowiąca jeden z najważniejszych gatunków uprawnych w Polsce, dojrzewa właśnie w lipcu, co determinuje harmonogram prac polowych. Mgła poranna, obserwowana nad obszarami podmokłymi i łąkami, jest wynikiem radiacyjnego wyziębienia gruntu w nocy i kondensacji pary wodnej przy gruncie. Temperatura punktu rosy zostaje osiągnięta w godzinach porannych. Wraz ze wzrostem temperatury po wschodzie słońca mgła ulega rozproszeniu poprzez odparowanie.

Drzewa liściaste, takie jak wiąz szypułkowy, pełnią w ekosystemie polnym rolę refugiów bioróżnorodności. Ich rozbudowane korony stanowią miejsce gniazdowania ptaków, a systemy korzeniowe wpływają na strukturę gleby. Wartość przyrodnicza starych okazów jest znacznie wyższa niż drzew młodych, co sprawia, że są one często obejmowane ochroną jako pomniki przyrody. Prace polowe w lipcu, w tym żniwa, stanowią jeden z najważniejszych etapów cyklu produkcji rolnej i wymagają odpowiedniego planowania logistycznego."""),

    # Para 2
    ("p2a", "human", "PARA",    "Para2A – portret postaci (ludzki)",
     """Zofia Merczyńska miała pięćdziesiąt trzy lata i wyglądała jakby miała czterdzieści pięć albo sześćdziesiąt — zależało od dnia. W dobre dni chodziła szybko, mówiła głośno i śmiała się z rzeczy, które innym wydawały się tylko trochę zabawne. W złe dni siedziała przy oknie z kubkiem herbaty i gapiła się na ulicę z taką miną, jakby czekała na kogoś, kto miał przyjść dawno temu i nie przyszedł.

Pracowała w muzeum — nie w tym dużym, przy rynku, tylko w tym małym, z kolekcją zegarów i trochę mebli z dziewiętnastego wieku. Zwiedzających przychodziło mało. Czasem cały ranek minął jej bez jednego gościa i tylko siedziała przy kasie z książką, słuchając tykania. Nie skarżyła się. Powiedziała raz swojej siostrze, że tykanie zegarów jest spokojniejsze od rozmów z ludźmi, i siostra przez miesiąc się do niej nie odzywała.

Miała kota o imieniu Konstanty — szarego, grubego, o oczach w kolorze herbaty z mlekiem. Konstanty nigdy nie siedział tam, gdzie chciała Zofia. Kiedy kładła mu posłanie przy kaloryferze, szedł spać na stertę gazet. Nie rozumiała go i lubiła go za to. Większość ludzi rozumiała za dobrze."""),

    ("p2b", "ai",    "PARA",    "Para2B – portret postaci (AI)",
     """Maria Kowalska jest kobietą w średnim wieku, pracującą jako pracownik instytucji kulturalnej. Charakteryzuje się złożoną osobowością, która łączy w sobie cechy introwertyczne z umiejętnościami interpersonalnymi wymaganymi w pracy z publicznością. Jej codzienna rutyna obejmuje zarówno obowiązki zawodowe, jak i życie prywatne, które wypełnia opieka nad zwierzęciem domowym oraz różne zainteresowania.

Jako pracownik muzeum, Maria odpowiada za obsługę odwiedzających i dbanie o eksponaty. Jej praca wymaga cierpliwości i wiedzy merytorycznej z zakresu historii sztuki lub kultury materialnej. Mimo stosunkowo małej liczby zwiedzających, wykonuje swoje obowiązki sumiennie i profesjonalnie. Środowisko pracy, charakteryzujące się ciszą i obecnością historycznych przedmiotów, wpływa na jej sposób postrzegania rzeczywistości.

W życiu prywatnym Maria znajduje równowagę poprzez opiekę nad kotem. Relacja człowiek-zwierzę pełni ważną funkcję psychologiczną, zapewniając poczucie towarzystwa i odpowiedzialności. Ogólna charakterystyka Marii wskazuje na osobę zrównoważoną, która znalazła swoje miejsce w świecie i funkcjonuje w nim w sposób adekwatny do swoich potrzeb i możliwości."""),

    # Para 3
    ("p3a", "human", "PARA",    "Para3A – proza obyczajowa (ludzki)",
     """Piotr dostał wiadomość o dziesiątej w nocy. Siedział wtedy przy biurku z laptopem otwartym na prezentacji, którą miał skończyć na jutro, i jedząc zimny makaron prosto z pojemnika. Telefon wibrował, podskoczył, obrócił się o dziewięćdziesiąt stopni. Spojrzał. Wiadomość od Kaśki: "Musimy pogadać." Trzy słowa. Wiedział, co znaczą. Każdy wiedział. "Musimy pogadać" nigdy nie znaczyło dobrego — znaczyło koniec czegoś albo zmianę czegoś, a zmiany, które przychodziły o dziesiątej w nocy przez wiadomość, rzadko kiedy były zmianami na lepsze.

Odpisał: "Ok, kiedy?" i od razu poczuł, że to głupie pytanie. Odpowiedź przyszła po minucie: "Teraz możesz?" Zamknął laptopa. Prezentacja poczeka. Prezentacje zawsze czekają. Wyszedł na balkon, żeby zadzwonić — jakoś wydawało mu się, że rozmowy, które mogą zmienić coś ważnego, powinno się odbywać na stojąco, na zewnątrz, a nie siedząc w ciepłym pokoju z zimnym makaronem na biurku.

Rozmawiali czterdzieści minut. Kiedy skończył, został na balkonie jeszcze przez chwilę, patrząc na okna naprzeciwko. W kilku paliło się jeszcze światło. Inni też nie spali. To trochę pomagało — ta świadomość, że za każdym oświetlonym oknem siedzi ktoś, kto też nie może zasnąć. Wszedł do środka, wziął zimny pojemnik po makaronie i wyrzucił go do kosza."""),

    ("p3b", "human", "PARA",    "Para3B – pozytywizm (ludzki)",
     """Ignacy Rzecki skończył właśnie porządkować szufladę z rachunkami, kiedy usłyszał dzwonek przy drzwiach sklepu. Spojrzał na zegarek — była siódma rano, czyli co najmniej godzinę przed otwarciem. Westchnął, poprawił okularki na nosie i wyszedł zza lady. W drzwiach stał Wokulski — blady, z podkrążonymi oczami, w płaszczu pokrytym śniegiem, jakby szedł przez noc całą.

Rzecki powiedział tylko: "Pan Stanisław" — i nie wiedział, co dodać. Wokulski wszedł bez słowa, zdjął kapelusz i stanął pośrodku sklepu, patrząc na półki z towarami z takim wyrazem, jakby widział je pierwszy raz w życiu. Rzecki czekał. Znał ten stan. "Rzecki" — odezwał się w końcu Wokulski — "powiedz mi szczerze. Jak długo można gonić za czymś, o czym wiadomo, że jest niemożliwe?"

Stary subiekt przez chwilę milczał, kręcąc w palcach ołówek. Znał Wokulskiego od lat. Widział, jak z chłopca z prowincji stał się kupcem, jak wzbogacił się na dostawach, i jak od kiedy zobaczył tę Łęcką — już nie był sobą. "Można gonić bardzo długo" — powiedział w końcu cicho. "Dopóki człowiek ma siłę." Wokulski spojrzał na niego przez chwilę. Potem tylko kiwnął głową i wyszedł, zostawiając na podłodze kałużę roztopionego śniegu."""),

    # Lektury
    ("l1",  "human", "LEKTURA", "Lektura1 – Sienkiewicz",
     """Petroniusz obudził się dopiero koło południa i jak zwykle był znużony. Poprzedniego wieczoru był na uczcie u Nerona, na której dla zabicia czasu zaproponował, by zamiast wina pić tym razem stopione złoto — żart, który rozbawił cesarza do łez i kosztował Petroniusza tylko małą bliznę na wardze od zbyt gorącego pucharu. Kazał się namaścić pachnącymi olejkami i zabrać się do ćwiczeń gimnastycznych, które uważał za niezbędny warunek zachowania zdrowego umysłu w zdrowym ciele.

Lecz zanim przyszło do ćwiczeń, wezwał do siebie Eunicę i kazał jej czytać na głos fragmenty z Homera, podczas gdy sam leżał na łożu z marmurowym zagłówkiem i patrzył w sufit, na którym majster Aleksandros z Antiochii namalował bogów olimpijskich w scenach tak wdzięcznych, że Petroniusz nigdy nie mógł na nie patrzeć bez pewnego szczególnego uczucia. Eunica czytała dobrze. Miała głos niski i spokojny, który nie narzucał się, lecz towarzyszył myślom jak muzyka w tle uczty.

Petroniusz słuchał i myślał o Ligii — tej barbarzyńskiej zakładniczce, którą Winicjusz zobaczył na uczcie i od której nie mógł oderwać oczu. Widział tę scenę i rozumiał ją całkowicie. Kiedy Eunica skończyła czytać, leżał przez chwilę w milczeniu. Potem powiedział: "Winicjusz mnie odwiedzi dziś po południu. Przyjmę go w ogrodzie. Każ przygotować wino z Falernum i owoce." """),

    ("l2",  "human", "LEKTURA", "Lektura2 – Prus/Lalka",
     """Wokulski wyszedł ze sklepu i skierował się ku Krakowskiemu Przedmieściu. Był marzec — mokry, wietrzny marzec warszawski, który nie wiedział jeszcze, czy chce być zimą, czy wiosną, i dlatego postanowił być oboma naraz. Błoto chlapało spod kół dorożek i przylepiało się do butów. Wokulski szedł szybko, nie zwracając na to uwagi. Myślał o Izabeli Łęckiej.

Właściwie myślał o niej nieustannie od trzech miesięcy, od tej chwili, gdy zobaczył ją w loży teatralnej i poczuł, że coś w nim pęka i łączy się zarazem w nowy kształt, którego wcześniej nie znał. Nie było to uczucie miłości — tak przynajmniej tłumaczył sobie, bo miłość kojarzył z czymś spokojnym, z ciepłem przy kominku i rozmowami o zwykłych rzeczach. To, co czuł do Łęckiej, było jak gorączka: nierozumna, wyczerpująca i niemożliwa do zignorowania.

Wiedział, że to niemądre. Wiedział, że ona jest arystokratką, a on synem rzemieślnika, który dorobił się majątku ciężką pracą. Wiedział, że jej ojciec spodziewa się zięcia z herbem, nie z ciężkimi rękami po pracy przy kontuarze. A jednak szedł w stronę jej kamienicy i nie mógł powiedzieć sobie, żeby zawrócił. W połowie drogi zaczął padać deszcz ze śniegiem i Wokulski nie przyśpieszył ani o krok."""),

    ("l3",  "human", "LEKTURA", "Lektura3 – Żeromski",
     """Judym wracał do Warszawy pociągiem nocnym. Siedział przy oknie przedziału trzeciej klasy i patrzył w ciemność, przez którą od czasu do czasu przebiegały światła mijanych stacji — żółte, migotliwe, znikające zanim zdążył się im przyjrzeć. Naprzeciwko spał gruby kupiec w futrzanym kołnierzu, jego żona, owinięta w chustę, chrapała cicho i miarowo, jakby demonstrowała spokój sumienia.

Judym nie mógł spać. Myślał o Cisach, o pracy, o tym, co zostawił i czego nie zdołał zrobić. Myślał o swoim zawodzie — o medycynie, która mogła tyle, a dawała tak niewiele biednym dzielnicom Warszawy, gdzie na jednego lekarza przypadało kilkanaście tysięcy mieszkańców i gdzie gruźlica przechodziła z ojca na syna jak rodzinny majątek.

A jednak czuł, że coś mu umknęło. Że gdzieś po drodze stracił wątek, który powinien był trzymać przez całe życie. Pociąg wjechał w tunelowy most nad rzeką i przez chwilę w wagonie zrobiło się zupełnie ciemno. Kupiec mruknął przez sen. A Judym siedział w ciemności z oczami otwartymi i czuł, jak coś w nim — coś, czemu nie umiał nadać nazwy — bardzo powoli, bez rozgłosu, gaśnie."""),

    # AI
    ("ai1", "ai",    "AI",      "AI1 – opis jesieni (AI)",
     """Jesień jest jedną z czterech pór roku i charakteryzuje się stopniowym obniżaniem temperatury oraz skracaniem dnia. W Polsce jesień trwa od września do listopada i jest okresem, w którym przyroda przygotowuje się do zimowego spoczynku. Drzewa liściaste tracą liście w procesie zwanym senescencją, który jest wynikiem zmniejszonej produkcji chlorofilu i odsłonięcia innych barwników — karotenoidów i antocyjanów — odpowiedzialnych za charakterystyczne żółte, pomarańczowe i czerwone barwy.

Las jesienią prezentuje wyjątkowe walory estetyczne i przyrodnicze. Grzyby, których owocniki pojawiają się właśnie jesienią, stanowią ważny element ekosystemu leśnego, uczestnicząc w rozkładzie materii organicznej. Dla wielu gatunków zwierząt jesień jest okresem intensywnego gromadzenia zapasów przed zimą. Wiewiórki chowają żołędzie i orzechy, niedźwiedzie intensywnie żerują, a ptaki wędrowne gromadzą się w stada i migrują na południe.

Jesień jest również ważnym okresem w kalendarzu rolniczym. Trwają zbiory późnych warzyw i owoców, a rolnicy przygotowują pola pod zasiewy ozime. Temperatura gleby i poziom opadów są w tym czasie kluczowymi czynnikami wpływającymi na planowanie prac agrotechnicznych. Warto podkreślić, że jesień stanowi ważny etap cyklu przyrodniczego, w którym natura przechodzi fazę transformacji i przygotowania do następnego sezonu wegetacyjnego."""),

    ("ai2", "ai",    "AI",      "AI2 – opowiadanie Jan Kowalski (AI)",
     """Jan Kowalski był pracownikiem biurowym, który każdego dnia dojeżdżał do pracy komunikacją miejską. Mieszkał w bloku na obrzeżach miasta i prowadził spokojne, zorganizowane życie. Lubił porządek i rutynę, ponieważ dawały mu poczucie stabilności i kontroli nad codziennością. Jego dzień zaczynał się zawsze o tej samej porze i kończył zgodnie z ustalonym harmonogramem.

Pewnego dnia, wracając do domu po pracy, Jan zauważył na przystanku autobusowym starszą panią, która sprawiała wrażenie zagubionej. Podszedł do niej i zapytał, czy potrzebuje pomocy. Okazało się, że kobieta nie pamięta, który autobus jedzie w kierunku jej dzielnicy. Jan, który znał dobrze siatkę połączeń komunikacyjnych, wyjaśnił jej szczegółowo, że powinna wsiąść do linii numer czternaście i wysiąść na trzecim przystanku.

Starsza pani podziękowała mu serdecznie i powiedziała, że ludzie potrafią być dla siebie uprzejmi. Jan poczuł się dobrze, że mógł pomóc. Wsiadł do swojego autobusu i przez resztę drogi do domu rozmyślał o tym, jak ważna jest życzliwość w codziennym życiu. Należy zaznaczyć, że drobne gesty pomocy mogą mieć duże znaczenie dla innych. Przygotował sobie kolację, obejrzał wiadomości i poszedł spać o zwykłej porze."""),

    ("ai3", "ai",    "AI",      "AI3 – esej o AI (AI)",
     """Sztuczna inteligencja stanowi jedno z najważniejszych wyzwań technologicznych i społecznych współczesności. Jej dynamiczny rozwój w ostatnich latach otworzył nowe możliwości w wielu dziedzinach, jednocześnie rodząc poważne pytania etyczne i filozoficzne dotyczące natury człowieczeństwa. Należy zauważyć, że modele językowe zdolne do generowania tekstów stanowią szczególnie istotne wyzwanie dla tradycyjnych form twórczości pisarskiej.

Warto podkreślić, że detekcja tekstu generowanego przez sztuczną inteligencję jest zadaniem złożonym z metodologicznego punktu widzenia. Metody oparte na analizie perplexity modeli językowych czy badaniu cech stylometrycznych tekstu oferują obiecujące rezultaty, jednak żadna z nich nie jest w stanie zagwarantować stuprocentowej skuteczności. Istotne jest zatem podejście wielowymiarowe, które łączy różne metody analizy.

Podsumowując, problem autentyczności tekstów w dobie generatywnej sztucznej inteligencji wymaga dalszych badań i rozwoju odpowiednich narzędzi weryfikacyjnych. Kluczowe znaczenie ma w tym kontekście współpraca między środowiskami naukowymi, technologicznymi i instytucjami edukacyjnymi. Tylko poprzez skoordynowane działania możliwe będzie skuteczne zarządzanie wyzwaniami, jakie niesie ze sobą masowe zastosowanie generatywnej sztucznej inteligencji w sferze produkcji tekstów."""),
]

# ─── PARY DO PORÓWNANIA ───────────────────────────────────────────────────────

PAIRS = [
    ("Para1: ludzki vs. AI (opis przyrody)", "p1a", "p1b", "NISKIE",  0.30),
    ("Para2: ludzki vs. AI (portret)",       "p2a", "p2b", "NISKIE",  0.30),
    ("Para3: ludzki vs. ludzki (epoki)",     "p3a", "p3b", "SREDNIE", 0.60),
    ("Lektura vs. AI (Sienkiewicz vs AI1)",  "l1",  "ai1", "NISKIE",  0.35),
    ("AI vs. AI (jednorodne)",               "ai1", "ai2", "WYSOKIE", 0.75),
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

# ─── GŁÓWNA EWALUACJA ────────────────────────────────────────────────────────

def run_detection_eval():
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  EWALUACJA DETEKCJI AI — checkLit"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    results = []
    correct = 0
    total = 0

    # Header
    print(f"{'Tekst':<40} {'Oczek.':<8} {'Wynik':<12} {'PPX':>7} {'P(AI)%':>7} {'TTR':>6} {'LD':>6} {'Entr.':>6} {'LIX':>6}")
    print("─" * 110)

    for tid, expected, category, name, text in TEXTS:
        try:
            r = requests.post(f"{BASE}/analyze", json={"text": text}, timeout=60)
            if r.status_code != 200:
                print(f"{name:<40} ERROR {r.status_code}")
                continue
            data = r.json()
        except Exception as e:
            print(f"{name:<40} TIMEOUT/ERROR: {e}")
            continue

        ai = data["ai_detection"]
        sty = data["stylometry"]
        qual = data.get("quality", {})

        ppx = ai.get("perplexity", 0) or 0
        ai_prob = ai.get("ai_probability", 0) * 100
        label = ai.get("label", "?")
        ttr = sty.get("ttr", 0)
        ld = sty.get("lexical_density", 0)
        entropy = sty.get("entropy", 0)
        lix = qual.get("lix", 0) if qual else sty.get("lix", 0)

        # Determine correctness
        is_correct = (expected == "ai" and label in ("AI-generated", "AI-Generated", "AI")) or \
                     (expected == "human" and label in ("Human-written", "Human")) or \
                     (expected in ("ai", "human") and "szara" in ai.get("confidence", "").lower())

        # Actually use ai_probability for accuracy check
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

        # Color the probability
        if ai_prob > 60:
            prob_str = red(f"{ai_prob:>6.1f}%")
        elif ai_prob > 40:
            prob_str = yellow(f"{ai_prob:>6.1f}%")
        else:
            prob_str = green(f"{ai_prob:>6.1f}%")

        exp_str = red("AI ") if expected == "ai" else green("HUM")

        print(f"{status} {name:<40} {exp_str}  {label:<12} {ppx:>7.1f} {prob_str}  {ttr:>5.3f}  {ld:>5.3f}  {entropy:>5.2f}  {lix:>5.1f}")

        results.append({
            "id": tid,
            "name": name,
            "category": category,
            "expected": expected,
            "label": label,
            "ai_probability": round(ai_prob, 1),
            "perplexity": round(ppx, 1),
            "correct": correct_flag,
            "ttr": round(ttr, 4),
            "lexical_density": round(ld, 4),
            "entropy": round(entropy, 3),
            "lix": round(lix, 1),
            "avg_sentence_length": round(sty.get("avg_sentence_length", 0), 1),
            "sentence_length_std": round(sty.get("sentence_length_std", 0), 2),
            "vocab_richness": round(sty.get("vocab_richness", 0), 4),
            "word_count": sty.get("word_count", 0),
        })
        time.sleep(0.2)

    print("─" * 110)
    acc = correct / total * 100 if total > 0 else 0
    print(f"\n  Poprawnych klasyfikacji: {green(str(correct))}/{total}  ({acc:.1f}%)\n")

    # Stats by category
    for cat in ["PARA", "LEKTURA", "AI"]:
        cat_r = [r for r in results if r["category"] == cat]
        if not cat_r:
            continue
        cat_correct = sum(1 for r in cat_r if r["correct"])
        cat_ai = [r for r in cat_r if r["expected"] == "ai"]
        cat_hum = [r for r in cat_r if r["expected"] == "human"]
        avg_ppx_ai = sum(r["perplexity"] for r in cat_ai) / len(cat_ai) if cat_ai else 0
        avg_ppx_hum = sum(r["perplexity"] for r in cat_hum) / len(cat_hum) if cat_hum else 0
        print(f"  {cat:<10}: {cat_correct}/{len(cat_r)} poprawnych | "
              f"avg PPX(AI)={avg_ppx_ai:.1f} | avg PPX(human)={avg_ppx_hum:.1f}")

    # Perplexity distribution
    ai_ppx = [r["perplexity"] for r in results if r["expected"] == "ai"]
    hum_ppx = [r["perplexity"] for r in results if r["expected"] == "human"]
    if ai_ppx and hum_ppx:
        print(f"\n  Perplexity AI:    min={min(ai_ppx):.1f}  max={max(ai_ppx):.1f}  avg={sum(ai_ppx)/len(ai_ppx):.1f}")
        print(f"  Perplexity human: min={min(hum_ppx):.1f}  max={max(hum_ppx):.1f}  avg={sum(hum_ppx)/len(hum_ppx):.1f}")
        overlap = sum(1 for p in ai_ppx if p > min(hum_ppx))
        print(f"  Nakładanie się zakresów: {overlap}/{len(ai_ppx)} tekstów AI ma PPX > min(human)")

    return results


def run_compare_eval(text_map):
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  EWALUACJA PORÓWNANIA STYLOMETRYCZNEGO"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    compare_results = []

    print(f"{'Para':<45} {'Oczek.':<8} {'Wynik':>7} {'Status':<8} {'MATTR-Δ':>8} {'LD-Δ':>7} {'Entr-Δ':>7} {'StdZd-Δ':>8}")
    print("─" * 110)

    for name, id_a, id_b, expected_level, expected_threshold in PAIRS:
        text_a = text_map[id_a]
        text_b = text_map[id_b]

        try:
            r = requests.post(f"{BASE}/compare", json={"text_a": text_a, "text_b": text_b}, timeout=60)
            if r.status_code != 200:
                print(f"{name:<45} ERROR {r.status_code}: {r.text[:100]}")
                continue
            data = r.json()
        except Exception as e:
            print(f"{name:<45} TIMEOUT/ERROR: {e}")
            continue

        score = data.get("similarity_score", 0) * 100
        ta = data.get("text_a", {})
        tb = data.get("text_b", {})

        mattr_diff = abs(ta.get("ttr", 0) - tb.get("ttr", 0))
        ld_diff = abs(ta.get("lexical_density", 0) - tb.get("lexical_density", 0))
        entr_diff = abs(ta.get("entropy", 0) - tb.get("entropy", 0))
        std_diff = abs(ta.get("sentence_length_std", 0) - tb.get("sentence_length_std", 0))

        # Check if similarity is in expected direction
        if expected_level == "NISKIE":
            ok = score < 60
        elif expected_level == "SREDNIE":
            ok = 40 <= score <= 75
        else:  # WYSOKIE
            ok = score >= 65

        status = green("✓ OK") if ok else red("✗ BUG")

        score_str = red(f"{score:.1f}%") if score > 75 and expected_level == "NISKIE" else \
                    yellow(f"{score:.1f}%") if 60 <= score <= 75 else \
                    green(f"{score:.1f}%")

        print(f"{status}  {name:<45} {expected_level:<8} {score:.1f}%  "
              f"  Δmattr={mattr_diff:.3f}  Δld={ld_diff:.3f}  Δentr={entr_diff:.2f}  Δstd={std_diff:.1f}")

        compare_results.append({
            "pair": name,
            "id_a": id_a,
            "id_b": id_b,
            "expected": expected_level,
            "similarity_pct": round(score, 1),
            "ok": ok,
            "mattr_a": round(ta.get("ttr", 0), 4),
            "mattr_b": round(tb.get("ttr", 0), 4),
            "ld_a": round(ta.get("lexical_density", 0), 4),
            "ld_b": round(tb.get("lexical_density", 0), 4),
            "entropy_a": round(ta.get("entropy", 0), 3),
            "entropy_b": round(tb.get("entropy", 0), 3),
            "avg_sl_a": round(ta.get("avg_sentence_length", 0), 1),
            "avg_sl_b": round(tb.get("avg_sentence_length", 0), 1),
            "std_sl_a": round(ta.get("sentence_length_std", 0), 2),
            "std_sl_b": round(tb.get("sentence_length_std", 0), 2),
            "vocab_a": round(ta.get("vocab_richness", 0), 4),
            "vocab_b": round(tb.get("vocab_richness", 0), 4),
        })
        time.sleep(0.2)

    print("─" * 110)

    # Diagnostic: what metrics actually differ most?
    if compare_results:
        print(f"\n  {'Para':<45} {'Δmattr':>8} {'Δld':>7} {'Δentr':>7} {'Δstd':>8} {'Δvoc':>7} {'Δasl':>7}")
        for r in compare_results:
            print(f"  {r['pair']:<45} "
                  f"{abs(r['mattr_a']-r['mattr_b']):>8.3f} "
                  f"{abs(r['ld_a']-r['ld_b']):>7.3f} "
                  f"{abs(r['entropy_a']-r['entropy_b']):>7.2f} "
                  f"{abs(r['std_sl_a']-r['std_sl_b']):>8.1f} "
                  f"{abs(r['vocab_a']-r['vocab_b']):>7.3f} "
                  f"{abs(r['avg_sl_a']-r['avg_sl_b']):>7.1f}")

    return compare_results


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


def print_diagnosis(results, compare_results):
    print(bold("\n═══════════════════════════════════════════════════════════════"))
    print(bold("  DIAGNOZA I REKOMENDACJE"))
    print(bold("═══════════════════════════════════════════════════════════════\n"))

    # Detection issues
    wrong = [r for r in results if not r["correct"]]
    if wrong:
        print(f"  {red('Błędne klasyfikacje detekcji')} ({len(wrong)}):")
        for r in wrong:
            direction = "za niskie PPX" if r["expected"] == "human" and r["ai_probability"] > 50 \
                        else "za wysokie PPX"
            print(f"    • {r['name']}: PPX={r['perplexity']:.1f}, P(AI)={r['ai_probability']:.1f}% [{direction}]")

    # Compare issues
    wrong_cmp = [r for r in compare_results if not r["ok"]]
    if wrong_cmp:
        print(f"\n  {red('Błędne wyniki porównania')} ({len(wrong_cmp)}):")
        for r in wrong_cmp:
            print(f"    • {r['pair']}: {r['similarity_pct']:.1f}% (oczekiwano: {r['expected']})")

    # Key finding: what metrics separate AI from human?
    ai_res = [r for r in results if r["expected"] == "ai"]
    hum_res = [r for r in results if r["expected"] == "human"]

    if ai_res and hum_res:
        print(f"\n  {cyan('Separowalność metryk (AI vs human):')} ")
        for metric in ["perplexity", "ttr", "lexical_density", "entropy", "avg_sentence_length", "sentence_length_std", "vocab_richness"]:
            ai_vals = [r[metric] for r in ai_res if metric in r]
            hum_vals = [r[metric] for r in hum_res if metric in r]
            if ai_vals and hum_vals:
                ai_avg = sum(ai_vals) / len(ai_vals)
                hum_avg = sum(hum_vals) / len(hum_vals)
                diff = abs(ai_avg - hum_avg)
                combined_std = ((sum((v - ai_avg)**2 for v in ai_vals) / len(ai_vals) +
                                 sum((v - hum_avg)**2 for v in hum_vals) / len(hum_vals)) / 2) ** 0.5
                d_prime = diff / (combined_std + 1e-9)
                bar = "█" * int(min(d_prime * 5, 20))
                print(f"    {metric:<22}: AI={ai_avg:>7.2f}  hum={hum_avg:>7.2f}  d'={d_prime:>5.2f}  {bar}")

    # Thresholds suggestion
    ai_ppx = [r["perplexity"] for r in results if r["expected"] == "ai"]
    hum_ppx = [r["perplexity"] for r in results if r["expected"] == "human"]
    if ai_ppx and hum_ppx:
        max_ai = max(ai_ppx)
        min_hum = min(hum_ppx)
        mid = (max_ai + min_hum) / 2
        print(f"\n  {cyan('Sugestia progów PPX:')}")
        print(f"    Aktualny próg AI:    check ai_detector.py → PERPLEXITY_AI_THRESHOLD")
        print(f"    Max PPX wśród AI:    {max_ai:.1f}")
        print(f"    Min PPX wśród human: {min_hum:.1f}")
        if max_ai < min_hum:
            print(f"    {green('Klasy separowalne!')} Sugerowany środek: {mid:.1f}")
            print(f"    Sugeruj: AI_THRESHOLD ≈ {max_ai + (mid - max_ai)*0.4:.1f}")
            print(f"    Sugeruj: HUMAN_THRESHOLD ≈ {min_hum - (min_hum - mid)*0.4:.1f}")
        else:
            print(f"    {red('Zakresy się nakładają — potrzebna recalibracja lub dodatkowe cechy!')}")
            overlap_ppx = [p for p in ai_ppx if p > min_hum]
            print(f"    Problematyczne teksty AI (PPX > {min_hum:.1f}): {len(overlap_ppx)}/{len(ai_ppx)}")

    # Compare fix suggestion
    if compare_results:
        print(f"\n  {cyan('Dlaczego compare daje za wysokie wyniki?')}")
        for r in compare_results:
            if r["expected"] == "NISKIE" and r["similarity_pct"] > 60:
                print(f"    Para '{r['pair']}':")
                print(f"      Δmattr={abs(r['mattr_a']-r['mattr_b']):.3f}  "
                      f"Δld={abs(r['ld_a']-r['ld_b']):.3f}  "
                      f"Δentr={abs(r['entropy_a']-r['entropy_b']):.2f}  "
                      f"Δstd={abs(r['std_sl_a']-r['std_sl_b']):.1f}")
                print(f"      → Metryki mają zbyt mały zakres naturalny — formula max(a,b) zawyża podobieństwo")
                print(f"      → Fix: znormalizuj przez stały zakres [lo, hi] zamiast przez max(a,b)")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(bold(f"\n  checkLit Evaluator  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
    print(f"  Backend: {BASE}\n")

    if not check_server():
        print(red("  BŁĄD: Backend nie odpowiada na http://localhost:8000"))
        print("  Uruchom: uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    print(green("  ✓ Backend działa\n"))

    text_map = {tid: text for tid, _, _, _, text in TEXTS}

    det_results   = run_detection_eval()
    cmp_results   = run_compare_eval(text_map)
    print_diagnosis(det_results, cmp_results)
    save_csv(det_results, cmp_results)

    print(bold("\n═══════════════════════════════════════════════════════════════\n"))