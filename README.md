# FOR DEVELOPERS
### **TO CONFIGURE**
```sh
git clone git@github.com:Kalebe16/tiny-code.git
cd tiny-code
pyenv local 3.12.1
python3 -m venv venv
source ./venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### **TO LINT**
```sh
blue .
```

### **TO USE IN COMMON MODE**
```sh
python3 -m tiny_code
```

### **TO USE IN DEBUG MODE**
- First initialize debug console
```sh
textual console
```
- After run app
```sh
textual run --dev ./tiny_code/__main__.py <path-to-any-file>
```
