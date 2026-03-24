#!/usr/bin/env python3
"""
create-module.py — Tao nhanh module cho du an MVVM Android.

Ten Module format:
    <n>          ->  :<n>/              top-level app module  (chon Type)
    core.<n>     ->  :core  (1 module, them package core/<n>/ ben trong)
    feature.<n>  ->  :features:<n>/    full boilerplate

Config:
    group  = com.huydt       (dung cho core, feature, lib)
    App nhap app_package rieng luc tao, vd: com.huydt.app

Type (chi ap dung cho app-level module):
    App     -> base.android.app  (Compose + Hilt + Navigation + MainActivity)
    Lib     -> base.android.library
    LibJar -> kotlin jvm only, build .jar

Usage:
    python create-module.py
    python create-module.py --reset-config
"""

import os, sys, re, json, argparse

RESET  = "\033[0m";  BOLD  = "\033[1m"
CYAN   = "\033[96m"; GREEN = "\033[92m"
YELLOW = "\033[93m"; RED   = "\033[91m"
GRAY   = "\033[90m"

def bold(s):   return f"{BOLD}{s}{RESET}"
def cyan(s):   return f"{CYAN}{s}{RESET}"
def green(s):  return f"{GREEN}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def gray(s):   return f"{GRAY}{s}{RESET}"

def clear(): os.system("cls" if os.name == "nt" else "clear")

# ── UI ────────────────────────────────────────────────────────────────────────
def banner(pkg, root):
    print(f"{CYAN}{BOLD}")
    print("  \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557")
    print("  \u2551       \U0001f916  Android Module Creator         \u2551")
    print("  \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d")
    print(RESET)
    print(f"  {gray('Group  :')} {cyan(pkg)}")
    print(f"  {gray('Root   :')} {cyan(root)}")
    print()

def show_menu(title, options):
    print(f"  {bold(title)}")
    print(f"  {gray('-' * 52)}")
    for key, label in options:
        print(f"  {cyan(bold('[' + key + ']'))}  {label}")
    print(f"  {gray('-' * 52)}")

def prompt(msg, default=None):
    hint = f" {gray('(' + str(default) + ')')}" if default is not None else ""
    try:
        val = input(f"  {YELLOW}> {msg}{hint}: {RESET}").strip()
        return val if val else (str(default) if default is not None else "")
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {gray('Tam biet! 👋')}\n")
        sys.exit(0)

def confirm(msg):
    return prompt(msg + f" {gray('(y/n)')}",  default="y").lower() in ("y", "yes", "co", "")

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, ".module-config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def setup_config(force=False):
    existing = load_config()
    if existing and not force:
        return existing

    clear()
    print(f"{CYAN}{BOLD}")
    print("  \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557")
    print("  \u2551         \u2699\ufe0f   Cau hinh lan dau            \u2551")
    print("  \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d")
    print(RESET)

    up_one = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
    guessed_root = (up_one if os.path.exists(os.path.join(up_one, "settings.gradle.kts"))
                    else os.getcwd() if os.path.exists(os.path.join(os.getcwd(), "settings.gradle.kts"))
                    else up_one)

    print(f"  {bold('Project root')} -- thu muc chua settings.gradle.kts")
    root = os.path.normpath(os.path.expanduser(prompt("Project root", default=guessed_root)))

    if not os.path.exists(os.path.join(root, "settings.gradle.kts")):
        print(f"\n  {red('Khong tim thay settings.gradle.kts tai:')} {root}")
        print(f"  {yellow('Tiep tuc nhung se khong update settings tu dong.')}\n")

    print()
    print(f"  {bold('Group')} -- namespace goc dung cho core/feature/lib (vd: com.huydt)")
    pkg = prompt("Group")
    while not pkg or not re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,}', pkg):
        print(f"  {red('Group khong hop le -- vi du: com.huydt')}")
        pkg = prompt("Group")

    cfg = {"base_package": pkg, "project_root": root}
    save_config(cfg)
    print(f"\n  {green('Da luu config')} -> {gray(os.path.relpath(CONFIG_FILE))}\n")
    return cfg

# ── Helpers ───────────────────────────────────────────────────────────────────
def to_pascal(name: str) -> str:
    return "".join(w.capitalize() for w in name.replace("-", "_").split("_"))

def validate_name(name: str):
    name = name.lower().replace("-", "_")
    return name if re.match(r'^[a-z][a-z0-9_]*$', name) else None

