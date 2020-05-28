import pytest
import sympy

from pharmpy.model import ModelSyntaxError


def S(x):
    return sympy.Symbol(x)


@pytest.mark.usefixtures('parser')
@pytest.mark.parametrize('buf,results', [
    ('$OMEGA 1', [('OMEGA(1,1)', 1, 0, sympy.oo, False)]),
    ('$OMEGA   0.123 \n\n', [('OMEGA(1,1)', 0.123, 0, sympy.oo, False)]),
    ('$OMEGA   (0 FIX) ; CL', [('OMEGA(1,1)', 0, 0, sympy.oo, True)]),
    ('$OMEGA DIAG(2) 1 2 FIX', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,2)', 2, 0, sympy.oo, True),
        ]),
    ('$OMEGA 1 2 3', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,2)', 2, 0, sympy.oo, False),
        ('OMEGA(3,3)', 3, 0, sympy.oo, False),
        ]),
    ('$OMEGA 0.15 ;CL', [('OMEGA(1,1)', 0.15, 0, sympy.oo, False)]),
    ('$OMEGA 1 \n2 ; S   \n  3 ', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,2)', 2, 0, sympy.oo, False),
        ('OMEGA(3,3)', 3, 0, sympy.oo, False),
        ]),
    ('$OMEGA 2 SD', [('OMEGA(1,1)', 4, 0, sympy.oo, False)]),
    ('$OMEGA ;CO\n (VAR 3)', [('OMEGA(1,1)', 3, 0, sympy.oo, False)]),
    ('$OMEGA (1)x2', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,2)', 1, 0, sympy.oo, False),
        ]),
    ('$OMEGA BLOCK(2) 1 0.5 2', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,1)', 0.5, -sympy.oo, sympy.oo, False),
        ('OMEGA(2,2)', 2, 0, sympy.oo, False),
        ]),
    ('$OMEGA BLOCK(2) SAME', []),
    ('$OMEGA BLOCK SAME(3)', []),
    ('$OMEGA BLOCK(2) 1 (0.1)x2', [
        ('OMEGA(1,1)', 1, 0, sympy.oo, False),
        ('OMEGA(2,1)', 0.1, -sympy.oo, sympy.oo, False),
        ('OMEGA(2,2)', 0.1, 0, sympy.oo, False),
        ]),
    ('$OMEGA BLOCK(2) CHOLESKY 0.8 -0.3 0.7', [
        ('OMEGA(1,1)', 0.64, 0, sympy.oo, False),
        ('OMEGA(2,1)', -0.24, -sympy.oo, sympy.oo, False),
        ('OMEGA(2,2)', 0.58, 0, sympy.oo, False),
        ]),
    ('$OMEGA BLOCK(2) SD 0.8 -0.394 0.762 CORR', [
        ('OMEGA(1,1)', 0.64, 0, sympy.oo, False),
        ('OMEGA(2,1)', -0.2401824, -sympy.oo, sympy.oo, False),
        ('OMEGA(2,2)', 0.580644, 0, sympy.oo, False),
        ]),
    ('$OMEGA BLOCK(1)   1.5', [
        ('OMEGA(1,1)', 1.5, 0, sympy.oo, False),
        ]),
    ('$OMEGA  0.0258583  ;      V2\n'
     ';$OMEGA BLOCK(1) 0.0075 FIX    ;.02 ; IOC\n'
     ';$OMEGA BLOCK(1) SAME\n', [
        ('OMEGA(1,1)', 0.0258583, 0, sympy.oo, False),
        ]),
])
def test_parameters(parser, buf, results):
    recs = parser.parse(buf)
    rec = recs.records[0]
    pset, _, _ = rec.parameters(1, 1)
    assert len(pset) == len(results)
    for res in results:
        name = res[0]
        init = res[1]
        lower = res[2]
        upper = res[3]
        fix = res[4]
        param = pset[name]
        assert param.name == name
        assert pytest.approx(param.init, 0.00000000000001) == init
        assert param.lower == lower
        assert param.upper == upper
        assert param.fix == fix


@pytest.mark.usefixtures('parser')
@pytest.mark.parametrize('buf', [
    ('$OMEGA 0 '),
    ('$OMEGA DIAG(1) 1 SD VARIANCE'),
    ('$OMEGA SD BLOCK(2) 0.1 0.001 0.1 STANDARD'),
    ('$OMEGA CHOLESKY BLOCK(2) 0.1 VAR 0.001 \n  0.1 '),
])
def test_errors(parser, buf):
    recs = parser.parse(buf)
    rec = recs.records[0]
    with pytest.raises(ModelSyntaxError):
        pset, _, _ = rec.parameters(1, None)


