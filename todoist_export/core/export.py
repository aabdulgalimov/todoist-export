import sys
import argparse
import asyncio
import itertools
import json
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Any

import requests
from todoist_api_python.api_async import TodoistAPIAsync

from todoist_export.core.api_token import get_token, set_token


REQUEST_MAX_ATTEMPTS = 3
REQUEST_RETRY_DELAY_SECONDS = 5


def export(args: argparse.Namespace) -> None:
    if args.file:
        path = Path(args.file)

        if path.is_dir():
            print(f"Path {path.absolute()} is a directory")
            sys.exit(1)

        if path.exists():
            answer = input(f"Overwrite existing file {path.absolute()}? (y/n) ")
            if not answer.startswith(("y", "Y")):
                sys.exit(1)

    data = asyncio.run(_download_data())
    output = json.dumps(data, ensure_ascii=False)

    if args.file:
        with open(args.file, "w") as file:
            file.write(output)
    else:
        print(output)


async def _download_data() -> dict:
    token = get_token() or set_token()
    api = TodoistAPIAsync(token)

    projects, sections, tasks, labels, shared_labels = await asyncio.gather(
        _request(api.get_projects),
        _request(api.get_sections),
        _request(api.get_tasks),
        _request(api.get_labels),
        _request(api.get_shared_labels),
    )

    comments_tasks = itertools.chain(
        (_request(api.get_comments, project_id=x.id) for x in projects),
        (_request(api.get_comments, task_id=x.id) for x in tasks),
    )
    collaborators_tasks = (
        _request(api.get_collaborators, project_id=x.id) for x in projects
    )
    comment_lists, collaborator_lists = await asyncio.gather(
        asyncio.gather(*comments_tasks),
        asyncio.gather(*collaborators_tasks),
    )

    comments = [comment for sublist in comment_lists for comment in sublist]

    collaborators = []
    seen_id_set = set()
    for sublist in collaborator_lists:
        for user in sublist:
            if user.id not in seen_id_set:
                collaborators.append(user)
                seen_id_set.add(user.id)

    return {
        "projects": [asdict(item) for item in projects],
        "sections": [asdict(item) for item in sections],
        "tasks": [asdict(item) for item in tasks],
        "labels": [asdict(item) for item in labels],
        "shared_labels": shared_labels,
        "comments": [asdict(item) for item in comments],
        "collaborators": [asdict(item) for item in collaborators],
    }


async def _request(api_call: Callable, *args, **kwargs) -> Any:
    for attempt in range(1, REQUEST_MAX_ATTEMPTS + 1):
        try:
            return await api_call(*args, **kwargs)
        except requests.exceptions.HTTPError as err:
            if attempt < REQUEST_MAX_ATTEMPTS and err.response.status_code >= 500:
                await asyncio.sleep(REQUEST_RETRY_DELAY_SECONDS)
            else:
                raise