def write_file(path: str, content: str, root: str, dry_run: bool = False):
    rel = os.path.relpath(path, root)
    if dry_run:
        print(f"    {yellow('[dry]')} {rel}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"    {green('+')} {rel}")

def write_file_skip_existing(path: str, content: str, root: str, dry_run: bool = False):
    """Write file, skip silently if already exists."""
    rel = os.path.relpath(path, root)
    if dry_run:
        exists = os.path.exists(path)
        print(f"    {yellow('[dry]')} {rel}" + (f" {gray('(skip, da co)')}" if exists else ""))
        return
    if os.path.exists(path):
        print(f"    {yellow('~')} {rel} (skip, da co)")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"    {green('+')} {rel}")

def add_to_settings(root: str, line: str, dry_run: bool = False):
    settings = os.path.join(root, "settings.gradle.kts")
    if not os.path.exists(settings):
        print(f"    {red('x')} settings.gradle.kts khong tim thay")
        return
    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()
    if line in content:
        print(f"    {yellow('~')} settings da co: {line}")
        return
    if dry_run:
        print(f"    {yellow('[dry]')} settings.gradle.kts <- {line}")
        return
    with open(settings, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"\n{line}")
    print(f"    {green('+')} settings.gradle.kts <- {line}")

# ── Parse Ten Module ──────────────────────────────────────────────────────────
def parse_ten_module(raw: str):
    """
    Parses Ten Module input. Returns (kind, data) or (None, error_str).

    Formats:
      app                       -> ("app",     "app")
      core domain result          -> ("core",    ["domain","result"], None)       shared core
      core.app domain result    -> ("core",    ["domain","result"], "app")    per-app core
      feature cart                -> ("feature", ["cart"],            None)       shared feature
      feature.app home          -> ("feature", ["home"],            "app")    per-app feature

    Returns:
      ("app",     name_str)
      ("core",    [sub, ...], app_name_or_None)
      ("feature", [sub, ...], app_name_or_None)
    """
    raw = raw.strip()
    if not raw:
        return None, "Ten khong duoc de trong."

    parts = raw.split()
    first = parts[0].lower()

    # core / core.<appname>  or  feature / feature.<appname>
    for kind in ("core", "feature"):
        if first == kind or first.startswith(f"{kind}."):
            app_ctx = first[len(kind)+1:] if "." in first else None
            if len(parts) < 2:
                return None, f"Thieu ten sub. Vi du: {kind} domain | {kind}.app domain"
            subs = []
            for p in parts[1:]:
                n = validate_name(p)
                if not n:
                    return None, f"Ten sub '{p}' khong hop le"
                subs.append(n)
            return kind, subs, app_ctx

    # plain app-level name
    if len(parts) == 1:
        name = validate_name(parts[0])
        if not name:
            return None, f"Ten '{parts[0]}' khong hop le -- chi dung chu thuong, so, dau _"
        return "app", name

    return None, "Dinh dang khong hop le. Vi du: app | core domain | core.app domain | feature cart | feature.app home"

# ── Type menu (app-level only) ────────────────────────────────────────────────
TYPE_OPTIONS = [
    ("1", "App     -- base.android.app  (Compose + Hilt + Navigation + MainActivity)"),
    ("2", "Lib     -- base.android.library"),
    ("3", "LibJar -- kotlin jvm only, build .jar"),
]
TYPE_MAP = {"1": "App", "2": "Lib", "3": "LibJar"}

def pick_type():
    print()
    show_menu("Buoc 2 -- Type:", TYPE_OPTIONS)
    print()
    while True:
        ch = prompt("Nhap lua chon", default="1")
        if ch in TYPE_MAP:
            return TYPE_MAP[ch]
        print(f"  {red('Lua chon khong hop le.')}")

