import os
import subprocess
from pathlib import Path

from pharmpy.plugins.nonmem import conf
from pharmpy.tools.workflows import Task, Workflow


def create_workflow(models):
    wf = Workflow()
    task_names, execute_tasks = [], []

    for i, model in enumerate(models):
        task = Task(f'run-{i}', execute_model, [model, i])
        execute_tasks.append(task)
        task_names.append(task.task_id)

    wf.add_tasks(execute_tasks)
    wf.add_tasks(Task('fit_results', results, [task_names]))

    return wf


def execute_model(model, i):
    path = Path.cwd() / f'NONMEM_run{i}'
    path.mkdir(parents=True, exist_ok=True)
    model = model.copy()
    model.update_source(nofiles=True)
    datapath = model.dataset.pharmpy.write_csv(path=path)
    model.dataset_path = datapath.name  # Make path in $DATA local
    model.write(path=path, force=True)
    args = [
        nmfe_path(),
        model.name + model.source.filename_extension,
        str(Path(model.name).with_suffix('.lst')),
        f'-rundir={str(path)}',
    ]
    subprocess.call(
        args, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
    return model


def results(models):
    for model in models:
        model._modelfit_results = None
        model.modelfit_results.ofv
    return models


def nmfe_path():
    if os.name == 'nt':
        nmfe_candidates = ['nmfe74.bat', 'nmfe75.bat', 'nmfe73.bat']
    else:
        nmfe_candidates = ['nmfe74', 'nmfe75', 'nmfe73']
    path = conf.default_nonmem_path
    if path != Path(''):
        path /= 'run'
    for nmfe in nmfe_candidates:
        candidate_path = path / nmfe
        if candidate_path.is_file():
            path = candidate_path
            break
    else:
        raise FileNotFoundError(f'Cannot find nmfe script for NONMEM ({path})')
    return str(path)
