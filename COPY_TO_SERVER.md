# Copy to Server - Simple Checklist

## What to Copy

Only copy **THREE things** to the server:

```
1. production/               ← Everything you need is inside this folder
2. README.md                ← (Optional) Main documentation
3. LINUX_DEPLOYMENT.md      ← (Optional) Deployment instructions
```

## Commands to Use

### On your computer (Windows):

```bash
# Using SCP (secure copy):
scp -r C:\Users\sj_89\Desktop\kaggle\production user@server:/home/user/
scp C:\Users\sj_89\Desktop\kaggle\README.md user@server:/home/user/
scp C:\Users\sj_89\Desktop\kaggle\LINUX_DEPLOYMENT.md user@server:/home/user/

# Or using WinSCP (GUI tool)
# Or using FileZilla (FTP)
```

### On the Linux server:

```bash
# Extract and verify
cd /home/user
ls -lh production/
du -sh production/

# Should see:
# production/
# ├── python_api/
# ├── nodejs_client/
# └── docs/
```

## What's Inside "production" Folder

```
production/
├── python_api/
│   ├── captcha_api.py               ✓ Flask REST API
│   ├── requirements.txt             ✓ Python packages
│   └── models/
│       ├── model.keras              ✓ AI model (included!)
│       └── labels.csv               ✓ Alphabet (included!)
│
├── nodejs_client/
│   ├── captcha_client_nodejs.js     ✓ API client
│   ├── captcha_solver_example.js    ✓ Puppeteer example
│   └── package.json                 ✓ NPM packages
│
├── docs/
│   ├── DEPLOYMENT.md                ✓ Deployment guide
│   ├── API.md                       ✓ API documentation
│   └── PACKAGE.md                   ✓ Package info
│
└── README.md                        ✓ Quick start
```

## Start on Server (5 Commands)

```bash
# 1. Go to production folder
cd production/

# 2. Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r python_api/requirements.txt

# 3. Start Python API (Terminal 1)
python3 python_api/captcha_api.py --host 0.0.0.0 --port 5000

# 4. In another terminal - Setup Node.js
cd production/nodejs_client
npm install

# 5. Start Node.js bot (Terminal 2)
node captcha_solver_example.js --url http://localhost:5000
```

## Test It Works

```bash
# In another terminal, test the API:
curl http://localhost:5000/health

# Should return:
# {"status":"ok","model_loaded":true,"version":"1.0"}
```

## What Files to DELETE (Optional)

You can safely delete these from your local machine:

```bash
rm -rf final-results/          # Old model location
rm -rf images/                 # Test data  
rm -rf test_captchas/          # Test results
rm -rf real_results/           # Test results
rm -rf results/                # Test results
rm -f *.ipynb                  # Jupyter notebooks
rm -f train.py                 # Training script
rm -f prepare_kaggle_data.py   # Old script
rm -f check_model_alphabet.py  # Old script
rm -f *.zip                    # Old packages
```

This will save ~500 MB space.

## Important Notes

✅ **Model is INCLUDED** in production/python_api/models/model.keras
✅ **Labels are INCLUDED** in production/python_api/models/labels.csv
✅ **All code is READY** - no modifications needed
✅ **Fully documented** - instructions included

❌ No need to copy anything else
❌ No need to setup anything else
❌ No need to install TensorFlow separately

## Troubleshooting

If something doesn't work:

1. Check Python version: `python3 --version` (need 3.8+)
2. Check Node.js: `node --version` (need 14+)
3. Check model file exists: `ls -lh production/python_api/models/`
4. Check ports available: `netstat -tlnp | grep 5000`

## That's All!

Just copy the "production" folder and follow the 5 commands above.

Questions? Check production/docs/DEPLOYMENT.md

Good luck! ���
