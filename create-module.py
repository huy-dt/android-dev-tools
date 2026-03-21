#!/usr/bin/env python3
"""
create-module.py — Tạo nhanh module cho dự án MVVM Android (Hybrid Architecture).

Cấu trúc hỗ trợ:
    app/                      ← tạo bằng mục [4]
    core/
     ├── common/
     ├── domain/
     ├── ui/
     ├── designsystem/
     └── data/
          └── {name}/         ← tạo bằng mục [3] "coredata"
    features/
     └── {name}/              ← tạo bằng mục [1] "feature"
          ├── data/           ← tạo kèm theo feature tự động
          └── src/

Usage:
    python create-module.py                        # interactive menu
    python create-module.py feature cart
    python create-module.py core analytics
    python create-module.py coredata auth
    python create-module.py app
    python create-module.py --dry-run feature cart
    python create-module.py --reset-config
"""

import os, sys, re, json, argparse

# ── ANSI colors ───────────────────────────────────────────────────────────────
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

# ── UI helpers ────────────────────────────────────────────────────────────────
def banner(pkg, root):
    print(f"{CYAN}{BOLD}")
    print("  ╔══════════════════════════════════════════╗")
    print("  ║       🤖  base_mvvm Module Creator       ║")
    print("  ╚══════════════════════════════════════════╝")
    print(RESET)
    print(f"  {gray('Package:')} {cyan(pkg)}")
    print(f"  {gray('Root   :')} {cyan(root)}")
    print()

def show_menu(title, options):
    print(f"  {bold(title)}")
    print(f"  {gray('─' * 52)}")
    for key, label in options:
        print(f"  {cyan(bold('[' + key + ']'))}  {label}")
    print(f"  {gray('─' * 52)}")

def prompt(msg, default=None):
    hint = f" {gray('(' + str(default) + ')')}" if default is not None else ""
    try:
        val = input(f"  {YELLOW}▶ {msg}{hint}: {RESET}").strip()
        return val if val else (str(default) if default is not None else "")
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {gray('Tạm biệt! 👋')}\n")
        sys.exit(0)

def confirm(msg):
    return prompt(msg + f" {gray('(y/n)')}").lower() in ("y", "yes", "co", "có")

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
    print("  ╔══════════════════════════════════════════╗")
    print("  ║         ⚙️   Cấu hình lần đầu            ║")
    print("  ╚══════════════════════════════════════════╝")
    print(RESET)

    up_one = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
    if os.path.exists(os.path.join(up_one, "settings.gradle.kts")):
        guessed_root = up_one
    elif os.path.exists(os.path.join(os.getcwd(), "settings.gradle.kts")):
        guessed_root = os.getcwd()
    else:
        guessed_root = up_one

    print(f"  {bold('📁 Project root')} — thư mục chứa settings.gradle.kts")
    root_input = prompt("Project root", default=guessed_root)
    root = os.path.normpath(os.path.expanduser(root_input))

    settings_path = os.path.join(root, "settings.gradle.kts")
    if not os.path.exists(settings_path):
        print(f"\n  {red('⚠️  Không tìm thấy settings.gradle.kts tại:')} {root}")
        print(f"  {yellow('Tiếp tục nhưng sẽ không update settings tự động.')}\n")

    print()
    print(f"  {bold('📦 Base package')} — package gốc (vd: com.example.myapp)")
    print(f"  {gray('Lưu ý: đây là package dùng cho mọi module, nhập đúng ngay từ đầu.')}")
    pkg = prompt("Base package")
    while not pkg or not re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,}', pkg):
        print(f"  {red('Package không hợp lệ — ví dụ: com.example.myapp')}")
        pkg = prompt("Base package")

    cfg = {"base_package": pkg, "project_root": root}
    save_config(cfg)
    print(f"\n  {green('✅ Đã lưu config')} → {gray(os.path.relpath(CONFIG_FILE))}\n")
    return cfg

# ── File helpers ──────────────────────────────────────────────────────────────
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

