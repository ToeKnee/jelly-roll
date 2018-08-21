from django.test import TestCase

from satchmo import caching

from satchmo.configuration.functions import (
    config_add_choice,
    config_exists,
    config_get,
    config_get_group,
    config_register,
    config_register_list,
    config_value,
    config_collect_values,
    config_choice_values,
    ConfigurationSettings,
)
from satchmo.configuration.models import LongSetting
from satchmo.configuration.values import (
    SHOP_GROUP,
    SettingNotSet,
    BooleanValue,
    IntegerValue,
    StringValue,
    ConfigurationGroup,
    MultipleStringValue,
    ModuleValue,
    LongStringValue,
)


class ConfigurationFunctionTest(TestCase):

    def testSetSingleConfigItem(self):
        value = IntegerValue(SHOP_GROUP, 'SingleItem')
        config_register(value)
        self.assertTrue(config_exists(SHOP_GROUP, 'SingleItem'))

    def testSetTwoConfigItems(self):
        s = [IntegerValue(SHOP_GROUP, 'testTwoA'), StringValue(SHOP_GROUP, 'testTwoB')]
        config_register_list(*s)

        self.assertTrue(config_exists(SHOP_GROUP, 'testTwoA'))
        self.assertTrue(config_exists(SHOP_GROUP, 'testTwoB'))

    def testSetGroup(self):
        g1 = ConfigurationGroup('test1', 'test1')
        value = IntegerValue(g1, 'SingleGroupedItem')
        config_register(value)
        self.assertFalse(config_exists(SHOP_GROUP, 'SingleGroupedItem'))
        self.assertTrue(config_exists(g1, 'SingleGroupedItem'))


