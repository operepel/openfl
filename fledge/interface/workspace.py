from cli_helper import *

from subprocess import check_call
from sys        import executable

@group()
@pass_context
def workspace(context):
    '''Manage Federated Learning Workspaces'''
    context.obj['group'] = 'workspace'

def create_dirs(context, prefix):

    echo(f'Creating Workspace Directories')

    (prefix / 'cert').mkdir(parents = True, exist_ok = True) # certifications
    (prefix / 'data').mkdir(parents = True, exist_ok = True) # training data
    (prefix / 'logs').mkdir(parents = True, exist_ok = True) # training logs
    (prefix / 'plan').mkdir(parents = True, exist_ok = True) # federated learning plans
    (prefix / 'save').mkdir(parents = True, exist_ok = True) # model weight saves / initialization
    (prefix / 'code').mkdir(parents = True, exist_ok = True) # model code

    src = WORKSPACE / 'workspace/plan/defaults' # from default workspace
    dst = prefix    /           'plan/defaults' #   to created workspace

    copytree(src = src, dst = dst, dirs_exist_ok = True)

def create_cert(context, prefix):

    echo(f'Creating Workspace Certifications')

    src = WORKSPACE  / 'workspace/cert/config' # from default workspace
    dst = prefix     /           'cert/config' #   to created workspace

    copytree(src = src, dst = dst, dirs_exist_ok = True)

def create_temp(context, prefix, template):

    echo(f'Creating Workspace Templates')

    copytree(src = WORKSPACE / template / 'code', dst = prefix / 'code', dirs_exist_ok = True, ignore = ignore_patterns('__pycache__')) # from template workspace
    copytree(src = WORKSPACE / template / 'plan', dst = prefix / 'plan', dirs_exist_ok = True, ignore = ignore_patterns('__pycache__')) # from template workspace

def get_templates():
    """
    Grab the default templates from the distribution
    """

    return [d.name for d in WORKSPACE.glob('*') if d.is_dir() and d.name not in ['__pycache__', 'workspace']]

@workspace.command()
@pass_context
@option('--prefix',   required = True, help = 'Workspace name or path', type = ClickPath())
@option('--template', required = True, type = Choice(get_templates()))
def create(context, prefix, template):
    """Create federated learning workspace"""

    prefix   = Path(prefix)
    template = Path(template)

    create_dirs(context, prefix)
    create_cert(context, prefix)
    create_temp(context, prefix, template)

    print_tree(prefix, level = 3)

@workspace.command(name = 'export')
@option('--include_certificates', required = False, help="Include PKI certificates", is_flag=True)
def export_(include_certificates):
    """Export federated learning workspace"""

    from shutil   import make_archive, copytree, ignore_patterns, rmtree
    from tempfile import mkdtemp
    from os       import getcwd
    from os.path  import basename, join

    requirements_filename = f'requirements.txt'

    with open(requirements_filename, "w") as f:
        check_call([executable, "-m", "pip", "freeze"], stdout=f)

    echo(f'{requirements_filename} written.')

    archiveType = 'zip'
    archiveName = basename(getcwd())
    archiveFileName = archiveName + '.' + archiveType

    # Aggregator workspace
    tmpDir = join(mkdtemp(), 'fledge', archiveName)

    if include_certificates:
        echo(style(f'WARNING:', fg='red', blink=True) + f' Including PKI certificates in export. This could be a security risk.')
        ignore = ignore_patterns('__pycache__')
    else:
        ignore = ignore_patterns('__pycache__', 'cert')

    copytree('.', tmpDir, ignore=ignore) # Copy the current directory into the temporary directory

    make_archive(archiveName, archiveType, tmpDir) # Create Zip archive of directory

    echo(f'Workspace exported to archive: {archiveFileName}')