def add_to_settings(root: str, line: str, dry_run: bool = False):
    settings = os.path.join(root, "settings.gradle.kts")
    if not os.path.exists(settings):
        print(f"    {red('✗')} settings.gradle.kts không tìm thấy tại: {settings}")
        return
    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()
    if line in content:
        print(f"    {yellow('~')} settings đã có: {line}")
        return
    if dry_run:
        print(f"    {yellow('[dry]')} settings.gradle.kts ← {line}")
        return
    with open(settings, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"\n{line}")
    print(f"    {green('+')} settings.gradle.kts ← {line}")

# ── [1] Feature module ────────────────────────────────────────────────────────
def create_feature(name: str, cfg: dict, dry_run: bool = False):
    pkg_base      = cfg["base_package"]
    root          = cfg["project_root"]
    pascal        = to_pascal(name)
    pkg           = f"{pkg_base}.feature.{name}"
    pkg_path      = pkg.replace(".", "/")
    mod_dir       = os.path.join(root, "features", name)
    src           = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    test_src      = os.path.join(mod_dir, "src", "test", "java", pkg_path)
    data_pkg      = f"{pkg}.data"
    data_pkg_path = data_pkg.replace(".", "/")
    data_src      = os.path.join(src, "data")          # thư mục trong cùng module
    data_test_src = os.path.join(test_src, "data")

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module features:' + name + ' đã tồn tại!')}\n")
        return

    print(f"\n  {bold('📦 Tạo files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.feature")
}}

android {{
    namespace = "{pkg}"
}}

