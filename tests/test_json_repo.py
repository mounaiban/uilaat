"""
UILAAT JSON Repository Tests

Test suite to verify functionality and behaviours of the JSON
Repository (JSONRepo) class

"""
import hashlib
from os import path
from unittest import TestCase
from json import JSONEncoder

from json_repo import JSONRepo, KEY_DB_NAME, SUFFIX_JSON
from uilaat import SUBPOINT, VERSION

# Test Resources
REPO_DIR = 'tests/test_json_repo'
FANCY_ONE_a = '\u07c1'
FANCY_ONE_b = '\U0001d7d9'
FANCY_ONE_c = '\U0001f019'
FANCY_E = '\uab33'
FANCY_F = '\uab35'
FANCY_Xm = '\u1450\u1455'
FANCY_Ym = '\u144c\ufe28'
SAY_NO = SUBPOINT + '\u20e0'
SAY_YES = SUBPOINT + '\U0001f44f'

je = JSONEncoder()

def write_json_file(name, dic, repo_dir=REPO_DIR):
    """
    Writes out a test database to a repository directory
    """
    out = je.encode(dic)
    filename = name+SUFFIX_JSON
    fpath = path.join(repo_dir, filename)
    fh = None
    try:
        fh = open(fpath, mode='x', encoding='utf-8')
        fh.write(out)
        fh.close()
    except FileExistsError:
        fh = open(fpath, mode='br')
        hasher = hashlib.md5  # not a crypto operation, so it's ok
        fc = fh.read()
        out_bytes = bytes(out, 'utf-8')
        sum_e = hasher(out_bytes).digest()
        sum_cur = hashlib.md5(fc).digest()
        if sum_cur != sum_e:
            fmt = '{}: file contains non-test data, please check and delete'
            msg = fmt.format(fpath)
            raise FileExistsError(msg)
    finally:
        if fh is not None:
            fh.close()

class JSONRepoLoadDbTests(TestCase):
    """
    Tests to verify database-loading behaviours

    """
    def test_load(self):
        """
        Load database with inclusions
        
        The assertions in this suite generally verify loading behaviour by
        means of the number of databases loaded, the correctness of database
        names and the correctness of the translations retrieved.

        """
        dbs = {
            'test_load_first': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database loading test',
                    },
                },
                'trans': {'e': FANCY_E},
            },
            'test_load_second': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database loading test',
                    },
                },
                'trans': {'x': FANCY_Xm},
                'trans-include': ['test_load_first',],
            },
            'test_load_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database loading test',
                    },
                },
                'trans': {'y': FANCY_Ym},
                'trans-include': ['test_load_second',],
            }
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)
        jr.load_db('test_load_last')

        # assertions
        for i in range(len(jr._tmp)):
            db_tmp = jr._tmp[i]
            run_name = db_tmp['meta'][KEY_DB_NAME]
            trans = db_tmp['trans']
            trans_expected = dbs.get(dbs_keys[i])['trans']
            with self.subTest(i=i):
                self.assertEqual(run_name, dbs_keys[i])
                self.assertEqual(trans, trans_expected)
        self.assertEqual(len(jr._tmp), len(dbs_keys))

    def test_load_multi_include(self):
        """
        Load database with multiple inclusions
        """
        dbs = {
            'test_load_multi_include_first': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database multi-inclusion test',
                    },
                },
                'trans': {'e': FANCY_E},
            },
            'test_load_multi_include_second': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database multi-inclusion test',
                    },
                },
                'trans': {'x': FANCY_Xm},
            },
            'test_load_multi_include_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database multi-inclusion test',
                    },
                },
                'trans': {'y': FANCY_Ym},
                'trans-include': [
                    'test_load_multi_include_second',
                    'test_load_multi_include_first',
                ],
            },
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)
        jr.load_db('test_load_multi_include_last')

        # assertions
        for i in range(len(jr._tmp)):
            db_tmp = jr._tmp[i]
            run_name = db_tmp['meta'][KEY_DB_NAME]
            trans = db_tmp['trans']
            trans_expected = dbs.get(dbs_keys[i])['trans']
            with self.subTest(i=i):
                self.assertEqual(run_name, dbs_keys[i])
                self.assertEqual(trans, trans_expected)
        self.assertEqual(len(jr._tmp), len(dbs_keys))

    def test_load_self_include(self):
        """
        Load database with self-inclusion loop

        The loading must stop at the first incidence of a self-inclusion,
        while retaining data loaded before the incident.
        """
        dbs = {
            'test_load_self_include_first': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database self inclusion handling test',
                    },
                },
                'trans': {'e': FANCY_E},
                'trans-include': ['test_load_self_include_first',],
            },
            'test_load_self_include_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database self inclusion handling test',
                    },
                },
                'trans': {'y': FANCY_Ym},
                'trans-include': ['test_load_self_include_first',],
            },
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)

        # assertions
        with self.assertWarns(RuntimeWarning):
            jr.load_db('test_load_self_include_last')
            for i in range(len(jr._tmp)):
                db_tmp = jr._tmp[i]
                run_name = db_tmp['meta'][KEY_DB_NAME]
                trans = db_tmp['trans']
                trans_expected = dbs.get(dbs_keys[i])['trans']
                with self.subTest(i=i):
                    self.assertEqual(run_name, dbs_keys[i])
                    self.assertEqual(trans, trans_expected)
        self.assertEqual(len(jr._tmp), len(dbs_keys))

    def test_load_loop(self):
        """
        Load database with inclusion loop

        The loading must stop as soon as a loop is detected, retaining data
        loaded before the loop was discovered.

        """
        dbs = {
            'test_load_loop_first': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database inclusion loop handling test',
                    },
                },
                'trans': {'e': FANCY_E},
                'trans-include': ['test_load_loop_last',],
            },
            'test_load_loop_second': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database inclusion loop handling test',
                    },
                },
                'trans': {'x': FANCY_Xm},
                'trans-include': ['test_load_loop_first',],
            },
            'test_load_loop_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Database inclusion loop handling test',
                    },
                },
                'trans': {'y': FANCY_Ym},
                'trans-include': ['test_load_loop_second',],
            },
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)
        jr.load_db('test_load_loop_last')

        # assertions
        # TODO: Find out how to correctly assert the RuntimeWarning
        for i in range(len(jr._tmp)):
            db_tmp = jr._tmp[i]
            run_name = db_tmp['meta'][KEY_DB_NAME]
            trans = db_tmp['trans']
            trans_expected = dbs.get(dbs_keys[i])['trans']
            with self.subTest(i=i):
                self.assertEqual(run_name, dbs_keys[i])
                self.assertEqual(trans, trans_expected)
        self.assertEqual(len(jr._tmp), len(dbs_keys))


