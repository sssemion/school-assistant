# school-assistant
An assistant you won't forget about homework

[Software requirements specification](https://docs.google.com/document/d/10-2b0d08dBXfpZ8_FU2gTfRhVtiyUkso0O42UgCanHc/edit?usp=sharing)

_There will be the description of the project soon_

## Project structure  
`.`  
`├── bot-app`  
`│ ├── bot_config.py*`  
`│ ├── data`  
`│ │ ├── __all_models.py`  
`│ │ └── db_session.py`  
`│ ├── db*`  
`│ ├── __init__.py`  
`│ ├── static`  
`│ │ ├── css`  
`│ │ └── img`  
`│ ├── templates`  
`│ │ └── base.html`  
`│ └── views.py`  
`├── config.py*`  
`├── logs*`  
`│ ├── archive`  
`├── README.md` < You are here  
`└── requirements.txt`  
`└── runner.py*`  
\* Files **_bot-app/bot_config.py_**, **_config.py_**, **_runner.py_** and directories **_db/_**, 
**_logs/_** are ignored by git because they may contain confidential information, such as api-keys and user data
