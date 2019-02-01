import logging
from django.core.management import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('begin', type=int)
    #     parser.add_argument('end', type=int)
    #     parser.add_argument('update', type=int)

    def handle(self, *args, **options):
        # begin = options.get('begin')
        # end = options.get('end')
        # update = options['update']
        # upgrade_asset_multi(begin, end, update)
        test()


def test():
    # raise(Exception('abcd'))
    return 10 / 0
