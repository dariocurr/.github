import os

import nox
import yaml


def _get_action_version(
    session: nox.Session,
    action_file_path: str = "action.yml",
) -> str:
    with open(file=action_file_path) as stream:
        action = yaml.safe_load(stream=stream)
    steps = action["runs"]["steps"]
    action_to_track = session.env["ACTION_TO_TRACK"]
    for step in steps:
        used_action: str = step.get("uses", "")
        if used_action.startswith(action_to_track):
            return used_action.split("@")[1]
    raise ValueError(f"Action {action_to_track} not found in {action_file_path}")


def _set_output(
    session: nox.Session,
    key: str,
    value: str,
):
    output_file = session.env["GITHUB_OUTPUT"]
    with open(file=output_file, mode="a") as f:
        f.write(f"{key}={value}\n")


@nox.session
def update_tags(session: nox.Session):
    os.chdir(session.env["GITHUB_WORKSPACE"])
    version = _get_action_version(session=session)
    _set_output(
        session=session,
        key="tag",
        value=version,
    )
    tags = [version]
    version_parts = version.split(".")
    len_version_parts = len(version_parts)
    if len_version_parts > 1:
        major = version_parts[0]
        tags.append(major)
    if len_version_parts > 2:
        minor = ".".join(version_parts[0:2])
        tags.append(minor)
    session.run(
        "git",
        "config",
        "user.name",
        "github-actions",
        external=True,
        silent=False,
    )
    session.run(
        "git",
        "config",
        "user.email",
        "github-actions@users.noreply.github.com",
        external=True,
        silent=False,
    )
    for tag in tags:
        session.run(
            "git",
            "tag",
            "--annotate",
            "--force",
            "--message",
            "",
            tag,
            external=True,
        )
        session.run(
            "git",
            "push",
            "--force",
            "origin",
            tag,
            external=True,
        )
