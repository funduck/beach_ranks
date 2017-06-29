# Deploy help

## Setup ansible
If you don't have ansible installed, you should do this step.
### Linux
```{r, engine='bash', count_lines}
$ sudo apt-get install ansible
```
### OS X
```{r, engine='bash', count_lines}
$ brew install ansible
```

After ansible successfully installed you need to generate ssh key
```{r, engine='bash', count_lines}
$ ssh-keygen
```
and provide public part of your key (~/.ssh/id-rsa.pub) to k1nkreet

## Deploying application
To deploy beachranks application you need to run this command from beach_ranks/ansible directory:
```{r, engine='bash', count_lines}
$ ansible-playbook -i hosts deploy.yml
```

This will make those steps
* stop beachranks application
* stop beachranks bot
* update sources from git
* update conda environment
* run tests
* start beachranks application
* start beachranks bot

## Deploying TEST application
test database, directories, bot
```{r, engine='bash', count_lines}
$ ansible-playbook -i hosts deploy_test.yml
```

This will make those steps
* stop beachranks_test application
* stop beachranks_test bot
* update sources from git - branch test
* update conda environment
* run tests
* start beachranks_test application
* start beachranks_test bot

## Change conda environment
To change beachranks conda environment you should edit **beachranks_env.yml** file, and run deploy script.

## Actions which is not provided by our deploy scripts yet
* Install anaconda
* Install postgres
* Update database
