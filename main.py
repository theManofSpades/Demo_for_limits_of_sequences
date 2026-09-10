import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider, Button
from matplotlib.animation import FuncAnimation

N_MAX = 60

SAFE = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
    'exp': np.exp, 'log': np.log, 'log10': np.log10, 'log2': np.log2,
    'sqrt': np.sqrt, 'abs': np.abs, 'sign': np.sign,
    'pi': np.pi, 'e': np.e, 'floor': np.floor, 'ceil': np.ceil,
}

def make_seq(expr):
    code = compile(expr, '<seq>', 'eval')
    def f(n):
        env = dict(SAFE); env['n'] = n
        return eval(code, {'__builtins__': {}}, env)
    return f

state = {
    'expr':  '1/n',
    'limit': 0.0,
    'eps':   0.2,
    'k':     N_MAX,
    'n':     np.arange(1, N_MAX + 1).astype(float),
    'y':     None,
    'err':   None,
    'help_page': 0,
    'help_open': False,
}

def compute():
    try:
        f = make_seq(state['expr'])
        y = np.asarray(f(state['n']), dtype=float)
        if y.ndim == 0:
            y = np.full_like(state['n'], float(y))
        state['y'] = y
        state['err'] = None
    except Exception as e:
        state['y'] = None
        state['err'] = str(e)


# =========================================================
#  Фигура
# =========================================================
fig = plt.figure(figsize=(15, 9))
fig.suptitle('Анимация определения предела последовательности',
             fontsize=14, y=0.985)

ax      = fig.add_axes([0.045, 0.44, 0.55, 0.50])
ax_nbhd = fig.add_axes([0.045, 0.07, 0.55, 0.28])

ax_info = fig.add_axes([0.65, 0.07, 0.33, 0.52])
ax_info.set_xticks([]); ax_info.set_yticks([])
for s in ax_info.spines.values():
    s.set_visible(False)
info_text = ax_info.text(0, 1, '', va='top', ha='left',
                         fontsize=10, family='monospace')

ax_expr = fig.add_axes([0.65, 0.93, 0.33, 0.045])
tb_expr = TextBox(ax_expr, 'a_n = ', initial=state['expr'])

ax_lim = fig.add_axes([0.65, 0.87, 0.33, 0.045])
tb_lim = TextBox(ax_lim, 'гипотеза L = ', initial='0')

ax_eps = fig.add_axes([0.65, 0.80, 0.33, 0.03])
sl_eps = Slider(ax_eps, 'ε', 0.001, 3.0, valinit=state['eps'])

ax_k = fig.add_axes([0.65, 0.74, 0.33, 0.03])
sl_k = Slider(ax_k, 'k ', 1, N_MAX, valinit=N_MAX, valstep=1)

ax_btn = fig.add_axes([0.65, 0.65, 0.33, 0.045])
btn = Button(ax_btn, '▶ Запустить анимацию')

ax_help_btn = fig.add_axes([0.65, 0.60, 0.33, 0.038])
btn_help = Button(ax_help_btn, '?  Справка и примеры формул',
                  color='#ffeeba', hovercolor='#ffd966')

# =========================================================
#  Оверлей со справкой (постранично)
# =========================================================
ax_help = fig.add_axes([0.02, 0.02, 0.96, 0.94], zorder=999)
ax_help.set_facecolor('#fffbe6')
ax_help.set_xticks([]); ax_help.set_yticks([])
for s in ax_help.spines.values():
    s.set_linewidth(2); s.set_color('#888')
ax_help.set_visible(False)

help_text_artist = ax_help.text(0.5, 0.965, '',
                                va='top', ha='center',
                                fontsize=11, family='monospace',
                                transform=ax_help.transAxes)

# Кнопки навигации внизу справки
ax_prev  = fig.add_axes([0.08, 0.045, 0.15, 0.045], zorder=1000)
ax_close = fig.add_axes([0.40, 0.045, 0.20, 0.045], zorder=1000)
ax_next  = fig.add_axes([0.77, 0.045, 0.15, 0.045], zorder=1000)

btn_prev  = Button(ax_prev,  '◀ Предыдущая', color='#d9edf7',
                   hovercolor='#bce8f1')
btn_close = Button(ax_close, '× Закрыть справку', color='#f2dede',
                   hovercolor='#ebcccc')
btn_next  = Button(ax_next,  'Следующая ▶', color='#d9edf7',
                   hovercolor='#bce8f1')

for a in (ax_prev, ax_close, ax_next):
    a.set_visible(False)

