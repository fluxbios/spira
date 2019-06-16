import numpy as np
import networkx as nx
from spira.core.parameters.restrictions import RestrictType, RestrictRange
from spira.core.parameters.descriptor import RestrictedParameter


NUMBER = RestrictType((int, float, np.int32, np.int64, np.float))
FLOAT = RestrictType(float)
INTEGER = RestrictType(int)
COMPLEX = RestrictType((int, float, complex))
STRING = RestrictType(str)
BOOL = RestrictType(bool)
DICTIONARY = RestrictType(dict)
LIST = RestrictType(list)
TUPLE = RestrictType(tuple)
NUMPY_ARRAY = RestrictType(np.ndarray)
GRAPH = RestrictType(nx.Graph)


def NumberField(restriction=None, **kwargs):
    if 'default' not in kwargs:
        kwargs['default'] = 0
    R = NUMBER & restriction
    return RestrictedParameter(restriction=R, **kwargs)


def ComplexField(restriction=None, **kwargs):
    from .variables import COMPLEX
    if 'default' not in kwargs:
        kwargs['default'] = 0
    return RestrictedParameter(restriction=COMPLEX, **kwargs)


def IntegerField(restriction=None, **kwargs):
    from .variables import INTEGER
    if 'default' not in kwargs:
        kwargs['default'] = 0
    return RestrictedParameter(restriction=INTEGER, **kwargs)


def FloatField(restriction=None, **kwargs):
    from .variables import FLOAT
    if 'default' not in kwargs:
        kwargs['default'] = 0.0
    return RestrictedParameter(restriction=FLOAT, **kwargs)


def StringField(restriction=None, **kwargs):
    from .variables import STRING
    if 'default' not in kwargs:
        kwargs['default'] = ''
    R = STRING & restriction
    return RestrictedParameter(restriction=R, **kwargs)


def BoolField(restriction=None, **kwargs):
    from .variables import BOOL
    if 'default' not in kwargs:
        kwargs['default'] = False
    return RestrictedParameter(restriction=BOOL, **kwargs)


def ListField(restriction=None, **kwargs):
    from .variables import LIST
    if 'default' not in kwargs:
        kwargs['default'] = []
    return RestrictedParameter(restriction=LIST, **kwargs)


def TupleField(restriction=None, **kwargs):
    from .variables import TUPLE
    if 'default' not in kwargs:
        kwargs['default'] = []
    return RestrictedParameter(restriction=TUPLE, **kwargs)


def DictField(local_name=None, restriction=None, **kwargs):
    from .variables import DICTIONARY
    if 'default' not in kwargs:
        kwargs['default'] = {}
    R = DICTIONARY & restriction
    return RestrictedParameter(local_name, restriction=R, **kwargs)


def NumpyArrayField(restriction=None, **kwargs):
    from .variables import NUMPY_ARRAY
    if 'default' not in kwargs:
        kwargs['default'] = np.array([])
    return RestrictedParameter(restriction=NUMPY_ARRAY, **kwargs)


def GraphField(restriction=None, **kwargs):
    from .variables import GRAPH
    if 'default' not in kwargs:
        kwargs['default'] = nx.Graph()
    R = GRAPH & restriction
    return RestrictedParameter(restriction=R, **kwargs)


def TimeField(local_name=None, restriction=None, **kwargs):
    import time
    R = NUMBER & restriction
    if not 'default' in kwargs:
        kwargs['default'] = time.time()
    return RestrictedParameter(local_name, restriction=R, **kwargs)