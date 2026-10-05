#!/usr/bin/env python3
"""Settings definition and translations for the tico module of FinalBurn Neo.

Run after merging upstream. FBNeo assembles its core options at runtime (per
game: dip switches, Neo Geo and PGM2 options), so this reads the global ones
straight from src/burner/libretro/retro_common.cpp's var_fbneo_* definitions:
tico/module/settings.json then lists exactly the keys, values and defaults the
libnx core accepts, laid out in tabs, followed by the overlay's own display and
controls options. Labels are translation keys; the strings go into
tico/lang/*.json, taken from tico's existing settings labels where an option
already had one. Choice labels stay English in settings.json; the overlay
translates them through settings_fbneo_value_* keys.

    python3 tico/tools/tico_module.py
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TICO = ROOT / "tico"
SETTINGS = TICO / "module/settings.json"
LANG_DIR = TICO / "lang"
LANGUAGES = ("en", "de", "es", "fr", "ja", "pt", "ru", "zh")
CORE_OPTIONS = ROOT / "src/burner/libretro/retro_common.cpp"
# tico-nx's own strings label the options it already knew; optional
TICO_NX = Path(os.environ.get("TICO_NX_DIR", ROOT.parents[1] / "tico-nx"))

# Core option -> label key, for the options tico already labelled.
LABEL_KEYS = {
    "fbneo-cpu-speed-adjust": "settings_fbneo_cpu_clock",
}

# Core options the frontend has no use for: the light gun crosshair needs
# pointer input it does not send, frameskip by audio buffer occupancy needs a
# frontend that reports it (FBNeo then only offers the fixed one), Cyclone is
# a 32-bit ARM core the libnx build leaves out, and the debug ones are only in
# debug builds.
EXCLUDED_PREFIXES = ("fbneo-debug-",)
EXCLUDED = {
    "fbneo-lightgun-crosshair-emulation", "fbneo-frameskip-type",
    "fbneo-frameskip-manual-threshold", "fbneo-cyclone",
}

# Options whose description asks to start the game again, which FBNeo says in
# prose rather than with a "(Restart)" note.
RESTART = {"fbneo-samplerate", "fbneo-allow-patched-romsets"}

# (tab, [(section, [option keys])]). Every core option parsed must be placed
# or excluded; the overlay's own tabs are added around these.
LAYOUT = [
    ("settings_fbneo_tab_system", [
        ("settings_fbneo_section_general", ["fbneo-allow-patched-romsets", "fbneo-hiscores"]),
        ("settings_fbneo_section_performance", ["fbneo-cpu-speed-adjust"]),
    ]),
    ("settings_fbneo_tab_video", [
        ("settings_fbneo_section_display", ["fbneo-vertical-mode", "fbneo-force-60hz",
                                            "fbneo-allow-depth-32", "fbneo-resolution"]),
        ("settings_fbneo_section_frameskip", ["fbneo-fixed-frameskip"]),
    ]),
    ("settings_fbneo_tab_audio", [
        ("settings_fbneo_section_quality", ["fbneo-samplerate", "fbneo-sample-interpolation",
                                            "fbneo-fm-interpolation", "fbneo-lowpass-filter"]),
    ]),
    ("settings_fbneo_tab_input", [
        ("settings_fbneo_section_controls", ["fbneo-diagnostic-input", "fbneo-analog-speed",
                                             "fbneo-socd"]),
    ]),
    ("settings_fbneo_tab_neogeo", [
        ("settings_fbneo_section_neogeo", ["fbneo-neogeo-mode", "fbneo-memcard-mode"]),
    ]),
]

# Listed only while another option has a value, like the core's own menus.
DEPENDS_ON: dict[str, tuple[str, str]] = {}

# Switch buttons a RetroPad button (or the fast-forward hotkey) can sit on.
SWITCH_BUTTONS = [("A", "A"), ("B", "B"), ("X", "X"), ("Y", "Y"), ("L", "L"), ("R", "R"),
                  ("ZL", "ZL"), ("ZR", "ZR"), ("Plus", "Plus"), ("Minus", "Minus"),
                  ("StickL", "Left stick"), ("StickR", "Right stick"), ("Up", "Up"),
                  ("Down", "Down"), ("Left", "Left"), ("Right", "Right"), ("None", "Disabled")]

POSITIONS = [("hidden", "Hidden"), ("top_left", "Top left"), ("top_right", "Top right"),
             ("bottom_left", "Bottom left"), ("bottom_right", "Bottom right")]

# The overlay's own options: how the game is scaled, fast forward and the HUD.
# Original (the game's own aspect ratio) by default: arcade screens vary, and
# vertical games are taller than wide. Shaders are picked in game.
OVERLAY_TAB = ("settings_fbneo_tab_display", [
    ("settings_fbneo_section_screen", [
        {"key": "display_mode", "label": "settings_fbneo_display_mode", "type": "enum",
         "default": "Display", "choices": [("Integer", "Integer"), ("Display", "Display")]},
        {"key": "display_size", "label": "settings_fbneo_display_size", "type": "enum",
         "default": "Original", "choices": [("Stretch", "Stretch"), ("4:3", "4:3"), ("16:9", "16:9"),
                                            ("Original", "Original"), ("1x", "1x"), ("2x", "2x"),
                                            ("Auto", "Auto")]},
    ]),
    ("settings_fbneo_section_fast_forward", [
        {"key": "fast_forward_speed", "label": "settings_fbneo_fast_forward_speed", "type": "enum",
         "default": "200", "choices": [("150", "150%"), ("200", "200%"), ("300", "300%"),
                                        ("400", "400%"), ("unlimited", "Unlimited")]},
        {"key": "fast_forward_mode", "label": "settings_fbneo_fast_forward_mode", "type": "enum",
         "default": "hold", "choices": [("hold", "Hold"), ("toggle", "Toggle")]},
        {"key": "fast_forward_hotkey", "label": "settings_fbneo_fast_forward_hotkey", "type": "enum",
         "default": "ZR", "choices": SWITCH_BUTTONS},
    ]),
    ("settings_fbneo_section_hud", [
        {"key": "fps_counter_position", "label": "settings_fbneo_fps_counter", "type": "enum",
         "default": "hidden", "choices": POSITIONS},
        {"key": "rendered_ir_position", "label": "settings_fbneo_rendered_resolution",
         "type": "enum", "default": "hidden", "choices": POSITIONS},
    ]),
])

# The overlay's button mapping: RetroPad button -> Switch button, each on its
# namesake by default (TicoMain.cpp's kButtonMappings). FBNeo lays every
# game's buttons out over the RetroPad itself.
CONTROLS_TAB = ("settings_fbneo_tab_controls", [
    ("settings_fbneo_section_button_mapping", [
        {"key": key, "label": "settings_fbneo_" + key, "type": "enum", "default": default,
         "choices": SWITCH_BUTTONS}
        for key, default in [
            ("map_a", "A"), ("map_b", "B"), ("map_x", "X"), ("map_y", "Y"),
            ("map_l", "L"), ("map_r", "R"), ("map_l2", "ZL"), ("map_r2", "ZR"),
            ("map_l3", "StickL"), ("map_r3", "StickR"),
            ("map_start", "Plus"), ("map_select", "Minus"),
            ("map_up", "Up"), ("map_down", "Down"), ("map_left", "Left"), ("map_right", "Right"),
        ]
    ] + [
        {"key": "analog_dpad", "label": "settings_fbneo_analog_dpad", "type": "bool",
         "default": "enabled"},
    ]),
])

# Labels. key -> (en, de, es, fr, ja, pt, ru, zh); tico's own wording wins
# where tico already has the key.
LABELS = {
    "settings_fbneo_tab_system": ("System", "System", "Sistema", "Système", "システム", "Sistema",
                                  "Система", "系统"),
    "settings_fbneo_section_general": ("General", "Allgemein", "General", "Général", "一般", "Geral",
                                       "Общие", "常规"),
    "settings_fbneo_section_performance": ("Performance", "Leistung", "Rendimiento", "Performances",
                                           "パフォーマンス", "Desempenho", "Производительность",
                                           "性能"),
    "settings_fbneo_tab_video": ("Video", "Video", "Vídeo", "Vidéo", "ビデオ", "Vídeo", "Видео",
                                 "视频"),
    "settings_fbneo_section_display": ("Display", "Anzeige", "Pantalla", "Affichage", "表示",
                                       "Exibição", "Отображение", "显示"),
    "settings_fbneo_section_frameskip": ("Frameskip", "Frameskip", "Salto de fotogramas",
                                         "Saut d'images", "フレームスキップ", "Pulo de quadros",
                                         "Пропуск кадров", "跳帧"),
    "settings_fbneo_tab_audio": ("Audio", "Audio", "Audio", "Audio", "オーディオ", "Áudio", "Звук",
                                 "音频"),
    "settings_fbneo_section_quality": ("Quality", "Qualität", "Calidad", "Qualité", "品質",
                                       "Qualidade", "Качество", "质量"),
    "settings_fbneo_tab_input": ("Input", "Eingabe", "Entrada", "Entrée", "入力", "Entrada", "Ввод",
                                 "输入"),
    "settings_fbneo_section_controls": ("Controls", "Steuerung", "Controles", "Commandes", "操作",
                                        "Controles", "Управление", "控制"),
    "settings_fbneo_tab_neogeo": ("Neo Geo", "Neo Geo", "Neo Geo", "Neo Geo", "ネオジオ", "Neo Geo",
                                  "Neo Geo", "Neo Geo"),
    "settings_fbneo_section_neogeo": ("Neo Geo", "Neo Geo", "Neo Geo", "Neo Geo", "ネオジオ",
                                      "Neo Geo", "Neo Geo", "Neo Geo"),
    "settings_fbneo_allow_patched_romsets": ("Allow patched romsets", "Gepatchte Romsets erlauben",
                                             "Permitir romsets parcheados", "Autoriser les romsets patchés",
                                             "パッチ済みROMセットを許可", "Permitir romsets modificados",
                                             "Разрешить пропатченные ромсеты", "允许修补的 ROM 集"),
    "settings_fbneo_hiscores": ("High scores", "Highscores", "Puntuaciones máximas",
                                "Meilleurs scores", "ハイスコア", "Recordes", "Рекорды", "最高分"),
    "settings_fbneo_cpu_clock": ("CPU clock", "CPU-Takt", "Reloj de CPU", "Fréquence CPU",
                                 "CPUクロック", "Clock da CPU", "Частота ЦП", "CPU 频率"),
    "settings_fbneo_vertical_mode": ("Vertical mode", "Vertikalmodus", "Modo vertical",
                                     "Mode vertical", "縦画面モード", "Modo vertical",
                                     "Вертикальный режим", "竖屏模式"),
    "settings_fbneo_force_60hz": ("Force 60 Hz", "60 Hz erzwingen", "Forzar 60 Hz", "Forcer 60 Hz",
                                  "60Hzを強制", "Forçar 60 Hz", "Принудительно 60 Гц", "强制 60Hz"),
    "settings_fbneo_allow_depth_32": ("32-bit color", "32-Bit-Farbe", "Color de 32 bits",
                                      "Couleurs 32 bits", "32ビットカラー", "Cor de 32 bits",
                                      "32-битный цвет", "32 位色彩"),
    "settings_fbneo_resolution": ("Vector resolution", "Vektor-Auflösung", "Resolución vectorial",
                                  "Résolution vectorielle", "ベクター解像度", "Resolução vetorial",
                                  "Векторное разрешение", "矢量分辨率"),
    "settings_fbneo_fixed_frameskip": ("Fixed frameskip", "Fester Frameskip",
                                       "Salto de fotogramas fijo", "Saut d'images fixe",
                                       "固定フレームスキップ", "Pulo de quadros fixo",
                                       "Фиксированный пропуск кадров", "固定跳帧"),
    "settings_fbneo_samplerate": ("Sample rate", "Abtastrate", "Frecuencia de muestreo",
                                  "Fréquence d'échantillonnage", "サンプリングレート",
                                  "Taxa de amostragem", "Частота дискретизации", "采样率"),
    "settings_fbneo_sample_interpolation": ("Sample interpolation", "Sample-Interpolation",
                                            "Interpolación de muestras",
                                            "Interpolation des échantillons", "サンプル補間",
                                            "Interpolação de amostras", "Интерполяция сэмплов",
                                            "采样插值"),
    "settings_fbneo_fm_interpolation": ("FM interpolation", "FM-Interpolation", "Interpolación FM",
                                        "Interpolation FM", "FM補間", "Interpolação FM",
                                        "Интерполяция FM", "FM 插值"),
    "settings_fbneo_lowpass_filter": ("Low-pass filter", "Tiefpassfilter", "Filtro de paso bajo",
                                      "Filtre passe-bas", "ローパスフィルター", "Filtro passa-baixa",
                                      "Фильтр нижних частот", "低通滤波"),
    "settings_fbneo_diagnostic_input": ("Service menu buttons", "Tasten für das Service-Menü",
                                        "Botones del menú de servicio",
                                        "Boutons du menu de service", "サービスメニューのボタン",
                                        "Botões do menu de serviço", "Кнопки сервисного меню",
                                        "服务菜单按键"),
    "settings_fbneo_analog_speed": ("Analog speed", "Analog-Geschwindigkeit", "Velocidad analógica",
                                    "Vitesse analogique", "アナログ速度", "Velocidade analógica",
                                    "Скорость аналога", "摇杆速度"),
    "settings_fbneo_socd": ("Opposing directions (SOCD)", "Gegenrichtungen (SOCD)",
                            "Direcciones opuestas (SOCD)", "Directions opposées (SOCD)",
                            "反対方向の同時入力 (SOCD)", "Direções opostas (SOCD)",
                            "Противоположные направления (SOCD)", "相反方向 (SOCD)"),
    "settings_fbneo_neogeo_mode": ("Neo Geo BIOS", "Neo-Geo-BIOS", "BIOS de Neo Geo",
                                   "BIOS Neo Geo", "ネオジオBIOS", "BIOS do Neo Geo", "BIOS Neo Geo",
                                   "Neo Geo BIOS"),
    "settings_fbneo_memcard_mode": ("Memory card", "Speicherkarte", "Tarjeta de memoria",
                                    "Carte mémoire", "メモリーカード", "Cartão de memória",
                                    "Карта памяти", "记忆卡"),
    "settings_fbneo_tab_display": ("Display", "Anzeige", "Pantalla", "Affichage", "表示", "Tela",
                                   "Экран", "显示"),
    "settings_fbneo_section_screen": ("Screen", "Bild", "Imagen", "Image", "画面", "Imagem",
                                      "Изображение", "画面"),
    "settings_fbneo_section_hud": ("On-screen info", "Bildschirmanzeige", "Información en pantalla",
                                   "Affichage à l'écran", "画面表示", "Informações na tela",
                                   "Экранная информация", "屏幕信息"),
    "settings_fbneo_display_mode": ("Display Mode", "Anzeigemodus", "Modo de pantalla",
                                    "Mode d'affichage", "表示モード", "Modo de exibição",
                                    "Режим отображения", "显示模式"),
    "settings_fbneo_display_size": ("Size", "Größe", "Tamaño", "Taille", "サイズ", "Tamanho",
                                    "Размер", "尺寸"),
    "settings_fbneo_fps_counter": ("FPS counter", "FPS-Zähler", "Contador de FPS",
                                   "Compteur de FPS", "FPSカウンター", "Contador de FPS",
                                   "Счётчик FPS", "帧率计数器"),
    "settings_fbneo_rendered_resolution": ("Rendered resolution", "Gerenderte Auflösung",
                                           "Resolución renderizada", "Résolution de rendu",
                                           "描画解像度", "Resolução renderizada",
                                           "Разрешение рендеринга", "渲染分辨率"),
    "settings_fbneo_section_fast_forward": ("Fast Forward", "Vorspulen", "Avance rápido",
                                            "Avance rapide", "早送り", "Avanço rápido",
                                            "Перемотка", "快进"),
    "settings_fbneo_fast_forward_speed": ("Fast forward speed", "Vorspul-Geschwindigkeit",
                                          "Velocidad de avance rápido", "Vitesse d'avance rapide",
                                          "早送りの速度", "Velocidade do avanço rápido",
                                          "Скорость перемотки", "快进速度"),
    "settings_fbneo_fast_forward_mode": ("Fast forward mode", "Vorspul-Modus",
                                         "Modo de avance rápido", "Mode d'avance rapide",
                                         "早送りモード", "Modo do avanço rápido",
                                         "Режим перемотки", "快进模式"),
    "settings_fbneo_fast_forward_hotkey": ("Fast forward button", "Vorspul-Taste",
                                           "Botón de avance rápido", "Bouton d'avance rapide",
                                           "早送りボタン", "Botão do avanço rápido",
                                           "Кнопка перемотки", "快进按键"),
    "settings_fbneo_tab_controls": ("Controls", "Steuerung", "Controles", "Commandes", "操作",
                                    "Controles", "Управление", "控制"),
    "settings_fbneo_section_button_mapping": ("Button mapping", "Tastenbelegung",
                                              "Asignación de botones", "Attribution des boutons",
                                              "ボタン割り当て", "Mapeamento de botões",
                                              "Назначение кнопок", "按键映射"),
    "settings_fbneo_map_a": ("A", "A", "A", "A", "A", "A", "A", "A"),
    "settings_fbneo_map_b": ("B", "B", "B", "B", "B", "B", "B", "B"),
    "settings_fbneo_map_x": ("X", "X", "X", "X", "X", "X", "X", "X"),
    "settings_fbneo_map_y": ("Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"),
    "settings_fbneo_map_l": ("L", "L", "L", "L", "L", "L", "L", "L"),
    "settings_fbneo_map_r": ("R", "R", "R", "R", "R", "R", "R", "R"),
    "settings_fbneo_map_l2": ("L2", "L2", "L2", "L2", "L2", "L2", "L2", "L2"),
    "settings_fbneo_map_r2": ("R2", "R2", "R2", "R2", "R2", "R2", "R2", "R2"),
    "settings_fbneo_map_l3": ("L3", "L3", "L3", "L3", "L3", "L3", "L3", "L3"),
    "settings_fbneo_map_r3": ("R3", "R3", "R3", "R3", "R3", "R3", "R3", "R3"),
    "settings_fbneo_map_start": ("Start", "Start", "Start", "Start", "スタート", "Start",
                                 "Start", "开始"),
    "settings_fbneo_map_select": ("Select (coin)", "Select (Münze)", "Select (moneda)",
                                  "Select (pièce)", "セレクト（コイン）", "Select (ficha)",
                                  "Select (монета)", "选择（投币）"),
    "settings_fbneo_map_up": ("D-Pad Up", "Steuerkreuz oben", "Cruceta arriba",
                              "Croix haut", "十字キー上", "Direcional para cima",
                              "Крестовина вверх", "方向键上"),
    "settings_fbneo_map_down": ("D-Pad Down", "Steuerkreuz unten", "Cruceta abajo",
                                "Croix bas", "十字キー下", "Direcional para baixo",
                                "Крестовина вниз", "方向键下"),
    "settings_fbneo_map_left": ("D-Pad Left", "Steuerkreuz links", "Cruceta izquierda",
                                "Croix gauche", "十字キー左", "Direcional para a esquerda",
                                "Крестовина влево", "方向键左"),
    "settings_fbneo_map_right": ("D-Pad Right", "Steuerkreuz rechts", "Cruceta derecha",
                                 "Croix droite", "十字キー右", "Direcional para a direita",
                                 "Крестовина вправо", "方向键右"),
    "settings_fbneo_analog_dpad": ("Left stick as D-Pad", "Linker Stick als Steuerkreuz",
                                   "Stick izquierdo como cruceta",
                                   "Stick gauche comme croix directionnelle",
                                   "左スティックを十字キーとして使う",
                                   "Analógico esquerdo como direcional",
                                   "Левый стик как крестовина", "左摇杆作为方向键"),
}

# Choice labels the core does not translate. English -> (de, es, fr, ja, pt, ru, zh)
CHOICES = {
    "Disabled": ("Deaktiviert", "Desactivado", "Désactivé", "無効", "Desativado", "Выключено",
                 "禁用"),
    "Enabled": ("Aktiviert", "Activado", "Activé", "有効", "Ativado", "Включено", "启用"),
    "Integer": ("Ganzzahlig", "Entero", "Entier", "整数倍", "Inteiro", "Целочисленный", "整数"),
    "Display": ("Anzeige", "Pantalla", "Écran", "画面", "Tela", "Экран", "屏幕"),
    "Stretch": ("Strecken", "Estirar", "Étirer", "引き伸ばし", "Esticar", "Растянуть", "拉伸"),
    "Original": ("Original", "Original", "Original", "オリジナル", "Original", "Оригинал", "原始"),
    "Auto": ("Auto", "Auto", "Auto", "自動", "Auto", "Авто", "自动"),
    "Unlimited": ("Unbegrenzt", "Ilimitado", "Illimité", "無制限", "Ilimitado", "Без ограничений",
                  "无限制"),
    "Hold": ("Halten", "Mantener", "Maintenir", "長押し", "Segurar", "Удерживать", "按住"),
    "Toggle": ("Umschalten", "Alternar", "Basculer", "切り替え", "Alternar", "Переключать", "切换"),
    "Right stick": ("Rechter Stick", "Stick derecho", "Stick droit", "右スティック", "Analógico direito",
                    "Правый стик", "右摇杆"),
    "Left stick": ("Linker Stick", "Stick izquierdo", "Stick gauche", "左スティック", "Analógico esquerdo",
                   "Левый стик", "左摇杆"),
    "Plus": ("Plus", "Más", "Plus", "プラス", "Mais", "Плюс", "加号"),
    "Minus": ("Minus", "Menos", "Moins", "マイナス", "Menos", "Минус", "减号"),
    "Up": ("Oben", "Arriba", "Haut", "上", "Cima", "Вверх", "上"),
    "Down": ("Unten", "Abajo", "Bas", "下", "Baixo", "Вниз", "下"),
    "Left": ("Links", "Izquierda", "Gauche", "左", "Esquerda", "Влево", "左"),
    "Right": ("Rechts", "Derecha", "Droite", "右", "Direita", "Вправо", "右"),
    "Hidden": ("Ausgeblendet", "Oculto", "Masqué", "非表示", "Oculto", "Скрыто", "隐藏"),
    "Top left": ("Oben links", "Arriba a la izquierda", "En haut à gauche", "左上",
                 "Superior esquerdo", "Сверху слева", "左上"),
    "Top right": ("Oben rechts", "Arriba a la derecha", "En haut à droite", "右上",
                  "Superior direito", "Сверху справа", "右上"),
    "Bottom left": ("Unten links", "Abajo a la izquierda", "En bas à gauche", "左下",
                    "Inferior esquerdo", "Снизу слева", "左下"),
    "Bottom right": ("Unten rechts", "Abajo a la derecha", "En bas à droite", "右下",
                     "Inferior direito", "Снизу справа", "右下"),
}



def value_key(label: str) -> str:
    """tico_config.cpp's ValueKey: settings_fbneo_value_ + label as a slug."""
    return "settings_fbneo_value_" + "_".join(re.findall(r"[a-z0-9]+", label.lower()))