HELP_PAGES = [
"""\
════════════════════════════════════════════════════════════════════════
              КАК ПОЛЬЗОВАТЬСЯ ПРОГРАММОЙ
════════════════════════════════════════════════════════════════════════

  Поле  a_n  принимает формулу общего элемента последовательности.
  Формула — это выражение на языке Python, где n — номер.

      Пример:  чтобы получить  a_n = 1/n,  введите   1/n

  Поле       L  — ваша гипотеза о пределе.
  Ползунок   ε  — радиус окрестности вокруг L.
  Ползунок   k  — сколько первых элементов последовательности показать.
  Кнопка     ▶  — проигрывает появление элементов по одному.

════════════════════════════════════════════════════════════════════════
                       ПРАВИЛА СИНТАКСИСА
════════════════════════════════════════════════════════════════════════

  Умножение — всегда через звёздочку:
         2n            ✗          2*n          ✓
         (n+1)(n+2)    ✗          (n+1)*(n+2)  ✓

  Степень — через две звёздочки:
         n^2           ✗          n**2         ✓
         2^n           ✗          2**n         ✓

  Скобки — только круглые:
         [n(n+1)]      ✗          (n*(n+1))    ✓

  Десятичный разделитель — точка, а не запятая:
         0,5           ✗          0.5          ✓

════════════════════════════════════════════════════════════════════════
  Страница 1 из 3.  Нажмите «Следующая ▶» или клавишу → .
""",
"""\
════════════════════════════════════════════════════════════════════════
              ДОСТУПНЫЕ ФУНКЦИИ И КОНСТАНТЫ
════════════════════════════════════════════════════════════════════════

  Переменная:  n

  Константы:   pi   (= 3.14159...)
               e    (= 2.71828...)

  Функции:     sin, cos, tan
               arcsin, arccos, arctan
               exp, log, log10, log2
               sqrt, abs, sign
               floor, ceil

  (тригонометрические функции — в радианах)

════════════════════════════════════════════════════════════════════════
              НАПОМИНАНИЕ ОПРЕДЕЛЕНИЯ ПРЕДЕЛА
════════════════════════════════════════════════════════════════════════

     L = lim a_n   ⇔   для КАЖДОГО ε > 0
                       найдётся такое N,
                       что для всех n > N
                       выполнено |a_n − L| < ε.

  Смысл: какую бы узкую полосу (L−ε, L+ε) мы ни взяли,
  начиная с некоторого номера N в неё попадают ВСЕ элементы
  последовательности, и больше из неё не выходят.

════════════════════════════════════════════════════════════════════════
  Страница 2 из 3.  Нажмите «Следующая ▶» или клавишу → .
""",
"""\
════════════════════════════════════════════════════════════════════════
                        ПРИМЕРЫ ФОРМУЛ
════════════════════════════════════════════════════════════════════════

        Формула a_n                        Разумная гипотеза L
   ────────────────────────────────────────────────────────────────
        1/n                                    0
        2*n/(n+3)                              2
        n/(n+1)                                1
        (-1)**n                                0    (предела нет!)
        (-1)**n / n                            0
        (1 + 1/n)**n                           2.718281828459045
        sin(n)/n                               0
        2**(1/n)                               1
        (3*n**2 - 1)/(2*n**2 + 5)              1.5
        sqrt(n + 1) - sqrt(n)                  0
        log(n)/n                               0
        n/(n**2 + 1)                           0
        (-1)**n * 2 + 3/n                      2    (частичный предел)

════════════════════════════════════════════════════════════════════════

  Попробуйте разные L и разные ε — и посмотрите, при каких условиях
  синяя линия N всё-таки появляется, а при каких выше неё всегда
  остаются красные точки.

  Нажмите «× Закрыть справку» или клавишу Esc, чтобы вернуться.

════════════════════════════════════════════════════════════════════════
  Страница 3 из 3.
""",
]


def render_help_page():
    p = state['help_page']
    help_text_artist.set_text(HELP_PAGES[p])
    btn_prev.label.set_text('◀ Предыдущая' if p > 0 else '◀  (это первая)')
    btn_next.label.set_text('Следующая ▶' if p < len(HELP_PAGES) - 1
                            else '(это последняя)  ▶')
    fig.canvas.draw_idle()


