import sympy
import sympy.stats
from numbers import Number

class Vector(object):

    def __init__(self, size, name='anon', xs=None, mkvar=None):
        if xs is None:
            if mkvar is None:
                mkvar = lambda i: sympy.Symbol('%s(%d)' % (name, i))
            xs = map(mkvar, range(size))
        self._xs = xs
        self._size = size

    @property
    def size(self):
        return self._size

    def __getitem__(self, index):
        return self._xs[index]

    def __str__(self):
        strs = []
        for i in range(self.size):
            strs.append('%s%s' % (str(self[i]), '\n'))
        return ''.join(strs)

    def dot(self, other):
        if other.is_matrix():
            return self.asmat().dot(other)
        elif other.is_vector():
            assert self.size == other.size 
            return sum(self[i]*other[i] for i in range(self.size))
        else:
            raise ValueError('not supported')

    @property
    def T(self):
        return self.asmat().transpose()

    def transpose(self):
        return self.asmat().transpose()

    def is_vector(self):
        return True

    def is_matrix(self):
        return False

    def asmat(self):
        return Matrix(shape=(self.size, 1), xs = map(lambda x: [x], self._xs))

class Matrix(object):

    def __init__(self, shape, name='anon', xs=None, mkvar=None):
        if xs is None:
            if mkvar is None:
                mkvar = lambda i, j: sympy.Symbol('%s(%d,%d)' % (name, i, j))
            xs = [[mkvar(i,j) for j in range(shape[1])] for i in range(shape[0])]
        self._xs = xs
        self._shape = shape

    @property
    def shape(self):
        return self._shape

    @property
    def nrow(self):
        return self._shape[0]

    @property
    def ncol(self):
        return self._shape[1]

    def trace(self):
        assert self.nrow == self.ncol
        ret = sympy.numbers.Zero
        for i in range(self.nrow):
            ret += self._xs[i][i]
        return ret

    def square(self):
        return self.dot(self)

    def __getitem__(self, indices):
        if isinstance(indices, tuple):
            ret = self._xs
            for index in indices:
                ret = ret[index]
            return ret
        else:
            return self[(indices,)]

    def __setitem__(self, indices, value):
        if isinstance(indices, tuple):
            ret = self._xs
            for i, index in enumerate(indices):
                if i == len(indices) - 1:
                    ret[index] = value
                else:
                    ret = ret[index]

    @classmethod
    def zeros(cls, shape):
        return Matrix(shape=shape, mkvar=lambda i, j: sympy.S.Zero)

    def is_vector(self):
        return False

    def is_matrix(self):
        return True


    def dot(self, other):
        if other.is_vector():
            return Vector(size=self.nrow, xs=self.dot(other.asmat())[0])
        elif other.is_matrix():
            assert self.ncol == other.nrow
            ret = Matrix.zeros((self.nrow, other.ncol))
            for i in range(self.nrow):
                for j in range(other.ncol):
                    for k in range(self.ncol):
                        ret[i,j] += self[i,k] * other[k,j]
            return ret
        else:
            raise ValueError('not supported')

    def __str__(self):
        strs = []
        for i in range(self.nrow):
            for j in range(self.ncol):
                strs.append('%s%s' % (str(self[i,j]), '\n' if j == self.ncol - 1 else '\t'))
        return ''.join(strs)

    def map(self, op):
        return Matrix(shape=self.shape, mkvar=lambda i, j: op(self[i,j]))

    @property
    def T(self):
        return self.transpose()

    def transpose(self):
        return Matrix(shape=self.shape[::-1], mkvar=lambda i, j: self[j,i])

    def __mul__(self, other):
        if isinstance(other, sympy.Expr) or isinstance(other, Number):
            return self.map(lambda x: x*other)
        else:
            import ipdb; ipdb.set_trace()

    __rmul__ = __mul__

    def __add__(self, other):
        assert self.nrow == other.nrow
        assert self.ncol == other.ncol
        return Matrix(shape=self.shape, mkvar=lambda i, j: self[i,j] + other[i,j])

    __radd__ = __add__

    @classmethod
    def eye(self, size):
        return Matrix(shape=(size,size), mkvar=lambda i, j: sympy.numbers.One if i == j else sympy.numbers.Zero)

def quad_form(x, A, y):
    return x.T.dot(A).dot(y)[0]

def outer(x, y):
    return x.dot(y.T)
