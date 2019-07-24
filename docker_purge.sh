#!/bin/bash
ansible-playbook --inventory="inventory_date/hosts" -c ssh inventory_date/playbook.yml