class ConfigurationTestSettings(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()
        g = ConfigurationGroup('test2', 'test2')
        self.g = g
        config_register(StringValue(g, 's1'))
        config_register(IntegerValue(g, 's2', default=10))
        config_register(IntegerValue(g, 's3', default=10))

    def testSetSetting(self):
        c = config_get('test2', 's1')
        c.update('test')

        self.assertEqual(c.value, 'test')
        self.assertEqual(c.setting.value, 'test')

    def testSettingDefault(self):
        c = config_get('test2', 's2')
        self.assertEqual(c.value, 10)

    def testSetAndReset(self):
        """Test setting one value and then updating"""
        c = config_get('test2', 's1')
        c.update('test1')

        self.assertEqual(c.value, 'test1')

        # should be true, since it is an update
        self.assertTrue(c.update('test2'))
        self.assertEqual(c.value, 'test2')

    def testTwice(self):
        """Config items should respond False to duplicate requests to update."""

        c = config_get('test2', 's1')
        c.update('test1')

        self.assertFalse(c.update('test1'))

    def testDeletesDefault(self):
        c = config_get('test2', 's3')
        # false because it isn't saving a default value
        self.assertFalse(c.update(10))

        self.assertTrue(c.update(20))
        self.assertEqual(c.value, 20)
        try:
            s = c.setting
        except SettingNotSet:
            self.fail("Should have a setting now")

        # now delete and go back to no setting by setting the default
        self.assertTrue(c.update(10))
        self.assertEqual(c.value, 10)

        try:
            s = c.setting
            self.fail('Should throw SettingNotSet')
        except SettingNotSet:
            pass


class ConfigTestDotAccess(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g = ConfigurationGroup('test3', 'test3')
        self.g = g
        c1 = config_register(BooleanValue(g, 's1', default=True))
        c2 = config_register(IntegerValue(g, 's2', default=10))
        c2.update(100)

    def testDotAccess(self):
        self.assertTrue(ConfigurationSettings().test3.s1.value)
        self.assertEqual(ConfigurationSettings().test3.s2.value, 100)

    def testSettingProperty(self):
        c = config_get('test3', 's2')
        s = c.setting
        self.assertTrue(s.value, 100)


class ConfigTestModuleValue(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g = ConfigurationGroup('modules', 'module test')
        self.g = g
        self.c = config_register(ModuleValue(g, 'test'))

    def testModule(self):
        c = config_get('modules', 'test')
        c.update('satchmo')

        self.assertTrue(hasattr(self.c.value, 'get_version'))


class ConfigTestSortOrder(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('group1', 'Group 1', ordering=-1001)
        g2 = ConfigurationGroup('group2', 'Group 2', ordering=-1002)
        g3 = ConfigurationGroup('group3', 'Group 3', ordering=-1003)

        self.g1 = g1
        self.g2 = g2
        self.g3 = g3

        self.g1c1 = config_register(IntegerValue(g1, 'c1'))
        self.g1c2 = config_register(IntegerValue(g1, 'c2'))
        self.g1c3 = config_register(IntegerValue(g1, 'c3'))

        self.g2c1 = config_register(IntegerValue(g2, 'c1'))
        self.g2c2 = config_register(IntegerValue(g2, 'c2'))
        self.g2c3 = config_register(IntegerValue(g2, 'c3'))

        self.g3c1 = config_register(IntegerValue(g3, 'c1'))
        self.g3c2 = config_register(IntegerValue(g3, 'c2'))
        self.g3c3 = config_register(IntegerValue(g3, 'c3'))

    def testGroupOrdering(self):
        mgr = ConfigurationSettings()
        self.assertEqual(mgr[2].key, self.g1.key)
        self.assertEqual(mgr[1].key, self.g2.key)
        self.assertEqual(mgr[0].key, self.g3.key)


class TestMultipleValues(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('m1', 'Multiple Group 1', ordering=1000)
        self.g1 = g1

        self.g1c1 = config_register(MultipleStringValue(g1,
                                                        'c1',
                                                        choices=((1, 'one'), (2, 'two'), (3, 'three'))))

    def testSave(self):

        c = config_get('m1', 'c1')
        c.update([1, 2])
        self.assertEqual(c.value, [1, 2])

    def testAddChoice(self):

        config_add_choice('m1', 'c1', (4, 'four'))
        c = config_get('m1', 'c1')
        self.assertEqual(c.choices, ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')))

    def testChoiceValues(self):
        self.g1c1.update([1, 2])

        choices = config_choice_values('m1', 'c1')
        self.assertEqual(choices, [(1, 'one'), (2, 'two')])


class TestMultipleValuesWithDefault(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('mv2', 'Multiple Group 2', ordering=1000)
        self.g1 = g1

        self.g1c1 = config_register(MultipleStringValue(g1,
                                                        'c1',
                                                        choices=((1, 'one'), (2, 'two'),
                                                                 (3, 'three')),
                                                        default=[1, 2]))

    def testDefault(self):

        c = config_get('mv2', 'c1')
        self.assertEqual(c.value, [1, 2])

        c.update([1, 2, 3])
        self.assertEqual(c.value, [1, 2, 3])


class ConfigTestChoices(TestCase):

    def testAddPreregisteredChoice(self):
        """Test that we can register choices before the config is actually set up."""
        config_add_choice('ctg1', 'c1', ('a', 'Item A'))
        config_add_choice('ctg1', 'c1', ('b', 'Item B'))
        config_add_choice('ctg1', 'c1', ('c', 'Item C'))

        g1 = ConfigurationGroup('ctg1', 'Choice 1', ordering=1000)
        config_register(StringValue(g1, 'c1'))

        c = config_get('ctg1', 'c1')

        self.assertEqual(c.choices, [('a', 'Item A'), ('b', 'Item B'), ('c', 'Item C')])


class ConfigTestRequires(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('req1', 'Requirements 1', ordering=1000)

        self.g1 = g1

        bool1 = config_register(BooleanValue(g1, 'bool1', default=False, ordering=1))
        bool2 = config_register(BooleanValue(g1, 'bool2', ordering=2))

        self.g1c1 = config_register(IntegerValue(g1, 'c1', requires=bool1, ordering=3))

        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=bool2, ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        bool2.update(True)

    def testSimpleRequires(self):
        v = config_value('req1', 'bool2')
        self.assertTrue(v)

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c2', 'c3', 'bool1', 'bool2'])

        c = config_get('req1', 'bool1')
        c.update(True)

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c1', 'c2', 'c3', 'bool1', 'bool2'])


class ConfigTestRequiresChoices(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('req2', 'Requirements 2', ordering=1000)

        self.g1 = g1

        choices1 = config_register(MultipleStringValue(SHOP_GROUP, 'rc1', ordering=1))

        self.g1c1 = config_register(IntegerValue(g1, 'c1', requires=choices1, ordering=3))
        self.g1c2 = config_register(IntegerValue(g1, 'c2', requires=choices1, ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        choices1.update('c1')

        g2 = ConfigurationGroup('req3', 'Requirements 3', ordering=1000)

        self.g2 = g2

        choices2 = config_register(StringValue(SHOP_GROUP, 'choices2', ordering=1))

        self.g2c1 = config_register(IntegerValue(g2, 'c1', requires=choices2, ordering=3))
        self.g2c2 = config_register(IntegerValue(g2, 'c2', requires=choices2, ordering=4))
        self.g2c3 = config_register(IntegerValue(g2, 'c3', requires=choices2, ordering=5))

        choices2.update('c1')

    def testSimpleRequiresChoices(self):

        v = config_value('SHOP', 'rc1')
        self.assertEqual(v, ['c1'])

        g = config_get_group('req2')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c3'])

        c = config_get('SHOP', 'rc1')
        c.update(['c1', 'c2'])

        g = config_get_group('req2')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])

    def testRequiresSingleValue(self):
        v = config_value('SHOP', 'choices2')
        self.assertEqual(v, 'c1')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c1'])

        c = config_get('SHOP', 'choices2')
        c.update('c2')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c2'])


class ConfigTestRequiresValue(TestCase):

    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        g1 = ConfigurationGroup('reqval', 'Requirements 3', ordering=1000)

        self.g1 = g1

        choices1 = config_register(MultipleStringValue(SHOP_GROUP, 'valchoices', ordering=1))

        self.g1c1 = config_register(IntegerValue(
            g1, 'c1', requires=choices1, requiresvalue='foo', ordering=3))
        self.g1c2 = config_register(IntegerValue(
            g1, 'c2', requires=choices1, requiresvalue='bar', ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

        choices1.update('foo')

        g2 = ConfigurationGroup('reqval2', 'Requirements 4', ordering=1000)

        self.g2 = g2

        choices2 = config_register(StringValue(SHOP_GROUP, 'valchoices2', ordering=1,
                                               choices=(('a', 'test a'), ('b', 'test b'), ('c', 'test c'))))

        self.g2c1 = config_register(IntegerValue(
            g2, 'c1', requires=choices2, requiresvalue='a', ordering=3))
        self.g2c2 = config_register(IntegerValue(
            g2, 'c2', requires=choices2, requiresvalue='b', ordering=4))
        self.g2c3 = config_register(IntegerValue(
            g2, 'c3', requires=choices2, requiresvalue='c', ordering=5))

        choices2.update('a')

    def testRequiresValue(self):
        v = config_value('SHOP', 'valchoices')
        self.assertEqual(v, ['foo'])

        g = config_get_group('reqval')

        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c3'])

        c = config_get('SHOP', 'valchoices')
        c.update(['foo', 'bar'])

        g = config_get_group('reqval')
        keys = [cfg.key for cfg in g]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])

    def testRequiresSingleValue(self):
        v = config_value('SHOP', 'valchoices2')
        self.assertEqual(v, 'a')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c1'])

        c = config_get('SHOP', 'valchoices2')
        c.update('b')

        keys = [cfg.key for cfg in self.g2]
        self.assertEqual(keys, ['c2'])


class ConfigTestGroupRequires(TestCase):
    def setUp(self):
        # clear out cache from previous runs
        caching.cache_delete()

        choices1 = config_register(MultipleStringValue(SHOP_GROUP, 'groupchoice', ordering=1))
        choices2 = config_register(MultipleStringValue(SHOP_GROUP, 'groupchoice2', ordering=1))

        g1 = ConfigurationGroup('groupreq', 'Requirements 4', ordering=1000, requires=choices1)
        self.g1 = g1

        self.g1c1 = config_register(IntegerValue(g1, 'c1', ordering=3))
        self.g1c2 = config_register(IntegerValue(
            g1, 'c2', requires=choices2, requiresvalue='bar', ordering=4))
        self.g1c3 = config_register(IntegerValue(g1, 'c3', ordering=5))

    def testRequiresValue(self):
        c = config_get('SHOP', 'groupchoice')
        self.assertEqual(c.value, [])

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, [])

        c2 = config_get('SHOP', 'groupchoice2')
        c2.update('bar')

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c2'])

        c.update(['groupreq'])

        keys = [cfg.key for cfg in self.g1]
        self.assertEqual(keys, ['c1', 'c2', 'c3'])


class ConfigCollectGroup(TestCase):
    def setUp(self):
        caching.cache_delete()
        choices = config_register(MultipleStringValue(SHOP_GROUP, 'collect', ordering=1))
        self.choices = choices

        g1 = ConfigurationGroup('coll1', 'Collection 1')
        g2 = ConfigurationGroup('coll2', 'Collection 2')
        g3 = ConfigurationGroup('coll3', 'Collection 3')

        g1c1 = config_register(StringValue(g1, 'test'))
        g1c2 = config_register(StringValue(g1, 'test1'))
        g2c1 = config_register(StringValue(g2, 'test'))
        g3c1 = config_register(StringValue(g3, 'test'))

        g1c1.update('set a')
        g1c2.update('set b')
        g2c1.update('set a')
        g3c1.update('set d')

        choices.update(['coll1', 'coll3'])

    def testCollectSimple(self):
        v = config_collect_values('SHOP', 'collect', 'test')

        self.assertEqual(v, ['set a', 'set d'])

    def testCollectUnique(self):
        self.choices.update(['coll1', 'coll2', 'coll3'])

        v = config_collect_values('SHOP', 'collect', 'test', unique=False)

        self.assertEqual(v, ['set a', 'set a', 'set d'])

        v = config_collect_values('SHOP', 'collect', 'test', unique=True)

        self.assertEqual(v, ['set a', 'set d'])


class LongSettingTest(TestCase):
    def setUp(self):
        caching.cache_delete()
        wide = config_register(LongStringValue(SHOP_GROUP, 'LONG', ordering=1, default="woot"))
        self.wide = wide
        self.wide.update('*' * 1000)

    def testLongStorage(self):
        w = config_value('SHOP', 'LONG')
        self.assertEqual(len(w), 1000)
        self.assertEqual(w, '*' * 1000)

    def testShortInLong(self):
        self.wide.update("test")
        w = config_value('SHOP', 'LONG')
        self.assertEqual(len(w), 4)
        self.assertEqual(w, 'test')

    def testDelete(self):
        remember = self.wide.setting.id
        self.wide.update('woot')

        try:
            q = LongSetting.objects.get(pk=remember)
            self.fail("Should be deletec")
        except LongSetting.DoesNotExist:
            pass
