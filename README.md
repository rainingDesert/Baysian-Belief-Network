## Readme File

---
### 1. Structure
#### 1.1 Attribute
{attr: type, outcome\}

Example: 
{'light-on': ['nature', 'true', 'false'], 'bowel-problem': ['nature', 'true', 'false']}

Explain: 
"light-on" and "bowel-problem" are attributes, both of type "nature" (I don't know what it is but just written in XML file), and outcome of them are both boolean value (attribute value).

#### 1.2 CPT
{node: [[parents], [children], [value]]}

Example:
{'dog-out': [['bowel-problem', 'family-out'], ['hear-bark'], [0.99, 0.01, 0.97, 0.03, 0.9, 0.1, 0.3, 0.7]]}

Explan: 
"dog-out" has parent nodes "bowel-problem" and "family-out", and has children node "hear-bark". And the CPT is shown as table below.

||dog-out|¬ dog-out|
|:---: |:---: |:---: |
|**bowel-problem**, **family-out**|0.99|0.01|
|**bowel-problem**, **¬ family-out**|0.97|0.03|
|**¬ bowel-problem**, **family-out**|0.9| 0.1|
|**¬ bowel-problem**, **¬ family-out**|0.3|0.7|

---
### 2. Note for Code
#### 2.1 xmlIO.py
1. **class LoadCPT**: parser function rewrite, no need to worry (only when a change in style of XML file)

2. **class GetCPT**: call from outside to get CPT, need to provide file name. The class make use of \textit{xml.sax}.
 
3. Example to call in figure below:
```python
if(__name__ == "__main__"):
    handler = GetCPT("./examples/aima-wet-grass.xml")

    print(handler.tableName)
    print("---------------------------")
    print(handler.attrs)
    print("---------------------------")
    print(handler.CPT)
```