def test_parameters_offseted(parser):
    rec = parser.parse("$OMEGA 1").records[0]
    pset, _, _ = rec.parameters(3, None)
    assert pset['OMEGA(3,3)'].init == 1

    rec = parser.parse('$OMEGA   BLOCK   SAME').records[0]
    pset, _, _ = rec.parameters(3, 2)
    assert len(pset) == 0


def test_update(parser):
    rec = parser.parse('$OMEGA 1').records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 2
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA 2.0'

    rec = parser.parse('$OMEGA 1 SD').records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 4
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA 2.0 SD'

    rec = parser.parse('$OMEGA (1)x3\n;FTOL').records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 4
    pset['OMEGA(2,2)'].init = 4
    pset['OMEGA(3,3)'].init = 4
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA (4.0)x3\n;FTOL'

    rec = parser.parse('$OMEGA (1)x2 2').records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 1
    pset['OMEGA(2,2)'].init = 2
    pset['OMEGA(3,3)'].init = 0.5
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA (1) (2.0) 0.5'

    rec = parser.parse("$OMEGA DIAG(2) (1 VAR) (SD 2)").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 1.5
    pset['OMEGA(2,2)'].init = 16
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA DIAG(2) (1.5 VAR) (SD 4.0)'

    rec = parser.parse("$OMEGA BLOCK(2) 1 2 4").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 7
    pset['OMEGA(2,1)'].init = 0.5
    pset['OMEGA(2,2)'].init = 8
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2) 7.0 0.5 8.0'

    rec = parser.parse("$OMEGA BLOCK(2)\n SD 1 0.5 ;COM \n 1\n").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 4
    pset['OMEGA(2,1)'].init = 0.25
    pset['OMEGA(2,2)'].init = 9
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2)\n SD 2.0 0.25 ;COM \n 3.0\n'

    rec = parser.parse("$OMEGA CORR BLOCK(2)  1 0.5 1\n").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 4
    pset['OMEGA(2,1)'].init = 1
    pset['OMEGA(2,2)'].init = 4
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA CORR BLOCK(2)  4.0 0.25 4.0\n'

    rec = parser.parse("$OMEGA CORR BLOCK(2)  1 0.5 SD 1\n").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 4
    pset['OMEGA(2,1)'].init = 1
    pset['OMEGA(2,2)'].init = 4
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA CORR BLOCK(2)  2.0 0.25 SD 2.0\n'

    rec = parser.parse("$OMEGA BLOCK(2) 1 0.1 1\n CHOLESKY").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 0.64
    pset['OMEGA(2,1)'].init = -0.24
    pset['OMEGA(2,2)'].init = 0.58
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2) 0.8 -0.3 0.7\n CHOLESKY'

    rec = parser.parse("$OMEGA BLOCK(2) (1)x3\n").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 0.64
    pset['OMEGA(2,1)'].init = -0.24
    pset['OMEGA(2,2)'].init = 0.58
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2) 0.64 -0.24 0.58\n'

    rec = parser.parse("$OMEGA BLOCK(3) 1 ;CL\n0.1 1; V\n0.1 0.1 1; KA").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].init = 1
    pset['OMEGA(2,1)'].init = 0.2
    pset['OMEGA(2,2)'].init = 3
    pset['OMEGA(3,1)'].init = 0.4
    pset['OMEGA(3,2)'].init = 0.5
    pset['OMEGA(3,3)'].init = 6
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(3) 1 ;CL\n0.2 3.0; V\n0.4 0.5 6.0; KA'

    rec = parser.parse("$OMEGA BLOCK(2) SAME").records[0]
    pset, _, _ = rec.parameters(3, 2)
    assert len(pset) == 0
    next_eta, prev_size = rec.update(pset, 3, 2)
    assert next_eta == 5
    assert prev_size == 2
    assert str(rec) == "$OMEGA BLOCK(2) SAME"

    rec = parser.parse("$OMEGA BLOCK SAME").records[0]
    pset, _, _ = rec.parameters(5, 4)
    assert len(pset) == 0
    next_eta, prev_size = rec.update(pset, 5, 4)
    assert next_eta == 9
    assert prev_size == 4
    assert str(rec) == "$OMEGA BLOCK SAME"


