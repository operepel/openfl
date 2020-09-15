
from subprocess import run, PIPE
from importlib  import import_module
from socket     import getfqdn
from click      import Group, CommandCollection, Choice, Path as ClickPath
from click      import group, command, argument, option, pass_context
from click      import clear, echo, style, progressbar
from sys        import path
from time       import sleep
from shutil     import copyfile, ignore_patterns
from logging    import getLogger, basicConfig
from pathlib    import Path
from itertools  import islice
from os import environ

SITEPACKS = Path(__file__).parent.parent.parent
WORKSPACE = SITEPACKS / 'fledge-workspace'
PKI_DIR   = Path('cert')

def pretty(o):
    m = max(map(len, o.keys()))

    for k,v in o.items():
        echo(style(f'{k:<{m}} : ', fg = 'blue') + style(f'{v}', fg = 'cyan'))

def vex(command, workdir = '.', env = None, expectcode = 0):
    if env:
        env = {**environ.copy(), **env}
    r = run(command, shell = True, cwd = workdir, stdout = PIPE, stderr = PIPE, universal_newlines = True, env = env)

    if  r.returncode != expectcode:
        echo('\n💔 ' + style(command, fg = 'red'))
        echo(style(r.stdout, fg = 'yellow'))
        echo(style(r.stderr, fg = 'yellow'))

        exit()

def tree(path):

    echo(f'+ {path}')

    for path in sorted(path.rglob('*')):

        depth = len(path.relative_to(path).parts)
        space = '    ' * depth

        if  path.is_file() : echo(f'{space}f {path.name}')
        else               : echo(f'{space}d {path.name}')

def print_tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False, length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""

    space  = '    '
    branch = '│   '
    tee    = '├── '
    last   = '└── '

    echo(f'\nNew workspace directory structure:')

    dir_path = Path(dir_path) # accept string coerceable to Path
    files = 0
    directories = 0
    def inner(dir_path: Path, prefix: str='', level=-1):
        nonlocal files, directories
        if not level:
            return # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path,prefix = prefix+extension,level = level-1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1
    echo(dir_path.name)
    iterator = inner(dir_path,level = level)
    for line in islice(iterator, length_limit):
        echo(line)
    if next(iterator, None):
        echo(f'... length_limit, {length_limit}, reached, counted:')
    echo(f'\n{directories} directories' + (f', {files} files' if files else ''))

def copytree(src, dst, symlinks = False, ignore = None, ignore_dangling_symlinks = False, dirs_exist_ok = False):
    """From Python 3.8 'shutil' which include 'dirs_exist_ok' option"""

    import os
    import shutil

    with os.scandir(src) as itr: entries = list(itr)

    copy_function = shutil.copy2

    def _copytree():

        if ignore is not None: ignored_names = ignore(os.fspath(src), [x.name for x in entries])
        else                 : ignored_names = set()

        os.makedirs(dst, exist_ok = dirs_exist_ok)
        errors = []
        use_srcentry = copy_function is shutil.copy2 or copy_function is shutil.copy

        for srcentry in entries:
            if  srcentry.name in ignored_names:
                continue
            srcname = os.path.join(src, srcentry.name)
            dstname = os.path.join(dst, srcentry.name)
            srcobj = srcentry if use_srcentry else srcname
            try:
                is_symlink = srcentry.is_symlink()
                if  is_symlink and os.name == 'nt':
                    lstat = srcentry.stat(follow_symlinks = False)
                    if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                        is_symlink = False
                if  is_symlink:
                    linkto = os.readlink(srcname)
                    if  symlinks:
                        os.symlink(linkto, dstname)
                        shutil.copystat(srcobj, dstname, follow_symlinks = not symlinks)
                    else:
                        if  not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        if  srcentry.is_dir():
                            copytree(srcobj, dstname, symlinks, ignore, dirs_exist_ok = dirs_exist_ok)
                        else:
                            copy_function(srcobj, dstname)
                elif srcentry.is_dir():
                    copytree(srcobj, dstname, symlinks, ignore, dirs_exist_ok = dirs_exist_ok)
                else:
                    copy_function(srcobj, dstname)
            except Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            if  getattr(why, 'winerror', None) is None:
                errors.append((src, dst, str(why)))
        if  errors:
            raise Error(errors)
        return dst

    return _copytree()
