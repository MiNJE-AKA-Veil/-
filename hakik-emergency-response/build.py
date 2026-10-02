#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학익가압장 운전 비상상황 대응절차 설명자료 생성 스크립트.
images/*.jpg (원문 PDF에서 무손실 추출한 원본 JPEG)를 base64로 내장한 단일 HTML을 만든다.
실행: python3 build.py  ->  hakik-emergency-response.html
"""
import base64, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 그림 목록
# id: (원문 그림번호, 원문 쪽, 제목, 대조 포인트[list], 비고)
FIGS = {
 'E21-01': (4, '정상 운전 상태 — H/E TOTALIZING OVERVIEW(2890) 화면',
   ['INTECO FLOW RATE(RECEIVE) 1380', 'CHEONGNA H/E 750', 'FUELCELL 330', 'HORANG 300'],
   '화면 붉은 테두리 표시값. 화면 단위 표기는 (m3/h)이며 본문은 [ton/hr]'),
 'E21-02': (5, '압력선도 — 정상 운전 상태',
   ['가압장 13 km 지점의 공급 가압·회수 가압 표기가 모두 보임'],
   '원문은 압력선도 수치를 설명하지 않음. 본 자료도 수치를 해석하지 않음 → 확인 #C22'),
 'E21-03': (5, '압력선도 — 공급·리턴 펌프(PP-003, 001) 동시 Trip 상태',
   ['가압장 13 km 지점의 공급 가압·회수 가압 표기가 보이지 않음', 'E21-02와 비교'], ''),
 'E21-04': (6, '학익가압장 펌프 계통 화면(화면번호 2951) — Trip 확인',
   ['PP-003 Trip 확인', 'PP-002 Trip 확인', 'PP-001 Trip 확인'],
   '화면에는 PP-002 표기도 있으나 본문·Flow Chart는 PP-003, 001만 언급 → 확인 #C1'),
 'E21-05': (6, 'CN H/E DCS OPERATION(2893) 화면',
   ['PIT-9334(CN H/E 공급 압력)', 'FIT-9338(유량 감소 확인)', '화면 문구 “11[kg/㎠] 초과 상태”'],
   '화면 문구는 “PIT-9338”로 표기되어 있고 원이 둘러진 위치는 PIT-9334. 본문은 PIT-9334, 10[kg/㎠] → 확인 #C2'),
 'E21-06': (6, '연료전지 화면 — 리턴 압력·DH RETURN PUMP',
   ['PIT-3501 압력 변화 확인', 'DH RETURN PUMP 상태 확인'], ''),
 'E21-07': (7, '호랑 화면 — 리턴 압력·DH RETURN PUMP',
   ['PIT-201 압력 변화 확인', 'DH RETURN PUMP 상태 확인'], ''),
 'E21-08': (7, '학익가압장 펌프 계통 화면 — 공급·리턴 Bypass Open',
   ['HV-9715 Open', 'HV-9708 Open'], ''),
 'E21-09': (7, '압력선도 — 연료전지&호랑 Pump Trip 발생',
   ['가압 표기(공급·회수)가 보이지 않음', 'E21-02와 비교'], '→ 확인 #C22'),
 'E21-10': (8, 'H/E TOTALIZING OVERVIEW — 외부 열원 유량 감소',
   ['INTECO FLOW RATE 760', 'CHEONGNA H/E 760', 'FUELCELL 0', 'HORANG 0'],
   '화면 예시값(붉은 테두리). 판단 기준값이 아님'),
 'E21-11': (8, 'Mean Pr 확인 화면 — Mean Pr 기준 5.5[kg/㎠]',
   ['붉은 박스로 표시된 Mean Pr 표시값'], '캡션: <Mean Pr 기준 5.5[kg/㎠]>'),
 'E21-12': (8, 'H/E TOTALIZING OVERVIEW — INTECO FLOW RATE 850 수준',
   ['INTECO FLOW RATE 850', 'CHEONGNA H/E 600', 'FUELCELL 150', 'HORANG 100'],
   '화면 예시값(붉은 테두리). 재개 시점 확인용 화면'),
 'E21-13': (10, '압력선도 — 공급 펌프 Trip 상태',
   ['공급 가압 표기 없음', '회수 가압 표기 있음'], '→ 확인 #C22'),
 'E21-14': (10, '학익가압장 펌프 계통 화면 — 공급 펌프 Trip',
   ['PP-003 Trip 확인'], ''),
 'E21-15': (11, '학익가압장 펌프 계통 화면 — 공급측 Bypass Open',
   ['HV-9715 Open'], ''),
 'E21-16': (11, '학익가압장 펌프 계통 화면 — 가압 펌프 재가동',
   ['PP-003 가동'], ''),
 'E21-17': (12, '학익가압장 펌프 계통 화면 — Spare 펌프(PP-002) 가동 전 밸브 상태',
   ['PP-002 가동', 'HV-9703 Open 확인', 'HV-9715 Open 확인', 'HV-9704 Close 확인', 'HV-9717 Close 확인'], ''),
 'E21-18': (12, '학익가압장 펌프 계통 화면 — 공급 Bypass Close',
   ['HV-9715 Close'], ''),
 'E21-19': (13, '압력선도 — 외부 열원 유량 및 Mean Pr만 감소시킨 경우',
   ['회수 가압 표기만 보임'], '캡션: (외부열원 유량 및 Mean Pr만 감소시킨 경우) → 확인 #C22'),
 'E21-20': (13, '학익가압장 펌프 계통 화면 — 리턴 가압 펌프(PP-001)',
   ['화면 문구 “PP-001 리턴 펌프 감소”'],
   '본문·Flow Chart는 “리턴 가압 펌프 증가”. 화면 문구와 방향이 다름 → 확인 #C6'),
 'E21-21': (14, '압력선도 — 리턴 펌프 Trip 상태',
   ['공급 가압 표기 있음', '회수 가압 표기 없음'], '→ 확인 #C22'),
 'E21-22': (14, '학익가압장 펌프 계통 화면 — 리턴 펌프 Trip',
   ['PP-001 Trip 확인'], ''),
 'E21-23': (15, '학익가압장 펌프 계통 화면 — 리턴측 Bypass Open',
   ['HV-9708 Open'], ''),
 'E21-24': (15, '압력선도 — 연료전지&호랑 Pump Trip 발생',
   ['공급 가압 표기만 보임'], '→ 확인 #C22'),
 'E21-25': (16, '학익가압장 펌프 계통 화면 — 공급 펌프 감소',
   ['PP-003 공급 펌프 감소'], ''),
 'E21-26': (16, '압력선도 — 유량 850ton 수준',
   ['공급 가압 표기만 보임'], '캡션: (유량 850ton 수준) → 확인 #C22'),
 'E21-27': (17, '학익가압장 펌프 계통 화면 — 리턴 펌프 기동',
   ['PP-001 기동'], ''),
 'E21-28': (17, '학익가압장 펌프 계통 화면 — 리턴측 Bypass Close',
   ['HV-9708 Close'], ''),
 'E21-29': (19, '압력선도 — 연료전지 또는 호랑에너지 Pump Trip 발생',
   ['공급 가압·회수 가압 표기가 모두 보임'], '→ 확인 #C22'),
 'E21-30': (19, '2621 CRITICAL POINT 화면 — CP-4 구도심 역차압',
   ['CP-4 압력 변화 확인 (SUP./RTN DIFF. PRESS. 열)'], ''),
 'E21-31-A': (20, '학익가압장 펌프 계통 화면 — 공급·리턴 펌프(PP-003, 001) 부하 감소',
   ['PP-003 부하 감소', 'PP-001 부하 감소'],
   '원문 그림번호가 E21-31로 중복(2회). 본 자료 내부 ID: E21-31-A → 확인 #C13'),
 'E21-31-B': (21, 'SK INCHEON H/E SYSTEM(2894) 화면 — SK IPC 펌프',
   ['P-402-10A, B, C 기동 상태 확인', '유량 변화 확인(SK CALORIMETER 1 FLOW RATE)'],
   '원문 그림번호가 E21-31로 중복(2회). 본 자료 내부 ID: E21-31-B → 확인 #C13'),
}

def fig_label(fid):
    return fid.replace('-A', ' (A)').replace('-B', ' (B)') if fid.endswith(('-A', '-B')) else fid

def orig_no(fid):
    return 'E21-31' if fid.startswith('E21-31') else fid

# ---------------------------------------------------------------- 마크업 헬퍼
def mk(s):
    s = s.replace('<t>', '<span class="tg">').replace('</t>', '</span>')
    s = s.replace('<v>', '<span class="vl">').replace('</v>', '</span>')
    s = s.replace('<op>', 'Open').replace('<cl>', 'Close')
    s = s.replace('<k>', '<strong class="kw">').replace('</k>', '</strong>')
    return s

def esc(s):
    return html.escape(s, quote=True)

def chlink(cid):
    return ''

INLINE = {
 'C1': ('본문·Flow Chart ↔ 그림', [('본문 나-1 · Flow Chart', 'PP-003, 001 Trip 확인'), ('그림 E21-04', 'PP-003 / PP-002 / PP-001 Trip 확인 표기')]),
 'C2': ('본문 ↔ 그림 내 문구', [('본문(E21.4.1·4.2)', '<t>PIT-9334</t>는 <v>10[kg/㎠]</v> 수준으로 조정'), ('그림 E21-05 안의 문구', '“PIT-9338 압력 변화 확인 / 11[kg/㎠]초과 상태” (원이 둘러진 위치의 태그는 PIT-9334)')]),
 'C4': ('개요 ↔ Case 1.1', [('E21.4.1 개요', '즉시 <t>HV-9715</t>/<t>HV-9708</t> Open <b>상태를 확인</b>한다 → Open이 확인되면 CN H/E 압력을 확인한다'), ('Case 1.1 본문·Flow Chart', 'CN H/E·연료전지·호랑 확인 <b>후</b> 나-4에서 Bypass를 Open<b>한다</b>')]),
 'C5': ('본문 ↔ Flow Chart', [('본문 나-7', '나-6(Spare 펌프 가동) 다음 줄에서 “가동 성공 시 가압을 실시하고 공급 Bypass Close”'), ('Flow Chart', '“재가동 성공” 열: 가압 실시·공급 Bypass Close / “재가동 불가” 열: Spare 펌프 가동')]),
 'C6': ('본문·Flow Chart ↔ 그림', [('본문 다-1 · Flow Chart', '필요 시 리턴 가압 펌프(<t>PP-001</t>) <b>증가</b>'), ('그림 E21-20 화면 문구', '“PP-001 리턴 펌프 <b>감소</b>”')]),
 'C7': ('본문 ↔ Flow Chart', [('본문 라-3·라-4', '부하 <b>증발</b>한다 (2곳)'), ('Flow Chart', '리턴 펌프 기동 및 부하 <b>증가</b>'), ('본 자료 표기', '“부하 증가”로 표기 (근거: Flow Chart·문맥)')]),
 'C9': ('본문 ↔ 그림 번호', [('본문 다-2', '공급 펌프(PP-003) 감소 … (그림 <b>E21-30</b> 참조)'), ('같은 동작의 라-2', '(그림 <b>E21-25, 30</b> 참조)')]),
 'C10': ('본문 ↔ Flow Chart', [('본문 나-2', '연료전지, 호랑 리턴 압력을 <b>확인</b>한다 (Pump Trip 확인)'), ('Flow Chart', '연료전지·호랑 리턴 압력 <b>과압</b> 확인 (Pump Trip 여부 확인)'), ('참고: Case 2.1 본문', '리턴 압력 <b>감소</b> 및 pump Trip 확인')]),
 'C24': ('본문 ↔ Flow Chart', [('본문 나-6', '가동 <b>전</b> <t>HV-9703</t>, <t>9715</t> Open / <t>HV-9704</t>, <t>9717</t> Close를 확인한다'), ('Flow Chart', '<t>PP-002</t>, 가동 <b>시</b> Line 확인 필 (밸브 태그 없음)')]),
 'C18': ('본문 ↔ Flow Chart', [('본문 다', 'Bypass Valve Open (그림 E21-08 참조) — 밸브 태그 미기재'), ('Flow Chart', 'Bypass Valve Open <t>HV-9715</t>, <t>9708</t>')]),
}

def fig_inline(fid, why=''):
    pg, title, cmp, note = FIGS[fid]
    chips = ''.join(f'<li>{esc(c)}</li>' for c in cmp)
    note_h = f'<p class="fnote">{esc(note)}</p>' if note else ''
    return f'''<figure class="fig" id="f-{fid}-{{uid}}">
<button class="zoom" type="button" data-fig="{fid}" aria-label="그림 {fig_label(fid)} 확대 보기">
<img data-src-id="{fid}" alt="그림 {orig_no(fid)} {esc(title)}" loading="lazy"><span class="zhint">🔍 클릭하여 확대</span></button>
<figcaption><b class="fno">그림 {orig_no(fid)}</b>{('<span class="iid">내부 ID '+fid+'</span>') if fid.endswith(('-A','-B')) else ''}
<span class="ftitle">{esc(title)}</span>
</figcaption></figure>'''

def ref_thumb(fid):
    pg, title, cmp, note = FIGS[fid]
    return f'''<button class="rth" type="button" data-fig="{fid}" title="{esc(title)}">
<img data-src-id="{fid}" alt="" loading="lazy"><span><b>그림 {orig_no(fid)}</b>{' ('+fid[-1]+')' if fid.endswith(('-A','-B')) else ''}<br>{esc(title)}</span></button>'''

WARN_TXT = {'C7': '', 'C12': '원문의 “그림 E21-31”이 두 장이라 어느 쪽을 가리키는지 불명확합니다.', 'C13': '그림 번호 E21-31이 원문에서 중복되어 있습니다(A/B로 구분).'}

_uid = [0]
def uid():
    _uid[0] += 1
    return _uid[0]

KIND = {'chk': ('확인', 'k-chk'), 'op': ('조작', 'k-op'), 'tell': ('연락·공유', 'k-tell'),
        'req': ('요청', 'k-tell'), 'go': ('재개', 'k-go'), 'rec': ('복구', 'k-op')}

def step(n, orig, kind, text, figs=(), refs=(), src='', flags=(), sub='', cond=''):
    kl, kc = KIND[kind]
    figs_h = ''.join(fig_inline(f).replace('{uid}', str(uid())) for f in figs)
    refs_h = ''
    if refs:
        refs_h = '<div class="refs"><span class="flab">참조 그림</span>' + ''.join(fig_inline(r).replace('{uid}', str(uid())) for r in refs if r not in figs) + '</div>'
    fl = ''
    src_h = ''
    cond_h = f'<p class="cond">{mk(cond)}</p>' if cond else ''
    sub_h = f'<div class="sub">{mk(sub)}</div>' if sub else ''
    return f'''<li class="step" id="s-{uid()}">
<div class="stxt"><div class="shead"><span class="sn" aria-label="{n}단계">{n}</span><span class="onum">{esc(orig)}</span></div>
{cond_h}<p class="main">{mk(text)}</p>{sub_h}{fl}{src_h}</div>
<div class="sfig">{figs_h}{refs_h}</div></li>'''

def situation(label, text, figs=(), refs=(), src=''):
    figs_h = ''.join(fig_inline(f).replace('{uid}', str(uid())) for f in figs)
    refs_h = ''
    if refs:
        refs_h = '<div class="refs"><span class="flab">참조 그림</span>' + ''.join(fig_inline(r).replace('{uid}', str(uid())) for r in refs if r not in figs) + '</div>'
    src_h = ''
    return f'''<li class="step sit"><div class="stxt"><div class="shead"><span class="onum">{esc(label)}</span></div>
<p class="main">{mk(text)}</p>{src_h}</div><div class="sfig">{figs_h}{refs_h}</div></li>'''

def branch(title, cond, body, tone='a'):
    return f'''<section class="branch br-{tone}"><header><span class="bl">분기 {tone.upper()}</span><h4>{mk(title)}</h4><p>{mk(cond)}</p></header>
<ol class="steps">{body}</ol></section>'''

def olist(s):
    return '<ol class="steps">' + s + '</ol>'

def stepsblock(items):
    return '<ol class="steps">' + ''.join(items) + '</ol>'

def conflict(items):
    rows = ''.join(f'<tr><th scope="row">{esc(a)}</th><td>{mk(b)}</td></tr>' for a, b in items)
    return rows

def cmpbox(cid, title, rows):
    return f'''<div class="cmpbox" role="note"><div class="cmph">{chlink(cid)} <b>{esc(title)}</b></div>
<table><tbody>{conflict(rows)}</tbody></table></div>'''

def fc(items, tone=''):
    out = []
    for it in items:
        if isinstance(it, tuple):
            cols = ''.join(f'<div class="fcc"><b>{mk(t)}</b>' + ''.join(f'<p>{mk(x)}</p>' for x in ls) + '</div>' for t, ls in it[1])
            out.append(f'<div class="fcbr">{cols}</div>')
        else:
            out.append(f'<div class="fcb">{mk(it)}</div>')
    return '<div class="fcflow">' + '<div class="fca" aria-hidden="true">↓</div>'.join(out) + '</div>'

def fcdetails(page, body, verdict):
    return f'''<details class="fcd"><summary>Flow Chart 보기</summary>
<div class="fcw">{body}</div></details>'''

# ---------------------------------------------------------------- Case 본문
def case_1_1():
    sit = olist(situation('가', '정상 운전 중이며 <k>INTECO FLOW RATE는 <v>1380[ton/hr]</v></k> 상태이다.', figs=['E21-02'], refs=['E21-01'],
                    src='정상 운전 INTECO FLOW RATE 1380[ton/hr]상태이다') + \
          situation('나', '학익가압장 <k>공급 펌프(<t>PP-003</t>)와 리턴 펌프(<t>PP-001</t>)가 동시에 Trip</k> 한 상황이다.', figs=['E21-03'],
                    src='학익가압장 공급, 리턴(PP-003, 001) 펌프 동시 Trip 발생 상황이다.'))
    main = stepsblock([
        step(1, '나-1', 'chk', '학익가압장 공급·리턴 펌프(<t>PP-003</t>, <t>PP-001</t>)의 <k>Trip</k>을 확인한다.', figs=['E21-04'],
             src='학익 가압장 공급, 리턴 펌프(PP-003, 001) Trip 확인한다.', flags=['C1']),
        step(2, '나-2', 'chk', 'CN H/E <k>공급 압력 초과</k>와 <k>유량 변화</k>를 확인한다.', figs=['E21-05'],
             sub='확인 항목: <t>PIT-9334</t>(압력), <t>FIT-9338</t>(유량)', src='CN H/E 공급 압력 초과, 유량 변화를 확인한다.(PIT-9334, FIT-9338)', flags=['C2']),
        step(3, '나-3', 'chk', '연료전지·호랑의 <k>리턴 압력 감소</k>와 <k>Pump Trip</k>을 확인한다.', figs=['E21-06', 'E21-07'],
             sub='연료전지: 리턴 압력 <t>PIT-3501</t> + Pump Trip 확인(그림 E21-06) / 호랑: 리턴 압력 <t>PIT-201</t> + Pump Trip 확인(그림 E21-07)',
             src='연료전지&호랑 리턴 압력 감소 및 pump Trip 확인한다. / 연료전지 리턴 압력(PIT-3501)&Pump Trip 확인한다. / 호랑 리턴 압력(PIT-201)&Pump Trip 확인한다.'),
        step(4, '나-4', 'op', '학익가압장 <k>공급·리턴 Bypass를 <op></k> 한다.', figs=['E21-08'],
             sub='조작 밸브: <t>HV-9715</t> (공급측 Bypass) <op> / <t>HV-9708</t> (리턴측 Bypass) <op>',
             src='학익가압장 공급&리턴 By pass Open한다.(HV-9715, HV-9708)', flags=['C4']),
        step(5, '나-5', 'tell', '<k>외부 열원</k>에 연락하여 상황을 공유한다.', src='외부열원에 연락하여 상황을 공유한다.'),
    ])
    a = branch('연료전지·호랑 Pump Trip이 <u>발생한</u> 경우', '', situation('다', '연료전지·호랑에서 Pump Trip이 발생한 경우이다.', figs=['E21-09']) +
      step(1, '다-1', 'chk', '외부 열원 <k>유량 감소</k>를 확인한다.', figs=['E21-10'], src='외부열원 유량 감소를 확인한다.') +
      step(2, '다-2', 'op', '<k>Mean Pr 압력을 조정</k>한다. (학익가압장 <k>기동 전 상태로 회귀</k>한다.)', figs=['E21-11'],
           sub='기준: <t>Mean Pr</t> <v>5.5[kg/㎠]</v>', src='Mean Pr 압력 조정한다.(학익가압장 기동전 상태로 회귀한다.) <Mean Pr 기준 5.5[kg/㎠]>') +
      step(3, '다-3', 'go', '외부 열원에 <k>정상화 상황을 공유</k>하고 학익가압장 운전을 <k>재개</k>한다.', figs=['E21-12'],
           sub='<b>재개 시점</b>: 학익가압장 정상화, <t>INTECO FLOW RATE</t> <v>850[ton/hr]</v> 수준',
           src='외부열원에 정상화 상황을 공유하고 학익가압장 운전을 재개한다. (재개 시점 : 학익가압장 정상화, 1INTECO FLOW RATE 850[ton/hr] 수준)'), 'a')
    b = branch('연료전지·호랑 Pump Trip이 <u>발생하지 않은</u> 경우', '',
      step(1, '라-1', 'chk', '외부 열원 <k>유량 감소 발생</k>을 확인한다.', refs=['E21-12'], src='외부열원 유량 감소 발생을 확인한다. (그림 E21-12 참조)') +
      step(2, '라-2', 'op', '<k>Mean Pr 압력을 조정</k>하고 학익가압장 <k>기동 전 조건 상태를 준비</k>한다.', refs=['E21-11'],
           sub='기준: <t>Mean Pr</t> <v>5.5[kg/㎠]</v>', src='Mean Pr 압력 조정하고 학익가압장 기동전 조건 상태 준비한다. <Mean Pr 기준 5.5[kg/㎠]> (그림 E21-11 참조)') +
      step(3, '라-3', 'go', '외부 열원에 <k>정상화 상황을 공유</k>하고 학익가압장 운전을 <k>재개</k>한다.', refs=['E21-12'],
           sub='<b>재개 시점</b>: 학익가압장 정상화, <t>INTECO FLOW RATE</t> <v>850[ton/hr]</v> 수준',
           src='외부열원에 정상화 상황 공유하고 학익가압장 운전을 재개한다. (그림 E21-12 참조) (재개 시점 : 학익가압장 정상화, 1INTECO FLOW RATE 850[ton/hr] 수준)'), 'b')
    flow = fc(['정상 운전 INTECO FLOW RATE 1,380[t/h]', '공급·리턴 펌프 동시 Trip 확인<br><t>PP-003, 001</t>',
               'CN H/E 공급 압력 초과·유량 변화 확인<br><t>PIT-9334, FIT-9338</t>', '연료전지·호랑 리턴 압력 감소 및 Pump Trip 확인<br><t>PIT-3501, PIT-201</t>',
               '공급·리턴 Bypass Open<br><t>HV-9715, HV-9708</t>', '외부 열원에 연락하여 상황 공유',
               ('br', [('연료전지·호랑 Pump Trip 발생', ['외부열원 유량 감소 확인', 'Mean Pr 조정 – 기동 전 상태로 회귀<br>Mean Pr 5.5[kg/㎠]']),
                       ('연료전지·호랑 Pump Trip 미발생', ['외부열원 유량 감소 발생 확인', 'Mean Pr 조정 – 기동 전 조건 준비<br>Mean Pr 5.5[kg/㎠]'])]),
               '외부 열원에 정상화 상황 공유, 학익가압장 운전 재개<br>INTECO FLOW RATE 850[t/h] 수준'])
    ver = '<ul><li>단계 순서·태그·분기는 <b>일치</b>합니다.</li><li>단위 표기만 다릅니다: 본문 [ton/hr] / Flow Chart [t/h] (각각 원문 표기 유지) → ' + chlink('C3') + '</li><li>E21.4.1 개요의 Bypass 서술(“즉시 Open 상태 확인”)과 순서가 다릅니다 → ' + chlink('C4') + '</li></ul>'
    return sit + main + '<div class="bhead">연료전지·호랑 Pump Trip 발생 여부에 따른 분기</div><div class="brs">' + a + b + '</div>' + fcdetails('p.23', flow, ver)

def case_1_2():
    sit = olist(situation('가', '정상 운전 중이며 <k>INTECO FLOW RATE는 <v>1380[ton/hr]</v></k> 이다.', refs=['E21-01'],
                    src='정상 운전 상태 INTECO FLOW RATE 1380[ton/hr]이다. (그림 E21-01 참조)') + \
          situation('나', '학익가압장 <k>공급 펌프(<t>PP-003</t>)가 Trip</k> 한 상황이다.', figs=['E21-13'], src='공급 펌프 Trip 발생 상황이다.'))
    main = stepsblock([
        step(1, '나-1', 'chk', '공급 펌프(<t>PP-003</t>)의 <k>Trip 발생</k>을 확인한다.', figs=['E21-14'], src='공급 펌프(PP-003) Trip 발생을 확인한다.'),
        step(2, '나-2', 'op', '<t>HV-9715</t>(공급측 Bypass)를 <op> 한다.', figs=['E21-15'], src='HV-9715(공급측 By pass) Open한다.'),
        step(3, '나-3', 'chk', 'CN H/E <k>공급 압력(<t>PIT-9334</t>) 초과</k>와 <k>유량 변화(<t>FIT-9338</t>)</k>를 확인한다.', refs=['E21-05'],
             src='CN H/E 공급 압력(PIT-9334) 초과, 유량 변화(FIT-9338)를 확인한다.(그림 E21-05 참조)', flags=['C2']),
        step(4, '나-4', 'req', '<k>외부 열원에 수열 감량을 요청</k>한다.', refs=['E21-11', 'E21-12'],
             sub='기준: <t>Mean Pr</t> <v>5.5[kg/㎠]</v>, <t>INTECO FLOW RATE</t> <v>850[ton/hr]</v> 수준',
             src='외부 열원 수열 감량 요청한다. (그림 E21-11, 12 참조) <Mean Pr 기준 5.5[kg/㎠], INTECO FLOW RATE 850[ton/hr] 수준>'),
        step(5, '나-5', 'op', '가압 펌프(<t>PP-003</t>)를 <k>재가동</k>한다.', figs=['E21-16'], src='가압 펌프(PP-003)를 재가동 한다.'),
    ])
    dec = ''
    cond = stepsblock([
        step(6, '나-6', 'op', '<k>Spare 펌프(<t>PP-002</t>)를 가동</k>한다.', figs=['E21-17'], cond='<b>조건</b>: 펌프 재가동이 불가한 상황일 때',
             sub='<b>가동 전 밸브 상태 확인</b>: <t>HV-9703</t> <op> · <t>HV-9715</t> <op> / <t>HV-9704</t> <cl> · <t>HV-9717</t> <cl>',
             src='펌프 재가동 불가 상황 시 Spare펌프(PP-002)를 가동한다. (가동전 HV-9703, 9715 Open / HV-9704, 9717 Close를 확인한다.)', flags=['C24']),
        step(7, '나-7', 'op', '<k>가압을 실시</k>하고 공급 Bypass(<t>HV-9715</t>)를 <cl> 한다.', figs=['E21-18'], cond='<b>조건</b>: 가동에 성공했을 때',
             src='가동 성공시 가압을 실시하고 공급 By pass Close한다. (HV-9715)', flags=['C5']),
        step(8, '나-8', 'tell', '외부 열원에 <k>상황을 공유</k>하고 가압을 진행한다. 추가 수열량이 발생하면 <k>가압 펌프 Trip 전 상태로 복구</k>한다.', refs=['E21-01'],
             cond='<b>조건</b>: 공급 가압 펌프(<t>PP-003</t>, <t>PP-002</t>) 가동이 가능한 경우',
             src='공급 가압 펌프(PP-003, 002) 가동이 가능한 경우 외부열원에 상황을 공유  가압을 진행하고, 추가 수열량이 발생하면 가압 펌프 Trip 전으로 복구한다.(그림 E21-01 참조)'),
        step(9, '나-9', 'chk', '외부 열원의 <k>유량 감량</k>을 확인한다.', refs=['E21-10'],
             cond='<b>조건</b>: 공급 가압 펌프(<t>PP-003</t>, <t>PP-002</t>) 가동이 불가한 경우',
             src='공급 가압 펌프(PP-003, 002) 가동이 불가한 경우, 외부열원 유량 감량을 확인한다.(그림 E21-10 참조)'),
    ])
    stab = '<div class="bhead">설비 안정화 (다)</div>' + stepsblock([
        step(10, '다-1', 'op', '외부 열원 <k>유량 및 Mean Pr을 감소</k>한다. <span class="nb">필요 시 리턴 가압 펌프(<t>PP-001</t>)를 증가한다.</span>', figs=['E21-19', 'E21-20'], refs=['E21-11', 'E21-12'],
             src='외부열원 유량 및 Mean Pr 감소한다.(그림 E21-11, 12 참조) (필요 시 리턴 가압 펌프(PP-001) 증가한다)', flags=['C6']),
        step(11, '다-2', 'chk', 'CN H/E <k>공급 압력 초과 및 유량 변화가 해소</k>되었는지 확인한다.', refs=['E21-05'], src='CN H/E 공급 압력 초과 및 유량 변화가 해소되었는지 확인한다. (그림 E21-05 참조)'),
        step(12, '다-3', 'go', '외부 열원에 <k>내용을 공유</k>하고 학익가압장 운전을 <k>재개</k>한다.', refs=['E21-11', 'E21-12'], src='외부열원에 내용을 공유하고 학익가압장 운전을 재개한다. (그림 E21-11, 12 참조)'),
    ])
    flow = fc(['정상 운전 INTECO FLOW RATE 1,380[t/h]', '공급 펌프 Trip 발생 확인<br><t>PP-003</t>', '<t>HV-9715</t> 공급측 Bypass Open',
               'CN H/E 공급 압력 초과·유량 변화 확인<br><t>PIT-9334, FIT-9338</t>', '외부 열원 수열 감량 요청<br>Mean Pr 5.5[kg/㎠] · INTECO FLOW RATE 850[t/h] 수준', '가압 펌프 재가동',
               ('br', [('재가동 성공', ['가압 실시 · 공급 Bypass Close', '외부열원에 상황 공유 · 가압 진행', '추가 수열량 발생 시 Trip 전으로 복구']),
                       ('재가동 불가', ['Spare 펌프 가동<br><t>PP-002</t>, 가동 시 Line 확인 필', '가동 불가 시 외부열원 유량 감량 확인', '외부열원 유량 및 Mean Pr 감소<br>필요 시 리턴 가압 펌프 증가'])]),
               'CN H/E 공급 압력 초과·유량 변화 해소 확인', '외부열원에 내용 공유, 학익가압장 운전 재개'])
    ver = '<ul><li>순서·태그는 대체로 일치합니다.</li><li>Flow Chart는 “가압 실시·공급 Bypass Close”를 <b>재가동 성공</b> 열에 두고, Spare 펌프(PP-002) 가동 성공 후의 경로는 따로 적지 않았습니다. 본문 나-7 “가동 성공 시”가 가리키는 대상이 불명확합니다 → ' + chlink('C5') + '</li><li>Spare 펌프 밸브 확인 시점: 본문 “가동 <b>전</b>” / Flow Chart “가동 <b>시</b> Line 확인 필” → ' + chlink('C24') + '</li><li>리턴 가압 펌프(PP-001) 조작 방향: 본문·Flow Chart “증가” / 그림 E21-20 화면 문구 “감소” → ' + chlink('C6') + '</li></ul>'
    return sit + main + dec + cond + stab + fcdetails('p.24', flow, ver)

def case_1_3():
    sit = olist(situation('가', '정상 운전 중이며 <k>INTECO FLOW RATE는 <v>1380[ton/hr]</v></k> 이다.', refs=['E21-01'], src='정상 운전 상태 1380[ton/hr]이다. (그림 E21-01 참조)') + \
          situation('나', '학익가압장 <k>리턴 펌프(<t>PP-001</t>)가 Trip</k> 한 상태이다.', figs=['E21-21'], src='리턴 펌프(PP-001) Trip 발생 상태이다.'))
    main = stepsblock([
        step(1, '나-1', 'chk', '리턴 펌프(<t>PP-001</t>)의 <k>Trip 발생</k>을 확인한다.', figs=['E21-22'], src='리턴 펌프(PP-001) Trip 발생 확인한다.'),
        step(2, '나-2', 'op', '<t>HV-9708</t>(리턴측 Bypass)를 <op> 한다.', figs=['E21-23'], src='HV-9708(리턴측 By pass) Open한다.'),
        step(3, '나-3', 'chk', '연료전지·호랑의 <k>리턴 압력 감소</k>와 <k>Pump Trip</k>을 확인한다.', refs=['E21-06', 'E21-07'],
             src='연료전지&호랑 리턴 압력 감소 및 Pump Trip 확인한다. 연료전지 리턴 압력(PIT-3501)&Pump Trip 확인한다.(그림 E21-06, 07 참조)'),
        step(4, '나-4', 'tell', '<k>외부 열원</k>에 연락하여 상황을 공유한다.', src='외부열원에 연락하여 상황을 공유한다.'),
    ])
    a = branch('연료전지·호랑 Pump Trip이 <u>발생한</u> 경우', '',
      situation('다', '연료전지·호랑에서 Pump Trip이 발생한 경우이다.', figs=['E21-24']) +
      step(1, '다-1', 'chk', '외부 열원 <k>유량 감소 발생</k>을 확인한다.', refs=['E21-10'], src='외부열원 유량 감소 발생을 확인한다.(그림 E21-10 참조)') +
      step(2, '다-2', 'op', '학익가압장 <k>공급 펌프(<t>PP-003</t>)를 감소</k>한다. <span class="nb">(구도심 차압 확보 <t>CP-4</t>)</span>', figs=['E21-25'], refs=['E21-30'],
           src='학익가압장 공급펌프(PP-003)를 감소한다.(구도심 차압 확보(CP-4)) (그림 E21-30 참조)', flags=['C9']) +
      step(3, '다-3', 'op', '<k>Mean Pr 압력을 조정</k>하고 학익가압장 <k>기동 전 조건 상태를 준비</k>한다.', refs=['E21-11', 'E21-12'],
           sub='기준: <t>Mean Pr</t> <v>5.5[kg/㎠]</v>, <t>INTECO FLOW RATE</t> <v>850[ton/hr]</v> 수준',
           src='Mean Pr 압력 조정하고 학익가압장 기동전 조건 상태 준비한다. (그림 E21-11, 12 참조) <Mean Pr 기준 5.5[kg/㎠], INTECO FLOW RATE 850[ton/hr] 수준>') +
      '', 'a')
    b = branch('연료전지·호랑 Pump Trip이 <u>발생하지 않은</u> 경우', '',
      situation('라', '외부 열원 유량 감소 상황이며 연료전지·호랑 Pump Trip은 발생하지 않았다.', figs=['E21-26'], refs=['E21-12'],
                src='외부열원 유량 감소(연료전지&호랑 Pump Trip 미발생)한다. (그림 E21-12 참조)') +
      '' +
      step(1, '라-1', 'chk', '외부 열원 <k>유량 감소</k>를 확인한다.', refs=['E21-12'], src='외부열원 유량 감소를 확인한다. (그림 E21-12 참조)') +
      step(2, '라-2', 'op', '학익가압장 <k>공급 펌프(<t>PP-003</t>)를 감소</k>한다. <span class="nb">(구도심 차압 확보 <t>CP-4</t>)</span>', refs=['E21-25', 'E21-30'],
           src='학익가압장 공급 펌프(PP-003) 감소(구도심 차압 확보(CP-4)) 한다.(그림 E21-25, 30 참조)') +
      step(3, '라-3', 'op', '학익가압장 <k>리턴 펌프(<t>PP-001</t>)를 기동</k>하고 <k>부하를 증가</k>한다.', figs=['E21-27'],
           src='학익가압장 리턴 펌프(PP-001) 기동 및 부하 증발한다.', flags=['C7']) +
      step(4, '라-4', 'op', '리턴 펌프(<t>PP-001</t>) <k>기동에 성공</k>하면 부하를 증가하면서 Bypass Valve(<t>HV-9708</t>)를 <cl> 한다.', figs=['E21-28'],
           src='리턴 펌프(PP-001) 기동 성공 시 부하를 증발하며 BY Pass Valve를 Close(HV-9708)한다.', flags=['C7']) +
      step(5, '라-5', 'go', '외부 열원에 <k>정상화 상황을 공유</k>하고 학익가압장 운전을 <k>재개</k>한다.', refs=['E21-11', 'E21-12'], src='외부열원에 정상화 상황 공유하고 학익가압장 운전을 재개한다. (그림 E21-11, 12 참조)'), 'b')
    flow = fc(['정상 운전 INTECO FLOW RATE 1,380[t/h]', '리턴 펌프 Trip 발생 확인<br><t>PP-001</t>', '<t>HV-9708</t> 리턴측 Bypass Open',
               '연료전지·호랑 리턴 압력 감소 및 Pump Trip 확인<br><t>PIT-3501, PIT-201</t>', '외부열원에 연락하여 상황 공유',
               ('br', [('연료전지·호랑 Trip (O)', ['외부열원 유량 감소 발생 확인', '공급펌프 감소(<t>PP-003</t>)<br>구도심 차압 확보(<t>CP-4</t>)', 'Mean Pr 조정 · 기동 전 조건 준비<br>Mean Pr 5.5[kg/㎠]']),
                       ('연료전지·호랑 Trip (X)', ['외부열원 유량 감소 확인', '공급펌프 감소(<t>PP-003</t>)<br>구도심 차압 확보(<t>CP-4</t>)', '리턴 펌프 기동 및 부하 증가(<t>PP-001</t>)', '기동 성공 시 부하 증가하며<br><t>HV-9708</t> Bypass Close'])]),
               '외부열원에 정상화 상황 공유, 학익가압장 운전 재개'])
    ver = '<ul><li>순서·태그는 대체로 일치합니다.</li><li>“부하 <b>증발</b>”(본문 라-3, 라-4) ↔ “부하 <b>증가</b>”(Flow Chart) → ' + chlink('C7') + '</li><li>다 경로의 재개 단계는 본문에 없고 Flow Chart 공통 박스에만 있습니다 → ' + chlink('C25') + '</li><li>그림 참조: 본문 다-2는 E21-30을 참조하지만 공급 펌프 감소 화면은 E21-25 → ' + chlink('C9') + '</li></ul>'
    return sit + main + '<div class="bhead">연료전지·호랑 Pump Trip 발생 여부에 따른 분기</div><div class="brs">' + a + b + '</div>' + fcdetails('p.25', flow, ver)

def case_2_1():
    ov = '''<div class="ovw"><h4>외부 열원·연료전지 펌프 Trip 개요</h4><ul>
<li>정상 운전 중 학익가압장은 공급측과 회수측에 각각 펌프 양정을 추가하고 있다.</li>
<li>외부 열원 또는 연료전지 Pump가 Trip되면 <k>즉시 학익가압장 공급·리턴 펌프 가동률을 저하시켜 구도심 차압을 보상</k>한다.</li>
<li>CN H/E <t>PIT-9334</t>(INT Hot Dis)와 <t>PIT-3501</t>(Fuel cell Re’ Pr’)을 확인하고, <t>PIT-9334</t>는 <v>10[kg/㎠]</v>, <t>PIT-3501</t>은 <v>2.5-3.5[kg/㎠]</v> 수준으로 압력을 조정한다.</li>
<li>기존에 토출되던 유량 <t>FIT-9338</t>(INT CN COLD)과 INTECO FLOW RATE가 감소했는지 확인한다.</li>
<li>학익가압장 기동 전 수준으로 조정한다.</li>
<li>외부 수열원에 연락해 상황을 공유하고, 수열량을 조정하여 설비를 안정화한 뒤 학익가압장을 정상화하고 재개한다.</li></ul>
</div>'''
    sit = ov + olist(situation('가', '정상 운전 중이며 <k>INTECO FLOW RATE는 <v>1380[ton/hr]</v></k> 이다.', refs=['E21-01'], src='정상 운전 상태 1380[ton/hr]이다. (그림 E21-01 참조)') + \
          situation('나', '<k>연료전지 또는 호랑에너지의 Pump가 Trip</k> 한 상황이다.', figs=['E21-29'], src='연료전지 또는 호랑에너지 Pump Trip 발생 상황이다.', refs=[]))
    main = stepsblock([
        step(1, '나-1', 'chk', '연료전지 또는 호랑의 <k>리턴 압력 감소</k>와 <k>Pump Trip</k>을 확인한다.', refs=['E21-06', 'E21-07'], sub='확인 항목: <t>PIT-3501</t>, <t>PIT-201</t>',
             src='연료전지 또는 호랑 리턴 압력 감소 및 pump Trip 확인한다. (PIT-3501, PIT-201) (그림 E21-06, 07 참조)'),
        step(2, '나-2', 'chk', '외부 수열 <k>유량 감소</k>를 확인한다.', refs=['E21-10'], src='외부 수열 유량 감소를 확인한다.(그림 E21-10 참조)'),
        step(3, '나-3', 'chk', '<k>구도심 역차압 발생</k>을 확인한다. (<t>CP-4</t>)', figs=['E21-30'], src='구도심 역차압 발생을 확인한다.(CP-4)'),
        step(4, '나-4', 'op', '학익가압장 공급·리턴 펌프(<t>PP-003</t>, <t>PP-001</t>)의 <k>부하를 감소</k>한다. <k>리턴 가압 펌프를 먼저 감소</k>한다.', figs=['E21-31-A'], refs=['E21-11', 'E21-12'],
             sub='감소 한도: 학익가압장 <b>초기 기동 조건 상태까지</b> 감소',
             src='학익가압장 공급, 리턴 펌프(PP-003, 001) 부하 감소(리턴 가압 펌프 먼저감소)한다.(학익가압장 초기 기동 조건 상태까지 감소한다.) ( 그림 E21-11, 12 참조 )'),
        step(5, '다', 'op', '학익가압장 <k>Bypass Valve를 <op></k> 한다.', refs=['E21-08'], sub='Flow Chart 표기 밸브: <t>HV-9715</t>, <t>HV-9708</t> (본문에는 태그 미기재)',
             src='학익가압장 BY Pass Valve 를 Open 한다.(그림 E21-08 참조)', flags=['C18']),
        step(6, '다-1', 'chk', '<k>구도심 역차압(<t>CP-4</t>)이 해소</k>되었는지 확인한다.', refs=['E21-30'], src='구도심 역차압(CP-4)이 해소되었는지 확인한다.(그림 E21-30 참조)'),
        step(7, '다-2', 'go', '연료전지 또는 호랑이 <k>정상화</k>된 후 학익가압장을 <k>재개</k>하고 <k>수열을 증량</k>한다.', refs=['E21-01'], src='연료전지 또는 호랑 정상화 후 학익가압장 재개 및 수열 증량한다.(그림 E21-01 참조)'),
    ])
    flow = fc(['정상 운전 INTECO FLOW RATE 1,380[t/h]', '연료전지 또는 호랑 리턴 압력 감소 및 Pump Trip 확인<br><t>PIT-3501, PIT-201</t>', '외부 수열 유량 감소 확인', '구도심 역차압 발생 확인(<t>CP-4</t>)',
               '공급·리턴 펌프(<t>PP-003, 001</t>) 부하 감소 (리턴 가압 펌프 먼저 감소)<br>학익가압장 초기 기동 조건 상태까지 감소', '학익가압장 Bypass Valve Open<br><t>HV-9715, 9708</t>', '구도심 역차압 해소 확인(<t>CP-4</t>)', '연료전지 또는 호랑 정상화 후 학익가압장 재개 및 수열 증량'])
    ver = '<ul><li>단계 순서·분기 구조 <b>일치</b>.</li><li>본문에는 Bypass 밸브 태그가 없고 Flow Chart에만 <t>HV-9715</t>, <t>HV-9708</t>이 있습니다 → ' + chlink('C18') + '</li><li>Case 1과 달리 이 Case는 <b>부하 감소 → Bypass Open</b> 순서입니다(원문 그대로).</li></ul>'
    return sit + main + fcdetails('p.26', flow, ver)

def case_2_2():
    sit = olist(situation('가', '정상 운전 중이며 <k>INTECO FLOW RATE는 <v>1380[ton/hr]</v></k> 기준이다.', refs=['E21-01'], src='정상 운전 상태 1380[ton/hr] 기준 (그림 E21-01 참조)') + \
          situation('나', '<k>SK IPC Pump가 Trip</k> 한 상황이다.', refs=['E21-29'], src='SK IPC Pump Trip 발생 상황이다. (그림 E21-29 참조)'))
    main = stepsblock([
        step(1, '나-1', 'chk', '<k>SK IPC Pump Trip</k>과 <k>유량</k>을 확인한다.', figs=['E21-31-B'], src='SK IPC Pump Trip 및 유량을 확인한다.', flags=['C13']),
        step(2, '나-2', 'chk', '연료전지·호랑의 <k>리턴 압력</k>을 확인한다. (<k>Pump Trip 확인</k>)', refs=['E21-06', 'E21-07'], sub='확인 항목: <t>PIT-3501</t>, <t>PIT-201</t>',
             src='연료전지, 호랑 리턴 압력을 확인한다.(Pump Trip 확인) PIT-3501, PIT-201 (그림 E21-06, 07 참조)', flags=['C10']),
        step(3, '나-3', 'chk', '외부 수열 <k>유량 감소</k>를 확인한다.', refs=['E21-10'], src='외부 수열 유량 감소를 확인한다.(그림 E21-10 참조)'),
        step(4, '나-4', 'chk', '<k>구도심 역차압(<t>CP-4</t>) 발생</k>을 확인한다.', refs=['E21-30'], src='구도심 역차압(CP-4) 발생을 확인한다.(그림 E21-30 참조)'),
        step(5, '나-5', 'op', '학익가압장 공급·리턴 펌프의 <k>부하를 감소</k>한다. <k>리턴 가압 펌프를 먼저 감소</k>한다.', refs=['E21-11', 'E21-12', 'E21-31-A'],
             sub='감소 한도: 학익가압장 <b>초기 기동 조건 상태까지</b> 감소',
             src='학익가압장 공급, 리턴 펌프 부하 감소(리턴 가압 펌프 먼저 감소)한다.(학익가압장 초기 기동 조건 상태까지 감소한다.) ( 그림 E21-11, 12, 31 참조 )', flags=['C12']),
        step(6, '다', 'op', '학익가압장 <k>Bypass Valve를 <op></k> 한다.', refs=['E21-08'], sub='Flow Chart 표기 밸브: <t>HV-9715</t>, <t>HV-9708</t> (본문에는 태그 미기재)',
             src='학익가압장 BY Pass Valve를 Open한다.(그림 E21-08 참조)', flags=['C18']),
        step(7, '다-1', 'chk', '<k>구도심 역차압(<t>CP-4</t>)이 해소</k>되었는지 확인한다.', refs=['E21-30'], src='구도심 역차압(CP-4)이 해소되었는지 확인한다.(그림 E21-30 참조)'),
        step(8, '라', 'go', 'SK IPC가 <k>정상화</k>된 후 학익가압장을 <k>재개</k>하고 <k>수열을 증량</k>한다.', refs=['E21-11', 'E21-12'], src='SK IPC 정상화 후 학익가압장 재개 및 수열 증량한다.(그림 E21-11, 12 참조)'),
    ])
    flow = fc(['정상 운전 INTECO FLOW RATE 1,380[t/h]', 'SK IPC Pump Trip 및 유량 확인', '연료전지·호랑 리턴 압력 <b>과압</b> 확인 (Pump Trip 여부 확인)<br><t>PIT-3501, PIT-201</t>', '외부 수열 유량 감소 확인', '구도심 역차압 발생 확인(<t>CP-4</t>)',
               '공급·리턴 펌프(<t>PP-003, 001</t>) 부하 감소 (리턴 가압 펌프 먼저 감소)<br>학익가압장 초기 기동 조건 상태까지 감소', '학익가압장 Bypass Valve Open<br><t>HV-9715, 9708</t>', '구도심 역차압 해소 확인(<t>CP-4</t>)', 'SK IPC 정상화 후 학익가압장 재개 및 수열 증량'])
    ver = '<ul><li>연료전지·호랑 리턴 압력: 본문 “리턴 압력을 <b>확인</b>한다(Pump Trip 확인)” ↔ Flow Chart “리턴 압력 <b>과압</b> 확인(Pump Trip 여부 확인)”. Case 2.1은 “압력 <b>감소</b>”로 서술 → ' + chlink('C10') + '</li><li>상황 그림으로 인용된 E21-29는 “연료전지 또는 호랑에너지 Pump Trip” 압력선도 → ' + chlink('C11') + '</li><li>그 밖의 단계 순서·태그는 일치합니다.</li></ul>'
    return sit + main + fcdetails('p.27', flow, ver)

# ---------------------------------------------------------------- 표 데이터
CHECKS = [
 ('C1', 'Case 1.1 · 그림 E21-04', '그림 E21-04에는 “PP-003 Trip 확인 / PP-002 Trip 확인 / PP-001 Trip 확인” 표기가 모두 있습니다. 본문 나-1과 Flow Chart는 PP-003, 001만 언급합니다. PP-002는 Case 1.2 나-6에서 Spare 펌프로 나옵니다.', 'PP-002 Trip 확인이 이 Case에서 필요한 단계인지, 화면 표기만 있는 것인지 확인 필요. 본 자료는 본문대로 PP-003, 001만 단계에 적었고 그림은 원본 그대로 두었습니다.'),
 ('C2', 'Case 1.1 나-2 · Case 1.2 나-3 · 그림 E21-05', '그림 E21-05 안의 붉은 문구는 “PIT-9338 압력 변화 확인, 11[kg/㎠]초과 상태”입니다. 원이 둘러진 위치의 태그는 PIT-9334이고, 본문은 “PIT-9334 … 10[kg/㎠] 수준으로 조정”입니다(E21.4.1·E21.4.2). FIT-9338은 유량 태그입니다.', '그림 문구의 PIT-9338 / 11[kg/㎠]이 PIT-9334 / 10[kg/㎠]의 오기인지, 별개 기준인지 확인 필요. 본 자료는 어느 쪽도 바꾸지 않았고 11[kg/㎠]를 새 기준으로 쓰지 않았습니다.'),
 ('C3', '유량 단위 표기', 'INTECO FLOW RATE 단위가 본문 [ton/hr], Flow Chart [t/h], 그림 E21-01·10·12 화면 (m3/h)로 각각 다르게 적혀 있습니다. 그림 E21-26 캡션은 “유량 850ton 수준”(시간 단위 없음).', '동일 단위의 표기 차이인지 확인 필요. 본 자료는 각 위치의 원문 단위를 그대로 보존했습니다.'),
 ('C4', 'E21.4.1 개요 ↔ Case 1.1 나-4', '개요: Trip 시 “즉시 HV-9715/HV-9708 <b>Open 상태를 확인</b>한다. Open 상태가 확인되면 CN H/E 압력을 확인…”. Case 1.1·Flow Chart: CN H/E·연료전지·호랑 확인 <b>이후</b> 나-4에서 Bypass를 “<b>Open한다</b>”.', '(1) Bypass가 자동으로 열리는지, 운전원이 조작하는지 (2) 확인 순서 — 개요와 Case 중 무엇을 따를지 확인 필요. 본 자료는 Case 본문 순서를 따랐고 개요 문장은 별도로 표시했습니다.'),
 ('C5', 'Case 1.2 나-7 ↔ Flow Chart', '본문 나-7 “가동 성공 시 가압을 실시하고 공급 Bypass Close(HV-9715)”는 나-6(Spare 펌프 PP-002 가동) 바로 다음에 나옵니다. Flow Chart는 같은 내용을 “재가동 성공” 열에 두고, “재가동 불가” 열에는 Spare 펌프 가동만 적었습니다.', '“가동 성공”이 PP-003 재가동 성공인지, Spare(PP-002) 가동 성공인지(또는 둘 다인지) 확인 필요. 본 자료는 본문 조건 문구를 그대로 표시했습니다.'),
 ('C6', 'Case 1.2 다-1 · 그림 E21-20', '본문·Flow Chart: “(필요 시) 리턴 가압 펌프(PP-001) <b>증가</b>”. 그림 E21-20 화면 문구: “PP-001 리턴 펌프 <b>감소</b>”.', '조작 방향(증가/감소) 확인 필요. 본 자료는 본문·Flow Chart의 “증가”를 표기하고 그림은 원본 그대로 두었으며, 불일치 경고를 붙였습니다.'),
 ('C7', 'Case 1.3 라-3·라-4 ↔ Flow Chart', '본문: “부하 <b>증발</b>한다”(2곳). Flow Chart: “부하 <b>증가</b>”.', '“증발”은 펌프 부하 표현으로 맞지 않고 Flow Chart와 문맥이 “증가”를 가리켜 본문에 “증가”로 적었습니다. 단, 원문 두 곳이 모두 “증발”이므로 원문 확정 확인 필요.'),
 ('C8', 'Case 1.3 라 항목', '원문: “외부열원 유량 감소(연료전지&호랑 Pump Trip 미발생)한다.” 라-1은 “외부열원 유량 감소를 확인한다”, Flow Chart X 열은 “외부열원 유량 감소 확인”. 라 항목만 “감소한다”로 끝나 상황 서술인지 조작인지 불명확합니다.', '상황(“감소 상황이며 …미발생”) 서술로 읽는 것이 Flow Chart와 일치하나, 별도 조작(외부 열원 유량 감소 조치)을 뜻하는지 확인 필요. 본 자료는 상황 서술로 정리하되 원문 문장을 함께 표기했습니다.'),
 ('C9', 'Case 1.3 다-2 ↔ 그림 번호', '다-2 “공급 펌프(PP-003) 감소(구도심 차압 확보(CP-4)) (그림 E21-30 참조)”. 공급 펌프 감소 화면은 E21-25이고 E21-30은 CP 화면입니다. 같은 동작의 라-2는 “(그림 E21-25, 30 참조)”.', '다-2의 참조가 E21-25 누락인지 확인 필요. 본 자료는 원문 배치대로 E21-25를 다-2 옆에 두고 E21-30을 참조 그림으로 연결했습니다.'),
 ('C10', 'Case 2.2 나-2 ↔ Flow Chart', '본문: “연료전지, 호랑 리턴 압력을 확인한다.(Pump Trip 확인)”. Flow Chart: “연료전지·호랑 리턴 압력 <b>과압</b> 확인 (Pump Trip 여부 확인)”. Case 1.1·1.3·2.1은 모두 “리턴 압력 <b>감소</b>”.', '확인 대상이 압력 감소인지 과압인지 확인 필요. 본 자료는 본문과 Flow Chart를 나란히 표시하고 하나로 통일하지 않았습니다.'),
 ('C11', 'Case 2.2 나 ↔ 그림 E21-29', 'Case 2.2 나는 “SK IPC Pump Trip 발생 상황(그림 E21-29 참조)”이지만 E21-29는 Case 2.1(연료전지 또는 호랑에너지 Pump Trip)에 쓰인 압력선도와 동일 번호의 그림입니다.', 'SK IPC 전용 압력선도가 따로 있는지 확인 필요. 본 자료는 참조 그림으로만 연결했습니다.'),
 ('C12', 'Case 2.2 나-5 ↔ 그림 E21-31', '나-5는 “(그림 E21-11, 12, 31 참조)”라고만 씁니다. 원문에는 E21-31이 두 장(p.20 부하 감소 화면, p.21 SK IPC 화면)입니다.', '나-5의 내용(부하 감소)과 그림 내용이 일치하는 (A)를 연결했으나, 원문이 지정한 쪽이 아니므로 확인 필요.'),
 ('C13', '그림 번호 E21-31 중복', '원문에서 E21-31이 p.20(Case 2.1, 부하 감소 화면)과 p.21(Case 2.2, SK IPC 화면)에 두 번 부여되어 있습니다. 이후 번호(E21-32 등)는 없습니다.', '본 자료는 내부 ID를 E21-31-A(p.20) / E21-31-B(p.21)로 구분하고 원문 번호·위치를 함께 적었습니다. 원문 번호 정정 여부는 확인 필요.'),
 ('C14', '명칭: 원도심 / 구도심 / 고시외', '원도심(E21.2 개요 “원도심 사용자 차압 확보”, E21.3.3 ACO “원도심 공급, 회수 압력”), 구도심(Case 1.3·2.1·2.2 “구도심 차압 확보(CP-4)”, “구도심 역차압”), 고시외(E21.3.3 ACO “고시외 공급, 회수 압력 … (CP-4)”)가 모두 쓰입니다. 구도심·고시외는 같은 CP-4를 가리킵니다.', '세 명칭이 같은 대상인지, 서로 다른 지역·사용자인지 원문에 정의가 없어 확인 필요. 본 자료는 각 위치의 원문 명칭을 그대로 썼고 통일하지 않았습니다.'),
 ('C15', '명칭: 외부 열원 호칭', '“외부 열원”(E21.4.1에서 SK IPC·연료전지·호랑으로 정의), “외부수열원”, “외부 수열원”, “외부 수열”(CO 항목·Case 2), “호랑에너지”(Case 2.1 나)이 혼용됩니다. 회수/리턴도 Case 제목은 “회수”, 본문은 “리턴”입니다.', '같은 대상으로 읽히지만 원문이 직접 정의하지 않은 호칭은 통일하지 않고 그대로 두었습니다. 회수=리턴(공급·회수 펌프 동시 Trip = 공급·리턴 PP-003, 001)은 Case 1.1 제목과 본문의 대응으로 확인됩니다.'),
 ('C16', '제목 범위: Case 2', 'E21.4 목차 “Case 2. 외부 열원 또는 연료전지 펌프 Trip”, E21.4.2 “외부 열원 또는 연료전지 펌프 Trip”, Case 2.1 “연료전지 또는 호랑 펌프 Trip”. 호랑이 상위 제목에 없습니다.', '상위 제목의 “연료전지”가 호랑을 포함하는지 확인 필요(외부 열원 정의에는 호랑이 포함).'),
 ('C17', 'E21.4.1 “공통 조건”', '“공통 조건 : CN H/E Flow 750[ton/hr], 연료전지&호랑 630[ton/hr]”. 적용 시점·성격(정상 운전 값인지 조정 기준인지)은 적혀 있지 않습니다. (두 값의 합 750+630=1380은 정상 운전 INTECO FLOW RATE와 같고 그림 E21-01의 750 / 330+300과도 맞지만 원문이 그렇게 설명하지는 않습니다.)', '본 자료는 “원문 ‘공통 조건’”이라는 이름으로만 표기하고 기준값으로 확대 해석하지 않았습니다.'),
 ('C18', 'Case 2.1·2.2 다 — Bypass 밸브', '본문 다는 “학익가압장 BY Pass Valve를 Open한다(그림 E21-08 참조)”로 밸브 태그를 적지 않았고, Flow Chart만 “HV-9715, 9708”을 적었습니다. 그림 E21-08은 HV-9715, HV-9708 Open 화면입니다.', '두 Bypass 모두 Open하는 것으로 정리했으나 원문 본문에 태그가 없어 확인 필요.'),
 ('C19', 'E21.6 안전사항 6)·9)', '6) “운영리더”는 E21.3의 직책(운영그룹장·운영팀장)에 없는 호칭입니다. 9) “…값이 발생할 경우 작업을 즉시 중지한다”는 무엇이 발생하는지(0이 아닌 값 등) 주어가 없습니다.', '직책명·조건 주어는 임의로 보충하지 않고 원문대로 표기했습니다. 확인 필요.'),
 ('C20', 'E21.4.2 개요 / FIT-9338 명칭', 'FIT-9338 괄호 명칭이 E21.4.1은 “(CN INTECO COLD)”, E21.4.2는 “(INT CN COLD)”로 다릅니다. 두 개요 모두 Case별 순서(Bypass, 부하 감소 등)와 직접 맞지 않는 부분이 있습니다(예: E21.4.2는 Bypass를 언급하지 않음).', '기기 태그·화면 명칭은 맞춤법 교정 대상에서 제외하여 그대로 두었습니다. 확인 필요.'),
 ('C21', '표지 개정 이력 표', '표에는 개정번호 0 / 발행일 2026.09 / 수정내용 제정 / 작성란에 “이정제, 심우준, 윤재호”가 적혀 있고 검토·검토·승인란은 대각선(공란)입니다. 작성란의 대각선이 이름과 겹쳐 판독이 어렵습니다.', '표에 적힌 대로 옮겼습니다. 검토·승인 서명 상태는 확인 필요. 파일명에 포함된 날짜(20261001)는 공식 개정일로 사용하지 않았습니다.'),
 ('C22', '압력선도 그림(E21-02·03·09·13·19·21·24·26·29)', '원문은 이 그림들의 출처·산출 조건·수치 의미를 설명하지 않습니다(그림 안에 “송도열원 → 연료전지 압력선도”, “2026-09-30 기준”, “허용설계압 16 bar” 등의 표기가 있음).', '본 자료는 그림 안의 표기를 새로운 운전 기준·Trip 설정값으로 해석하지 않았고, 가압 표기의 유무만 대조 포인트로 적었습니다. 수치 해설이 필요하면 원문 작성자 확인 필요.'),
 ('C23', 'E21.3.3 ACO “#5-10 PUMP”', '“지역차압에 추종하여 #5-10 PUMP 부하조정”의 대상 범위(#5~#10인지)와 PUMP의 소속 설비가 설명되어 있지 않습니다.', '원문 표기 그대로 두었습니다. 확인 필요.'),
 ('C24', 'Case 1.2 나-6 ↔ Flow Chart', '본문: “가동<b>전</b> HV-9703, 9715 Open / HV-9704, 9717 Close를 확인한다”. Flow Chart: “PP-002, 가동 <b>시</b> Line 확인 필”(밸브 태그 없음).', '밸브 상태 확인 시점(가동 전/가동 시)이 같은 의미인지 확인 필요. 본 자료는 본문의 “가동 전” 표현과 밸브 상태를 표기했습니다.'),
 ('C25', 'Case 1.3 다 경로의 종료 단계', '본문 다 경로는 다-3(Mean Pr 조정, 기동 전 조건 준비)에서 끝나고 재개 단계가 없습니다. 라 경로는 라-5에서 재개합니다. Flow Chart는 두 분기 아래에 공통 “정상화 상황 공유, 학익가압장 운전 재개” 박스가 있습니다.', 'Flow Chart 기준으로는 다 경로도 재개로 이어지나 본문에 없어 확인 필요. 본 자료는 본문 단계를 그대로 두고 경고를 표시했습니다.'),
]

TYPOS = [
 ('T1', '“Pump <b>Tirp</b> 발생 경우이다”', '“Pump <b>Trip</b> 발생 경우이다”', 'Case 1.1 다 (p.7)', 'Trip의 철자 오류. 문서 전체의 다른 모든 곳이 “Trip”.'),
 ('T2', '“<b>1</b>INTECO FLOW RATE 850[ton/hr]”', '“INTECO FLOW RATE 850[ton/hr]”', 'Case 1.1 다-3·라-3 재개 시점 (p.9, 2곳)', '선행 숫자 “1”이 수치·단위와 연결되지 않고, 같은 항목의 다른 모든 표기가 “INTECO FLOW RATE”. 불필요한 문자로 판단.'),
 ('T3', '“부하 <b>증발</b>한다” / “부하를 <b>증발</b>하며”', '“부하 <b>증가</b>한다” / “부하를 <b>증가</b>하며”', 'Case 1.3 라-3·라-4 (p.17)', 'Flow Chart가 “부하 증가”로 적었고 펌프 기동 후 부하 상승이라는 문맥과 일치. 다만 원문 2곳이 모두 “증발”이므로 확인 #C7에도 올림.'),
 ('T4', '“By-pass / By pass / BY Pass / Bypass”', '“Bypass”', 'E21.3.3, Case 1.1 나-4, 1.2 나-2·나-7, 1.3 나-2·라-4, 2.1 다, 2.2 다 / Flow Chart', '같은 설비 용어의 표기 혼용. 영문 표기를 하나로 통일. (그림 안의 표기는 수정하지 않음)'),
 ('T5', '“<b>p</b>ump Trip” (소문자)', '“Pump Trip”', 'Case 1.1 나-3, 2.1 나-1', '대소문자 혼용 정리.'),
 ('T6', '“case 1.2 / case 1.3” (소문자)', '“Case 1.2 / Case 1.3”', 'Flow Chart 제목 (p.24, 25)', '다른 Case 제목과 표기 통일.'),
 ('T7', '“연료 전지 회수 압력”', '“연료전지 회수 압력”', 'E21.3.3 ACO', '본문 전체가 “연료전지”로 붙여 씀.'),
 ('T8', '“학익 가압장 공급, 리턴 펌프”', '“학익가압장 공급·리턴 펌프”', 'Case 1.1 나-1', '“학익가압장”은 문서 전체에서 붙여 씀. 쉼표를 가운뎃점으로 정리(의미 불변).'),
 ('T9', '“하고있다” / “Trip상태” / “Open상태” / “1380[ton/hr]상태이다” / “가동 한다” / “Open 한다” / “재가동 한다”', '“하고 있다” / “Trip 상태” / “Open 상태” / “1380[ton/hr] 상태이다” / “가동한다” / “Open한다” / “재가동한다”', 'E21.4.1, Case 1.1 가, Case 1.2 나-5, 2.1 다 등', '띄어쓰기 교정.'),
 ('T10', '“공급 가압 펌프(PP-003, 002) 가동이 가능한 경우 외부열원에 상황을 공유 가압을 진행하고”', '“…상황을 공유하고 가압을 진행하고”', 'Case 1.2 나-8 (p.12)', '“공유”와 “가압” 사이 연결 어미 누락(원문에 빈 간격). Flow Chart “상황 공유 · 가압 진행”으로 뒷받침.'),
 ('T11', '“연료전지&호랑 Pump Trip 발생 경우이다”', '“…발생한 경우이다”', 'Case 1.1 다, Case 1.3 다', '문장 호응(라 항목 “발생하지 않은 경우”와 대칭).'),
 ('T12', '“…정상화 후 재개 및 수열 증량한다”', '“…정상화된 후 재개하고 수열을 증량한다”', 'Case 2.1 다-2, 2.2 라', '“및”으로 이어진 동사 호응 정리(의미 불변).'),
 ('T13', '“Trip 확인한다”, “압력 조정한다” 등 조사가 빠진 문장', '“Trip을 확인한다”, “압력을 조정한다”', '여러 Case', '조사 보충(의미 불변). 조작 대상·순서는 바꾸지 않음.'),
 ('T14', '“INTECO FLOW RATE 유량이 감소하였는지”', '“INTECO FLOW RATE가 감소했는지”', 'E21.4.1, E21.4.2', 'RATE와 유량의 중복 표현 정리.'),
 ('T15', '“연료전지 리턴 압력(PIT-3501)&Pump Trip 확인한다.”(바로 앞 문장과 반복)', '연료전지(PIT-3501)와 호랑(PIT-201)을 한 항목에 정리', 'Case 1.3 나-3 (p.15)', '앞 문장이 두 설비를 다루는데 반복 문장은 연료전지만 적음. 인용 그림(E21-06, 07)과 Flow Chart(PIT-3501, PIT-201)로 뒷받침.'),
 ('T16', '“하며운영리더는” / “따라야함은” / “안된다” / “3)현장근무자는” / “지시없이” / “작업시” / “출입전” / “초과시” / “이하시”', '“하며 운영리더는” / “따라야 함은” / “안 된다” / “3) 현장근무자는” / “지시 없이” / “작업 시” / “출입 전” / “초과 시” / “이하 시”', 'E21.6 안전사항 2)~8)', '띄어쓰기 교정(안전 수치·조건은 변경 없음).'),
 ('T17', '“농도감지기에 값이 \"0\"를 지시할”', '“…값이 \"0\"을 지시할”', 'E21.6 9)', '조사 교정(“영”으로 읽는 숫자 뒤 “을”).'),
]

NOT_CHANGED = [
 ('수치·단위·밸브 상태·조작 순서', '[ton/hr]·[t/h]·[kg/㎠], 10 / 2.5-3.5 / 5.5 / 850 / 1380 / 750 / 630, Open/Close, 조작 순서는 모두 원문 그대로(교정 대상 아님).'),
 ('기기 태그·화면 명칭', 'PP-001~003, HV-9703/9704/9708/9715/9717, PIT-9334·3501·201, FIT-9338, CP-4, Mean Pr, “INT Hot Dis”, “Fuel cell Re’ Pr’”, “(CN INTECO COLD)/(INT CN COLD)” 등은 맞춤법 교정에서 제외.'),
 ('원문 쪽 표기', 'E21.4의 “Page 4 ~ 17 / 18 ~ 22”는 원문 쪽번호이며 실제 쪽 구성과 일치함을 확인.'),
 ('그림 내부', '그림 안의 글씨·색·기기 태그·화살표·붉은 표기는 일절 수정하지 않았고(예: “PIT-9338”, “11[kg/㎠]초과”, “리턴 펌프 감소”) 확인 필요 항목으로만 기록.'),
]

IMAGE_REPORT = '''PDF 30쪽(표지 포함)에서 로고를 제외한 운전화면·압력선도 <b>32장을 모두 무손실로 추출</b>했습니다(누락 0장). 원본 JPEG 스트림을 재압축 없이 그대로 내장했고, 확대 시 원본 해상도 그대로 볼 수 있습니다.
원문 그림번호는 E21-01 ~ E21-31이고 E21-31이 2장이라 총 32장입니다. 이 자료의 Flow Chart(p.23~27)와 표지·목차·안전사항에는 이미지가 없습니다(표·글자만 있음).'''


def overview():
    def chain(items):
        return '<ol class="ovc">' + ''.join(f'<li>{mk(i)}</li>' for i in items) + '</ol>'
    def branch(q, kind, paths):
        cols = ''.join(f'<div class="ovp"><b><span class="pl">경로 {l}</span> {mk(t)}</b>{chain(it)}</div>' for l, t, it in paths)
        return f'<div class="ovb"><div class="ovq"><span class="ovk">{kind}</span> ◆ {mk(q)}</div><div class="ovpp">{cols}</div></div>'
    def case(cid, name, trip, pre, br, end):
        return f'''<article class="ovcase"><header><a class="cbadge" href="#{cid}">{name}</a><h3>{mk(trip)}</h3><a class="go" href="#{cid}">상세 절차 보기 →</a></header>
{chain(pre)}{br}<div class="ove">{mk(end)}</div></article>'''
    C = []
    C.append(case('case-1-1', 'Case 1.1', '공급·리턴 펌프(<t>PP-003</t>, <t>PP-001</t>) <b>동시</b> Trip',
        ['공급·리턴 펌프 동시 Trip 확인 <t>PP-003, 001</t>', 'CN H/E 공급 압력 초과·유량 변화 확인 <t>PIT-9334, FIT-9338</t>', '연료전지·호랑 리턴 압력 감소 및 Pump Trip 확인 <t>PIT-3501, PIT-201</t>', '공급·리턴 Bypass <op> <t>HV-9715, HV-9708</t>', '외부 열원에 연락하여 상황 공유'],
        branch('연료전지·호랑 Pump Trip 발생 여부', '상태 분기 · 앞서 확인한 결과로 선택', [
            ('A', '발생', ['외부 열원 유량 감소 확인', 'Mean Pr 조정 – 기동 전 상태로 회귀 <v>5.5[kg/㎠]</v>']),
            ('B', '미발생', ['외부 열원 유량 감소 발생 확인', 'Mean Pr 조정 – 기동 전 조건 준비 <v>5.5[kg/㎠]</v>'])]),
        '합류 → 외부 열원에 정상화 상황 공유, 학익가압장 운전 <b>재개</b> (<t>INTECO FLOW RATE</t> <v>850[t/h]</v> 수준)'))
    C.append(case('case-1-2', 'Case 1.2', '공급 펌프(<t>PP-003</t>) Trip',
        ['공급 펌프 Trip 발생 확인 <t>PP-003</t>', '공급측 Bypass <op> <t>HV-9715</t>', 'CN H/E 공급 압력 초과·유량 변화 확인 <t>PIT-9334, FIT-9338</t>', '외부 열원 수열 감량 요청 (Mean Pr <v>5.5[kg/㎠]</v> · <t>INTECO FLOW RATE</t> <v>850[t/h]</v> 수준)', '가압 펌프 재가동 <t>PP-003</t>'],
        branch('가압 펌프 재가동 결과', '결과 분기 · 조작한 결과로 선택', [
            ('A', '재가동 성공', ['가압 실시 · 공급 Bypass <cl> <t>HV-9715</t>', '외부 열원에 상황 공유 · 가압 진행', '추가 수열량 발생 시 Trip 전으로 복구']),
            ('B', '재가동 불가', ['Spare 펌프 가동 <t>PP-002</t> (가동 시 Line 확인)', '가동 불가 시 외부 열원 유량 감량 확인', '외부 열원 유량 및 Mean Pr 감소 (필요 시 리턴 가압 펌프 증가)'])]),
        '합류 → CN H/E 공급 압력 초과·유량 변화 해소 확인 → 외부 열원에 내용 공유, 학익가압장 운전 <b>재개</b>'))
    C.append(case('case-1-3', 'Case 1.3', '리턴 펌프(<t>PP-001</t>) Trip',
        ['리턴 펌프 Trip 발생 확인 <t>PP-001</t>', '리턴측 Bypass <op> <t>HV-9708</t>', '연료전지·호랑 리턴 압력 감소 및 Pump Trip 확인 <t>PIT-3501, PIT-201</t>', '외부 열원에 연락하여 상황 공유'],
        branch('연료전지·호랑 Pump Trip 발생 여부', '상태 분기 · 앞서 확인한 결과로 선택', [
            ('A', 'Trip 발생', ['외부 열원 유량 감소 발생 확인', '공급 펌프 감소 <t>PP-003</t> (구도심 차압 확보 <t>CP-4</t>)', 'Mean Pr 조정 · 기동 전 조건 준비 <v>5.5[kg/㎠]</v>']),
            ('B', 'Trip 미발생', ['외부 열원 유량 감소 확인', '공급 펌프 감소 <t>PP-003</t> (구도심 차압 확보 <t>CP-4</t>)', '리턴 펌프 기동 및 부하 증가 <t>PP-001</t>', '기동 성공 시 부하 증가하며 <t>HV-9708</t> Bypass <cl>'])]),
        '합류 → 외부 열원에 정상화 상황 공유, 학익가압장 운전 <b>재개</b>'))
    C.append(case('case-2-1', 'Case 2.1', '연료전지 또는 호랑 펌프 Trip',
        ['연료전지 또는 호랑 리턴 압력 감소 및 Pump Trip 확인 <t>PIT-3501, PIT-201</t>', '외부 수열 유량 감소 확인', '구도심 역차압 발생 확인 <t>CP-4</t>', '공급·리턴 펌프 부하 감소 <t>PP-003, 001</t> (<b>리턴 가압 펌프 먼저</b> 감소) – 학익가압장 초기 기동 조건 상태까지', '학익가압장 Bypass Valve <op> <t>HV-9715, 9708</t>', '구도심 역차압 해소 확인 <t>CP-4</t>'],
        '', '연료전지 또는 호랑 정상화 후 학익가압장 <b>재개</b> 및 수열 증량 (분기 없음)'))
    C.append(case('case-2-2', 'Case 2.2', 'SK IPC 펌프 Trip',
        ['SK IPC Pump Trip 및 유량 확인', '연료전지·호랑 리턴 압력 확인 (Pump Trip 여부 확인) <t>PIT-3501, PIT-201</t>', '외부 수열 유량 감소 확인', '구도심 역차압 발생 확인 <t>CP-4</t>', '공급·리턴 펌프 부하 감소 <t>PP-003, 001</t> (<b>리턴 가압 펌프 먼저</b> 감소) – 학익가압장 초기 기동 조건 상태까지', '학익가압장 Bypass Valve <op> <t>HV-9715, 9708</t>', '구도심 역차압 해소 확인 <t>CP-4</t>'],
        '', 'SK IPC 정상화 후 학익가압장 <b>재개</b> 및 수열 증량 (분기 없음)'))
    pick = '''<div class="ovpick">
<div class="ovask">Case 구분</div>
<div class="ovgrp"><section><h4>Case 1 : 학익가압장 Pump Trip</h4><ul>
<li><a href="#case-1-1"><b>공급·리턴 동시</b> Trip<em>Case 1.1</em></a><p class="ovbr">분기: 연료전지·호랑 Pump Trip 발생 / 미발생</p></li>
<li><a href="#case-1-2"><b>공급 펌프만</b> Trip<em>Case 1.2</em></a><p class="ovbr">분기: 재가동 성공 / 재가동 불가</p></li>
<li><a href="#case-1-3"><b>리턴 펌프만</b> Trip<em>Case 1.3</em></a><p class="ovbr">분기: 연료전지·호랑 Pump Trip 발생 / 미발생</p></li></ul></section>
<section><h4>Case 2 : 외부열원 Pump Trip</h4><ul>
<li><a href="#case-2-1"><b>연료전지 또는 호랑</b> Pump Trip<em>Case 2.1</em></a></li>
<li><a href="#case-2-2"><b>SK IPC</b> Pump Trip<em>Case 2.2</em></a></li></ul></section></div></div>'''
    return f'<section id="s0" class="sec"><h2>개요</h2>{pick}</section>'

# ---------------------------------------------------------------- HTML 조립
CSS = open(os.path.join(HERE, 'style.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'app.js'), encoding='utf-8').read()

def img_lib():
    d = {}
    for fid in FIGS:
        with open(os.path.join(HERE, 'images', fid + '.jpg'), 'rb') as f:
            d[fid] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()
    items = ',\n'.join(f'"{k}":"{v}"' for k, v in d.items())
    meta = ',\n'.join(
        '"%s":{"no":"%s","pg":%d,"title":"%s"}' % (k, orig_no(k), FIGS[k][0], FIGS[k][1].replace('"', '\\"')) for k in FIGS)
    return '{' + items + '}', '{' + meta + '}'

def build():
    lib, meta = img_lib()
    roles = [
     ('E21.3.1', '운영그룹장', ['발전설비 및 DH 설비 이상 유무 확인', '열 공급 이상 유무 확인', '운영팀장 및 현재 상태 보고', '발전설비 및 DH 설비 정상화 진행사항 파악', '외부 열원 압력 및 유량 정상화 진행사항 파악']),
     ('E21.3.2', 'CO', ['학익가압장 비상 상황 발생원인 파악', '외부 수열 압력 및 유량 확인, 외부 열원 측 상황 공유', '발전소 공급, 회수 압력 확인']),
     ('E21.3.3', 'ACO', ['학익가압장 펌프 및 Bypass 상태 확인 및 대응', 'CN H/E 공급 압력 확인 및 대응(Case 참조)', '연료전지 회수 압력 확인 및 대응(Case 참조)', '지역차압에 추종하여 #5-10 PUMP 부하조정', '원도심 공급, 회수 압력 확인 및 대응', '고시외 공급, 회수 압력 확인 및 대응(CP-4)', '가압장 기동 전, 후 연계유량 변화 확인(급감 또는 역방향 여부)', '외부 열원 펌프 운전 상태 확인 및 대응']),
     ('E21.3.4', 'CLO', ['학익가압장 차단기 Fault 발생 시 Reset 조치(운영그룹장 확인필)', '무전 지시에 따른 현장 상황 대응']),
     ('E21.3.5', 'DLO', ['무전 지시에 따른 현장 상황 대응']),
    ]
    role_h = ''.join(
        f'<article class="role"><header><span class="rid">{rid}</span><h3>{name}</h3></header><ul>' + ''.join(f'<li>{mk(esc(i))}</li>' for i in items) + '</ul></article>'
        for rid, name, items in roles)

    eq = [
     ('PP-003', '공급(가압) 펌프', '“공급 펌프(PP-003)”, “가압 펌프(PP-003)”', 'Case 1.1~1.3, 2.1, 2.2'),
     ('PP-001', '리턴(회수) 가압 펌프', '“리턴 펌프(PP-001)”, “리턴 가압 펌프(PP-001)”', 'Case 1.1~1.3, 2.1, 2.2'),
     ('PP-002', 'Spare 펌프', 'Case 1.2 나-6 “Spare 펌프(PP-002)”', 'Case 1.2 (그림 E21-04에도 표기)'),
     ('HV-9715', '공급측 Bypass', '“HV-9715(공급측 Bypass)”', 'Case 1.1·1.2 Open, 1.2 나-7 Close, 2.x Flow Chart'),
     ('HV-9708', '리턴측 Bypass', '“HV-9708(리턴측 Bypass)”', 'Case 1.1·1.3 Open, 1.3 라-4 Close, 2.x Flow Chart'),
     ('HV-9703 · HV-9715', 'Spare 펌프(PP-002) 가동 전 Open 확인', 'Case 1.2 나-6', 'Open'),
     ('HV-9704 · HV-9717', 'Spare 펌프(PP-002) 가동 전 Close 확인', 'Case 1.2 나-6', 'Close'),
     ('PIT-9334', 'CN H/E 공급 압력 (INT Hot Dis)', 'E21.4.1·4.2, Case 1.1 나-2, 1.2 나-3', '조정 수준 10[kg/㎠]'),
     ('FIT-9338', 'CN H/E 유량 (E21.4.1 CN INTECO COLD / E21.4.2 INT CN COLD)', '“기존에 토출되던 유량”', '감소 여부 확인'),
     ('PIT-3501', '연료전지 리턴 압력 (Fuel cell Re’ Pr’)', 'E21.4.1·4.2, Case 1.1 나-3, 1.3 나-3, 2.x', '조정 수준 2.5-3.5[kg/㎠]'),
     ('PIT-201', '호랑 리턴 압력', 'Case 1.1 나-3, 1.3 나-3, 2.x', '리턴 압력 확인'),
     ('INTECO FLOW RATE', '그림 E21-01 화면의 INTECO FLOW RATE(RECEIVE)', '정상 1380[ton/hr] → 재개 시점 850[ton/hr] 수준', '단위 표기'),
     ('Mean Pr', '“Mean Pr”', '“Mean Pr 기준 5.5[kg/㎠]”', '압력 조정 기준'),
     ('CP-4', '구도심 역차압·차압 확인 항목', 'Case 1.3, 2.1, 2.2, ACO “고시외 … (CP-4)”', '명칭'),
     ('P-402-10A/B/C', 'SK IPC 펌프(그림 E21-31 (B) 화면 표기)', 'Case 2.2 나-1', '기동 상태 확인'),
    ]
    eq_h = ''.join(f'<tr><th scope="row"><span class="tg">{a}</span></th><td>{esc(b)}</td><td>{esc(c)}</td><td>{mk(esc(d))}</td></tr>' for a, b, c, d in eq)

    values = [
     ('정상 운전 상태', 'INTECO FLOW RATE', '<v>1380[ton/hr]</v>', 'Case 1.1~2.2 “가. 정상 운전”, Flow Chart [t/h]', '정상 운전 상태 예시'),
     ('“공통 조건”', 'CN H/E Flow / 연료전지&호랑', '<v>750[ton/hr]</v> / <v>630[ton/hr]</v>', 'E21.4.1', '“공통 조건”으로 표기'),
     ('압력 조정 수준', '<t>PIT-9334</t>', '<v>10[kg/㎠]</v> 수준', 'E21.4.1 · E21.4.2', '조정 기준 (Trip 설정값 아님)'),
     ('압력 조정 수준', '<t>PIT-3501</t>', '<v>2.5-3.5[kg/㎠]</v> 수준', 'E21.4.1 · E21.4.2', '조정 기준 (Trip 설정값 아님)'),
     ('압력 조정 기준', '<t>Mean Pr</t>', '<v>5.5[kg/㎠]</v>', 'Case 1.1~1.3 “Mean Pr 기준”', '조정 기준'),
     ('유량 조정 수준', '학익가압장 기동 전 수준 (INTECO FLOW RATE)', '약 <v>850[ton/hr]</v>', 'E21.4.1', '조정 기준'),
     ('재개 조건', '학익가압장 정상화 + INTECO FLOW RATE', '<v>850[ton/hr]</v> 수준', 'Case 1.1 다-3·라-3, Flow Chart [t/h]', '재개 시점'),
     ('감량 요청 시 기준', 'Mean Pr / INTECO FLOW RATE', '<v>5.5[kg/㎠]</v> / <v>850[ton/hr]</v> 수준', 'Case 1.2 나-4, Case 1.3 다-3', '조정 기준'),
    ]
    val_h = ''.join(f'<tr><td>{a}</td><td>{mk(b)}</td><td class="num">{mk(c)}</td><td>{d}</td><td><span class="ty">{mk(e)}</span></td></tr>' for a, b, c, d, e in values)

    cmp_rows = [
     ('Trip 대상', '공급·리턴 펌프(<t>PP-003</t>, <t>PP-001</t>) 동시', '공급 펌프(<t>PP-003</t>)', '리턴 펌프(<t>PP-001</t>)', '연료전지 또는 호랑 Pump', 'SK IPC Pump'),
     ('첫 확인', '<t>PP-003</t>, <t>PP-001</t> Trip (나-1)', '<t>PP-003</t> Trip (나-1)', '<t>PP-001</t> Trip (나-1)', '<t>PIT-3501</t>, <t>PIT-201</t> 리턴 압력 감소·Pump Trip (나-1)', 'SK IPC Pump Trip·유량 (나-1)'),
     ('Bypass 조작', '<t>HV-9715</t> <op> + <t>HV-9708</t> <op> (나-4, 압력·유량 확인 후)', '<t>HV-9715</t> <op> (나-2, Trip 확인 직후)', '<t>HV-9708</t> <op> (나-2, Trip 확인 직후)', 'Bypass Valve <op> (다, 부하 감소 후) · Flow Chart <t>HV-9715</t>, <t>9708</t>', 'Bypass Valve <op> (다, 부하 감소 후) · Flow Chart <t>HV-9715</t>, <t>9708</t>'),
     ('CN H/E 확인<br>(<t>PIT-9334</t>, <t>FIT-9338</t>)', '나-2', '나-3, 다-2(해소 확인)', '— (기재 없음)', '— (기재 없음)', '— (기재 없음)'),
     ('연료전지·호랑 리턴 압력<br>(<t>PIT-3501</t>, <t>PIT-201</t>)', '나-3', '— (기재 없음)', '나-3', '나-1', '나-2'),
     ('외부 열원 유량 감소 확인', '다-1 / 라-1', '나-9(가동 불가 시)', '다-1 / 라-1', '나-2', '나-3'),
     ('구도심 역차압·차압 (<t>CP-4</t>)', '— (기재 없음)', '— (기재 없음)', '다-2·라-2 “구도심 차압 확보”', '나-3, 다-1', '나-4, 다-1'),
     ('학익가압장 펌프 조작', '(펌프 조작 기재 없음)', '<t>PP-003</t> 재가동 → 불가 시 Spare <t>PP-002</t> 가동 (가동 전 밸브 상태 확인)', '발생 시: <t>PP-003</t> 감소<br>미발생 시: <t>PP-003</t> 감소 → <t>PP-001</t> 기동·부하 증가 → <t>HV-9708</t> <cl>', '<t>PP-003</t>, <t>PP-001</t> 부하 감소(<k>리턴 가압 펌프 먼저</k>), 초기 기동 조건까지', '<t>PP-003</t>, <t>PP-001</t> 부하 감소(<k>리턴 가압 펌프 먼저</k>), 초기 기동 조건까지'),
     ('Mean Pr 조정 (<v>5.5[kg/㎠]</v>)', '다-2 / 라-2', '나-4(감량 요청 시 기준), 다-1(감소)', '다-3', '— (기재 없음)', '— (기재 없음)'),
     ('재개', '학익가압장 정상화 + <t>INTECO FLOW RATE</t> <v>850[ton/hr]</v> 수준', 'CN H/E 압력·유량 해소 확인 후 공유·재개', '정상화 상황 공유 후 재개 (라-5, Flow Chart)', '연료전지 또는 호랑 정상화 후 재개 및 수열 증량', 'SK IPC 정상화 후 재개 및 수열 증량'),
    ]
    cmp_h = '<thead><tr><th scope="col">구분</th><th scope="col"><a href="#case-1-1">Case 1.1</a></th><th scope="col"><a href="#case-1-2">Case 1.2</a></th><th scope="col"><a href="#case-1-3">Case 1.3</a></th><th scope="col"><a href="#case-2-1">Case 2.1</a></th><th scope="col"><a href="#case-2-2">Case 2.2</a></th></tr></thead><tbody>' + ''.join(
        '<tr><th scope="row">' + mk(r[0]) + '</th>' + ''.join(f'<td>{mk(c)}</td>' for c in r[1:]) + '</tr>' for r in cmp_rows) + '</tbody>'

    safety = [
     '현장근무자(CLO, DLO)와 제어실 근무자(CO, ACO)는 동료 상호 간 예의를 지켜야 하며, 설비의 안전 운전을 위하여 화합해야 한다.',
     '명령계통은 확립되어 있어야 하며, 조작지시를 따라야 함은 물론 <k>독단적인 행동을 절대 금한다.</k>',
     '현장근무자는 설비조작의 신속처리 등을 이유로 <k>안전조치 및 안전장구(안전화, 안전모, 귀마개 등)의 사용을 생략하여서는 안 된다.</k>',
     '<k>제어실 근무자의 명령이나 지시 없이 임의적으로 설비를 조작하거나 독단으로 기기를 조작하여서는 안 된다.</k>',
     '현장근무자는 근무성격과 기상, 주위환경 등을 고려하여 근무에 지장이 없도록 적합한 복장을 단정히 착용하고, 불필요한 물건을 부착 또는 착용하지 말아야 하며, 작업화의 끈은 작업화 안에 집어넣어야 한다.',
     '현장근무자는 근무성질상 필요한 안전장구를 반드시 사용하여야 하며, 운영리더는 현장 근무자가 안전장구를 착용하고 사용하도록 하는 책임을 진다. ' + chlink('C19'),
     '현장근무자는 안전장구의 위치, 사용법, 성능 등을 숙지하고 사용범위를 초과하여 사용하지 않도록 하여야 한다.',
     '<k>밀폐공간 작업 시</k> 작업지휘자를 배치하고, 출입 전 산소농도를 필히 측정하여야 하며, 작업장소에는 측정기를 비치하여 산소농도에 대한 지속적인 측정이 이루어져야 한다. 산소농도 <v>18% 이하</v> 시 출입을 금하며, 충분한 산소공급이 이루어지는 상태에서 산소농도 측정값이 <v>18%를 초과</v>할 때 출입하여야 한다.',
     '<k>폭발위험지역에서 작업 시</k> 작업 전 인화성가스의 농도 측정이 필히 이루어져야 하고, 농도감지기에 값이 <v>“0”</v>을 지시할 경우에만 작업을 시행하며, 가스농도측정기를 작업장소에 비치하고 지속적인 측정이 이루어지도록 하며, <b>값이 발생할 경우 작업을 즉시 중지한다.</b> ' + chlink('C19'),
    ]
    safety_h = ''.join(f'<li><span class="sn2">{i+1})</span><span>{mk(s)}</span></li>' for i, s in enumerate(safety))

    chk_h = ''.join(f'<article class="citem" id="c-{cid}"><h4><span class="cid">#{cid}</span> {esc(loc)}</h4><div class="cwhat"><b>원문 내용</b><p>{mk(what)}</p></div><div class="cdo"><b>본 자료의 처리 / 필요한 확인</b><p>{mk(do)}</p></div></article>' for cid, loc, what, do in CHECKS)
    typo_h = ''.join(f'<tr id="t-{tid}"><th scope="row">{tid}</th><td class="bf">{mk(b)}</td><td class="af">{mk(a)}</td><td>{esc(loc)}</td><td>{esc(why)}</td></tr>' for tid, b, a, loc, why in TYPOS)
    nc_h = ''.join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in NOT_CHANGED)

    cases = [
     ('case-1-1', 'Case 1.1', '공급·회수 펌프 동시 Trip', '', case_1_1()),
     ('case-1-2', 'Case 1.2', '공급 펌프 Trip', '', case_1_2()),
     ('case-1-3', 'Case 1.3', '리턴 펌프 Trip', '', case_1_3()),
     ('case-2-1', 'Case 2.1', '연료전지 또는 호랑 펌프 Trip', '', case_2_1()),
     ('case-2-2', 'Case 2.2', 'SK IPC 펌프 Trip', '', case_2_2()),
    ]
    cases_h = ''.join(f'<section class="case" id="{cid}"><header class="chead"><span class="cbadge">{cn}</span><h3>{esc(ct)}</h3><span class="cpg">{cp}</span></header>{cb}</section>' for cid, cn, ct, cp, cb in cases)

    gallery = ''.join(ref_thumb(f) for f in ['E21-01', 'E21-04', 'E21-05', 'E21-06', 'E21-07', 'E21-08', 'E21-30', 'E21-31-A', 'E21-31-B'])

    nav = '''<nav id="toc" aria-label="목차"><div class="navin"><a class="brand" href="#top">학익가압장 비상상황 대응</a>
<ul class="navl"><li><a href="#s0">개요</a></li><li><a href="#s5">① 상황별 대응</a></li></ul>
<ul class="casel" aria-label="Case 바로가기"><li><a href="#case-1-1">1.1 공급·회수 동시</a></li><li><a href="#case-1-2">1.2 공급</a></li><li><a href="#case-1-3">1.3 리턴</a></li><li><a href="#case-2-1">2.1 연료전지·호랑</a></li><li><a href="#case-2-2">2.2 SK IPC</a></li></ul>
<div class="tools"><button id="btnPrint" type="button">인쇄 / PDF</button></div></div></nav>'''

    body = f'''<a class="skip" href="#s0">본문으로 건너뛰기</a><a class="totop" href="#toc">↑ 목차</a>
{nav}
<main id="top">
<header class="hero"><p class="eyebrow">운전원 교육용 설명자료</p><h1>학익가압장 운전 비상상황 대응절차</h1>
</header>

{overview()}
<section id="s5" class="sec"><h2><span class="no">①</span> 상황별 상세 대응</h2>


{cases_h}
</section>




</main>
<div id="lb" class="lb" hidden role="dialog" aria-modal="true" aria-label="그림 확대 보기"><div class="lbbar"><span id="lbt"></span><span class="lbc"><button type="button" id="lbm" aria-label="축소">−</button><button type="button" id="lbf">화면 맞춤</button><button type="button" id="lbo">원본 크기</button><button type="button" id="lbp" aria-label="확대">＋</button><button type="button" id="lbx" aria-label="닫기">✕ 닫기 (Esc)</button></span></div><div class="lbv" id="lbv"><img id="lbi" alt=""></div></div>
<noscript><p style="padding:16px;background:#fff3cd">이 문서의 이미지는 JavaScript로 표시됩니다. JavaScript를 켜거나, 함께 제공된 images 폴더의 원본 JPEG(E21-01.jpg 등)를 직접 열어 확인하십시오.</p></noscript>'''

    body = mk(body)
    doc = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>학익가압장 운전 비상상황 대응절차 설명자료</title>
<meta name="description" content="학익가압장 운전 비상상황 대응절차 설명자료">
<style>{CSS}</style></head><body>
{body}
<script>const IMG={lib};const META={meta};</script>
<script>{JS}</script></body></html>'''
    out = os.path.join(HERE, 'hakik-emergency-response.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(doc)
    print('wrote', out, round(len(doc) / 1e6, 2), 'MB')

if __name__ == '__main__':
    build()
