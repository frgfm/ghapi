# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict

__all__ = ["parse_repo", "parse_pull", "parse_comment", "parse_user", "parse_review"]


def parse_repo(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parses high-level information from the repository payload"""
    return {
        "full_name": payload["full_name"],
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
        "description": payload["description"],
        "is_fork": payload["fork"],
        "is_private": payload["private"],
        "language": payload["language"],
        "stars_count": payload["stargazers_count"],
        "forks_count": payload["forks_count"],
        "watchers_count": payload["watchers_count"],
        "topics": payload["topics"],
        "license": payload["license"],
    }


def parse_pull(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parses high-level information from the pull request payload"""
    return {
        "title": payload["title"],
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
        "closed_at": payload["closed_at"],
        "merged_at": payload["merged_at"],
        "description": payload["body"],
        "labels": payload["labels"],
        "user": payload["user"]["login"],
        "mergeable": payload["mergeable"],
        "changed_files": payload["changed_files"],
        "additions": payload["additions"],
        "deletions": payload["deletions"],
        "num_comments": payload["comments"],
        "num_review_comments": payload["review_comments"],
        "base": {"branch": payload["base"]["ref"], "sha": payload["base"]["sha"]},
        "head": {
            "repo": payload["head"]["repo"]["full_name"],
            "branch": payload["head"]["ref"],
            "sha": payload["head"]["sha"],
        },
    }


def parse_comment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parses high-level information from the comment payload"""
    return {
        "id": payload["id"],
        "user": payload["user"]["login"],
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
        "body": payload["body"],
        "reactions": payload["reactions"],
    }


def parse_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parses high-level information from the users payload"""
    return {
        "login": payload["login"],
        "name": payload["name"],
        "company": payload["company"],
        "blog": payload["blog"],
        "location": payload["location"],
        "bio": payload["bio"],
        "email": payload["email"],
        "twitter_username": payload["twitter_username"],
        "num_followers": payload["followers"],
        "num_public_repos": payload["public_repos"],
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
    }


def parse_review(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parses high-level information from the review payload"""
    return {
        "id": payload["id"],
        "user": payload["user"]["login"],
        "body": payload["body"],
        "state": payload["state"],
        "submitted_at": payload["submitted_at"],
        "commit_id": payload["commit_id"],
    }