def english_choice(value: str, label: str) -> str:
    # the core leaves on/off style values unlabelled
    return label.capitalize() if label == value and value in ("disabled", "enabled") else label


def c_tokens(text: str):
    """String literals, NULL, braces and names of a C initializer, in order."""
    for match in re.finditer(r'"((?:[^"\\]|\\.)*)"|(NULL)|([{}])|([A-Za-z_][A-Za-z0-9_]*)', text):
        literal, null, brace, name = match.groups()
        if literal is not None:
            yield ("str", bytes(literal, "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8"))
        elif null:
            yield ("null", None)
        elif brace:
            yield (brace, brace)
        else:
            yield ("name", name)


def parse_options() -> list[dict]:
    """The var_fbneo_* definitions: key, desc, info, values and default."""
    source = CORE_OPTIONS.read_text(encoding="utf-8")
    # value lists shared through macros (PERCENT_VALUES in retro_common.h)
    header = CORE_OPTIONS.with_suffix(".h").read_text(encoding="utf-8")
    macros = dict(re.findall(r"#define\s+(\w+)[ \t]+((?:.*\\\n)*.*)", header + "\n" + source))
    options = []
    for match in re.finditer(r"retro_core_option_v2_definition\s+var_fbneo_\w+\s*=\s*\{", source):
        depth, end = 1, match.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(source[end], 0)
            end += 1
        block = source[match.end():end - 1]
        for name, expansion in macros.items():
            if name in block:
                block = re.sub(rf"\b{name}\b", lambda _: expansion.replace("\\\n", "\n"), block)
        tokens = list(c_tokens(block))
        # key, desc, desc_categorized, info, info_categorized, category
        head, rest = [], tokens
        while len(head) < 6:
            kind, value = rest[0]
            rest = rest[1:]
            if kind in ("str", "null"):
                head.append(value)
        assert rest[0][0] == "{", head[0]
        values, depth, pair, i = [], 0, [], 0
        for i, (kind, value) in enumerate(rest):
            if kind == "{":
                depth += 1
                pair = []
            elif kind == "}":
                depth -= 1
                if depth == 1 and pair and pair[0] is not None:
                    values.append((pair[0], pair[1] if len(pair) > 1 and pair[1] else pair[0]))
                if depth == 0:
                    break
            elif kind in ("str", "null"):
                pair.append(value)
        default = next(value for kind, value in rest[i + 1:] if kind == "str")
        options.append({"key": head[0], "desc": head[1], "info": head[3] or "",
                        "default": default, "values": values})
    return options


