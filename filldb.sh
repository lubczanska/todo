#! /usr/bin/env bash

for value in {1..100} ; do
  ./todo.py add list-auto "task $value" --deadline wednesday --notes 'some example notes'
done