# ── CORE generator (single :core module) ─────────────────────────────────────
# Known sub-names and their preset file structures
CORE_PRESETS = {
    "domain": [
        # (rel_path_from_pkg_dir, content_fn)  content_fn(pkg, pascal) -> str
        ("model/Entity.kt",      lambda pkg, _: f"package {pkg}.model\n\n// TODO: them domain entities\n"),
        ("repository/Repository.kt", lambda pkg, p: f"package {pkg}.repository\n\ninterface {p}Repository {{\n    // TODO: suspend fun / Flow\n}}\n"),
        ("usecase/UseCase.kt",   lambda pkg, _: f"package {pkg}.usecase\n\nabstract class UseCase<in P, out R> {{\n    abstract suspend operator fun invoke(params: P): R\n}}\n\nabstract class FlowUseCase<in P, out R> {{\n    abstract operator fun invoke(params: P): kotlinx.coroutines.flow.Flow<R>\n}}\n"),
    ],
    "result": [
        ("Result.kt", lambda pkg, _: f"""package {pkg}

sealed class Result<out T> {{
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable, val message: String? = null) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}}

fun <T> Result<T>.onSuccess(action: (T) -> Unit): Result<T> {{
    if (this is Result.Success) action(data)
    return this
}}

fun <T> Result<T>.onError(action: (Throwable, String?) -> Unit): Result<T> {{
    if (this is Result.Error) action(exception, message)
    return this
}}

fun <T> Result<T>.getOrNull(): T? = if (this is Result.Success) data else null
"""),
    ],
    "usecase": [
        ("UseCase.kt", lambda pkg, _: f"""package {pkg}

abstract class UseCase<in P, out R> {{
    abstract suspend operator fun invoke(params: P): R
}}

abstract class FlowUseCase<in P, out R> {{
    abstract operator fun invoke(params: P): kotlinx.coroutines.flow.Flow<R>
}}

object NoParams
"""),
    ],
    "common": [
        ("extension/FlowExt.kt", lambda pkg, _: f"package {pkg}.extension\n\nimport kotlinx.coroutines.flow.Flow\nimport kotlinx.coroutines.flow.catch\nimport kotlinx.coroutines.flow.map\n\n// Flow extensions\n"),
        ("extension/ContextExt.kt", lambda pkg, _: f"package {pkg}.extension\n\nimport android.content.Context\n\n// Context extensions\n"),
        ("util/Logger.kt", lambda pkg, _: f"package {pkg}.util\n\nimport android.util.Log\n\nobject Logger {{\n    private const val TAG = \"AppLogger\"\n    fun d(msg: String) = Log.d(TAG, msg)\n    fun e(msg: String, t: Throwable? = null) = Log.e(TAG, msg, t)\n}}\n"),
    ],
    "ui": [
        ("component/LoadingScreen.kt", lambda pkg, _: f"""package {pkg}.component

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier

@Composable
fun LoadingScreen(modifier: Modifier = Modifier) {{
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {{
        CircularProgressIndicator()
    }}
}}
"""),
        ("component/ErrorScreen.kt", lambda pkg, _: f"""package {pkg}.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ErrorScreen(
    message: String,
    onRetry: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {{
    Column(
        modifier.fillMaxSize().padding(24.dp),
        verticalArrangement   = Arrangement.Center,
        horizontalAlignment   = Alignment.CenterHorizontally,
    ) {{
        Text(message)
        if (onRetry != null) {{
            Button(onClick = onRetry) {{ Text("Retry") }}
        }}
    }}
}}
"""),
    ],
    "designsystem": [
        ("theme/Theme.kt", lambda pkg, _: f"""package {pkg}.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable

@Composable
fun AppTheme(content: @Composable () -> Unit) {{
    MaterialTheme(content = content)
}}
"""),
        ("theme/Color.kt", lambda pkg, _: f"package {pkg}.theme\n\nimport androidx.compose.ui.graphics.Color\n\n// TODO: define app colors\nval Purple80 = Color(0xFFD0BCFF)\nval PurpleGrey80 = Color(0xFFCCC2DC)\n"),
        ("theme/Type.kt", lambda pkg, _: f"package {pkg}.theme\n\nimport androidx.compose.material3.Typography\n\nval AppTypography = Typography()\n"),
    ],
}

def gen_core(sub: str, cfg: dict, app_ctx: str = None, dry_run: bool = False):
    """
    Them sub-package vao module core.
    app_ctx=None  -> :core          shared,   pkg = <group>.core.<sub>
    app_ctx="g1"  -> :core.g1       per-app,  pkg = <group>.g1.core.<sub>
    """
    pkg_base  = cfg["base_package"]
    root      = cfg["project_root"]
    pascal    = to_pascal(sub)

    if app_ctx:
        mod_name  = f"core.{app_ctx}"   # Gradle: :core.app
        dir_name  = f"core-{app_ctx}"   # folder: core-app/
        core_pkg  = f"{pkg_base}.{app_ctx}.core"
    else:
        mod_name  = "core"
        dir_name  = "core"
        core_pkg  = f"{pkg_base}.core"

    sub_pkg   = f"{core_pkg}.{sub}"
    core_dir  = os.path.join(root, dir_name)
    src_base  = os.path.join(core_dir, "src", "main", "java", core_pkg.replace(".", "/"))
    sub_dir   = os.path.join(src_base, sub)
    test_base = os.path.join(core_dir, "src", "test", "java", core_pkg.replace(".", "/"))
    sub_test  = os.path.join(test_base, sub)

    print(f"\n  {bold('Tao files...')}\n")

    # build.gradle.kts — tao neu chua co
    write_file_skip_existing(os.path.join(core_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.library")
    // id("base.android.hilt")    // bo comment neu can Hilt
    // id("base.android.compose") // bo comment neu can Compose
}}

