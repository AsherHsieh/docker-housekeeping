# docker-housekeeping

## check each container on a server:
- whether the name registered inside 'container_registry' file
	- failed: email alert first, after 3 times delete the container
- whether the name follows the naming standard, starting with "<username>" or "project"
	- failed: email alert first, after 3 times delete the container
- whether the container has been stopped for more than 3 months
	- failed: email alert first, after 10 times delete the container
- log deleted containers
- prune image and volume to free up space