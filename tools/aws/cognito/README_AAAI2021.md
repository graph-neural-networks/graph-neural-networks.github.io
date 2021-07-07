# The instructions for importing AAAI-2021 users

## Environment
1. Please install the requirements: both the project requirements and the cognito requirements
```bash
pip install -r requirements.txt
pip install -r tools/aws/cognito/requirements.txt
```

To test your environment, I recommend you run the following command:
```python
cd tools/aws/cognito
python list.py aws_profile.yml
```
It will export the users to ``all_users.csv``.

2. Create users
```python
python cognito_user.py aaaiusers.csv aws_profile.yml
```

Notes: You will see the output: XXX was created successfully.

I recommend you to run the following command first to ensure there is no problem for importing users:
```python
python cognito_user.py users.csv aws_profile.yml
```
``users.csv`` contains all volunteers which have already been registered. You can see the output: XXX exists. 