android {{
    namespace = "{core_pkg}"
}}

dependencies {{
    // Them deps khi can.

    // implementation(libs.coroutines.android)
    // implementation(libs.lifecycle.runtime.compose)
    // implementation(libs.compose.material.icons.extended)
}}
""", root, dry_run)

    # AndroidManifest — tao neu chua co
    manifest = os.path.join(core_dir, "src", "main", "AndroidManifest.xml")
    write_file_skip_existing(manifest, f"""\
<?xml version="1.0" encoding="utf-8"?>
<manifest package="{core_pkg}" />
""", root, dry_run)

    # Preset files for known sub-names
    presets = CORE_PRESETS.get(sub)
    if presets:
        for rel, content_fn in presets:
            write_file(os.path.join(sub_dir, rel), content_fn(sub_pkg, pascal), root, dry_run)
    else:
        # Generic placeholder
        write_file(os.path.join(sub_dir, f"{pascal}.kt"), f"""\
package {sub_pkg}

// TODO: them code cho core.{sub}
""", root, dry_run)

    # Test placeholder
    write_file_skip_existing(os.path.join(sub_test, f"{pascal}Test.kt"), f"""\
package {sub_pkg}

import org.junit.Test

class {pascal}Test {{

    @Test
    fun `placeholder test`() {{
        // TODO
    }}
}}
""", root, dry_run)

    add_to_settings(root, f'include(":{dir_name}")', dry_run)

    tag       = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('Done!')}"
    impl      = f'implementation(project(":{mod_name}"))'
    ctx_label = f".{app_ctx}" if app_ctx else " (shared)"
    print()
    print(f"{tag} Core{ctx_label}.{sub} {'preview' if dry_run else 'tao xong!'}")
    print(f"  {gray('Package :')} {sub_pkg}")
    print(f"  {gray('Depend  :')} {impl}")
    print()

# ── FEATURE generator ─────────────────────────────────────────────────────────
def gen_feature(name: str, cfg: dict, app_ctx: str = None, dry_run: bool = False):
    """
    app_ctx=None  -> :features:<name>          shared,  pkg = <group>.feature.<name>
    app_ctx="g1"  -> :features-g1:<name>       per-app, pkg = <group>.g1.feature.<name>
    """
    pkg_base  = cfg["base_package"]
    root      = cfg["project_root"]
    pascal    = to_pascal(name)

    if app_ctx:
        feat_mod_root = f"features.{app_ctx}"    # Gradle: :features.app:home
        feat_dir_root = os.path.join(root, f"features-{app_ctx}")  # folder: features-app/
        pkg           = f"{pkg_base}.{app_ctx}.feature.{name}"
        settings_line = f'include(":features-{app_ctx}:{name}")'
    else:
        feat_mod_root = "features"
        feat_dir_root = os.path.join(root, "features")
        pkg           = f"{pkg_base}.feature.{name}"
        settings_line = f'include(":features:{name}")'

    data_pkg  = f"{pkg}.data"
    mod_dir   = os.path.join(feat_dir_root, name)
    src       = os.path.join(mod_dir, "src", "main", "java", pkg.replace(".", "/"))
    test_src  = os.path.join(mod_dir, "src", "test", "java", pkg.replace(".", "/"))
    data_src  = os.path.join(src, "data")
    data_test = os.path.join(test_src, "data")

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module ' + mod_dir + ' da ton tai!')}\n")
        return

    print(f"\n  {bold('Tao files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.feature")
    // id("base.android.hilt")       // bo comment neu can Hilt
    // id("base.android.compose") // bo comment neu can Compose
}}

android {{
    namespace = "{pkg}"
}}

dependencies {{
    // implementation(project(":core"))

    // implementation(libs.coroutines.android)
    // implementation(libs.lifecycle.runtime.compose)
    // implementation(libs.compose.material.icons.extended)
}}
""", root, dry_run)

    write_file(os.path.join(src, "state", f"{pascal}State.kt"), f"""\
package {pkg}.state

data class {pascal}UiState(
    val isLoading: Boolean = false,
    val error: String? = null,
)

sealed interface {pascal}UiEvent {{
    data object NavigateBack : {pascal}UiEvent
    data class ShowSnackbar(val message: String) : {pascal}UiEvent
}}
""", root, dry_run)

    write_file(os.path.join(src, "viewmodel", f"{pascal}ViewModel.kt"), f"""\
package {pkg}.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import {pkg}.state.{pascal}UiEvent
import {pkg}.state.{pascal}UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class {pascal}ViewModel @Inject constructor(
    // TODO: inject UseCase
) : ViewModel() {{

    private val _uiState = MutableStateFlow({pascal}UiState())
    val uiState: StateFlow<{pascal}UiState> = _uiState.asStateFlow()

    private val _uiEvent = Channel<{pascal}UiEvent>(Channel.BUFFERED)
    val uiEvent = _uiEvent.receiveAsFlow()

    fun onBack() {{
        viewModelScope.launch {{ _uiEvent.send({pascal}UiEvent.NavigateBack) }}
    }}
}}
""", root, dry_run)

    write_file(os.path.join(src, "screen", f"{pascal}Screen.kt"), f"""\
package {pkg}.screen

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import {pkg}.state.{pascal}UiEvent
import {pkg}.state.{pascal}UiState
import {pkg}.viewmodel.{pascal}ViewModel
import kotlinx.coroutines.flow.collectLatest

@Composable
fun {pascal}Route(
    onNavigateBack: () -> Unit,
    viewModel: {pascal}ViewModel = hiltViewModel(),
) {{
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember {{ SnackbarHostState() }}

    LaunchedEffect(Unit) {{
        viewModel.uiEvent.collectLatest {{ event ->
            when (event) {{
                is {pascal}UiEvent.NavigateBack -> onNavigateBack()
                is {pascal}UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }}
        }}
    }}

    {pascal}Screen(
        uiState           = uiState,
        snackbarHostState = snackbarHostState,
        onNavigateBack    = viewModel::onBack,
    )
}}

@Composable
internal fun {pascal}Screen(
    uiState: {pascal}UiState,
    snackbarHostState: SnackbarHostState = remember {{ SnackbarHostState() }},
    onNavigateBack: () -> Unit = {{}},
) {{
    Scaffold(
        snackbarHost = {{ SnackbarHost(snackbarHostState) }},
    ) {{ padding ->
        Box(
            modifier         = Modifier.fillMaxSize().padding(padding),
            contentAlignment = Alignment.Center,
        ) {{
            Text("{pascal} Screen")
        }}
    }}
}}
""", root, dry_run)

    route_const = name.upper() + "_ROUTE"
    write_file(os.path.join(src, "navigation", f"{pascal}Navigation.kt"), f"""\
package {pkg}.navigation

import androidx.navigation.NavController
import androidx.navigation.NavGraphBuilder
import androidx.navigation.compose.composable
import {pkg}.screen.{pascal}Route

const val {route_const} = "{name}"

fun NavController.navigateTo{pascal}() = navigate({route_const})

fun NavGraphBuilder.{name}Screen(
    onNavigateBack: () -> Unit,
) {{
    composable(route = {route_const}) {{
        {pascal}Route(onNavigateBack = onNavigateBack)
    }}
}}
""", root, dry_run)

    write_file(os.path.join(mod_dir, "src", "main", "res", "values", "strings.xml"), f"""\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="feature_{name}_title">{pascal}</string>
</resources>
""", root, dry_run)

    write_file(os.path.join(test_src, "viewmodel", f"{pascal}ViewModelTest.kt"), f"""\
package {pkg}.viewmodel

import app.cash.turbine.test
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Before
import org.junit.Test
import {pkg}.state.{pascal}UiEvent

@OptIn(ExperimentalCoroutinesApi::class)
class {pascal}ViewModelTest {{

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var viewModel: {pascal}ViewModel

    @Before
    fun setUp() {{
        Dispatchers.setMain(testDispatcher)
        viewModel = {pascal}ViewModel()
    }}

    @After
    fun tearDown() {{
        Dispatchers.resetMain()
    }}

    @Test
    fun `initial state is correct`() = runTest {{
        assert(!viewModel.uiState.value.isLoading)
        assert(viewModel.uiState.value.error == null)
    }}

    @Test
    fun `onBack emits NavigateBack event`() = runTest {{
        viewModel.uiEvent.test {{
            viewModel.onBack()
            testDispatcher.scheduler.advanceUntilIdle()
            assert(awaitItem() is {pascal}UiEvent.NavigateBack)
        }}
    }}
}}
""", root, dry_run)

    write_file(os.path.join(data_src, "repository", f"{pascal}Repository.kt"), f"""\
package {data_pkg}.repository

interface {pascal}Repository {{
    // TODO: suspend fun / Flow
}}
""", root, dry_run)

    write_file(os.path.join(data_src, "repository", f"{pascal}RepositoryImpl.kt"), f"""\
package {data_pkg}.repository

import javax.inject.Inject

class {pascal}RepositoryImpl @Inject constructor() : {pascal}Repository {{
    // TODO: implement
}}
""", root, dry_run)

    write_file(os.path.join(data_src, "di", f"{pascal}DataModule.kt"), f"""\
package {data_pkg}.di

import {data_pkg}.repository.{pascal}Repository
import {data_pkg}.repository.{pascal}RepositoryImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class {pascal}DataModule {{

    @Binds
    @Singleton
    abstract fun bind{pascal}Repository(
        impl: {pascal}RepositoryImpl,
    ): {pascal}Repository
}}
""", root, dry_run)

    write_file(os.path.join(data_test, "repository", f"{pascal}RepositoryTest.kt"), f"""\
package {data_pkg}.repository

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

class {pascal}RepositoryTest {{

    private lateinit var repository: {pascal}RepositoryImpl

    @Before
    fun setUp() {{ repository = {pascal}RepositoryImpl() }}

    @Test
    fun `placeholder test`() = runTest {{ /* TODO */ }}
}}
""", root, dry_run)

    add_to_settings(root, settings_line, dry_run)

    impl = f'implementation(project("{settings_line[9:-2]}"))'  # extract path from include(":x:y")
    imp1 = f'import {pkg}.navigation.{name}Screen'
    imp2 = f'import {pkg}.navigation.navigateTo{pascal}'
    nav  = f'{name}Screen(onNavigateBack = {{ navController.popBackStack() }})'
    ctx_label = f".{app_ctx}" if app_ctx else " (shared)"

    tag = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('Done!')}"
    print()
    print(f"{tag} Feature{ctx_label} {bold(name)} {'preview' if dry_run else 'tao xong!'}")
    print()
    print(f"  {bold('Buoc tiep theo:')}")
    print(f"  1. {cyan('app/build.gradle.kts')}: {gray(impl)}")
    print(f"  2. {cyan('AppNavHost.kt')}:")
    print(f"     {gray(imp1)}")
    print(f"     {gray(imp2)}")
    print(f"     {gray(nav)}")
    print()

