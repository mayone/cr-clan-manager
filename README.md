# CR Clan Manager
- Utilize Clash Royale API to manage Google Sheets

## Setup APIs
### Google Drive API (OAuth2 credentials and Service Accounts)
1. Go to [Google API Console](https://console.developers.google.com/)
2. Create a new project
3. Search for `Google Drive API` and Enable it
4. Add credentials
	- calling from `Web server`
	- accessing `Application data`
	- `Not` using Google Engine
	- Create service account
		- Role as `Project Editor`
		- Download JSON file
5. Move JSON file to code directory and rename it to `client_secret.json`
6. Share Google Sheet with service account
	- Copy `client_email` inside `client_secret.json`
	- Go to spreadsheet, `Share` it with that account and give it `edit` right

### [Clash Royale API](https://developer.clashroyale.com/#/)
- Generate key and fill `token` into `crapi.json`

## Setup Virtual Environment
```sh
source venv_setup.sh
```

## Execute
```sh
python manager.py
```

## Exit Virtual Environment
```sh
deactivate
```
