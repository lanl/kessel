#!/bin/bash

GIT_CHECKOUT="$1"

if [ -z "$GIT_CHECKOUT" ]; then
  echo "Usage: $0 [git_checkout]"
  exit 1
fi

cd "$GIT_CHECKOUT"

git remote update --prune

REMOTE_BRANCHES=$(git branch -r | grep -E 'origin/(master|main|develop|stable)' | grep -v " ->" | sed 's/^[ *]*//')

for REMOTE_BRANCH in $REMOTE_BRANCHES; do
  LOCAL_BRANCH="${REMOTE_BRANCH#origin/}"

  if git show-ref --verify --quiet "refs/heads/$LOCAL_BRANCH"; then
    git checkout "$LOCAL_BRANCH"
    git pull origin "$LOCAL_BRANCH"
  else
    git checkout -b "$LOCAL_BRANCH" "$REMOTE_BRANCH"
  fi
done
