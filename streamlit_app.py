import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Предел последовательности",
    page_icon="📈",
    layout="wide",
)

st.title("Предел последовательности: ε-окрестность")
st.caption(
    "Введите формулу общего элемента последовательности, гипотезу о пределе L "
    "и радиус ε. Программа покажет, какие элементы попали в ε-окрестность, "
    "а какие — нет, и подскажет, с какого номера N все элементы внутри."
)

# ---------- Безопасное окружение для формул ----------
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


# ---------- Виджеты управления ----------
col1, col2 = st.columns(2)
with col1:
    expr = st.text_input(
        "Формула a_n (переменная — n)",
        value="1/n",
        help="Примеры: 1/n, 2*n/(n+3), (-1)**n / n, (1 + 1/n)**n, sin(n)/n",
    )
with col2:
    limit_str = st.text_input(
        "Гипотеза L = ",
        value="0",
        help="Число — ваше предположение о пределе. Например: 0, 1, 2, 2.71828, -2",
    )

col3, col4 = st.columns(2)
with col3:
    eps = st.slider("ε (радиус окрестности)", 0.001, 3.0, 0.2, step=0.001,
                    format="%.3f")
with col4:
    k = st.slider("Сколько первых элементов показать", 1, 200, 60)

# ---------- Разбор ввода ----------
try:
    L = float(limit_str)
except ValueError:
    st.error("Гипотеза L должна быть числом. Например: 0, 1, 2, 2.71828.")
    st.stop()

N_MAX = 200
n = np.arange(1, N_MAX + 1).astype(float)

try:
    f = make_seq(expr)
    y = np.array([f(i) for i in n], dtype=float)
except Exception as e:
    st.error(f"Ошибка в формуле: {e}")
    st.info(
        "Проверьте синтаксис: умножение — через `*` (например `2*n`), "
        "степень — через `**` (например `n**2`), скобки — круглые."
    )
    st.stop()

# ---------- Поиск N по полному диапазону ----------
full_inside = np.abs(y - L) < eps
outside_idx = np.where(~full_inside)[0]
if len(outside_idx) == 0:
    N_val = None
else:
    N_val = int(n[outside_idx[-1]])

# ---------- Информационная панель ----------
st.markdown("---")
if N_val is None:
    st.success(
        f"Все {N_MAX} показанных элементов последовательности попали "
        f"в ε-окрестность. Можно взять **N = 0**."
    )
else:
    st.info(
        f"Последний элемент последовательности, не попавший "
        f"в ε-окрестность: **n = {N_val}**.  \n"
        f"Начиная с n = {N_val + 1}, все элементы внутри. "
        f"Можно взять **N = {N_val}**."
    )

st.caption(
    "Напоминание: L = lim a_n ⇔ для **каждого** ε > 0 найдётся такое N, "
    "что для всех n > N выполнено |a_n − L| < ε."
)

