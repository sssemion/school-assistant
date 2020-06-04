# school-assistant
A chat-bot that won't let you forget about homework

[Software requirements specification](https://docs.google.com/document/d/10-2b0d08dBXfpZ8_FU2gTfRhVtiyUkso0O42UgCanHc/edit?usp=sharing)

## Project structure  

`.`  
`├── bot_app`  
`│   ├── __init__.py`  
`│   ├── bot_config.py*`  
`│   ├── controllers.py`  
`│   ├── data`  
`│   │   ├── __all_models.py`  
`│   │   ├── api_session.py`  
`│   │   ├── db_session.py`  
`│   │   ├── mark.py`  
`│   │   ├── student.py`  
`│   │   └── subject.py`  
`│   ├── db*`  
`│   │   └── school_assistant.sqlite`  
`│   ├── form_models`  
`│   │   ├── ReigsterForm.py`  
`│   ├── services`  
`│   │   ├── CRYPTO_KEYS.py*`    
`│   │   ├── school_services.py`  
`│   │   └── vk_services.py`  
`│   ├── static`  
`│   └── templates`  
`│       ├── base.html`  
`│       ├── register.html`  
`│       └── success.html`  
`├── config.py*`  
`├── logs*`  
`├── README.md` < You are here  
`├── requirements.txt`  
`└── runner.py*`  
\* Files **_bot-app/bot_config.py_**, **_config.py_**, **_runner.py_** and directories **_db/_**, 
**_logs/_** are ignored by git because they may contain confidential information, such as api-keys and user data