# ── APP-LEVEL generators ──────────────────────────────────────────────────────
def gen_app(name: str, app_pkg: str, cfg: dict, dry_run: bool = False):
    """
    name    : module dir name, vd: app
    app_pkg : full package,    vd: com.huydt.app
    """
    root     = cfg["project_root"]
    pkg      = app_pkg
    pkg_path = pkg.replace(".", "/")
    mod_dir  = os.path.join(root, name)
    src      = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    res      = os.path.join(mod_dir, "src", "main", "res")

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module :' + name + ' da ton tai!')}\n")
        return

    print(f"\n  {bold('Tao files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.app")
}}

android {{
    namespace = "{pkg}"

    defaultConfig {{
        applicationId = "{pkg}"
        versionCode   = 1
        versionName   = "1.0.0"
    }}
}}

dependencies {{
    // Core
    // implementation(project(":core"))

    // Features
    // implementation(project(":features:home"))

    // implementation(libs.compose.material.icons.extended)

    // base.android.app da tu dong them:
    // Compose BOM, Navigation, Hilt, test libs
}}
""", root, dry_run)

    write_file(os.path.join(src, "App.kt"), f"""\
package {pkg}

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application()
""", root, dry_run)

    write_file(os.path.join(src, "MainActivity.kt"), f"""\