# ★ ---------- Функция отрисовки одного кадра ----------
def draw_fig(k_show):
    n_show = n[:k_show]
    y_show = y[:k_show]
    inside = np.abs(y_show - L) < eps

    fig, (ax_main, ax_nbhd) = plt.subplots(
        2, 1, figsize=(11, 8),
        gridspec_kw={'height_ratios': [2, 1]},
    )

    # ===== Верхний: a_n от n =====
    ax_main.axhspan(L - eps, L + eps, color='#f7e08a', alpha=0.55, zorder=0)
    ax_main.axhline(L, color='black', lw=1.2, ls='--', zorder=1)

    if inside.any():
        ax_main.scatter(n_show[inside], y_show[inside],
                        c='#1e8449', s=55, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='внутри ε-окрестности')
    if (~inside).any():
        ax_main.scatter(n_show[~inside], y_show[~inside],
                        c='#c0392b', s=55, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='вне окрестности')

    for xi, yi, ins in zip(n_show, y_show, inside):
        ax_main.plot([xi, xi], [L, yi],
                     color=('#1e8449' if ins else '#c0392b'),
                     alpha=0.3, lw=0.7, zorder=2)

    if N_val is not None and k_show > N_val:
        ax_main.axvline(N_val + 0.5, color='blue', ls='--', lw=1.6, zorder=4)
        ax_main.text(N_val + 0.5, 0.98, f'  N = {N_val}',
                     transform=ax_main.get_xaxis_transform(),
                     color='blue', va='top', fontsize=11)

    ax_main.set_xlim(0.5, k_show + 0.5)

    finite = np.isfinite(y_show)
    if finite.any():
        ymin = min(np.nanmin(y_show[finite]), L - eps)
        ymax = max(np.nanmax(y_show[finite]), L + eps)
        pad = 0.10 * (ymax - ymin + 1e-9)
        ax_main.set_ylim(ymin - pad, ymax + pad)

    ax_main.set_xlabel('n')
    ax_main.set_ylabel('a_n')
    ax_main.set_title(f'a_n = {expr},   L = {L:g},   ε = {eps:g}')
    ax_main.grid(True, alpha=0.3)
    if inside.any() or (~inside).any():
        ax_main.legend(loc='lower right', fontsize=9, framealpha=0.9)

    # ===== Нижний: портрет окрестности =====
    ax_nbhd.axvspan(L - eps, L + eps, color='#f7e08a', alpha=0.6, zorder=0)
    ax_nbhd.axvline(L, color='black', lw=1.2, ls='--', zorder=1)
    ax_nbhd.axvline(L - eps, color='#c0392b', lw=1.0, ls=':', zorder=1)
    ax_nbhd.axvline(L + eps, color='#c0392b', lw=1.0, ls=':', zorder=1)

    if inside.any():
        ax_nbhd.scatter(y_show[inside], n_show[inside],
                        c='#1e8449', s=40, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='внутри (L−ε, L+ε)')
    if (~inside).any():
        ax_nbhd.scatter(y_show[~inside], n_show[~inside],
                        c='#c0392b', s=40, zorder=3,
                        edgecolors='black', linewidths=0.4,
                        label='вне окрестности')

    if N_val is not None and k_show > N_val:
        ax_nbhd.axhline(N_val + 0.5, color='blue', ls='--', lw=1.4, zorder=4)
        ax_nbhd.text(0.99, (N_val + 0.5) / (k_show + 1), f' N = {N_val}',
                     transform=ax_nbhd.transAxes,
                     color='blue', ha='left', va='center', fontsize=10)

    y_lbl = k_show + 1
    ax_nbhd.text(L, y_lbl, f' L={L:g}',
                 color='black', ha='center', va='bottom', fontsize=9)
    ax_nbhd.text(L - eps, y_lbl, 'L−ε',
                 color='#c0392b', ha='right', va='bottom', fontsize=9)
    ax_nbhd.text(L + eps, y_lbl, 'L+ε',
                 color='#c0392b', ha='left', va='bottom', fontsize=9)

    if finite.any():
        xmin = min(np.nanmin(y_show[finite]), L - eps)
        xmax = max(np.nanmax(y_show[finite]), L + eps)
        pad = 0.08 * (xmax - xmin + 1e-9)
        ax_nbhd.set_xlim(xmin - pad, xmax + pad)
    ax_nbhd.set_ylim(0, k_show + 2)
    ax_nbhd.set_xlabel('значение a_n')
    ax_nbhd.set_ylabel('n', rotation=0, labelpad=16)
    ax_nbhd.set_title('ε-окрестность: значения — по горизонтали, '
                      'номера — по вертикали')
    ax_nbhd.grid(True, alpha=0.3, axis='x')
    if inside.any() or (~inside).any():
        ax_nbhd.legend(loc='upper right', fontsize=9, framealpha=0.9)

    plt.tight_layout()
    return fig


# ★ ---------- Кнопка анимации и скорость ----------
colA, colB = st.columns([1, 2])
with colA:
    run_anim = st.button("▶  Запустить анимацию", use_container_width=True)
with colB:
    speed = st.slider("Скорость анимации (мс между кадрами)",
                      10, 300, 70, step=10,
                      help="Меньше — быстрее, больше — медленнее")

# ★ Место, куда будем вставлять кадры
plot_placeholder = st.empty()

# ★ Если кнопка нажата — проигрываем анимацию от 1 до k
if run_anim:
    for k_frame in range(1, k + 1):
        fig = draw_fig(k_frame)
        plot_placeholder.pyplot(fig)
        plt.close(fig)
        time.sleep(speed / 1000.0)
else:
    fig = draw_fig(k)
    plot_placeholder.pyplot(fig)
    plt.close(fig)

# ---------- Справка ----------
with st.expander("?  Справка и примеры формул"):
    st.markdown(
        """
        **Правила синтаксиса**

        - Умножение — всегда через `*`: `2*n`, `(n+1)*(n+2)`.
        - Степень — через `**`: `n**2`, `2**n`, `(-1)**n`.
        - Скобки — только круглые: `(n*(n+1))`.
        - Десятичный разделитель — точка: `0.5`.

        **Доступные функции и константы**

        - Переменная: `n`.
        - Константы: `pi`, `e`.
        - Функции: `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`,
          `exp`, `log`, `log10`, `log2`, `sqrt`, `abs`, `sign`,
          `floor`, `ceil`.

        **Примеры формул**

        | Формула `a_n` | Разумная гипотеза `L` |
        |---|---|
        | `1/n` | `0` |
        | `2*n/(n+3)` | `2` |
        | `n/(n+1)` | `1` |
        | `(-1)**n` | `0` (предела нет!) |
        | `(-1)**n / n` | `0` |
        | `(1 + 1/n)**n` | `2.718281828459045` |
        | `sin(n)/n` | `0` |
        | `2**(1/n)` | `1` |
        | `(3*n**2 - 1)/(2*n**2 + 5)` | `1.5` |
        | `sqrt(n + 1) - sqrt(n)` | `0` |
        | `log(n)/n` | `0` |
        | `(-1)**n * 2 + 3/n` | `2` (частичный предел) |
        """
    )