def label_key(key: str) -> str:
    return LABEL_KEYS.get(key, "settings_fbneo_" + key.removeprefix("fbneo-").replace("-", "_"))


def excluded(key: str) -> bool:
    return key in EXCLUDED or key.startswith(EXCLUDED_PREFIXES)


def build_settings(options: list[dict]) -> dict:
    core = {o["key"]: o for o in options}
    placed = {key for _, sections in LAYOUT for _, keys in sections for key in keys}
    missing = sorted(k for k in set(core) - placed if not excluded(k))
    if missing:
        raise SystemExit(f"core options not placed in LAYOUT: {missing}")
    unknown = sorted(placed - set(core))
    if unknown:
        raise SystemExit(f"LAYOUT names options the core does not have: {unknown}")

    tabs = []
    for tab, sections in LAYOUT:
        out_sections = []
        for title, keys in sections:
            out = []
            for key in keys:
                source = core[key]
                values = [v for v, _ in source["values"]]
                option = {"key": key, "label": label_key(key)}
                if sorted(values) == ["disabled", "enabled"]:
                    option.update(type="bool", default=source["default"])
                else:
                    option.update(type="enum", default=source["default"], choices=[
                        {"label": english_choice(v, l), "value": v} for v, l in source["values"]])
                if key in RESTART:
                    option["restart"] = True
                if key in DEPENDS_ON:
                    on, value = DEPENDS_ON[key]
                    option["depends_on"] = {"key": on, "value": value}
                out.append(option)
            out_sections.append({"title": title, "options": out})
        tabs.append({"name": tab, "sections": out_sections})

    def overlay_tab(definition):
        tab, sections = definition
        return {"name": tab, "sections": [
            {"title": title, "options": [
                {**o, "choices": [{"label": l, "value": v} for v, l in o["choices"]]}
                if "choices" in o else dict(o)
                for o in options]}
            for title, options in sections]}

    tabs.insert(1, overlay_tab(OVERLAY_TAB))
    tabs.append(overlay_tab(CONTROLS_TAB))

    return {
        "core_id": "fbneo",
        "display_name": "FinalBurn Neo",
        "config_file": "fbneo.jsonc",
        "slugs": ["fbneo", "arcade", "neogeo"],
        "bool_true_value": "enabled",
        "bool_false_value": "disabled",
        "tabs": tabs,
    }


