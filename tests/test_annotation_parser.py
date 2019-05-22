import unittest

from historic_hebrew_dates.annotation_parser import get_patterns

class TestAnnotationParser(unittest.TestCase):
    def test_parse(self):
        patterns = get_patterns(
            'Deze tekst is geschreven op de {{22}(dag)e van de maand {mei}(maand) in het jaar {2019}(jaar)}(datum)',
            {
                'dag': 'nummer',
                'jaar': 'nummer'
            })

        self.assertListEqual(
            patterns,
            [('datum', 'datum', 'datum', '{dag:nummer}e van de maand {maand} in het jaar {jaar:nummer}'),
             ('datum', 'dag', 'nummer', '22'),
             ('datum', 'maand', 'maand', 'mei'),
             ('datum', 'jaar', 'nummer', '2019')]
        )
