import re
import warnings

from sympy import exp

import pharmpy.symbols as symbols
from pharmpy.parameter import Parameter
from pharmpy.statements import Assignment


def boxcox(model, list_of_etas):
    etas = get_etas(model, list_of_etas)
    eta_transformation = EtaTransformation.boxcox(len(etas))
    transform_etas(model, eta_transformation, etas)


def get_etas(model, list_of_etas):
    rvs = model.random_variables

    if len(list_of_etas) == 0:
        etas = rvs.etas
    else:
        etas = []
        for eta in list_of_etas:
            try:
                etas.append(rvs[eta])
            except KeyError:
                warnings.warn(f'Random variable "{eta}" does not exist')

    return etas


def transform_etas(model, eta_transformation, etas):
    etas_assignment, etas_subs = create_etas(etas)
    thetas = create_thetas(model, len(etas))

    eta_transformation.apply(etas_assignment, thetas)
    statements_new = eta_transformation.assignments
    sset = model.statements
    sset.subs(etas_subs)

    statements_new.extend(sset)

    model.statements = statements_new


def create_etas(etas_original):
    etas_subs = dict()
    etas_assignment = dict()

    for i, eta in enumerate(etas_original):
        eta_no = int(re.findall(r'\d', eta.name)[0])
        etas_subs[eta.name] = f'ETAB{eta_no}'
        etas_assignment[f'etab{i + 1}'] = f'ETAB{eta_no}'
        etas_assignment[f'eta{i + 1}'] = f'ETA({eta_no})'

    return etas_assignment, etas_subs


def create_thetas(model, no_of_thetas):
    pset = model.parameters
    thetas = dict()
    theta_name = str(model.create_symbol(stem='COVEFF', force_numbering=True))

    if no_of_thetas == 1:
        pset.add(Parameter(theta_name, 0.01, -3, 3))
        thetas['theta1'] = theta_name
    else:
        theta_no = int(re.findall(r'\d', theta_name)[0])

        for i in range(1, no_of_thetas+1):
            pset.add(Parameter(theta_name, 0.01, -3, 3))
            thetas[f'theta{i}'] = theta_name
            theta_name = f'COVEFF{theta_no + i}'

    model.parameters = pset

    return thetas


class EtaTransformation:
    def __init__(self, assignments):
        self.assignments = assignments

    def apply(self, etas, thetas):
        for assignment in self.assignments:
            assignment.subs(etas)
            assignment.subs(thetas)

    @classmethod
    def boxcox(cls, no_of_etas):
        assignments = []
        for i in range(1, no_of_etas + 1):
            symbol = S(f'etab{i}')
            expression = ((exp(S(f'eta{i}')**(S(f'theta{i}')-1))) /
                          (S(f'theta{i}')))

            assignment = Assignment(symbol, expression)
            assignments.append(assignment)

        return cls(assignments)


def S(x):
    return symbols.symbol(x)
