========
AttrDict
========

AttrDict is a 2.6, 2.7, 3-compatible dictionary that allows its elements
to be accessed both as keys and as attributes::

    > from attrdict import AttrDict
    > a = AttrDict({'foo': 'bar'})
    > a.foo
    'bar'
    > a['foo']
    'bar'

With this, you can easily create convenient, heirarchical settings
objects.

::

    with open('settings.yaml', 'r') as fileobj:
        settings = AttrDict(yaml.safe_load(fileobj))

    cursor = connect(**settings.db.credentials).cursor()

    cursor.execute("SELECT column FROM table");


Installation
============
AttrDict is in PyPI, so it can be installed directly using::

    $ pip install attrdict

Or from Github::

    $ git clone https://github.com/bcj/AttrDict
    $ cd AttrDict
    $ python setup.py install

Documentation
=============

Documentation is available at https://github.com/bcj/AttrDict

Usage
=====
Creation
--------
An empty AttrDict can be created with::

    a = AttrDict()

Or, you can pass an existing ``dict`` (or other type of ``Mapping`` object)::

    a = AttrDict({'foo': 'bar'})

NOTE: Unlike ``dict``, AttrDict will not clone on creation. AttrDict's
internal dictionary will be the same instance as the dict passed in.

Access
------
AttrDict can be used *exactly* like a normal dict::

    > a = AttrDict()
    > a['foo'] = 'bar'
    > a['foo']
    'bar'
    > '{foo}'.format(**a)
    'bar'
    > del a['foo']
    > a.get('foo', 'default')
    'default'

AttrDict can also have it's keys manipulated as attributes to the object::

    > a = AttrDict()
    > a.foo = 'bar'
    > a.foo
    'bar'
    > del a.foo

Both methods operate on the same underlying object, so operations are
interchangeable. The only difference between the two methods is that
where dict-style access would return a dict, attribute-style access will
return an AttrDict. This allows recursive attribute-style access::

    > a = AttrDict({'foo': {'bar': 'baz'}})
    > a.foo.bar
    'baz'
    > a['foo'].bar
    AttributeError: 'dict' object has no attribute 'bar'

There are some valid keys that cannot be accessed as attributes. To be
accessed as an attribute, a key must:

 * be a string

 * start with an alphabetic character

 * be comprised solely of alphanumeric characters and underscores

 * not map to an existing attribute name (e.g., get, items)

To access these attributes while retaining an AttrDict wrapper (or to
dynamically access any key as an attribute)::

    > a = AttrDict({'_foo': {'bar': 'baz'}})
    > a('_foo').bar
    'baz'

Merging
-------
AttrDicts can be merged with eachother or other dict objects using the
``+`` operator. For conflicting keys, the right dict's value will be
preferred, but in the case of two dictionary values, they will be
recursively merged::

    > a = {'foo': 'bar', 'alpha': {'beta': 'a', 'a': 'a'}}
    > b = {'lorem': 'ipsum', 'alpha': {'bravo': 'b', 'a': 'b'}}
    > AttrDict(a) + b
    {'foo': 'bar', 'lorem': 'ipsum', 'alpha': {'beta': 'a', 'bravo': 'b', 'a': 'b'}}

NOTE: AttrDict's add is not associative, ``a + b != b + a``::

    > a = {'foo': 'bar', 'alpha': {'beta': 'b', 'a': 0}}
    > b = {'lorem': 'ipsum', 'alpha': {'bravo': 'b', 'a': 1}}
    > b + AttrDict(a)
    {'foo': 'bar', 'lorem': 'ipsum', 'alpha': {'beta': 'a', 'bravo': 'b', 'a': }}

Sequences
---------
By default, items in non-string Sequences (e.g. lists, tuples) will be
converted to AttrDicts::

    > adict = AttrDict({'list': [{'value': 1}, 'value': 2]})
    > for element in adict.list:
    >     element.value
    1
    2

This will not occur if you access the AttrDict as a dictionary::

    > adict = AttrDict({'list': [{'value': 1}, 'value': 2]})
    > for element in adict['list']:
    >     isinstance(element, AttrDict)
    False
    False

To disable this behavior globally, pass the attribute ``recursive=False`` to
the constructor::

    > adict = AttrDict({'list': [{'value': 1}, 'value': 2]}, recursive=False)
    > for element in adict['list']:
    >     isinstance(element, AttrDict)
    False
    False

When merging an AttrDict with another mapping, this behavior will be disabled
if at least one of the merged items is an AttrDict that has set ``recursive``
to ``False``.

Cookbook
========
A common usage for AttrDict is to use it in combination with settings files to create hierarchical settings::

    from attrdict import AttrDict
    import yaml

    def load(*filenames):
        """
        Returns a settings dict built from a list of settings files.

        filenames: The names of any number of settings files.
        """
        settings = AttrDict()

        for filename in filenames:
            with open(filename, 'r') as fileobj:
                settings += yaml.safe_load(fileobj)

        return settings

By accepting multiple files, settings can allow for default settings and provide overrides, e.g.::

    # config.yaml =
    # emergency:
    #   email: everyone@example.com
    #   message: Something went wrong
    #
    # user.yaml =
    # emergency:
    #   email: user@example.com
    settings = load('config.yaml', 'user.yaml')

    assert settings.email == 'user@example.com'
    assert settings.message == 'Something went wrong'

License
=======
AttrDict is released under a MIT license.