# =========================================================
#  Рисование
# =========================================================
def draw_main():
    ax.clear()
    if state['y'] is None:
        ax.text(0.5, 0.5, f'Ошибка в формуле:\n{state["err"]}',
                transform=ax.transAxes, ha='center', va='center',
                color='crimson', fontsize=12)
        return

    k = state['k']
    n = state['n'][:k]
    y = state['y'][:k]
    L = state['limit']
    eps = state['eps']
    inside = np.abs(y - L) < eps

    ax.axhspan(L - eps, L + eps, color='#f7e08a', alpha=0.55, zorder=0)
    ax.axhline(L, color='black', lw=1.2, ls='--', zorder=1)

    if inside.any():
        ax.scatter(n[inside], y[inside], c='#1e8449', s=45, zorder=3,
                   edgecolors='black', linewidths=0.4)
    if (~inside).any():
        ax.scatter(n[~inside], y[~inside], c='#c0392b', s=45, zorder=3,
                   edgecolors='black', linewidths=0.4)

    for xi, yi, ins in zip(n, y, inside):
        ax.plot([xi, xi], [L, yi],
                color=('#1e8449' if ins else '#c0392b'),
                alpha=0.3, lw=0.7, zorder=2)

    full_inside = np.abs(state['y'] - L) < eps
    outside_idx = np.where(~full_inside)[0]
    if len(outside_idx) > 0:
        N_val = int(state['n'][outside_idx[-1]])
        if k > N_val:
            ax.axvline(N_val + 0.5, color='blue', ls='--', lw=1.6, zorder=4)
            ax.text(N_val + 0.5, 0.98, f'  N = {N_val}',
                    transform=ax.get_xaxis_transform(),
                    color='blue', va='top', fontsize=11)

    ax.set_xlim(0.5, N_MAX + 0.5)
    finite = np.isfinite(state['y'])
    if finite.any():
        ymin = min(np.nanmin(state['y'][finite]), L - eps)
        ymax = max(np.nanmax(state['y'][finite]), L + eps)
        pad = 0.10 * (ymax - ymin + 1e-9)
        ax.set_ylim(ymin - pad, ymax + pad)

    ax.set_xlabel('n')
    ax.set_ylabel('a_n')
    ax.set_title(f'a_n = {state["expr"]},   L = {L:g},   '
                 f'ε = {eps:g},   k = {k}')
    ax.grid(True, alpha=0.3)


def draw_nbhd():
    ax_nbhd.clear()
    if state['y'] is None:
        return

    k = state['k']
    n = state['n'][:k]
    y = state['y'][:k]
    L = state['limit']
    eps = state['eps']
    inside = np.abs(y - L) < eps

    ax_nbhd.axvspan(L - eps, L + eps, color='#f7e08a', alpha=0.6, zorder=0)
    ax_nbhd.axvline(L,       color='black',   lw=1.2, ls='--', zorder=1)
    ax_nbhd.axvline(L - eps, color='#c0392b', lw=1.0, ls=':',  zorder=1)
    ax_nbhd.axvline(L + eps, color='#c0392b', lw=1.0, ls=':',  zorder=1)

    if inside.any():
        ax_nbhd.scatter(y[inside], n[inside], c='#1e8449', s=34, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='внутри (L−ε, L+ε)')
    if (~inside).any():
        ax_nbhd.scatter(y[~inside], n[~inside], c='#c0392b', s=34, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='вне окрестности')

    full_inside = np.abs(state['y'] - L) < eps
    outside_idx = np.where(~full_inside)[0]
    if len(outside_idx) > 0:
        N_val = int(state['n'][outside_idx[-1]])
        ax_nbhd.axhline(N_val + 0.5, color='blue', ls='--', lw=1.4, zorder=4)
        ax_nbhd.text(0.99, (N_val + 0.5) / (N_MAX + 1),
                     f' N = {N_val}',
                     transform=ax_nbhd.transAxes,
                     color='blue', ha='left', va='center', fontsize=10)

    y_lbl = N_MAX + 1
    ax_nbhd.text(L, y_lbl, f' L={L:g}',
                 color='black', ha='center', va='bottom', fontsize=9)
    ax_nbhd.text(L - eps, y_lbl, 'L−ε',
                 color='#c0392b', ha='right', va='bottom', fontsize=9)
    ax_nbhd.text(L + eps, y_lbl, 'L+ε',
                 color='#c0392b', ha='left', va='bottom', fontsize=9)

    finite = np.isfinite(state['y'])
    if finite.any():
        xmin = min(np.nanmin(state['y'][finite]), L - eps)
        xmax = max(np.nanmax(state['y'][finite]), L + eps)
        pad = 0.08 * (xmax - xmin + 1e-9)
        ax_nbhd.set_xlim(xmin - pad, xmax + pad)
    ax_nbhd.set_ylim(0, N_MAX + 2)

    ax_nbhd.set_xlabel('значение a_n')
    ax_nbhd.set_ylabel('n', rotation=0, labelpad=16)
    ax_nbhd.set_title('ε-окрестность и элементы последовательности')
    ax_nbhd.grid(True, alpha=0.3, axis='x')
    if inside.any() or (~inside).any():
        ax_nbhd.legend(loc='upper right', fontsize=9, framealpha=0.9)


