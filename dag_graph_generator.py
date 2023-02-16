from pprint import pprint
import json
import logging
import sys
from airflow.models import DAG
from airflow.models.baseoperator import BaseOperator
from airflow.models.xcom import BaseXCom
from airflow.models.xcom_arg import XComArg
from airflow.hooks.base import BaseHook
from airflow.sensors.base import BaseSensorOperator
from airflow.decorators import task
from airflow.utils.dates import datetime, timedelta, timezone, croniter

from importlib import import_module
from types import ModuleType
from typing import Any, Dict, List, Set, Union
from warnings import catch_warnings, simplefilter


logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

# Reference data mapping a missing object's name to a Base* Airflow type.
TYPE_BASE_MAPPING = dict(
    operator=dict(path="airflow.models.baseoperator", base=BaseOperator),
    transfer=dict(path="airflow.models.baseoperator", base=BaseOperator),
    hook=dict(path="airflow.hooks.base", base=BaseHook),
    sensor=dict(path="airflow.sensors.base", base=BaseSensorOperator),
)


class _Dummy:
    """
    This class is used to create a blank entry in sys.modules for classes which are
    not based on Base* Airflow modules.
    """

    def __init__(self, *args, **kwargs):
        pass


class DagGraphGenerator:
    """
    Creates a JSON reprsentation of DAGs defined in DAG modules.  The output is
    similar to the Tree View in the Airflow UI.

    Since it is not feasible to import every Provider in Airflow and to render the DAG
    graph a `DAG` object must be instantiated, this generator replaces modules that are
    not natively installed in the environment to their Base* Airflow equivalents.  This
    logic will recursively attempt to import the DAG module while handling
    `ModuleNotFoundError`, `ImportError`, and `AttributeError` exceptions.

    :param full_module_name: module name to be imported.
        For example:
            `airflow.example_dags.example_bash_operator`
    :type full_module_name: str
    """

    def __init__(self, full_module_name: str) -> None:
        self.full_module_name = full_module_name

    @staticmethod
    def _handle_exceptions(exception: Exception) -> None:
        exception_type = type(exception).__name__
        if exception_type == "ModuleNotFoundError":
            # Find the entry from the TYPE_BASE_MAPPING reference dictionary based on
            # the name of the missing module (e.g. if the module name is
            # `some_provider.stuff.operators`, the "operator" entry would be returned.)
            base_path = tuple(
                metadata["path"]
                for type, metadata in TYPE_BASE_MAPPING.items()
                if type in exception.name.lower()
            )
            # If a TYPE_BASE_MAPPING entry can be returned -- meaning the missing module
            # is similar to a Base* Airflow module, add the missing module to
            # sys.modules at the base path.  Otherwise, register a placeholder module in
            # sys.modules with the missing module's name.
            if base_path:
                sys.modules[exception.name] = sys.modules[base_path[0]]
            else:
                sys.modules[exception.name] = ModuleType(exception.name)
        elif exception_type == "ImportError":
            missing = exception.args[0].split("'")[1]
            missing_path = exception.args[0].split("from", 1)[1].split("'")[1]
            # Retrieve the entry from the TYPE_BASE_MAPPING reference dictionary based
            # on the path of the Base* Airflow type.  Using the path of the missing
            # object is used because the missing object should already be applied to a
            # Base* Airflow module (i.e. the ImportError is being thrown based on an
            # import from a Base* Airflow type.)
            base = tuple(
                metadata["base"]
                for type, metadata in TYPE_BASE_MAPPING.items()
                if metadata["path"] == missing_path
            )
            # If a TYPE_BASE_MAPPING entry can be returned, register an entry of the
            # missing object at the Base* Airflow path using the Base* Airflow object's
            # attributes.  Otherwise, register a placeholder entry using the _Dummy
            # class object.
            if base:
                base_dict = {key: value for key,
                             value in base[0].__dict__.items()}
                sys.modules[f"{exception.name}.{missing}"] = type(
                    missing, (base[0],), base_dict
                )
            else:
                sys.modules[f"{exception.name}.{missing}"] = type(
                    missing, (_Dummy,), dict()
                )
        elif exception_type == "AttributeError":
            attr_object_name = exception.args[0].split("'")[1]
            missing_attr_name = exception.args[0].split("'")[3]
            # Find object entry in sys.modules to add missing attribute to.
            object_path = tuple(
                path for path in sys.modules.keys() if path.endswith(attr_object_name)
            )
            # Use the `setattr()` method to dynamically add the missing attribute to the
            # offending object if an existing object has been registered in sys.modules.
            if object_path:
                setattr(sys.modules[object_path[0]], missing_attr_name, None)
        else:
            exception_type, value, traceback = sys.exc_info()
            # print(exception_type, value, traceback)
            logger.info(
                "DAG graph data could not be generated. The following exception was raised: "
                f"{exception_type.__name__}: {exception.with_traceback(traceback)}"
            )
            raise exception.with_traceback(traceback)

    def _mock_import(self) -> ModuleType:
        try:
            # Attempt to import the DAG module straight away.
            return import_module(self.full_module_name)

        except Exception as e:
            DagGraphGenerator._handle_exceptions(e)
            # Recursively call the _mock_import() function after handling exceptions.
            return self._mock_import()

    def _recurse_nodes(
        self, task: Union[BaseOperator, BaseSensorOperator], visited: set
    ) -> Dict[str, Any]:
        # from pprint import pprint

        # pprint(dir(task))
        visited.add(task)
        task_id = task.task_id
        # Define a node of a the branch for a given input task.
        node = dict(
            id=task.task_id,
            data=dict(
                operator=task.task_type,
                # template_fields=task.template_fields,
                # output=task.output.key,
            ),
        )
        # If the input task has downstream task dependencies, recurse those child tasks.
        if task.downstream_list:
            children = list(
                self._recurse_nodes(t, visited) for t in task.downstream_list
            )
            # D3 tree uses children vs _children to define what is expanded or not.
            # The following block makes it such that repeated nodes are collapsed by
            # default.
            if task.task_id not in self.expanded:
                children_key = "children"
                self.expanded.add(task.task_id)
            else:
                children_key = "_children"

            node[children_key] = children

        return node

    def build_task_dependency_tree(self) -> List[List[Dict[str, Any]]]:
        # Init local variables for recursion of branches.
        self.expanded = set()
        # Import the DAG module to begin building the task dependency tree.
        # Catching PendingDeprecationWarnings thrown by the BaseOperator for "illegal
        # arguments" aka kwargs not explicitly used in the BaseOperator.
        with catch_warnings():
            simplefilter("ignore", category=PendingDeprecationWarning)

            dag_module = self._mock_import()
            print(dag_module.__dict__.items())

        # Build a list of attributes of the DAG module which are DAG objects.
        if dag_module:
            dags = list(
                key
                for key, value in dag_module.__dict__.items()
                if isinstance(value, DAG)
            )
            print(dags)
            # Initialize the single task dependency tree for the DAG module.
            dag_tree = list()

            for _dag in dags:
                dag = getattr(dag_module, _dag)
                # Setting a limit of nodes visited as done in Airflow.
                # Begin building task dependency tree starting with roots of a DAG.
                root_tree = list()
                for root in dag.roots:
                    print(root.output)
                    # from pprint import pprint
                    # pprint(vars(root))
                    branch = dict(
                        id=root.task_id,
                        data=dict(
                            operator=root.task_type,
                            # template_fields=root.template_fields,
                            # output=root.output[root.output.key],
                        ),
                        children=list(
                            self._recurse_nodes(task=task, visited=set())
                            for task in root.downstream_list
                        ),
                    )
                    # Add each root branch to the overall task dependency tree.
                    root_tree.append(branch)

                # Unfortunately there are example DAG modules which contain multiple
                # DAGs. Collecting all DAG trees into a single output.
                dag_tree.append(root_tree)

            return json.dumps(dag_tree)


