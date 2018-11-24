# Readme File

---
## 1. Files
### 1.1. Picture
Pictures for report or experiment results.

### 1.2. Code
1. Python file are included in "code" file.
2. "examples" file includes problems to be solved, which are represented as "xml" files.

---
## 2. How to Run
### 2.1. Steps
Step1: under directory of code.
Step2: implement python file with instructions.

### 2.2. Instructions
#### 2.2.1. Choice for \<algorithm name>
1. **enum**: *enumeration* algorithm
2. **elim**: *variable elimination* algorithm
3. **rej**: *rejection sampling*
4. **wei**: *likelihood weighting*
5. **gib**: *Gibbs sampling*

#### 2.2.2. Run alarm problem, wet grass problem or dog problem with exact inference algorithms.
```
$ python3 Exec.py <file> <query> <variable> <value>(...) <algorithm name>
```

Example:
```
$ python3 Exec.py ./examples/aima-alarm.xml B J true M true enum
```

#### 2.2.3. Run alarm problem, wet grass problem or dog problem with approximate inference algorithms.
```
$ python3 Exec.py <sampling time> <file> <query> <variable> <value>(...) <algorithm name>
```

Example:
```
$ python3 Exec.py 1000 ./examples/aima-alarm.xml B J true M true rej
```

#### 2.2.4. Run alterable size tree problem with exact inference algorithms.
```
$ python3 Exec.py test <nodeNumber> <query> <varbale> <value>(...) <algorithm name>
```

Example:
```
$ python3 Exec.py test 10 1 2 true enum
```

#### 2.2.4. Run alterable size tree problem with approximate inference algorithms.
```
$ python3 Exec.py <sampling number> test <nodeNumber> <query> <varbale> <value>(...) <algorithm name>
```

Example:
```
$ python3 Exec.py 1000 test 10 1 2 true rej
```