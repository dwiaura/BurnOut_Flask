import model yang telah dilakukan pemodelan (bisa .joblib atau .pkl)

buat venv
1. buat venv: py -m venv venv
2. aktifkan venv: venv\Scripts\Activate

install library
- pip install (masukin lib apa saja. lihat di app.py karena belum pernah di run. masukin lib yang dibawahnya masih ada garis kuning)

buat requirement.txt (untuk mempermudah saat beda laptop. bisa langsung install aja. supaya walaupun versinya beda, tetapi tetap bisa di run)
pip freeze > requirements.txt

lanjut ke app.py
- run program: py app.py (kalau ada error karena ada lib yang belum di install. langsung 'pip install' aja)
- untuk mematikan web nya ctrl + c

buat templates
1. index.html
2. app.py untuk database pakai SQLite

Running on http://127.0.0.1:5000