dependencies {{
    // Thêm core modules khi cần:
    // implementation(project(":core:domain"))
    // implementation(project(":core:ui"))
    // implementation(project(":core:designsystem"))
    // implementation(project(":core:data:auth"))
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

    private fun setLoading(loading: Boolean) {{
        _uiState.update {{ it.copy(isLoading = loading) }}
    }}

    private fun setError(message: String?) {{
        _uiState.update {{ it.copy(error = message) }}
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

// Stateful — kết nối ViewModel, xử lý events
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

// Stateless — dễ preview và test UI
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
        val state = viewModel.uiState.value
        assert(!state.isLoading)
        assert(state.error == null)
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

    # ── data/ folder — thư mục trong cùng src/main, cùng module ──────────────
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

    write_file(os.path.join(data_test_src, "repository", f"{pascal}RepositoryTest.kt"), f"""\
package {data_pkg}.repository

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

class {pascal}RepositoryTest {{

    private lateinit var repository: {pascal}RepositoryImpl

    @Before
    fun setUp() {{
        repository = {pascal}RepositoryImpl()
    }}

    @Test
    fun `placeholder test`() = runTest {{
        // TODO
    }}
}}
""", root, dry_run)

    add_to_settings(root, f'include(":features:{name}")', dry_run)

    impl = f'implementation(project(":features:{name}"))'
    imp1 = f'import {pkg}.navigation.{name}Screen'
    imp2 = f'import {pkg}.navigation.navigateTo{pascal}'
    nav  = f'{name}Screen(onNavigateBack = {{ navController.popBackStack() }})'

    tag = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('✅')}"
    print()
    print(f"{tag} Feature {bold(name)} {'preview' if dry_run else 'tạo xong!'}")
    print()
    print(f"  {bold('📋 Bước tiếp theo:')}")
    print(f"  1. {cyan('app/build.gradle.kts')}: {gray(impl)}")
    print(f"  2. {cyan('AppNavHost.kt')}:")
    print(f"     {gray(imp1)}")
    print(f"     {gray(imp2)}")
    print(f"     {gray(nav)}")
    print()

# ── [2] Core module ───────────────────────────────────────────────────────────
def create_core(name: str, cfg: dict, dry_run: bool = False):
    pkg_base = cfg["base_package"]
    root     = cfg["project_root"]
    pascal   = to_pascal(name)
    pkg      = f"{pkg_base}.core.{name}"
    pkg_path = pkg.replace(".", "/")
    mod_dir  = os.path.join(root, "core", name)
    src      = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    test_src = os.path.join(mod_dir, "src", "test", "java", pkg_path)

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module core:' + name + ' đã tồn tại!')}\n")
        return

    print(f"\n  {bold('📦 Tạo files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.library")
    // id("base.android.hilt")  // bỏ comment nếu module này cần DI
}}

android {{
    namespace = "{pkg}"
}}

dependencies {{
    // Thêm deps khi cần.
}}
""", root, dry_run)

    # src/main — placeholder để tạo thư mục đúng cấu trúc
    write_file(os.path.join(src, f"{pascal}.kt"), f"""\
package {pkg}

// TODO: thêm code cho module {name}
""", root, dry_run)

    write_file(os.path.join(test_src, f"{pascal}Test.kt"), f"""\
package {pkg}

import org.junit.Test

class {pascal}Test {{

    @Test
    fun `placeholder test`() {{
        // TODO
    }}
}}
""", root, dry_run)

    add_to_settings(root, f'include(":core:{name}")', dry_run)

    tag  = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('✅')}"
    impl = f'implementation(project(":core:{name}"))'
    print()
    print(f"{tag} Core module {bold(name)} {'preview' if dry_run else 'tạo xong!'}")
    print(f"  {gray(impl)}")
    print()

# ── [3] Core data module (shared) ─────────────────────────────────────────────
def create_core_data(name: str, cfg: dict, dry_run: bool = False):
    pkg_base = cfg["base_package"]
    root     = cfg["project_root"]
    pascal   = to_pascal(name)
    pkg      = f"{pkg_base}.core.data.{name}"
    pkg_path = pkg.replace(".", "/")
    mod_dir  = os.path.join(root, "core", "data", name)
    src      = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    test_src = os.path.join(mod_dir, "src", "test", "java", pkg_path)

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module core:data:' + name + ' đã tồn tại!')}\n")
        return

    print(f"\n  {bold('📦 Tạo files...')}\n")

    write_file(os.path.join(mod_dir, "build.gradle.kts"), f"""\
plugins {{
    id("base.android.data")
}}

android {{
    namespace = "{pkg}"
}}

dependencies {{
    // Thêm deps khi cần:
    // implementation(project(":core:domain"))
    // implementation(project(":core:common"))
}}
""", root, dry_run)

    write_file(os.path.join(src, "repository", f"{pascal}Repository.kt"), f"""\
package {pkg}.repository

interface {pascal}Repository {{
    // TODO: suspend fun / Flow
}}
""", root, dry_run)

    write_file(os.path.join(src, "repository", f"{pascal}RepositoryImpl.kt"), f"""\
package {pkg}.repository

import javax.inject.Inject

class {pascal}RepositoryImpl @Inject constructor() : {pascal}Repository {{
    // TODO: implement
}}
""", root, dry_run)

    write_file(os.path.join(src, "di", f"{pascal}DataModule.kt"), f"""\
package {pkg}.di

import {pkg}.repository.{pascal}Repository
import {pkg}.repository.{pascal}RepositoryImpl
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

    write_file(os.path.join(test_src, "repository", f"{pascal}RepositoryTest.kt"), f"""\
package {pkg}.repository

import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test

class {pascal}RepositoryTest {{

    private lateinit var repository: {pascal}RepositoryImpl

    @Before
    fun setUp() {{
        repository = {pascal}RepositoryImpl()
    }}

    @Test
    fun `placeholder test`() = runTest {{
        // TODO
    }}
}}
""", root, dry_run)

    add_to_settings(root, f'include(":core:data:{name}")', dry_run)

    tag  = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('✅')}"
    impl = f'implementation(project(":core:data:{name}"))'
    print()
    print(f"{tag} Core data module {bold(name)} {'preview' if dry_run else 'tạo xong!'}")
    print(f"  {gray(impl)}")
    print()

