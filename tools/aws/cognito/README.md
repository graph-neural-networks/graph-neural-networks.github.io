We use AWS Cognito to manage user pools.
See [here](https://github.com/acl-org/acl-2020-virtual-conference/issues/53) for documents.

This folder contains some helper scripts to manage the user pool.

This repo is forked from [acl](https://github.com/acl-org/acl-2020-virtual-conference-tools) and modified for AAAI-2021.

* create batch user from .csv file.
```python
python cognito_user.py users.csv aws_profile.yml
```

* reset password for specific users (there is a problem with SMS)
```python

```

* reset specific password for user
```python
python reset_password.py -p Aa123456 aws_profile.yml shenkai@zju.edu.cn
```

* extract user list from cognito
```python
 python list.py aws_profile.yml
```