def test_update_fix(parser):
    rec = parser.parse("$OMEGA 2 FIX 4 (FIX 6)").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].fix = False
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA 2 4 (FIX 6)'

    rec = parser.parse("$OMEGA 2 4 6 ;STRAML").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].fix = True
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA 2 FIX 4 6 ;STRAML'
    pset['OMEGA(1,1)'].fix = False
    pset['OMEGA(2,2)'].fix = True
    pset['OMEGA(3,3)'].fix = True
    pset['OMEGA(3,3)'].init = 23
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA 2 4 FIX 23.0 FIX ;STRAML'

    rec = parser.parse("$OMEGA BLOCK(2) 1 .1 2 ;CLERMT").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].fix = True
    # Cannot fix parts of block
    with pytest.raises(ValueError):
        rec.update(pset, 1, None)
    pset['OMEGA(2,1)'].fix = True
    pset['OMEGA(2,2)'].fix = True
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2) FIX 1 .1 2 ;CLERMT'

    rec = parser.parse("$OMEGA BLOCK(2) 1 .1 FIX 1").records[0]
    pset, _, _ = rec.parameters(1, None)
    pset['OMEGA(1,1)'].fix = False
    pset['OMEGA(2,1)'].fix = False
    pset['OMEGA(2,2)'].fix = False
    rec.update(pset, 1, None)
    assert str(rec) == '$OMEGA BLOCK(2) 1 .1 1'


def test_random_variables(parser):
    rec = parser.parse("$OMEGA BLOCK(3) 1 ;CL\n0.1 1; V\n0.1 0.1 1; KA").records[0]
    rvs, nxt, cov, zero_fix = rec.random_variables(1)
    assert nxt == 4
    assert len(rvs) == 3
    assert rvs[0].name == 'ETA(1)'
    assert rvs[1].name == 'ETA(2)'
    assert rvs[2].name == 'ETA(3)'
    assert len(cov) == 9
    assert len(zero_fix) == 0

    rec = parser.parse("$OMEGA BLOCK(1) 1.5").records[0]
    rvs, nxt, cov, zero_fix = rec.random_variables(2)
    assert nxt == 3
    assert len(rvs) == 1
    assert rvs[0].name == 'ETA(2)'
    assert isinstance(rvs[0].pspace.distribution, sympy.stats.crv_types.NormalDistribution)
    assert cov == S('OMEGA(2,2)')
    assert len(zero_fix) == 0

    p = parser.parse("$OMEGA BLOCK(2) 1 0.01 1\n$OMEGA BLOCK(2) SAME\n")
    rec0 = p.records[0]
    rec1 = p.records[1]
    rvs, nxt, cov, zero_fix = rec0.random_variables(1)
    assert nxt == 3
    assert len(rvs) == 2
    assert rvs[0].name == 'ETA(1)'
    assert rvs[1].name == 'ETA(2)'
    assert len(cov) == 4
    assert len(zero_fix) == 0
    A = sympy.Matrix([[S('OMEGA(1,1)'), S('OMEGA(2,1)')], [S('OMEGA(2,1)'), S('OMEGA(2,2)')]])
    assert rvs[0].pspace.distribution.sigma == A
    rvs, nxt, cov, zero_fix = rec1.random_variables(nxt, cov)
    assert nxt == 5
    assert len(rvs) == 2
    assert rvs[0].name == 'ETA(3)'
    assert rvs[1].name == 'ETA(4)'
    assert len(cov) == 4
    assert len(zero_fix) == 0
    assert rvs[0].pspace.distribution.sigma == A

    rec = parser.parse("$OMEGA 0 FIX").records[0]
    rvs, _, _, zero_fix = rec.random_variables(1)
    assert len(rvs) == 0
    assert zero_fix == ['ETA(1)']

    rec = parser.parse("$OMEGA  BLOCK(2) FIX 0 0 0").records[0]
    rvs, _, _, zero_fix = rec.random_variables(1)
    assert len(rvs) == 0
    assert zero_fix == ['ETA(1)', 'ETA(2)']

    p = parser.parse("$OMEGA BLOCK(1) 0 FIX\n$OMEGA BLOCK(1) SAME")
    rec0 = p.records[0]
    rec1 = p.records[1]
    rvs, nxt, _, zero_fix = rec0.random_variables(1)
    assert nxt == 2
    assert len(rvs) == 0
    assert zero_fix == ['ETA(1)']
    rvs, nxt, _, zero_fix = rec1.random_variables(2, previous_cov='ZERO')
    assert nxt == 3
    assert len(rvs) == 0
    assert zero_fix == ['ETA(2)']

    rec = parser.parse("$OMEGA BLOCK SAME").records[0]
    A = sympy.Matrix([[1, 0.01], [0.01, 1]])
    rvs, _, _, _ = rec.random_variables(3, A)
    assert len(rvs) == 2
    assert list(rvs)[0].name == 'ETA(3)'
    assert list(rvs)[1].name == 'ETA(4)'
