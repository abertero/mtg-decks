python .\tts.py .\story\002-tarkir\01-1-the-madness-of-sarkhan.txt --output-dir 002-tarkir --voice es-CL-CatalinaNeural
python .\tts.py .\story\002-tarkir\01-2-the-madness-of-sarkhan.txt --output-dir 002-tarkir --voice es-AR-TomasNeural
python .\tts.py .\story\002-tarkir\01-3-the-madness-of-sarkhan.txt --output-dir 002-tarkir --voice es-CL-LorenzoNeural

python .\ambient.py .\dialog\002-tarkir\01-3-the-madness-of-sarkhan.wav --type rain --volume 60

python .\concat.py .\dialog\002-tarkir\01-1-the-madness-of-sarkhan.wav .\dialog\002-tarkir\01-2-the-madness-of-sarkhan.wav .\dialog\002-tarkir\01-3-the-madness-of-sarkhan.mp3 .\dialog\outro.wav -o .\dialog\002-tarkir\01-the-madness-of-sarkhan.mp3