@workspace.command(name = 'import')
@option('--file',   required = True, help = 'Zip file containing workspace to import', type = ClickPath(exists=True))
def import_(file):
    """Import federated learning workspace"""

    from shutil   import unpack_archive
    from os.path  import isfile, basename
    from os       import chdir
    
    dirPath = basename(file).split('.')[0]
    unpack_archive(file, extract_dir=dirPath)
    chdir(dirPath)

    requirements_filename = "requirements.txt"

    if isfile(requirements_filename):
        check_call([executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        echo("No " + requirements_filename + " file found.")

    echo(f'Workspace {file} has been imported.')
    echo(f'You may need to copy your PKI certificates to join the federation.')


@workspace.command()
@pass_context
def certify(context):
    '''Create certificate authority for federation'''

    echo('Setting Up Certificate Authority...\n')

    echo('1.  Create Root CA')
    echo('1.1 Create Directories')

    (PKI_DIR / 'ca/root-ca/private').mkdir(parents = True, exist_ok = True, mode = 0o700)
    (PKI_DIR / 'ca/root-ca/db'     ).mkdir(parents = True, exist_ok = True)

    echo('1.2 Create Database')

    with open(PKI_DIR / 'ca/root-ca/db/root-ca.db',      'w') as f: pass # write empty file
    with open(PKI_DIR / 'ca/root-ca/db/root-ca.db.attr', 'w') as f: pass # write empty file

    with open(PKI_DIR / 'ca/root-ca/db/root-ca.crt.srl', 'w') as f: f.write('01') # write file with '01'
    with open(PKI_DIR / 'ca/root-ca/db/root-ca.crl.srl', 'w') as f: f.write('01') # write file with '01'

    echo('1.3 Create CA Request')

    root_conf = 'config/root-ca.conf'
    root_csr  = 'ca/root-ca.csr'
    root_crt  = 'ca/root-ca.crt'
    root_key  = 'ca/root-ca/private/root-ca.key'

    vex(f'openssl req -new '
        f'-config {root_conf} '
        f'-out {root_csr} '
        f'-keyout {root_key}', workdir = PKI_DIR)

    echo('1.4 Create CA Certificate')

    vex(f'openssl ca -batch -selfsign '
        f'-config {root_conf} '
        f'-in {root_csr} '
        f'-out {root_crt} '
        f'-extensions root_ca_ext', workdir = PKI_DIR)

    echo('2.  Create Signing Certificate')
    echo('2.1 Create Directories')

    (PKI_DIR / 'ca/signing-ca/private').mkdir(parents = True, exist_ok = True, mode = 0o700)
    (PKI_DIR / 'ca/signing-ca/db'     ).mkdir(parents = True, exist_ok = True)

    echo('2.2 Create Database')

    with open(PKI_DIR / 'ca/signing-ca/db/signing-ca.db',      'w') as f: pass # write empty file
    with open(PKI_DIR / 'ca/signing-ca/db/signing-ca.db.attr', 'w') as f: pass # write empty file

    with open(PKI_DIR / 'ca/signing-ca/db/signing-ca.crt.srl', 'w') as f: f.write('01') # write file with '01'
    with open(PKI_DIR / 'ca/signing-ca/db/signing-ca.crl.srl', 'w') as f: f.write('01') # write file with '01'

    echo('2.3 Create Signing Certificate CSR')

    signing_conf = 'config/signing-ca.conf'
    root_conf    = 'config/root-ca.conf'
    signing_csr  = 'ca/signing-ca.csr'
    signing_crt  = 'ca/signing-ca.crt'
    signing_key  = 'ca/signing-ca/private/signing-ca.key'

    vex(f'openssl req -new '
        f'-config {signing_conf} '
        f'-out {signing_csr} '
        f'-keyout {signing_key}', workdir = PKI_DIR)

    echo('2.4 Sign Signing Certificate CSR')

    vex(f'openssl ca -batch '
        f'-config {root_conf} '
        f'-in {signing_csr} '
        f'-out {signing_crt} '
        f'-extensions signing_ca_ext', workdir = PKI_DIR)

    echo('3   Create Certificate Chain')

  # create certificate chain file by combining root-ca and signing-ca
    with open(PKI_DIR / 'cert_chain.crt', 'w') as d:
        with open(PKI_DIR / 'ca/root-ca.crt'   ) as s: d.write(s.read())
        with open(PKI_DIR / 'ca/signing-ca.crt') as s: d.write(s.read())

 
    echo('\nDone.')