# ── [4] App module ────────────────────────────────────────────────────────────
def create_app(name: str, cfg: dict, dry_run: bool = False):
    pkg_base = cfg["base_package"]
    root     = cfg["project_root"]
    # Package cho app module: lấy 2 phần đầu của base_package + name
    # vd: base_package=com.xxx.app, name=app1 → com.xxx.app1
    pkg_parts = pkg_base.split(".")
    pkg       = ".".join(pkg_parts[:2]) + f".{name}"
    pkg_path = pkg.replace(".", "/")
    mod_dir  = os.path.join(root, name)
    src      = os.path.join(mod_dir, "src", "main", "java", pkg_path)
    res      = os.path.join(mod_dir, "src", "main", "res")

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module :' + name + ' đã tồn tại!')}\n")
        return

    print(f"\n  {bold('📦 Tạo files...')}\n")

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
    // ── Core modules — thêm khi cần ──────────────────────────────────
    // implementation(project(":core:common"))
    // implementation(project(":core:domain"))
    // implementation(project(":core:ui"))
    // implementation(project(":core:designsystem"))

    // ── Shared data — thêm khi cần ────────────────────────────────────
    // implementation(project(":core:data:auth"))
    // implementation(project(":core:data:user"))

    // ── Feature modules — thêm khi cần ───────────────────────────────
    // implementation(project(":features:home"))

    // base.android.app đã tự động thêm:
    // Compose BOM + UI + Activity, Navigation, Hilt, test libs
}}
""", root, dry_run)

    # keystore.properties mẫu — chỉ tạo nếu chưa có (đặt ở root, KHÔNG commit git)
    keystore_file = os.path.join(root, "keystore.properties")
    if not dry_run and not os.path.exists(keystore_file):
        write_file(keystore_file, """\
# ⚠️  KHÔNG COMMIT FILE NÀY LÊN GIT — thêm vào .gitignore
#
# Hướng dẫn tạo keystore:
#   keytool -genkey -v -keystore keystore/release.jks -alias my-key -keyalg RSA -keysize 2048 -validity 10000
#
RELEASE_STORE_FILE=keystore/release.jks
RELEASE_STORE_PASSWORD=your_store_password
RELEASE_KEY_ALIAS=your_key_alias
RELEASE_KEY_PASSWORD=your_key_password
""", root, dry_run)
    elif dry_run:
        print(f"    {yellow('[dry]')} keystore.properties (root)")
    else:
        print(f"    {yellow('~')} keystore.properties đã tồn tại, bỏ qua")

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
        startDestination = "home", // TODO: thay bằng route thực
    ) {{
        // TODO: thêm destinations ở đây
        // homeScreen(onNavigateBack = {{ navController.popBackStack() }})
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
        android:theme="@style/Theme.BaseMvvm">

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
    <style name="Theme.BaseMvvm" parent="android:Theme.DeviceDefault.Light.NoActionBar">
        <!-- Không cần gì thêm — Compose tự vẽ toàn bộ UI -->
    </style>
</resources>
""", root, dry_run)

    write_file(os.path.join(mod_dir, "proguard-rules.pro"),
               "# Add project specific ProGuard rules here.\n", root, dry_run)

    add_to_settings(root, f'include(":{name}")', dry_run)

    tag = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('✅')}"
    print()
    print(f"{tag} Module {bold(name)} {'preview' if dry_run else 'tạo xong!'}")
    print(f"  {gray('Package:')} {cyan(pkg_base)}")
    print()