package {pkg}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import {pkg}.navigation.AppNavHost
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {{

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {{
            AppNavHost()
        }}
    }}
}}
""", root, dry_run)

    write_file(os.path.join(src, "navigation", "AppNavHost.kt"), f"""\
package {pkg}.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.rememberNavController

@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController(),
) {{
    NavHost(
        navController    = navController,
        startDestination = "home",
    ) {{
        // TODO: them destinations
    }}
}}
""", root, dry_run)

    write_file(os.path.join(mod_dir, "src", "main", "AndroidManifest.xml"), f"""\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:name=".App"
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.App">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
""", root, dry_run)

    write_file(os.path.join(res, "values", "strings.xml"), f"""\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{name.capitalize()}</string>
</resources>
""", root, dry_run)

    write_file(os.path.join(res, "values", "themes.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.App" parent="android:Theme.DeviceDefault.Light.NoActionBar" />
</resources>
""", root, dry_run)

    write_file(os.path.join(mod_dir, "proguard-rules.pro"),
               "# Add project specific ProGuard rules here.\n", root, dry_run)

    add_to_settings(root, f'include(":{name}")', dry_run)

    tag = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('Done!')}"
    print()
    print(f"{tag} Module {bold(name)} [App] {'preview' if dry_run else 'tao xong!'}")
    print()


