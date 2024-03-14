git# Basic Flask Application for 3rd Year Gymnasium Students as part of their Maturity Project

## Author
Joana Silva Gonçalves

## Description
The current directory is as a foundational Flask template connected to an SQLite database, serving as a starting point for 3rd-year students at Collège du Sud as for their Maturity Project. With pedagogical objectives in mind, and to provide a fundamental grasp of web application architecture, the project intentionally omits any Object-Relational Mapping (ORM) or data validation modules.

## How to run the project
1. Create a virtual environment
```bash
python -m venv <VIRTUAL-ENVIRONMENT-NAME>
```

2. Activate the virtual environment
  * Windows users:
```bash
<VIRTUAL-ENVIRONMENT-NAME\Scripts\activate
```
  * MacOS users:
```bash
source <VIRTUAL-ENVIRONMENT-NAME>/bin/activate
```

3. Install the dependencies that are in requirements.txt
```bash
pip install -r requirements.txt
```

4. Create a "config.py" file and define necessary configuration variables
   
5. Run the project
```bash
python -m flask run --debug
```
