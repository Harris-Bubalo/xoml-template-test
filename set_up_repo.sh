#! /bin/bash

# Once a repo has been created from xoml-template, clone the repo to your local machine and run this script in the base dir 

set -e

git fetch origin main

git checkout main
git checkout -b dev
git push origin dev

git checkout main
git checkout -b stage
git push origin stage

git checkout main

repo_name=$(basename `git rev-parse --show-toplevel`)

gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/xometry/$repo_name/branches/main/protection \
    -F "required_status_checks[strict]=true" \
    -f "required_status_checks[contexts][]=check-main-branch" \
    -F "enforce_admins=true" \
    -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
    -F "required_pull_request_reviews[required_approving_review_count]=1" \
    -F "required_linear_history=true" \
    -F "allow_force_pushes=false" \
    -F "restrictions=null" &&
gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/xometry/$repo_name/branches/stage/protection \
    -F "required_status_checks[strict]=true" \
    -f "required_status_checks[contexts][]=check-stage-branch" \
    -F "enforce_admins=true" \
    -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
    -F "required_pull_request_reviews[required_approving_review_count]=1" \
    -F "required_linear_history=true" \
    -F "allow_force_pushes=false" \
    -F "allow_deletion=false" \
    -F "restrictions=null" &&
gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/xometry/$repo_name/branches/dev/protection \
    -F "required_status_checks=null" \
    -F "enforce_admins=true" \
    -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
    -F "required_pull_request_reviews[required_approving_review_count]=1" \
    -F "required_linear_history=true" \
    -F "allow_force_pushes=false" \
    -F "allow_deletion=false" \
    -F "restrictions=null" &&
gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/xometry/$repo_name \
    -F "has_issues=false" \
    -F "has_projects=false" \
    -F "has_wiki=false" \
    -F "allow_forking=false" \
    -F "allow_squash_merge=true" \
    -F "allow_merge_commit=false" \
    -F "allow_rebase_merge=false" \
    -F "delete_branch_on_merge=false" \
    -f "squash_merge_commit_title=PR_TITLE" \
    -f "squash_merge_commit_message=PR_BODY"