"""
Test the merge function
"""
from nose.tools import assert_equals


def test_merge():
    """
    Test the merge function.
    """
    from attrdict.merge import merge

    left = {
        'foo': 'bar',
        'mismatch': False,
        'sub': {'alpha': 'beta', 'a': 'b'},
    }
    right = {
        'lorem': 'ipsum',
        'mismatch': True,
        'sub': {'alpha': 'bravo', 'c': 'd'},
    }

    assert_equals(merge({}, {}), {})
    assert_equals(merge(left, {}), left)
    assert_equals(merge({}, right), right)
    assert_equals(
        merge(left, right),
        {
            'foo': 'bar',
            'lorem': 'ipsum',
            'mismatch': True,
            'sub': {'alpha': 'bravo', 'a': 'b', 'c': 'd'}
        }
    )
