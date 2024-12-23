#!/bin/bash
for i in $(find . -name "*.i" -type f); do
  sparrow -il -frontend claml $i &>/dev/null || mv $i $i.x && echo $i
done