# ── Interactive menu ──────────────────────────────────────────────────────────
def run_menu(cfg: dict):
    clear()
    banner(cfg["base_package"], cfg["project_root"])

    while True:
        show_menu("Chọn loại module:", [
            ("1", "module    — :{name} (MainActivity + NavHost + Application)  vd: app, app1"),
            ("2", "core      — Library (shared utility, không có Hilt mặc định)"),
            ("3", "feature   — Screen + ViewModel + State + Navigation + data/"),
            ("4", "libjar    — Kotlin library thuần, build ra .jar, có Main.kt"),
            ("5", "coredata  — core/data/{name}: shared Repository (auth, user, settings…)"),
            ("c", "config    — Đổi package / root dir"),
            ("0", "exit      — Thoát"),
        ])
        print()
        choice = prompt("Nhập lựa chọn")

        if choice in ("0", "q", "exit"):
            print(f"\n  {gray('Tạm biệt! 👋')}\n")
            sys.exit(0)

        if choice == "c":
            cfg = setup_config(force=True)
            clear()
            banner(cfg["base_package"], cfg["project_root"])
            continue

        # App module — nhập tên (app, app1, app2, …)
        if choice == "1":
            print()
            while True:
                raw = prompt(f"Tên module {cyan('module')} (vd: app, app1, app2)")
                if not raw:
                    print(f"  {red('Tên không được để trống.')}")
                    continue
                name = validate_name(raw)
                if not name:
                    print(f"  {red('Tên không hợp lệ — chỉ dùng chữ thường, số, dấu _')}")
                    continue
                break
            print()
            _parts   = cfg["base_package"].split(".")
            _pkg_prev = ".".join(_parts[:2]) + f".{name}"
            print(f"  {bold('Preview:')}")
            print(f"  {gray('Module  :')} :{name}")
            print(f"  {gray('Package :')} {_pkg_prev}")
            print(f"  {gray('Files   :')} App.kt · MainActivity.kt · AppNavHost.kt · AndroidManifest.xml")
            print()
            if confirm("Xác nhận tạo?"):
                create_app(name, cfg)
            else:
                print(f"\n  {yellow('Đã huỷ.')}\n")
            input("\nEnter to continue...")
            clear()
            banner(cfg["base_package"], cfg["project_root"])
            continue

        if choice not in ("2", "3", "4", "5"):
            print(f"  {red('Lựa chọn không hợp lệ.')}\n")
            continue

        type_map = {"2": "core", "3": "feature", "4": "libjar", "5": "coredata"}
        module_type = type_map[choice]
        examples    = {"core": "analytics", "feature": "cart", "libjar": "socket_utils", "coredata": "auth"}

        print()
        while True:
            raw = prompt(f"Tên module {cyan(module_type)} (vd: {examples[module_type]})")
            if not raw:
                print(f"  {red('Tên không được để trống.')}")
                continue
            name = validate_name(raw)
            if not name:
                print(f"  {red('Tên không hợp lệ — chỉ dùng chữ thường, số, dấu _')}")
                continue
            break

        pascal = to_pascal(name)
        pkg    = cfg["base_package"]

        print()
        print(f"  {bold('Preview:')}")
        if module_type == "feature":
            print(f"  {gray('Module  :')} :features:{name}")
            print(f"  {gray('Data    :')} features/{name}/src/main/java/.../data/ (cùng module)")
            print(f"  {gray('Package :')} {pkg}.feature.{name}")
            print(f"  {gray('UI      :')} {pascal}UiState · {pascal}ViewModel · {pascal}Route · {pascal}Screen · {pascal}Navigation")
            print(f"  {gray('Data    :')} {pascal}Repository · {pascal}RepositoryImpl · {pascal}DataModule")
        elif module_type == "core":
            print(f"  {gray('Module  :')} :core:{name}")
            print(f"  {gray('Package :')} {pkg}.core.{name}")
            print(f"  {gray('Files   :')} {pascal}.kt (placeholder)")
        elif module_type == "libjar":
            print(f"  {gray('Module  :')} :libs:{name}")
            print(f"  {gray('Package :')} {pkg}.lib.{name}")
            print(f"  {gray('Files   :')} Main.kt · {pascal}.kt (Kotlin JVM only, no Android)")
        else:
            print(f"  {gray('Module  :')} :core:data:{name}")
            print(f"  {gray('Package :')} {pkg}.core.data.{name}")
            print(f"  {gray('Files   :')} {pascal}Repository · {pascal}RepositoryImpl · {pascal}DataModule")
        print()

        if not confirm("Xác nhận tạo?"):
            print(f"\n  {yellow('Đã huỷ.')}\n")
        else:
            dispatch(module_type, name, cfg, dry_run=False)

        input("\nEnter to continue...")
        clear()
        banner(cfg["base_package"], cfg["project_root"])

# ── [5] Kotlin library module (.jar) ─────────────────────────────────────────
def create_libjar(name: str, cfg: dict, dry_run: bool = False):
    """
    Tạo Kotlin-only library module, build ra .jar (không có Android deps).
    Dùng cho: shared utils, SDK thuần Kotlin, công cụ CLI, protocol buffers...
    """
    pkg_base = cfg["base_package"]
    root     = cfg["project_root"]
    pascal   = to_pascal(name)
    pkg      = f"{pkg_base}.lib.{name}"
    pkg_path = pkg.replace(".", "/")
    mod_dir  = os.path.join(root, "libs", name)
    src      = os.path.join(mod_dir, "src", "main", "kotlin", pkg_path)
    test_src = os.path.join(mod_dir, "src", "test", "kotlin", pkg_path)

    if not dry_run and os.path.exists(mod_dir):
        print(f"\n  {red('Module libs:' + name + ' đã tồn tại!')}\n")
        return

    print(f"\n  {bold('📦 Tạo files...')}\n")

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
    // Thuần Kotlin — không có Android deps.
    // Thêm khi cần, ví dụ:
    // implementation(libs.kotlinx.serialization.json)
    // implementation(libs.coroutines.android)

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}}

