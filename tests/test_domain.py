import copy, json, unittest
from pathlib import Path
from cryptolab import analyze

EXAMPLE = json.loads(Path("examples/input.json").read_text())
EXPECTED = json.loads(Path("examples/expected.json").read_text())


def at(document, pointer):
    for key in pointer.strip("/").split("/"):
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


class DomainTests(unittest.TestCase):
    def test_example_regression(self):
        self.assertEqual(analyze(EXAMPLE), EXPECTED)

    def test_input_isolation(self):
        snapshot = copy.deepcopy(EXAMPLE)
        analyze(EXAMPLE)
        self.assertEqual(EXAMPLE, snapshot)

    def test_deterministic_replay(self):
        self.assertEqual(analyze(EXAMPLE), analyze(copy.deepcopy(EXAMPLE)))

    def test_missing_required_fields(self):
        with self.assertRaises(ValueError):
            analyze({})

    def test_nonobject_document(self):
        for value in ([], None, True, "data"):
            with self.assertRaises(ValueError):
                analyze(value)

    def test_nonfinite_document(self):
        bad = copy.deepcopy(EXAMPLE)
        bad["nonfinite"] = float("nan")
        with self.assertRaises(ValueError):
            analyze(bad)

    def test_domain_rejection(self):
        bad = copy.deepcopy(EXAMPLE)
        bad.update(INVALID)
        with self.assertRaises(ValueError):
            analyze(bad)


INVALID = {"market_bps": 9500}


def check_0(self):
    self.assertEqual(at(analyze(EXAMPLE), "/sales/0/seller_net"), 875)


DomainTests.test_known_answer_0 = check_0


def check_1(self):
    self.assertEqual(at(analyze(EXAMPLE), "/market_total"), 25)


DomainTests.test_known_answer_1 = check_1


def check_2(self):
    self.assertEqual(at(analyze(EXAMPLE), "/royalty_totals/artist"), 100)


DomainTests.test_known_answer_2 = check_2


def check_3(self):
    self.assertEqual(at(analyze(EXAMPLE), "/gross"), 1000)


DomainTests.test_known_answer_3 = check_3


def alternate_scenario(self):
    d = copy.deepcopy(EXAMPLE)
    d.update({"sales": [{"id": "s", "seller": "alice", "price": 3}]})
    observed = at(analyze(d), "/sales/0/seller_net")
    self.assertEqual(observed, 3)


DomainTests.test_alternate_scenario = alternate_scenario
