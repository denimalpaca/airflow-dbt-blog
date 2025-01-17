import json
import logging
import os

from airflow.datasets import Dataset
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from include.utils.dbt_env import dbt_env_vars

class DbtDagParser:
    """
    A utility class that parses out a dbt project and creates the respective task groups

    :param model_name: The model to parse
    :param dbt_root_dir: The directory containing the models
    :param dbt_profiles_dir: The directory containing the profiles.yml
    :param dag: The Airflow DAG
    :param dbt_global_cli_flags: Any global flags for the dbt CLI
    :param dbt_target: The dbt target profile (e.g. dev, prod)
    :param env_vars: Dict of environment variables to pass to the generated dbt tasks
    """

    def __init__(
        self,
        model_name: str,
        dbt_root_dir="/usr/local/airflow/include/dbt",
        dbt_profiles_dir="/usr/local/airflow/include/dbt",
        dag=None,
        dbt_global_cli_flags=None,
        dbt_target="dev",
        env_vars: dict = None,
    ):
        self.model_name = model_name
        self.dbt_root_dir = dbt_root_dir
        self.dbt_profiles_dir = dbt_profiles_dir
        self.dag = dag
        self.dbt_global_cli_flags = dbt_global_cli_flags
        self.dbt_target = dbt_target
        self.env_vars = env_vars


        # Parse the manifest and populate the two task groups
        self.make_dbt_task_groups()

    def make_dbt_task(self, node_name, dbt_verb):
        """
        Takes the manifest JSON content and returns a BashOperator task
        to run a dbt command.

        Args:
            node_name: The name of the node
            dbt_verb: 'run' or 'test'

        Returns: A BashOperator task that runs the respective dbt command

        """

        model_name = node_name.split(".")[-1]
        if dbt_verb == "test":
            node_name = node_name.replace("model", "test")  # Just a cosmetic renaming of the task
            outlets = [Dataset(f"DBT://{model_name}".upper())]
        else:
            outlets = None

        # Set default env vars and add to them
        if self.env_vars:
            for key, value in self.env_vars.items():
                dbt_env_vars[key] = value

        dbt_task = BashOperator(
            task_id=node_name,
            bash_command=(
                f"dbt {self.dbt_global_cli_flags} {dbt_verb} --target {self.dbt_target} --models {model_name} \
                  --profiles-dir {self.dbt_profiles_dir} --project-dir {self.dbt_root_dir}/{self.model_name}"
            ),
            env=dbt_env_vars,
            dag=self.dag,
            outlets=outlets,
        )

        # Keeping the log output, it's convenient to see when testing the python code outside of Airflow
        logging.info("Created task: %s", node_name.replace(".", "_"))
        return dbt_task

    def make_dbt_task_groups(self):
        """
        Parse out a JSON file and populates the task groups with dbt tasks

        Returns: None

        """
        project_dir = f"{self.dbt_root_dir}/{self.model_name}"
        manifest_json = load_dbt_manifest(project_dir=project_dir)
        dbt_tasks = {}
        groups = {}

        # Create the tasks for each model
        for node_name in manifest_json["nodes"].keys():
            if node_name.split(".")[0] == "model":
                with TaskGroup(group_id=node_name.replace(".", "_").replace("core", self.model_name)) as node_group:
                    # Make the run nodes
                    dbt_tasks[node_name] = self.make_dbt_task(node_name, "run")
                    # Make the test nodes
                    node_test = node_name.replace("model", "test")
                    dbt_tasks[node_test] = self.make_dbt_task(node_name, "test")
                    dbt_tasks[node_name] >> dbt_tasks[node_test]
                    groups[node_name.replace(".", "_")] = node_group

        # Add upstream and downstream dependencies for each run task
        for node_name in manifest_json["nodes"].keys():
            if node_name.split(".")[0] == "model":
                for upstream_node in manifest_json["nodes"][node_name]["depends_on"]["nodes"]:
                    upstream_node_type = upstream_node.split(".")[0]
                    if upstream_node_type == "model":
                        groups[upstream_node.replace(".", "_")] >> groups[node_name.replace(".", "_")]

    def get_dbt_run_group(self):
        """
        Getter method to retrieve the previously constructed dbt tasks.
        Returns: An Airflow task group with dbt run nodes.
        """
        return self.dbt_run_group

    def get_dbt_test_group(self):
        """
        Getter method to retrieve the previously constructed dbt tasks.
        Returns: An Airflow task group with dbt test nodes.
        """
        return self.dbt_test_group


def load_dbt_manifest(project_dir):
    """
    Helper function to load the dbt manifest file.

    Returns: A JSON object containing the dbt manifest content.

    """
    manifest_path = os.path.join(project_dir, "target/manifest.json")
    with open(manifest_path) as f:
        file_content = json.load(f)
    return file_content
