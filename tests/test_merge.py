"""
Test the merge function
"""
from nose.tools import assert_equals


def test_merge():
    """
    merge function.
    """
    from attrdict.merge import merge

    left = {
        'baz': 'qux',
        'mismatch': False,
        'sub': {'alpha': 'beta', 1: 2},
    }
    right = {
        'lorem': 'ipsum',
        'mismatch': True,
        'sub': {'alpha': 'bravo', 3: 4},
    }

    assert_equals(merge({}, {}), {})
    assert_equals(merge(left, {}), left)
    assert_equals(merge({}, right), right)
    assert_equals(
        merge(left, right),
        {
            'baz': 'qux',
            'lorem': 'ipsum',
            'mismatch': True,
            'sub': {'alpha': 'bravo', 1: 2, 3: 4}
        }
    )
