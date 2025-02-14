from pathlib import Path

import pharmpy.execute as execute

from .psn_helpers import tool_name


class RunDirectory:
    def __init__(self, method_name, path=None):
        i = 1
        while True:
            name = f'{method_name}_dir{i}'
            if path is not None:
                test_path = path / name
            else:
                test_path = Path(name)
            if not test_path.exists():
                test_path.mkdir()
                self.path = test_path
                self.models_path = test_path / 'models'
                self.models_path.mkdir()
                break
            i += 1


class Tool:
    def __init__(self, dispatcher=None, database=None, workflow_creator=None, path=None):
        self.rundir = RunDirectory(type(self).__name__.lower(), path=path)
        if dispatcher is None:
            self.dispatcher = execute.default_dispatcher
        else:
            self.dispatcher = dispatcher
        if database is None:
            self.database = execute.default_database
        else:
            self.database = database
        if workflow_creator is None:
            import pharmpy.plugins.nonmem.run

            self.workflow_creator = pharmpy.plugins.nonmem.run.create_workflow
        else:
            self.workflow_creator = workflow_creator


def create_results(path, **kwargs):
    name = tool_name(path)
    # FIXME: Do something automatic here
    if name == 'qa':
        from pharmpy.tools.qa.results import psn_qa_results

        res = psn_qa_results(path, **kwargs)
    elif name == 'bootstrap':
        from pharmpy.tools.bootstrap.results import psn_bootstrap_results

        res = psn_bootstrap_results(path, **kwargs)
    elif name == 'cdd':
        from pharmpy.tools.cdd.results import psn_cdd_results

        res = psn_cdd_results(path, **kwargs)
    elif name == 'frem':
        from pharmpy.tools.frem.results import psn_frem_results

        res = psn_frem_results(path, **kwargs)
    elif name == 'linearize':
        from pharmpy.tools.linearize.results import psn_linearize_results

        res = psn_linearize_results(path, **kwargs)
    elif name == 'resmod':
        from pharmpy.tools.resmod.results import psn_resmod_results

        res = psn_resmod_results(path, **kwargs)

    elif name == 'scm':
        from pharmpy.tools.scm.results import psn_scm_results

        res = psn_scm_results(path, **kwargs)
    elif name == 'simeval':
        from pharmpy.tools.simeval.results import psn_simeval_results

        res = psn_simeval_results(path, **kwargs)
    else:
        raise ValueError("Not a valid run directory")
    return res
