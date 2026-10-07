"""Local HTML scorecards without external assets or scripts."""
import html
from pathlib import Path
from .core import overall_score


def write_html(path, report):
    overall = report.get('overall') or overall_score(report['tasks'])
    if overall['score'] is None:
        headline = '— / 100'
        explanation = 'Для итогового балла пройди все четыре направления.'
    else:
        headline = f"{overall['display_score']} / 100"
        explanation = f"Точный балл: {overall['score']:.2f}. Четыре направления имеют равный вес — по 25%."
        if overall['status'] == 'provisional':
            explanation += ' Предварительный результат: есть пропуски или ошибки API; для сравнения заверши прогон.'
    overall_card = f'<section class="overall"><h2>Итоговый балл AxiomBench</h2><strong>{headline}</strong><p>{explanation}</p></section>'
    cards=[]
    scores=[('Рассуждение',report['summary']['general']),
            ('C++: написание',report['cpp_modes']['generation']),
            ('C++: исправление',report['cpp_modes']['repair']),
            ('Математика',report['summary']['math'])]
    for title,score in scores:
        value=score['accuracy_percent']
        cards.append(f'<section><h2>{title}</h2><strong>{value if value is not None else "—"}%</strong><p>{score["passed"]} / {score["total"]} заданий</p></section>')
    rows=[]
    repair_details=[]
    for kind,title in [('syntax','Синтаксис и ошибки компиляции'),('semantic','Логические ошибки кода')]:
        score=report.get('cpp_repair_types',{}).get(kind)
        if score and score['total']:
            repair_details.append(f'{title}: <b>{score["accuracy_percent"]}%</b> ({score["passed"]}/{score["total"]})')
    repair_details='<p>'+ ' · '.join(repair_details)+'</p>' if repair_details else ''
    for task in report['tasks']:
        fields=[task['id'],task['track'],task['category'],task['difficulty'],task['status']]
        rows.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in fields)+'</tr>')
    model=(report.get('run_metadata') or {}).get('model','Ручной импорт')
    text=f'''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AxiomBench — результаты</title>
<style>body{{background:#101724;color:#e8edf7;font:16px system-ui;margin:0 auto;max-width:1150px;padding:32px}}h1{{font-size:36px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}section{{border:1px solid #344259;border-radius:14px;padding:20px;background:#1a2638}}h2{{font-size:17px;color:#aebbd0}}strong{{font-size:38px;color:#81d4c8}}table{{width:100%;border-collapse:collapse}}td,th{{padding:9px;border-bottom:1px solid #344259;text-align:left}}.table{{overflow:auto}}code{{overflow-wrap:anywhere}}.note{{color:#adbcd1}}</style>
<h1>AxiomBench</h1><p>Модель: <b>{html.escape(model)}</b> · профиль: {html.escape(report.get('profile','quick'))}</p>{overall_card}<p class="note">Сравнивай баллы на одинаковом наборе, профиле и настройках запуска. Более высокий балл означает лучший средний результат на этом наборе.</p><div class="cards">{''.join(cards)}</div>
{repair_details}<p class="note">Публичный development-набор. Варианты одного семейства зависимы; это не измерение IQ и не официальный балл стороннего бенчмарка. Пропуски и ошибки API входят в знаменатель.</p>
<p>SHA-256 набора: <code>{report['suite_sha256']}</code></p><div class="table"><table><thead><tr><th>ID</th><th>Направление</th><th>Категория</th><th>Сложность</th><th>Результат</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></html>'''
    Path(path).write_text(text,encoding='utf-8')