// Build executable jar (optional — bỏ comment nếu cần chạy standalone)
// tasks.jar {{
//     manifest {{ attributes["Main-Class"] = "{pkg}.MainKt" }}
//     from(configurations.runtimeClasspath.get().map {{ if (it.isDirectory) it else zipTree(it) }})
//     duplicatesStrategy = DuplicatesStrategy.EXCLUDE
// }}
""", root, dry_run)

    write_file(os.path.join(src, "Main.kt"), f"""\
package {pkg}

fun main() {{
    println("Hello from {pascal}!")
}}
""", root, dry_run)

    write_file(os.path.join(src, f"{pascal}.kt"), f"""\
package {pkg}

object {pascal} {{
    // TODO: thêm logic cho library {name}
}}
""", root, dry_run)

    write_file(os.path.join(test_src, f"{pascal}Test.kt"), f"""\
package {pkg}

import org.junit.Test

class {pascal}Test {{

    @Test
    fun `placeholder test`() {{
        // TODO
    }}
}}
""", root, dry_run)

    add_to_settings(root, f'include(":libs:{name}")', dry_run)

    impl = f'implementation(project(":libs:{name}"))'
    tag  = f"  {yellow('[DRY RUN]')}" if dry_run else f"  {green('✅')}"
    print()
    print(f"{tag} Lib jar {bold(name)} {'preview' if dry_run else 'tạo xong!'}")
    print(f"  {gray(impl)}")
    print()

# ── Dispatch ──────────────────────────────────────────────────────────────────
def dispatch(module_type: str, name, cfg: dict, dry_run: bool):
    if module_type == "feature":
        create_feature(name, cfg, dry_run)
    elif module_type == "core":
        create_core(name, cfg, dry_run)
    elif module_type == "coredata":
        create_core_data(name, cfg, dry_run)
    elif module_type == "module":
        create_app(name, cfg, dry_run)
    elif module_type == "libjar":
        create_libjar(name, cfg, dry_run)
    else:
        print(red(f"Loại không hợp lệ: '{module_type}'"))
        sys.exit(1)

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="create-module",
        description="Tạo nhanh Android MVVM module.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create-module.py
  python create-module.py feature cart
  python create-module.py core analytics
  python create-module.py coredata auth
  python create-module.py app
  python create-module.py --dry-run feature cart
  python create-module.py --reset-config
""",
    )
    parser.add_argument("module_type", nargs="?",
                        choices=["module", "core", "feature", "libjar", "coredata"],
                        help="Loại module")
    parser.add_argument("name", nargs="?",
                        help="Tên module (snake_case) — không dùng cho app")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview danh sách file, không ghi thực")
    parser.add_argument("--reset-config", action="store_true",
                        help="Xoá config cũ, chạy lại setup wizard")

    args = parser.parse_args()
    cfg  = setup_config(force=args.reset_config)

    if args.module_type:
        if args.module_type == "module":
            if not args.name:
                print(red("Thiếu tên module cho loại 'module'."))
                sys.exit(1)
            name = validate_name(args.name)
            if not name:
                print(red(f"Tên không hợp lệ: '{args.name}'"))
                sys.exit(1)
            create_app(name, cfg, dry_run=args.dry_run)
            return
        if not args.name:
            print(red(f"Thiếu tên module cho loại '{args.module_type}'."))
            parser.print_help()
            sys.exit(1)
        name = validate_name(args.name)
        if not name:
            print(red(f"Tên không hợp lệ: '{args.name}'"))
            sys.exit(1)
        dispatch(args.module_type, name, cfg, dry_run=args.dry_run)
        return

    if args.dry_run:
        print(red("--dry-run yêu cầu cung cấp module_type."))
        parser.print_help()
        sys.exit(1)

    run_menu(cfg)

if __name__ == "__main__":
    main()