def gen_lib_app(name: str, cfg: dict, dry_run: bool = False):
    pkg_base      = cfg["base_package"]
    root          = cfg["project_root"]
    pkg           = f"{pkg_base}.{name}"
    pkg_path      = pkg.replace(".", "/")
    pascal        = to_pascal(name)
    mod_dir       = os.path.join(root, name)
    src           = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    test_src      = os.path.join(mod_dir, "src", "test", "java", pkg_path)
    settings_line = f'include(":{name}")'

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module :' + name + ' da ton tai!')}\n")
        return

    print(f"\n  {bold('Tao files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.library")
    // id("base.android.hilt")    // bo comment neu can Hilt
    // id("base.android.compose") // bo comment neu can Compose
}}

android {{
    namespace = "{pkg}"
}}

dependencies {{
    // Them deps khi can.

    // implementation(libs.compose.material.icons.extended)
}}
""", root, dry_run)

    write_file(os.path.join(src, f"{pascal}.kt"),
               f"package {pkg}\n\n// TODO: them code\n", root, dry_run)
    write_file(os.path.join(test_src, f"{pascal}Test.kt"), f"""\
package {pkg}

import org.junit.Test

class {pascal}Test {{
    @Test fun `placeholder test`() {{ /* TODO */ }}
}}
""", root, dry_run)

    add_to_settings(root, settings_line, dry_run)

    tag  = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('Done!')}"
    impl = f'implementation(project(":{name}"))'
    print()
    print(f"{tag} Module {bold(name)} [Lib] {'preview' if dry_run else 'tao xong!'}")
    print(f"  {gray(impl)}")
    print()


def gen_LibJar_app(name: str, cfg: dict, dry_run: bool = False):
    pkg_base      = cfg["base_package"]
    root          = cfg["project_root"]
    pkg           = f"{pkg_base}.lib.{name}"
    pascal        = to_pascal(name)
    mod_dir       = os.path.join(root, "libs", name)
    src           = os.path.join(mod_dir, "src", "main", "kotlin", pkg.replace(".", "/"))
    test_src      = os.path.join(mod_dir, "src", "test", "kotlin", pkg.replace(".", "/"))
    settings_line = f'include(":libs:{name}")'

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module :libs:' + name + ' da ton tai!')}\n")
        return

    print(f"\n  {bold('Tao files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("org.jetbrains.kotlin.jvm")
}}

group   = "{pkg}"
version = "1.0.0"

java {{
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}}

kotlin {{
    compilerOptions {{
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }}
}}

dependencies {{
    testImplementation(libs.junit)
}}
""", root, dry_run)

    write_file(os.path.join(src, "Main.kt"),
               f"package {pkg}\n\nfun main() {{\n    println(\"Hello from {pascal}!\")\n}}\n",
               root, dry_run)
    write_file(os.path.join(src, f"{pascal}.kt"),
               f"package {pkg}\n\nobject {pascal} {{\n    // TODO\n}}\n", root, dry_run)
    write_file(os.path.join(test_src, f"{pascal}Test.kt"), f"""\
package {pkg}

import org.junit.Test

class {pascal}Test {{
    @Test fun `placeholder test`() {{ /* TODO */ }}
}}
""", root, dry_run)

    add_to_settings(root, settings_line, dry_run)

    tag  = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('Done!')}"
    impl = f'implementation(project(":libs:{name}"))'
    print()
    print(f"{tag} Module {bold(name)} [LibJar] {'preview' if dry_run else 'tao xong!'}")
    print(f"  {gray(impl)}")
    print()

