#!/bin/bash
ansible-playbook --inventory="/ailab/inventory_date/hosts" -c ssh /ailab/inventory_date/playbook.yml
