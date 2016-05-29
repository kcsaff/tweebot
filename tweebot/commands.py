from collections import namedtuple
import argparse
import sys
from tweebot.client import TwitterClient
from tweebot.console import Console


Directives = namedtuple('Directives', ['filename', 'directive'])


DEFAULT_DIRECTIVE = ']'


import pkg_resources
try:
    VERSION = pkg_resources.require("tweebot")[0].version
except:
    VERSION = 'DEV'


def make_parser(parser=None, subparsers=None):
    if parser is None:
        parser = argparse.ArgumentParser(
            description='Tweebot: A simple twitter bot\n  Version {}'.format(VERSION),
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
    if subparsers is None:
        subparsers = parser.add_subparsers()

    parser.add_argument(
        '--keys', '-k', type=str,
        help='Keys file needed to post to Twitter',
    )
    parser.add_argument(
        '--verbose', '-v', action='count',
        help='More v\'s, more verbose'
    )
    parser.add_argument(
        '--version', action='store_true',
        help='Print version ({}) and exit'.format(VERSION)
    )

    tweet_parser = subparsers.add_parser('tweet', help='Tweet a status update')
    _make_pipeline_parser(tweet_parser, 'tweet')
    tweet_parser.set_defaults(handler=do_tweet)

    print_parser = subparsers.add_parser('print', help='Print a status update without sending -- can be piped')
    _make_pipeline_parser(print_parser, 'print')
    print_parser.set_defaults(handler=do_print)

    follow_parser = subparsers.add_parser('follow', help='Follow users, or auto follow your followers')
    follow_parser.add_argument(
        'user_ids', type=str, nargs='*',
        help='User ids to follow'
    )
    follow_parser.add_argument(
        '--auto', '-A', action='store_true',
        help='Auto-follow your followers, unfollow unfollowers'
    )
    follow_parser.set_defaults(handler=do_follow)

    return parser


def _make_pipeline_parser(parser, verb):
    parser.add_argument(
        'status', type=str, nargs='*',
        help='Text status to {verb}: "enclose multiple words in quotes", use - to pipe input'
        .format(verb=verb)
    )
    parser.add_argument(
        '--filename', '-f', type=str, default=None,
        help='Path to image/media file to {verb}, if any'.format(verb=verb)
    )
    parser.add_argument(
        '--directive', '-D', type=str, default=DEFAULT_DIRECTIVE,
        help=('Escape sequence that, when appearing at the beginning of a status line, modifies {verb} arguments,' +
              ' allowing for example setting the media filename from within the status text').format(verb=verb)
    )


def loads_status(status, directives):
    """
    Returns status and dict of directives from status string and directive info.

    :param args:  Parsed args
    :return: tuple of (status string, directive dict)
    """
    if status == '-':
        status = sys.stdin.read()

    if directives.directive:
        status_lines = list()
        for line in status.splitlines(True):
            stripped = line.strip()
            if directives.directive and stripped.startswith(directives.directive) and value:
                arg, value = stripped[len(directives.directive):].split(None, 1)
                directives = directives._replace(**{arg: value})
            else:
                status_lines.append(line)
        status = ''.join(status_lines)

    return status, directives


def dumps_status(status, directives):
    initial_directive = DEFAULT_DIRECTIVE
    directive = initial_directive
    for line in status.splitlines(True):
        while line.startswith(directive):
            directive += DEFAULT_DIRECTIVE

    status_lines = list()
    if initial_directive != directive:
        status_lines.append('{}directive {}\n'.format(initial_directive, directive))

    for key, value in sorted(directives._asdict().items()):
        if key != 'directive' and value:
            status_lines.append('{}{} {}\n'.format(directive, key, value))

    status_lines.append(status)

    return ''.join(status_lines)


def generate_status(args, generators=()):
    status, directives = loads_status(' '.join(args.status), Directives(args.filename, args.directive))
    for generator in generators:
        generated = generator(status, directives)
        if isinstance(generated, dict):
            status = generated.pop('status')
            directives = generated
        elif isinstance(generated, tuple):
            status, directives = generated
        else:
            status, directives = loads_status(generated, directives)

    return status, directives


def do_tweet(args, generators=()):
    status, directives = generate_status(args, generators)

    client = TwitterClient(args.keys, console=Console(args.verbose))
    client.tweet(status, filename=directives.filename)


def do_print(args, generators=()):
    status, directives = generate_status(args, generators)
    print(dumps_status(status, directives))


def do_follow(args, generator=None):
    client = TwitterClient(args.keys, console=Console(args.verbose))
    if args.user_ids:
        raise NotImplementedError('Haven\'t implemented individual follows yet')
    if args.auto:
        client.autofollow()


def main(
        generators=()
):
    parser = make_parser()
    args = parser.parse_args()
    if args.version:
        print(VERSION)
        return
    if callable(generators):
        generators = [generators]

    parser.handler(args, generators)

if __name__ == '__main__':
    main()
