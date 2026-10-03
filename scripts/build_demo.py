"""Build a reproducible, wholly synthetic UI fixture; not patient analysis.

Phase 1 facts are computed here in Python, then rendered directly by the UI.
No raw FIT, GPS, patient readings, LLM or imported UltraSoul logic is used.
"""
from pathlib import Path
import csv
import json
import math
import random
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]


def build_demo(seed=20261003):
    rng = random.Random(seed)
    samples = []
    distance = 0
    for minute in range(95):
        hill = math.exp(-((minute - 82) / 3.8) ** 2)
        pace = round(5.52 + .12 * math.sin(minute / 3) + 1.6 * hill + rng.uniform(-.07, .07), 3)
        if minute:
            distance += 1 / pace
        samples.append(dict(minute=minute, pace=pace, hr=round(118 + minute * .43 + 10 * hill + rng.uniform(-2, 2)), altitude=round(205 + 3 * math.sin(minute / 8) + 43 * hill), distanceKm=round(distance, 3)))
    glucose = []
    anchors = {0: 137, 5: 143, 10: 153, 15: 138, 20: 119, 25: 110, 50: 114, 55: 121, 60: 128, 65: 131, 70: 112, 75: 84, 80: 65, 85: 68, 90: 106, 94: 111}
    for minute, value in anchors.items():
        glucose.append(dict(minute=minute, value=value))
    segments = []
    for point in glucose:
        if not segments or point['minute'] - segments[-1][-1]['minute'] > 10:
            segments.append([])
        segments[-1].append(point)
    covered = sum(b['minute'] - a['minute'] for a, b in zip(glucose, glucose[1:]) if b['minute'] - a['minute'] <= 10)
    gaps = [dict(start=a['minute'], end=b['minute']) for a, b in zip(glucose, glucose[1:]) if b['minute'] - a['minute'] > 10]
    moments = []
    for key, minute, label, title in [('gap',37,'Luka w danych','Tutaj historia jest niepełna.'),('steady',58,'Spokojny odcinek','Ten odcinek widać w obu źródłach.'),('together',82,'Dwa sygnały','Spadek tempa zbiegł się z dwoma sygnałami.')]:
        readings = [p['value'] for p in glucose if minute - 10 <= p['minute'] <= minute + 10]
        minimum = min(readings) if readings else None
        factors = []
        if minimum is not None and minimum < 70:
            factors.append(dict(id='low_glucose_nearby',label='Niski odczyt glukozy',evidence=f'Najniższy odczyt w oknie: {minimum} mg/dL.',factId=f'{key}.glucose.minimum'))
        if key == 'together':
            factors.append(dict(id='uphill',label='Podbieg',evidence='W tym samym oknie wzrasta wysokość trasy.',factId=f'{key}.altitude.change'))
        if not readings:
            factors.append(dict(id='no_glucose_data',label='Brak odczytów glukozy',evidence='W całym wybranym oknie nie ma odczytów.',factId=f'{key}.glucose.count'))
        before=samples[max(0,minute-5)]['altitude']
        after=samples[minute]['altitude']
        narratives = {
            'gap':'W tym miejscu nie ma odczytu glukozy. Nie możemy porównać go z przebiegiem biegu.',
            'steady':'Tempo i tętno są względnie równe, a odczyty glukozy są dostępne. To obserwacja z tego odcinka.',
            'together':'Na tym odcinku wystąpił też podbieg. Te dane nie pozwalają rozdzielić ich wpływu.'}
        unknowns = ['Brak informacji o posiłku.', 'Nie zapisano odczuć biegacza.']
        if not readings:
            unknowns.insert(0,'Brak odczytów glukozy w wybranym oknie.')
        else:
            unknowns.insert(0,'Odczyt sensora i zmiana tempa nie dowodzą przyczyny.')
        moments.append(dict(id=key,minute=minute,label=label,title=title,distanceKm=round(samples[minute]['distanceKm'],1),windowStart=minute-10,windowEnd=minute+10,minGlucose=minimum,readingCount=len(readings),pace=samples[minute]['pace'],hr=samples[minute]['hr'],altitudeChange=after-before,factors=factors,narrative=narratives[key],unknowns=unknowns,question='Jak omówić te odczyty w kontekście wysiłku?' if readings else 'Jak przygotować pełniejsze dane z kolejnego biegu?',separable=key=='steady'))
    return dict(schemaVersion=1,synthetic=True,seed=seed,title='Bieg nad Wisłą',date='2026-10-03',start='2026-10-03T08:30:00+02:00',timezone='Europe/Warsaw',durationMinutes=94,distanceKm=round(distance,1),samples=samples,glucose=glucose,glucoseSegments=segments,gaps=gaps,moments=moments,facts=dict(coveragePct=round(100*covered/94),coveredMinutes=covered,minGlucose=min(anchors.values()),below70Count=sum(v<70 for v in anchors.values()),below54Count=sum(v<54 for v in anchors.values()),readingCount=len(glucose),averagePace=round(94/distance,3),basis='Odczyty punktowe; pokrycie liczone tylko między odczytami oddalonymi o najwyżej 10 minut. Bez uzupełniania luki i bez wyliczania czasu poniżej progu.'),provenance=dict(kind='synthetic',generator='scripts/build_demo.py',engineUsed=False,clinicalValidation=False))


if __name__ == '__main__':
    demo=build_demo()
    (ROOT/'data/demo-run.json').write_text(json.dumps(demo,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    output=ROOT/'public/demo-glucose.csv'
    output.parent.mkdir(exist_ok=True)
    with output.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['Timestamp (YYYY-MM-DDThh:mm:ss)','Event Type','Glucose Value (mg/dL)'])
        start=datetime.fromisoformat(demo['start'])
        for p in demo['glucose']:
            writer.writerow([(start+timedelta(minutes=p['minute'])).strftime('%Y-%m-%dT%H:%M:%S'),'EGV',p['value']])
    print(f"Synthetic fixture: {demo['distanceKm']} km, {demo['facts']['coveragePct']}% observed coverage; {len(demo['moments'])} illustrative moments")