def tico_owned(key: str) -> bool:
    """Labels tico itself defines, whose wording tico keeps."""
    return key in LABEL_KEYS.values() or key.startswith(("settings_fbneo_tab_",
                                                          "settings_fbneo_section_"))


def build_strings(settings: dict, existing: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    strings: dict[str, dict[str, str]] = {lang: {} for lang in LANGUAGES}
    for lang in LANGUAGES:
        out = strings[lang]
        index = LANGUAGES.index(lang)
        for key, texts in LABELS.items():
            out[key] = texts[index]
        if lang != "en":
            for choice, translations in CHOICES.items():
                out[value_key(choice)] = translations[index - 1]
    # tico's own labels keep tico's wording: from tico-nx when it is checked
    # out, otherwise as the language files already have them
    for lang in LANGUAGES:
        path = TICO_NX / "assets/lang" / f"{lang}.json"
        source = json.loads(path.read_text()) if path.exists() else existing[lang]
        for key, value in source.items():
            if tico_owned(key):
                strings[lang][key] = value
    used = set()

    def walk(node):
        if isinstance(node, dict):
            for field in ("label", "name", "title"):
                if isinstance(node.get(field), str) and node[field].startswith("settings_"):
                    used.add(node[field])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(settings)
    unlabelled = sorted(used - set(strings["en"]))
    if unlabelled:
        raise SystemExit(f"labels without English text: {unlabelled}")
    return strings


def main() -> None:
    settings = build_settings(parse_options())
    SETTINGS.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    current_files = {lang: json.loads((LANG_DIR / f"{lang}.json").read_text())
                     if (LANG_DIR / f"{lang}.json").exists() else {} for lang in LANGUAGES}
    for lang, strings in build_strings(settings, current_files).items():
        path = LANG_DIR / f"{lang}.json"
        current = {k: v for k, v in current_files[lang].items()
                   if not k.startswith("settings_fbneo_")}
        current.update(dict(sorted(strings.items())))
        path.write_text(json.dumps(current, indent=4, ensure_ascii=False) + "\n")
    print(f"wrote {SETTINGS.relative_to(ROOT)} and {len(LANGUAGES)} language files")


if __name__ == "__main__":
    main()
