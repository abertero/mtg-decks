python .\tts.py .\story\002-tarkir\01-the-madness-of-sarkhan-1.txt --output-dir 002-tarkir --voice es-CL-CatalinaNeural
python .\tts.py .\story\002-tarkir\01-the-madness-of-sarkhan-2.txt --output-dir 002-tarkir --voice es-AR-TomasNeural
python .\tts.py .\story\002-tarkir\01-the-madness-of-sarkhan-3.txt --output-dir 002-tarkir --voice es-CL-LorenzoNeural

python .\ambient.py .\dialog\002-tarkir\01-the-madness-of-sarkhan-3.wav --type rain --volume 60

python .\concat.py .\dialog\002-tarkir\01-the-madness-of-sarkhan-1.wav .\dialog\002-tarkir\01-the-madness-of-sarkhan-2.wav .\dialog\002-tarkir\01-the-madness-of-sarkhan-3.mp3 .\dialog\outro.wav -o .\dialog\002-tarkir\01-the-madness-of-sarkhan.mp3