def draw_info():
    if state['y'] is None:
        info_text.set_text('Ошибка в формуле')
        return

    k = state['k']
    L = state['limit']
    eps = state['eps']

    full_inside = np.abs(state['y'] - L) < eps
    outside_idx = np.where(~full_inside)[0]

    if len(outside_idx) == 0:
        info_N = (f'Все {N_MAX} показанных элементов\n'
                  f'последовательности попали в\n'
                  f'ε-окрестность.  Можно взять N = 0.')
    else:
        N_val = int(state['n'][outside_idx[-1]])
        info_N = (f'Последний «плохой» элемент\n'
                  f'последовательности:  n = {N_val}.\n'
                  f'Начиная с n = {N_val + 1}, все\n'
                  f'элементы внутри.  Можно\n'
                  f'взять  N = {N_val}.')

    lines = [
        f'a_n = {state["expr"]}',
        f'L = {L:g}   ε = {eps:g}   k = {k}',
        '',
        '─' * 32,
        info_N,
        '─' * 32,
        '',
        'Верх: a_n от n.',
        'Низ: «портрет окрестности».',
        'Значения по горизонтали,',
        'номера по вертикали.',
        'Зелёные — внутри полосы,',
        'красные — снаружи.',
        '',
        'Синяя линия — N: выше неё',
        'все элементы зелёные.',
        '',
        'Определение: для КАЖДОГО',
        'ε > 0 найдётся такое N, что,',
        'начиная с него, ВСЕ элементы',
        'последовательности попадают',
        'в полосу (L−ε, L+ε).',
        '',
        '→ нажмите «? Справка»:',
        '  правила ввода формул',
        '  и примеры.',
    ]
    info_text.set_text('\n'.join(lines))


def draw():
    if state['help_open']:
        fig.canvas.draw_idle()
        return
    draw_main()
    draw_nbhd()
    draw_info()
    fig.canvas.draw_idle()


# =========================================================
#  Колбэки
# =========================================================
_quiet = {'v': False}

def _set_k_quiet(val):
    _quiet['v'] = True
    sl_k.set_val(val)
    _quiet['v'] = False

def on_expr(text):
    state['expr'] = text.strip()
    compute()
    state['k'] = N_MAX
    _set_k_quiet(N_MAX)
    draw()

def on_lim(text):
    try:
        state['limit'] = float(text)
    except ValueError:
        return
    draw()

def on_eps(val):
    state['eps'] = float(val)
    draw()

def on_k(val):
    if _quiet['v']:
        return
    state['k'] = int(val)
    draw()

tb_expr.on_submit(on_expr)
tb_lim.on_submit(on_lim)
sl_eps.on_changed(on_eps)
sl_k.on_changed(on_k)

main_axes = [ax, ax_nbhd, ax_info, ax_expr, ax_lim, ax_eps, ax_k,
             ax_btn, ax_help_btn]
help_axes = [ax_help, ax_prev, ax_close, ax_next]

def open_help():
    state['help_open'] = True
    state['help_page'] = 0
    for a in main_axes:
        a.set_visible(False)
    for a in help_axes:
        a.set_visible(True)
    render_help_page()

def close_help():
    state['help_open'] = False
    for a in help_axes:
        a.set_visible(False)
    for a in main_axes:
        a.set_visible(True)
    draw()

btn_help.on_clicked(lambda ev: open_help())
btn_close.on_clicked(lambda ev: close_help())

def prev_page(ev):
    if state['help_page'] > 0:
        state['help_page'] -= 1
        render_help_page()

def next_page(ev):
    if state['help_page'] < len(HELP_PAGES) - 1:
        state['help_page'] += 1
        render_help_page()

btn_prev.on_clicked(prev_page)
btn_next.on_clicked(next_page)

# --- клавиатура в справке ---
def on_key(event):
    if not state['help_open']:
        return
    if event.key in ('right', 'pagedown', ' '):
        next_page(None)
    elif event.key in ('left', 'pageup'):
        prev_page(None)
    elif event.key in ('escape', 'q'):
        close_help()

fig.canvas.mpl_connect('key_press_event', on_key)

# =========================================================
#  Анимация
# =========================================================
anim_ref = {'anim': None}

def animate(frame):
    state['k'] = frame
    _set_k_quiet(frame)
    draw()

def run_animation(event):
    if state['help_open']:
        return
    if anim_ref['anim'] is not None:
        try: anim_ref['anim'].event_source.stop()
        except Exception: pass
    state['k'] = 1
    anim = FuncAnimation(fig, animate,
                         frames=list(range(1, N_MAX + 1)),
                         interval=70, repeat=False, blit=False)
    anim_ref['anim'] = anim
    fig.canvas.draw_idle()

btn.on_clicked(run_animation)

# =========================================================
#  Старт
# =========================================================
compute()
draw()
plt.show()