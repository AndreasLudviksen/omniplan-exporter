import logging
import argparse
from omniplan_exporter.db import operations
from omniplan_exporter.jira.integration import create_jira_task
from omniplan_exporter.config import JIRA_BASE_URL  # Added import

logger = logging.getLogger(__name__)


def create_epic_and_subtasks(conn, task_uid, bearer_token, dry_run=False):
    """
    Creates a Jira task of type "Epos" for the given task UID and Jira tasks
    of type "Forbedring" for all its subtasks.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        task_uid (str): The UID of the OmniPlan task.
        bearer_token (str): The bearer token for Jira API authentication.
        dry_run (bool): If True, no changes will be made; only logs the actions.

    Returns:
        dict: A dictionary containing the created epic and subtasks details.
    """
    logger.info(f"Creating Jira tasks for OmniPlan task UID: {task_uid}")

    # Fetch the main task name using the new function
    main_task_name = operations.fetch_task_name_by_uid(conn, task_uid)
    if not main_task_name:
        logger.error(f"No task found with UID: {task_uid}")
        return None

    if dry_run:
        logger.info(f"[DRY RUN] Would create epic with summary: {main_task_name}")
        epic = {"key": "DRY-RUN-EPIC"}
    else:
        # Create the epic in Jira
        epic = create_jira_task(
            summary=main_task_name,
            description="",
            issue_type="Epos",
            jira_base_url=JIRA_BASE_URL,
            bearer_token=bearer_token,
            epic_name=main_task_name,
        )
        if not epic:
            logger.error(f"Failed to create epic for task UID: {task_uid}")
            return None

    epic_key = epic.get("key")
    logger.info(f"Created epic with key: {epic_key}")

    # Fetch subtasks for the main task
    subtasks, _ = operations.get_sub_tasks(conn, task_uid)
    created_subtasks = []

    for subtask in subtasks:
        subtask_name = subtask[1]

        if dry_run:
            logger.info(
                f"[DRY RUN] Would create subtask with summary: {subtask_name} "
                f"with epic link: {epic_key}"
            )
            created_subtasks.append({"key": "DRY-RUN-SUBTASK"})
        else:
            # Create a subtask in Jira with Epic Link set to the created epic
            subtask_result = create_jira_task(
                summary=subtask_name,
                description="",
                issue_type="Forbedring",
                jira_base_url=JIRA_BASE_URL,
                bearer_token=bearer_token,
                epic_link=epic_key,
            )
            if subtask_result:
                created_subtasks.append(subtask_result)
                logger.info(f"Created subtask with key: {subtask_result.get('key')}")
            else:
                logger.error(f"Failed to create subtask: {subtask_name}")

    return {
        "epic": epic,
        "subtasks": created_subtasks,
    }


def main():
    """
    Main function to create a Jira epic and subtasks.
    """
    logger.info("Starting the create Jira epic and subtasks script.")
    parser = argparse.ArgumentParser(
        description=("Create a Jira epic and its subtasks.")
    )
    parser.add_argument(
        "--bearer-token",
        required=True,
        help="Bearer token for Jira API authentication.",
    )
    parser.add_argument(
        "--omniplan-uid",
        required=True,
        help="UID of the OmniPlan task.",
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to the SQLite database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, no changes will be made; only logs the actions.",
    )
    args = parser.parse_args()

    try:
        # Connect to the SQLite database
        conn = operations.create_connection(args.db_path)

        # Fetch the OmniPlan task details
        task_name = operations.fetch_task_name_by_uid(conn, args.omniplan_uid)
        if not task_name:
            logger.error(f"No task found with UID: {args.omniplan_uid}")
            return

        create_epic_and_subtasks(
            conn, args.omniplan_uid, args.bearer_token, dry_run=args.dry_run
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if "conn" in locals() and conn:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