# ── Menu ──────────────────────────────────────────────────────────────────────
def run_menu(cfg: dict):
    clear()
    banner(cfg["base_package"], cfg["project_root"])

    while True:
        show_menu("Menu chinh:", [
            ("1", "Tao module"),
            ("2", "Config    -- doi package / root dir"),
            ("3", "Exit"),
        ])
        print()
        choice = prompt("Nhap lua chon", default="1")

        if choice in ("3", "0", "q", "exit"):
            print(f"\n  {gray('Tam biet! 👋')}\n")
            sys.exit(0)

        if choice == "2":
            cfg = setup_config(force=True)
            clear()
            banner(cfg["base_package"], cfg["project_root"])
            continue

        if choice != "1":
            print(f"  {red('Lua chon khong hop le.')}\n")
            continue

        # ── Tao module ───────────────────────────────────────────────────────
        clear()
        banner(cfg["base_package"], cfg["project_root"])

        print(f"  {green('App module:')}")
        print(f"  {gray('  app, xxx [App, Lib, Jar]     -> :app, :xxx')}")
        print(f"  {green('Shared core/feature:')}")
        print(f"  {gray('  core domain result           -> :core (shared)')}")
        print(f"  {gray('  feature cart                 -> :features:cart (shared)')}")
        print(f"  {green('Per-app core/feature:')}")
        print(f"  {gray('  core.app domain result       -> :core-app')}")
        print(f"  {gray('  feature.app home             -> :features-app:home')}")
        print()

        while True:
            raw = prompt("Ten Module")
            parsed = parse_ten_module(raw)
            if parsed[0] is None:
                print(f"  {red(parsed[1])}")
                continue
            break

        prefix   = parsed[0]
        app_ctx  = None

        if prefix == "core":
            _, subs, app_ctx = parsed
        elif prefix == "feature":
            _, subs, app_ctx = parsed
            module_type = None
        else:
            name        = parsed[1]
            module_type = pick_type()

        pkg_base = cfg["base_package"]

        # Preview
        print()
        print(f"  {bold('Preview:')}")
        if prefix == "feature":
            mod_label = f"features.{app_ctx}" if app_ctx else "features"
            dir_label = f"features-{app_ctx}" if app_ctx else "features"
            ctx_label = f".{app_ctx}" if app_ctx else ""
            for s in subs:
                print(f"  {gray('Module  :')} :{mod_label}:{s}  {gray('(folder: ' + dir_label + '/' + s + ')')}")
                print(f"  {gray('Package :')} {pkg_base}{ctx_label}.feature.{s}")
                print(f"  {gray('Files   :')} Screen + ViewModel + State + Navigation + data/")
        elif prefix == "core":
            mod_name  = f"core.{app_ctx}" if app_ctx else "core"
            dir_name  = f"core-{app_ctx}" if app_ctx else "core"
            ctx_label = f".{app_ctx}" if app_ctx else ""
            print(f"  {gray('Module  :')} :{mod_name}  {gray('(folder: ' + dir_name + ')')}  (them {len(subs)} sub-package)")
            for s in subs:
                files = [f for f, _ in CORE_PRESETS[s]] if s in CORE_PRESETS else [f"{to_pascal(s)}.kt"]
                print(f"  {gray('  ' + s + ' :')} {pkg_base}{ctx_label}.core.{s}  [{', '.join(files)}]")
        else:
            print(f"  {gray('Module  :')} :{name}")
            print(f"  {gray('Type    :')} {module_type}")
            if module_type == "App":
                print(f"  {gray('Package :')} {pkg_base}.{name}  {gray('(co the doi)')}")
            else:
                print(f"  {gray('Package :')} {pkg_base}.{name}")
        print()

        if prefix == "core":
            for s in subs:
                gen_core(s, cfg, app_ctx=app_ctx)
        elif prefix == "feature":
            for s in subs:
                gen_feature(s, cfg, app_ctx=app_ctx)
        elif module_type == "App":
            gen_app(name, f"{pkg_base}.{name}", cfg)
        elif module_type == "Lib":
            gen_lib_app(name, cfg)
        else:
            gen_LibJar_app(name, cfg)

        input(f"\n  {GRAY}Enter to continue...{RESET}")
        clear()
        banner(cfg["base_package"], cfg["project_root"])

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(prog="create-module",
                                     description="Tao nhanh Android MVVM module.")
    parser.add_argument("--reset-config", action="store_true",
                        help="Xoa config cu, chay lai setup wizard")
    args = parser.parse_args()
    cfg  = setup_config(force=args.reset_config)
    run_menu(cfg)

if __name__ == "__main__":
    main()