class JSONRepoGetTransTests(TestCase):
    """
    Tests to verify translation dictionary-building routines 

    """
    # TODO: Wanted Tests:
    # * maketrans flag test
    # * repeated alternate translations (e.g. {'a': ['\u2227', '4', '\u2227']})

    def test_get_trans(self):
        """
        Get single-database translations
        """
        name = 'test_get_trans'
        db = {
            'meta': {
                'reverse': False,
                'version': VERSION,
                'desc': {
                    'en-au': 'Single-database get translation test',
                },
            },
            'trans': {'x': FANCY_Xm, 'y': FANCY_Ym, 'f': FANCY_F},
        }
        write_json_file(name, db)
        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        # assertions
        trans_expected = db['trans']
        trans = jr.get_trans() 
        self.assertEqual(trans, trans_expected)

    def test_get_trans_multi(self):
        """
        Get multi-database translations using trans-include

        """
        dbs = {
            'test_get_trans_multi_first_a': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database get translation test',
                    },
                },
                'trans': {'': SAY_YES,},
            },
            'test_get_trans_multi_second': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database get translation test',
                    },
                },
                'trans-include': ['test_get_trans_multi_first_a'],
                'trans': {'y': FANCY_Ym,},
            },
            'test_get_trans_multi_first_b': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database get translation test',
                    },
                },
                'trans': {'f': FANCY_F},
            },
            'test_get_trans_multi_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database get translation test',
                    },
                },
                'trans-include': [
                    'test_get_trans_multi_second',
                    'test_get_trans_multi_first_b',
                ],
                'trans': {'e': FANCY_E},
            },
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)
        jr.load_db('test_get_trans_multi_last')

        # assertions
        trans_expected = {'y':FANCY_Ym, '':SAY_YES, 'f':FANCY_F, 'e':FANCY_E}
        trans = jr.get_trans() 
        self.assertEqual(trans, trans_expected)

    def test_get_trans_override(self):
        """
        Overrides in multi-database translations

        """
        dbs = {
            'test_get_trans_override_first_a': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database translation overrides test',
                    },
                },
                'trans': {'1': FANCY_ONE_a, '':SAY_NO},
            },
            'test_get_trans_override_second': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database translation overrides test',
                    },
                },
                'trans-include': ['test_get_trans_override_first_a'],
                'trans': {'1': FANCY_ONE_b,}, 
            },
            'test_get_trans_override_first_b': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database translation overrides test',
                    },
                },
                'trans': {'x': FANCY_Xm}, # no overrides
            },
            'test_get_trans_override_last': {
                'meta': {
                    'reverse': False,
                    'version': VERSION,
                    'desc': {
                        'en-au': 'Multi-database translation overrides test',
                    },
                },
                'trans-include': [
                    'test_get_trans_override_second',
                    'test_get_trans_override_first_b',
                ],
                'trans': {'1': FANCY_ONE_c, '': SAY_YES},
            },
        }
        dbs_keys = tuple(dbs.keys())
        for k in dbs_keys:
            write_json_file(k, dbs[k])
        jr = JSONRepo(REPO_DIR)
        jr.load_db('test_get_trans_override_last')

        # assertions
        trans_expected = {'x':FANCY_Xm, '1':FANCY_ONE_c, '':SAY_YES}
        trans = jr.get_trans() 
        self.assertEqual(trans, trans_expected)

    def test_get_trans_reverse(self):
        """
        Translation reversals

        The reverse flag when set to True causes swaps keys (targets) and
        values (replacements) in the database's translations.

        """
        name = 'test_get_trans_reverse'
        db = {
            'meta': {
                'reverse': True,
                'version': VERSION,
                'desc': {
                    'en-au': 'Standalone reversed translation',
                },
            },
            'trans': {'e': FANCY_E, 'f': FANCY_F},
        }
        write_json_file(name, db)
        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        # assertions
        trans_expected = {FANCY_E: 'e', FANCY_F: 'f'}
        trans = jr.get_trans() 
        self.assertEqual(trans, trans_expected)

    def test_get_trans_default_reverse(self):
        """
        Reversal of default translations

        Reversals of default translations are not allowed and must be ignored.

        """
        name = 'test_get_trans_default_reverse'
        db = {
            'meta': {
                'reverse': True,
                'version': VERSION,
                'desc': {
                    'en-au': 'Defaults in reversed translation handling',
                },
            },
            'trans': {'e': FANCY_E, '': SAY_NO},
        }
        write_json_file(name, db)
        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        # assertions
        trans_expected = {FANCY_E: 'e'}
        trans = jr.get_trans() 
        self.assertEqual(trans, trans_expected)

    def test_get_trans_alts(self):
        """
        Alternative translations in standalone databases

        """
        name = 'test_get_trans_alts_reverse'
        db = {
            'meta': {
                'reverse': True,
                'version': VERSION,
                'desc': {
                    'en-au': 'Standalone reversed translation with alts.',
                },
            },
            'trans': {'1': [FANCY_ONE_a, FANCY_ONE_b, FANCY_ONE_c]},
        }
        write_json_file(name, db)

        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        self.assertEqual(jr.get_trans(), {FANCY_ONE_a: '1'})
        self.assertEqual(jr.get_trans(n=0), {FANCY_ONE_a: '1'})
        self.assertEqual(jr.get_trans(n=1), {FANCY_ONE_b: '1'})
        self.assertEqual(jr.get_trans(n=2), {FANCY_ONE_c: '1'})

    def test_get_trans_alts_oor(self):
        """
        Out-of-range handling when getting alternative translations 

        """
        name = 'test_get_trans_alts_oor'
        db = {
            'meta': {
                'reverse': False,
                'version': VERSION,
                'desc': {
                    'en-au': 'Standalone translation with alts. (OOR test)',
                },
            },
            'trans': {
                '1': [FANCY_ONE_a, FANCY_ONE_b, FANCY_ONE_c],
                '': [SAY_NO, SAY_YES],
            },
        }
        write_json_file(name, db)

        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        self.assertEqual(jr.get_trans(), {'1':FANCY_ONE_a, '':SAY_NO})
        self.assertEqual(jr.get_trans(n=0), {'1':FANCY_ONE_a, '':SAY_NO})
        self.assertEqual(jr.get_trans(n=1), {'1':FANCY_ONE_b, '':SAY_YES})
        self.assertEqual(jr.get_trans(n=2), {'1':FANCY_ONE_c, '':SAY_NO})

    def test_get_trans_alts_reverse(self):
        """
        Reversal of alternate translations, with standalone database

        """
        name = 'test_get_trans_alts'
        db = {
            'meta': {
                'reverse': False,
                'version': VERSION,
                'desc': {
                    'en-au': 'Standalone translation with alternatives',
                },
            },
            'trans': {'1': [FANCY_ONE_a, FANCY_ONE_b, FANCY_ONE_c]},
        }
        write_json_file(name, db)

        jr = JSONRepo(REPO_DIR)
        jr.load_db(name)

        self.assertEqual(jr.get_trans(), {'1': FANCY_ONE_a})
        self.assertEqual(jr.get_trans(n=0), {'1': FANCY_ONE_a})
        self.assertEqual(jr.get_trans(n=1), {'1': FANCY_ONE_b})
        self.assertEqual(jr.get_trans(n=2), {'1': FANCY_ONE_c})