# module_name = "dags.example_s3_bucket"
# module_name = "dags.bigquery_sensors"
# module_name = "dags.xcomargs"
# module_name = "dags.greenplum_advanced"
# module_name = "dags.example_fivetran"
# module_name = "dags.dummy_dag"
# module_name = "dags.dummy_dag0"
# module_name = "dags.write_data"
# module_name = "dags.test_dynamic_pipelines"
# module_name = "dags.example-automl-vision-classification"
# module_name = "dags.example_great_expectations_dag"
# module_name = "dags.bigquery_example"
# module_name = "dags.mysql_sample_dag"
# module_name = "dags.generic_recipe_sample_dag"
# module_name = "dags.lineage_backend_demo"
# module_name = "dags.example_passing_params_via_test_command"
# module_name = "dags.example_kubernetes"

## FAILING (some work locally)

# module_name = "dags.lineage_emission_dag" # **
# module_name = "dags.task_flow_ray_pandas_example" # **
# module_name = "dags.example-facebook-ads-to-gcs"  # **
# module_name = "dags.example-cloud-memorystore" # **
# module_name = "dags.example-workflows" # **
# module_name = "dags.example-qubole" # *works locally but not in cloud
# module_name = "dags.example-bigquery-dts" # *works locally but not in cloud
# module_name = "dags.example_docker_swarm" # *works locally but not in cloud
# module_name = "dags.example_docker_copy_data" # *works locally but not in cloud
# module_name = "dags.example-tableau-refresh-workbook" # *works locally but not in cloud
# module_name = "dags.example-salesforce-to-gcs" # *works locally but not in cloud
# module_name = "dags.example-docker" # *works locally but not in cloud
# module_name = "dags.example-jenkins-job-trigger" # *works locally but not in cloud
# module_name = "dags.example-telegram" # *works locally but not in cloud
# module_name = "dags.example_fivetran_dbt" # ** needs variable explicitly

## CERTIFIED
# module_name = "dags.certified.greenplum-advanced"
# module_name = "dags.certified.covid_to_azure_blob"
# module_name = "dags.certified.azure-data-factory-dag"
# module_name = "dags.certified.databricks"
# module_name = "dags.certified.azure-container-instance"
# module_name = "dags.certified.azure-data-explorer"
# module_name = "dags.certified.dbt-basic"
module_name = "dags.extract_dag"


## CERTIFIED FAILING
# module_name = "dags.certified.xgboost_pandas_breast_cancer_tune" #  **
# module_name = "dags.certified.task_flow_ray_pandas_example"  #  **
# module_name = "dags.certified.task_flow_xgboost_modin" #  **
# module_name = "dags.certified.dbt-advanced" # ** requires local file to generate tasks
# module_name = "dags.certified.dbt-elt-demo" # ** requires local file to generate tasks


dag_graph = DagGraphGenerator(module_name)
# dag_graph = DagGraphGenerator(sys.argv[1])
task_dependency_tree = dag_graph.build_task_dependency_tree()


pprint(task_dependency_tree)

if task_dependency_tree:
    with open("task_dependency_tree.json", "w") as output:
        output.write(task_dependency_tree)
