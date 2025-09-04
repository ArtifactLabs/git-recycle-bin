import argparse
import os

from .printer import printer

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def tuple1(key):
    def f(value):
        return (key, value)
    return f


def parse_args(args=None):
    class CustomHelpFormatter(argparse.HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, indent_increment=2, max_help_position=40)

    class keyvalue(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            my_dict = getattr(namespace, self.dest) or {}
            key, value = values
            my_dict[key] = value
            setattr(namespace, self.dest, my_dict)

    def ignore_attr_except(func, *args, **kwargs):
        # useful in case args should be patched
        try:
            return func(*args, **kwargs)
        except AttributeError:
            pass
    # top parser describes the options which should be available for all commands
    top_parser = argparse.ArgumentParser(description="Generic", add_help=False, formatter_class=CustomHelpFormatter)

    g = top_parser.add_argument_group('niche options')
    g.add_argument(               "--user-name",       metavar='fullname', required=False, type=str, default=os.getenv('GITRB_USERNAME'), help="Author of artifact commit. Defaults to yourself.")
    g.add_argument(               "--user-email",      metavar='address',  required=False, type=str, default=os.getenv('GITRB_EMAIL'),    help="Author's email of artifact commit. Defaults to your own.")
    dv = 'False';  g.add_argument("--rm-expired",      metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_RM_EXPIRED', dv), help=f"Delete expired artifact branches. Default {dv}.")
    dv = 'False';  g.add_argument("--flush-meta",      metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_RM_FLUSH_META', dv), help=f"Delete expired meta-for-commit refs. Default {dv}.")
    dv = 'origin'; g.add_argument("--src-remote-name", metavar='name',     required=False, type=str, default=os.getenv('GITRB_SRC_REMOTE', dv), help=f"Name of src repo's remote. Defaults {dv}.")
    dv = 'True' ;  g.add_argument("--rm-tmp",          metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_RM_TMP', dv), help=f"Remove local bin-repo. Default {dv}.")

    g = top_parser.add_argument_group('terminal output style')
    g.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit.")
    g.add_argument('-v', '--verbose', action='count', dest='verbosity', default=1, help="Increase output verbosity. Can be repeated, e.g. -vv.")
    g.add_argument('-q', '--quiet', action='store_const', dest='verbosity', const=0, help="Suppress output.")
    dv = 'True' ;  g.add_argument("--color", metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_COLOR', dv), help=f"Colorized output. Default {dv}.")

    parser = argparse.ArgumentParser(description="Create and push artifacts in git - with expiry and traceability.", parents=[top_parser], add_help=False)

    commands = parser.add_subparsers(dest='command')
    commands.required = True
    g = commands.add_parser("push", parents=[top_parser], add_help=False, help="push artifact")
    g.add_argument(                   "remote",                   metavar='URL', type=str, help="Git remote URL")
    g.add_argument(                   "--path",                   metavar='file|dir', required=True,  type=str, default=os.getenv('GITRB_PATH'),       help="Path to artifact in src-repo. Directory or file.")
    g.add_argument(                   "--name",                   metavar='string',   required=True,  type=str, default=os.getenv('GITRB_NAME'),       help="Name to assign to the artifact. Will be sanitized.")
    dv = 'in 30 days'; g.add_argument("--expire",                 metavar='fuzz',     required=False, type=str, default=os.getenv('GITRB_EXPIRE', dv), help=f"Expiry of artifact's branch. Fuzzy date. Default '{dv}'.")
    dv = 'False';      g.add_argument("--tag",  dest='push_tag',  metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_PUSH_TAG', dv), help=f"Push tag to artifact to remote. Default {dv}.")
    dv = 'False';      g.add_argument("--note", dest='push_note', metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_PUSH_NOTE', dv),     help=f"Push note to src remote. Default {dv}.")
    dv = 'False';      g.add_argument("--add-ignored",            metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_ADD_IGNORED', dv), help=f"Add despite gitignore. Default {dv}.")
    dv = 'False';      g.add_argument("--force-branch",           metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_FORCE_BRANCH', dv), help=f"Force push of branch. Default {dv}.")
    dv = 'False';      g.add_argument("--force-tag",              metavar='bool', type=str2bool, nargs='?', const=True, default=os.getenv('GITRB_FORCE_TAG', dv), help=f"Force push of tag. Default {dv}.")
    g.add_argument("--trailer", nargs=2, metavar=('key', 'value'), dest='trailers', action=keyvalue, default={}, help="Add trailer to commit. Can be specified multiple times.")

    g = commands.add_parser("clean", parents=[top_parser], add_help=False, help="clean expired artifacts")
    g.add_argument("remote", metavar='URL', type=str, help="Git remote URL")

    g = commands.add_parser("list", parents=[top_parser], add_help=False, help="list artifacts")
    g.add_argument("remote", metavar='URL', type=str, help="Git remote URL")
    g.add_argument("--all", action='store_true', dest='list_all_shas', default=False, help="List all artifacts, regardless of HEAD sha")
    query = g.add_mutually_exclusive_group()
    opt="path"; query.add_argument(f"--{opt}", dest='query', metavar='file|dir', required=False, type=tuple1(opt), default=os.getenv('GITRB_PATH'), help="Path to artifact in src-repo. Directory or file.")
    opt="name"; query.add_argument(f"--{opt}", dest='query', metavar='string',   required=False, type=tuple1(opt), default=os.getenv('GITRB_NAME'), help="Name of artifact, as specified in the meta-data. Will be sanitized.")

    g = commands.add_parser("download", parents=[top_parser], add_help=False, help="download artifact")
    g.add_argument("remote", metavar='URL', type=str, help="Git remote URL")
    g.add_argument("artifacts", metavar='artifact', nargs='+', type=str, help="Artifact SHA(s) to download")
    g.add_argument("--force", "-f", action='store_true', help="Force download, even if local files ")

    args = parser.parse_args(args)

    def patch_query(args):
        if args.query is None:
            args.query = ("none", None)

    ignore_attr_except(patch_query, args)

    printer.verbosity = args.verbosity
    printer.colorize = args.color

    # Sanity-check
    try:
        if args.force_tag and not args.force_branch:
            printer.error("Error: `--force-tag` requires `--force-branch`")
            return None
    except AttributeError:
        pass

    try:
        args.remote
    except AttributeError:
        printer.error("Error: command is missing a remote argument, contact maintainers")
        return None

    return args
